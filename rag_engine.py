"""
RAG Engine - 检索增强生成引擎（轻量版）
功能：读取 rag_data/ 下的文本文件，分块、用 TF-IDF 建索引，提供检索接口。

工作原理：
1. 读取 rag_data/ 下所有 .txt 文件
2. 按段落分块（每块约 300-500 字，有少量重叠）
3. 用 sklearn 的 TfidfVectorizer 将每块转为 TF-IDF 向量（无需深度学习，内存约 100MB 内）
4. 持久化到 rag_index/ 目录
5. 查询时：用户问题 → TF-IDF 向量 → 余弦相似度 top-k → 返回最相关的文本块

适用于 Render 等 512MB 内存的免费环境。
"""

import os
import pickle

# ============ 配置 ============
RAG_DATA_DIR = os.path.join(os.path.dirname(__file__), 'rag_data')
RAG_INDEX_DIR = os.path.join(os.path.dirname(__file__), 'rag_index')
CHUNK_SIZE = 400        # 每块大约的字符数
CHUNK_OVERLAP = 80      # 相邻块之间的重叠字符数
TOP_K = 5                # 检索返回的最相关块数

# ============ 全局变量（延迟加载）============
_vectorizer = None
_matrix = None   # scipy.sparse 矩阵
_chunks = None


# ============ 1. 读取数据 ============
def load_documents():
    """读取 rag_data/ 目录下所有 .txt 文件"""
    documents = []
    if not os.path.exists(RAG_DATA_DIR):
        print(f"[RAG] 警告：数据目录不存在: {RAG_DATA_DIR}")
        return documents

    for filename in sorted(os.listdir(RAG_DATA_DIR)):
        if filename.endswith('.txt'):
            filepath = os.path.join(RAG_DATA_DIR, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            if content:
                documents.append({
                    'filename': filename,
                    'content': content
                })
    print(f"[RAG] 加载了 {len(documents)} 个文档。")
    return documents


# ============ 2. 分块 ============
def split_into_chunks(documents):
    """
    把文档分成较小的块。
    策略：先按段落（双换行）分，如果单个段落太长则按字符数再切。
    """
    all_chunks = []

    for doc in documents:
        source = doc['filename']
        text = doc['content']

        # 先按双换行分段落
        paragraphs = text.split('\n\n')

        current_chunk = ""
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            # 如果当前块 + 新段落不超限，合并
            if len(current_chunk) + len(para) + 2 <= CHUNK_SIZE:
                current_chunk = (current_chunk + "\n\n" + para).strip()
            else:
                # 当前块已满，保存并开始新块
                if current_chunk:
                    all_chunks.append({
                        'text': current_chunk,
                        'source': source
                    })

                # 如果单个段落就超过 CHUNK_SIZE，需要拆分
                if len(para) > CHUNK_SIZE:
                    for i in range(0, len(para), CHUNK_SIZE - CHUNK_OVERLAP):
                        sub = para[i:i + CHUNK_SIZE]
                        if sub.strip():
                            all_chunks.append({
                                'text': sub.strip(),
                                'source': source
                            })
                    current_chunk = ""
                else:
                    current_chunk = para

        # 别忘了最后一块
        if current_chunk.strip():
            all_chunks.append({
                'text': current_chunk.strip(),
                'source': source
            })

    print(f"[RAG] 共分成 {len(all_chunks)} 个文本块。")
    return all_chunks


# ============ 3. 建立 TF-IDF 索引 ============
def build_index(chunks):
    """
    用 TF-IDF 为所有文本块建索引并持久化。
    使用字符级 n-gram，兼顾中英文，无需额外分词依赖。
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    import scipy.sparse

    global _vectorizer, _matrix, _chunks

    texts = [chunk['text'] for chunk in chunks]

    # 字符级 n-gram，适合中英文混合；max_features 控制内存
    vectorizer = TfidfVectorizer(
        analyzer='char',
        ngram_range=(2, 4),
        max_features=50000,
        sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform(texts)

    os.makedirs(RAG_INDEX_DIR, exist_ok=True)
    vectorizer_path = os.path.join(RAG_INDEX_DIR, 'vectorizer.pkl')
    matrix_path = os.path.join(RAG_INDEX_DIR, 'tfidf_matrix.npz')
    chunks_path = os.path.join(RAG_INDEX_DIR, 'chunks.pkl')

    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)
    scipy.sparse.save_npz(matrix_path, matrix)
    with open(chunks_path, 'wb') as f:
        pickle.dump(chunks, f)

    _vectorizer = vectorizer
    _matrix = matrix
    _chunks = chunks

    print(f"[RAG] TF-IDF 索引建立完成，共 {len(chunks)} 个文本块。")
    print(f"[RAG] 索引已保存到: {RAG_INDEX_DIR}")

    # 返回兼容 build_rag.py 的 (index_like, chunks)
    class _IndexLike:
        ntotal = len(chunks)
    return (_IndexLike(), chunks)


# ============ 4. 加载已有索引 ============
def load_index():
    """从磁盘加载已建好的 TF-IDF 索引和文本块"""
    global _vectorizer, _matrix, _chunks
    import scipy.sparse

    vectorizer_path = os.path.join(RAG_INDEX_DIR, 'vectorizer.pkl')
    matrix_path = os.path.join(RAG_INDEX_DIR, 'tfidf_matrix.npz')
    chunks_path = os.path.join(RAG_INDEX_DIR, 'chunks.pkl')

    if not os.path.exists(vectorizer_path) or not os.path.exists(matrix_path) or not os.path.exists(chunks_path):
        print("[RAG] 未找到已有索引，将重新构建...")
        documents = load_documents()
        if not documents:
            print("[RAG] 没有数据文件，跳过索引构建。")
            return None, None
        chunks = split_into_chunks(documents)
        return build_index(chunks)

    with open(vectorizer_path, 'rb') as f:
        _vectorizer = pickle.load(f)
    _matrix = scipy.sparse.load_npz(matrix_path)
    with open(chunks_path, 'rb') as f:
        _chunks = pickle.load(f)

    print(f"[RAG] 已加载索引：{_matrix.shape[0]} 个文本块。")
    return _vectorizer, _chunks


# ============ 5. 检索 ============
def search(query, top_k=TOP_K):
    """
    核心检索函数：给定用户问题，返回最相关的 top_k 个文本块。

    返回格式:
    [
        {'text': '...', 'source': 'xxx.txt', 'score': 0.85},
        ...
    ]
    """
    global _vectorizer, _matrix, _chunks

    if _vectorizer is None or _matrix is None or _chunks is None:
        load_index()

    if _vectorizer is None or _chunks is None:
        print("[RAG] 索引未就绪，无法检索。")
        return []

    from sklearn.metrics.pairwise import cosine_similarity

    query_vec = _vectorizer.transform([query])
    scores = cosine_similarity(query_vec, _matrix).ravel()

    # top_k 下标（从大到小）
    top_indices = scores.argsort()[::-1][:top_k]

    results = []
    for idx in top_indices:
        if idx < 0 or idx >= len(_chunks):
            continue
        score = float(scores[idx])
        results.append({
            'text': _chunks[idx]['text'],
            'source': _chunks[idx]['source'],
            'score': score
        })

    return results


def format_context(results):
    """
    把检索结果格式化成一段上下文文本，用于塞进 LLM 的 prompt。
    """
    if not results:
        return ""

    context_parts = []
    for i, r in enumerate(results, 1):
        context_parts.append(f"[参考资料{i} - 来源: {r['source']}]\n{r['text']}")

    return "\n\n---\n\n".join(context_parts)


# ============ 初始化函数（Flask 启动时调用） ============
def init_rag():
    """
    初始化 RAG 系统：加载索引（如不存在则自动构建）。
    建议在 Flask app 启动时调用一次。
    """
    print("[RAG] 初始化 RAG 系统（轻量 TF-IDF 版）...")
    load_index()
    print("[RAG] RAG 系统就绪。")
