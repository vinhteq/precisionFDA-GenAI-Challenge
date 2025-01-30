import os
from langchain_community.document_loaders import Docx2txtLoader, UnstructuredHTMLLoader, PyMuPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from typing import List
from pdf_utils import process_pdf

def process_embeddings():
    return OllamaEmbeddings(
        model="mxbai-embed-large"
    )

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
embedding_function = process_embeddings()
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embedding_function)



def load_and_split_document(file_path: str) -> List[Document]:
    if file_path.endswith('.pdf'):
        documents = process_pdf(file_path)
        return documents
    elif file_path.endswith('.docx'):
        loader = Docx2txtLoader(file_path)
        documents = loader.load()
        documents = text_splitter.split_documents(documents)
        return documents
    elif file_path.endswith('.html'):
        loader = UnstructuredHTMLLoader(file_path)
        documents = loader.load()
        documents = text_splitter.split_documents(documents)
        return documents
    else:
        raise ValueError(f"Unsupported file type: {file_path}")



def index_document_to_chroma(file_path: str, file_id: int) -> bool:
    try:
        splits = load_and_split_document(file_path)

        # Add metadata to each split
        for split in splits:
            split.metadata['file_id'] = file_id

        vectorstore.add_documents(splits)
        # vectorstore.persist()
        return True
    except Exception as e:
        print(f"Error indexing document: {e}")
        return False

def delete_doc_from_chroma(file_id: int):
    try:
        docs = vectorstore.get(where={"file_id": file_id})
        print(f"Found {len(docs['ids'])} document chunks for file_id {file_id}")

        vectorstore._collection.delete(where={"file_id": file_id})
        print(f"Deleted all documents with file_id {file_id}")

        return True
    except Exception as e:
        print(f"Error deleting document with file_id {file_id} from Chroma: {str(e)}")
        return False
