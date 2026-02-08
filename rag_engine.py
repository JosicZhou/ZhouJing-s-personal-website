"""
RAG Engine - 检索增强生成引擎
功能：读取 rag_data/ 下的文本文件，分块、embedding、存入 FAISS 向量库，提供检索接口。

工作原理：
1. 读取 rag_data/ 下所有 .txt 文件
2. 按段落分块（每块约 300-500 字，有少量重叠）
3. 用 sentence-transformers 的多语言模型把每块变成向量
4. 存入 FAISS 向量库（持久化到 rag_index/ 目录）
5. 查询时：用户问题 → 向量 → FAISS 搜索 top-k → 返回最相关的文本块
"""

import os
import json
import pickle
import numpy as np

# ============ 配置 ============
RAG_DATA_DIR = os.path.join(os.path.dirname(__file__), 'rag_data')
RAG_INDEX_DIR = os.path.join(os.path.dirname(__file__), 'rag_index')
CHUNK_SIZE = 400        # 每块大约的字符数
CHUNK_OVERLAP = 80      # 相邻块之间的重叠字符数
TOP_K = 5               # 检索返回的最相关块数
EMBEDDING_MODEL = 'paraphrase-multilingual-MiniLM-L12-v2'  # 支持中英文的轻量模型

# ============ 全局变量（延迟加载）============
_model = None
_index = None
_chunks = None


def _get_model():
    """延迟加载 embedding 模型（首次调用时才加载，避免启动变慢）"""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        print(f"[RAG] 正在加载 embedding 模型: {EMBEDDING_MODEL} ...")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        print("[RAG] 模型加载完成。")
    return _model


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


# ============ 3. 建立向量索引 ============
def build_index(chunks):
    """
    把所有文本块编码成向量，存入 FAISS 索引。
    同时把 chunks 元数据（文本、来源）保存到磁盘。
    """
    import faiss

    model = _get_model()

    # 提取所有文本
    texts = [chunk['text'] for chunk in chunks]

    # 编码成向量
    print("[RAG] 正在计算向量（embedding）...")
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    embeddings = np.array(embeddings, dtype='float32')

    # 创建 FAISS 索引（使用内积，因为向量已归一化，等效余弦相似度）
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    print(f"[RAG] FAISS 索引建立完成，共 {index.ntotal} 个向量，维度 {dimension}。")

    # 持久化到磁盘
    os.makedirs(RAG_INDEX_DIR, exist_ok=True)
    faiss.write_index(index, os.path.join(RAG_INDEX_DIR, 'faiss.index'))
    with open(os.path.join(RAG_INDEX_DIR, 'chunks.pkl'), 'wb') as f:
        pickle.dump(chunks, f)

    print(f"[RAG] 索引已保存到: {RAG_INDEX_DIR}")
    return index, chunks


# ============ 4. 加载已有索引 ============
def load_index():
    """从磁盘加载已建好的 FAISS 索引和文本块"""
    global _index, _chunks
    import faiss

    index_path = os.path.join(RAG_INDEX_DIR, 'faiss.index')
    chunks_path = os.path.join(RAG_INDEX_DIR, 'chunks.pkl')

    if not os.path.exists(index_path) or not os.path.exists(chunks_path):
        print("[RAG] 未找到已有索引，将重新构建...")
        documents = load_documents()
        if not documents:
            print("[RAG] 没有数据文件，跳过索引构建。")
            return None, None
        chunks = split_into_chunks(documents)
        _index, _chunks = build_index(chunks)
        return _index, _chunks

    _index = faiss.read_index(index_path)
    with open(chunks_path, 'rb') as f:
        _chunks = pickle.load(f)

    print(f"[RAG] 已加载索引：{_index.ntotal} 个向量，{len(_chunks)} 个文本块。")
    return _index, _chunks


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
    global _index, _chunks

    # 确保索引已加载
    if _index is None or _chunks is None:
        load_index()

    if _index is None or _chunks is None:
        print("[RAG] 索引未就绪，无法检索。")
        return []

    model = _get_model()

    # 用户问题 → 向量
    query_embedding = model.encode([query], normalize_embeddings=True)
    query_embedding = np.array(query_embedding, dtype='float32')

    # FAISS 搜索
    scores, indices = _index.search(query_embedding, top_k)

    results = []
    for i, idx in enumerate(indices[0]):
        if idx < 0 or idx >= len(_chunks):
            continue
        results.append({
            'text': _chunks[idx]['text'],
            'source': _chunks[idx]['source'],
            'score': float(scores[0][i])
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
    print("[RAG] 初始化 RAG 系统...")
    load_index()
    print("[RAG] RAG 系统就绪。")
