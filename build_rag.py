#!/usr/bin/env python3
"""
RAG 建库脚本
用法：python build_rag.py

功能：
1. 读取 rag_data/ 下所有 .txt 文件
2. 分块
3. 用 embedding 模型转向量
4. 存入 FAISS 索引（保存到 rag_index/ 目录）

每次更新了 rag_data/ 里的资料后，重新运行此脚本即可更新向量库。
"""

from rag_engine import load_documents, split_into_chunks, build_index

def main():
    print("=" * 50)
    print("开始构建 RAG 向量库")
    print("=" * 50)

    # 1. 加载文档
    documents = load_documents()
    if not documents:
        print("错误：rag_data/ 目录下没有找到 .txt 文件！")
        print("请先在 rag_data/ 目录中添加你的个人资料文本文件。")
        return

    # 2. 分块
    chunks = split_into_chunks(documents)

    # 3. 构建索引
    index, chunks = build_index(chunks)

    print("=" * 50)
    print(f"构建完成！共 {index.ntotal} 个向量块。")
    print("索引已保存到 rag_index/ 目录。")
    print("现在启动 Flask 应用后，个人模式聊天将使用 RAG 检索。")
    print("=" * 50)

if __name__ == '__main__':
    main()
