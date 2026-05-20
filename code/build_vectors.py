"""
向量库构建脚本
从文档构建ChromaDB向量数据库
"""

import os
import sys
import shutil
from pathlib import Path
from typing import List

from langchain.document_loaders import TextLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma

# 本地配置
from config import Config

def build_vectorstore(
    data_dir: str = None,
    persist_directory: str = None,
    force_rebuild: bool = False
) -> int:
    """
    构建向量数据库
    
    Args:
        data_dir: 数据目录路径
        persist_directory: 向量库保存路径
        force_rebuild: 是否强制重建
    
    Returns:
        构建的文档块数量
    """
    print("="*50)
    print("🔧 向量库构建工具")
    print("="*50)
    
    # 使用默认配置
    if data_dir is None:
        data_dir = Config.DATA_DIR
    if persist_directory is None:
        persist_directory = Config.VECTOR_DB_PATH
    
    print(f"📁 数据目录: {data_dir}")
    print(f"💾 向量库路径: {persist_directory}")
    print(f"🔨 强制重建: {force_rebuild}")
    
    # 检查数据目录
    if not os.path.exists(data_dir):
        print(f"❌ 数据目录不存在: {data_dir}")
        print("💡 请在data/目录下添加.txt格式的知识库文档")
        return 0
    
    # 检查是否有文档文件
    txt_files = list(Path(data_dir).glob("**/*.txt"))
    if not txt_files:
        print(f"❌ 在 {data_dir} 中未找到.txt文件")
        print("💡 请添加至少一个.txt文件到数据目录")
        return 0
    
    print(f"📄 找到 {len(txt_files)} 个文档文件:")
    for file in txt_files[:5]:  # 只显示前5个
        print(f"   - {file.name}")
    if len(txt_files) > 5:
        print(f"   ... 还有 {len(txt_files) - 5} 个文件")
    
    # 检查是否需要清理旧向量库
    if os.path.exists(persist_directory) and force_rebuild:
        print(f"🗑️ 清理旧向量库: {persist_directory}")
        shutil.rmtree(persist_directory)
        os.makedirs(persist_directory, exist_ok=True)
    
    # 初始化嵌入模型
    print(f"🧠 初始化嵌入模型: {Config.EMBED_MODEL}（模式: {Config.EMBED_MODE}）")
    
    if Config.EMBED_MODE == "api":
        embedding = OpenAIEmbeddings(
            openai_api_key=Config.SILICONFLOW_API_KEY,
            openai_api_base=Config.SILICONFLOW_API_BASE,
            model=Config.EMBED_MODEL
        )
    else:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        embedding = HuggingFaceEmbeddings(
            model_name=Config.EMBED_MODEL,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
    
    # 加载文档
    print("📚 加载文档...")
    loader = DirectoryLoader(
        data_dir,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    
    documents = loader.load()
    print(f"✅ 加载了 {len(documents)} 个文档")
    
    # 文档分割
    print(f"✂️ 分割文档 (块大小: {Config.CHUNK_SIZE}, 重叠: {Config.CHUNK_OVERLAP})...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " "]
    )
    
    texts = text_splitter.split_documents(documents)
    print(f"✅ 分割为 {len(texts)} 个文本块")
    
    # 显示分割示例
    if texts:
        print(f"📝 分割示例（前2个块）:")
        for i, doc in enumerate(texts[:2]):
            print(f"   块{i+1}: {doc.page_content[:100]}...")
    
    # 创建向量库
    print("🏗️ 创建向量数据库...")
    vectorstore = Chroma.from_documents(
        documents=texts,
        embedding=embedding,
        persist_directory=persist_directory,
        collection_name=Config.COLLECTION_NAME
    )
    
    # 持久化
    print("💾 保存向量数据库...")
    vectorstore.persist()
    
    # 验证：使用 get() 替代私有属性 _collection
    print("🔍 验证向量数据库...")
    stored_docs = vectorstore.get()
    doc_count = len(stored_docs.get('ids', []))
    
    print("="*50)
    print(f"✅ 向量库构建完成!")
    print(f"📊 文档块数量: {doc_count}")
    print(f"💾 保存位置: {persist_directory}")
    print(f"🧠 嵌入模型: {Config.EMBED_MODEL}")
    print("="*50)
    
    # 生成元数据文件
    metadata_file = os.path.join(persist_directory, "metadata.txt")
    with open(metadata_file, "w", encoding="utf-8") as f:
        f.write(f"构建时间: {__import__('datetime').datetime.now()}\n")
        f.write(f"文档数量: {len(documents)}\n")
        f.write(f"文档块数量: {doc_count}\n")
        f.write(f"块大小: {Config.CHUNK_SIZE}\n")
        f.write(f"重叠大小: {Config.CHUNK_OVERLAP}\n")
        f.write(f"嵌入模型: {Config.EMBED_MODEL}\n")
        f.write(f"数据目录: {data_dir}\n")
    
    return doc_count

def incremental_update(data_dir: str = None, persist_directory: str = None) -> int:
    """
    基于文件修改时间的增量更新向量库
    
    Args:
        data_dir: 数据目录路径
        persist_directory: 向量库保存路径
    
    Returns:
        新增的文档块数量
    """
    import hashlib
    
    print("="*50)
    print("🔄 增量更新向量库")
    print("="*50)
    
    if data_dir is None:
        data_dir = Config.DATA_DIR
    if persist_directory is None:
        persist_directory = Config.VECTOR_DB_PATH
    
    # 检查是否有现有向量库
    if not os.path.exists(persist_directory):
        print("⚠️ 向量库不存在，执行完整构建")
        return build_vectorstore(data_dir, persist_directory, force_rebuild=True)
    
    # 加载现有向量库
    print("📂 加载现有向量库...")
    embedding = OpenAIEmbeddings(
        openai_api_key=Config.SILICONFLOW_API_KEY,
        openai_api_base=Config.SILICONFLOW_API_BASE,
        model=Config.EMBED_MODEL
    )
    
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding,
        collection_name=Config.COLLECTION_NAME
    )
    
    # 获取已索引的文件哈希
    existing_data = vectorstore.get()
    existing_metadatas = existing_data.get('metadatas', []) if existing_data.get('ids') else []
    
    # 获取当前数据目录中所有文件及其哈希
    txt_files = list(Path(data_dir).glob("**/*.txt"))
    current_files = {}
    
    for file_path in txt_files:
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        current_files[str(file_path)] = {
            'hash': file_hash,
            'mtime': os.path.getmtime(file_path)
        }
    
    new_files = []
    changed_files = []
    
    for file_path, info in current_files.items():
        found = False
        for meta in existing_metadatas:
            if meta.get('source') == file_path and meta.get('hash') == info['hash']:
                found = True
                break
        if not found:
            if any(meta.get('source') == file_path for meta in existing_metadatas):
                changed_files.append(file_path)
            else:
                new_files.append(file_path)
    
    if not new_files and not changed_files:
        print("✅ 没有新增或变更的文档，无需更新")
        return 0
    
    print(f"📄 新增文档: {len(new_files)} 个")
    print(f"🔄 变更文档: {len(changed_files)} 个")
    
    # 加载新文档和变更文档
    loader = DirectoryLoader(
        data_dir,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=Config.CHUNK_SIZE,
        chunk_overlap=Config.CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", "！", "？", "；", "，", " "]
    )
    texts = text_splitter.split_documents(documents)
    
    # 为文本块添加元数据
    for doc in texts:
        source_path = doc.metadata.get('source', '')
        if source_path in current_files:
            doc.metadata['hash'] = current_files[source_path]['hash']
    
    # 增量添加
    print("➕ 增量添加到向量库...")
    vectorstore.add_documents(texts)
    vectorstore.persist()
    
    print(f"✅ 增量更新完成，新增 {len(texts)} 个文本块")
    return len(texts)

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="向量库构建工具")
    parser.add_argument("--data-dir", type=str, help="数据目录路径")
    parser.add_argument("--persist-dir", type=str, help="向量库保存路径")
    parser.add_argument("--force", action="store_true", help="强制重建")
    parser.add_argument("--incremental", action="store_true", help="增量更新")
    
    args = parser.parse_args()
    
    try:
        # 验证配置
        Config.validate()
        
        if args.incremental:
            count = incremental_update(args.data_dir, args.persist_dir)
        else:
            count = build_vectorstore(
                args.data_dir,
                args.persist_dir,
                force_rebuild=args.force
            )
        
        if count > 0:
            print(f"\n🚀 下一步: 启动API服务")
            print(f"   python api.py")
            print(f"\n🧪 测试查询:")
            print(f"   python workflow_langchain.py '你的问题'")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()