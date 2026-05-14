"""
Модуль для загрузки и обработки пользовательских файлов.
Поддерживает: .txt, .md, .pdf
"""
import os
import tempfile
from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader

def load_file_content(file_path: str) -> str:
    """
    Загружает содержимое файла в зависимости от расширения.
    """
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.pdf':
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        return "\n\n".join([doc.page_content for doc in docs])
    elif ext in ['.txt', '.md', '.py', '.json']:
        loader = TextLoader(file_path, encoding='utf-8')
        docs = loader.load()
        return "\n\n".join([doc.page_content for doc in docs])
    else:
        raise ValueError(f"Неподдерживаемый формат файла: {ext}")

def process_uploaded_file(file_bytes: bytes, file_name: str, chunk_size: int = 512, chunk_overlap: int = 50) -> List[str]:
    """
    Принимает байты файла, сохраняет во временный файл, читает и разбивает на чанки.
    Возвращает список строк (чанков).
    """
    # Создаем временный файл
    suffix = os.path.splitext(file_name)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(file_bytes)
        tmp_path = tmp_file.name
    
    try:
        # Читаем содержимое
        full_text = load_file_content(tmp_path)
        
        # Разбиваем на чанки
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        chunks = text_splitter.split_text(full_text)
        return chunks
    finally:
        # Удаляем временный файл
        os.unlink(tmp_path)
