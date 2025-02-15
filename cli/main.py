import os, shutil
from src.pdf_utils import process_pdf
from src.config_utils import process_embeddings
from src.llm_engine import LLMQueryEngine
from src.document_processor import DocumentProcessor
from src.results_processor import ResultsProcessor, OutputFormat

class Config:
    RAG_DOCUMENT = "./docs/MERGED_cosmetic_guidances.pdf"
    RAG_QUESTIONS = "./docs/test-questions.txt"
    CHROMA_PATH = "chroma"
    OUTPUT_FILE = "llm-output"
    MODEL = "llama3.2"

def main():

    # Reset the existing database // uncomment if needed
    # clear_database()

    config = Config()
    embedding_function = process_embeddings()

    # Load and process documents
    data = process_pdf(config.RAG_DOCUMENT)
    print(f"{len(data)} document pages loaded")

    # Upload documents to vector db
    doc_processor = DocumentProcessor(config.CHROMA_PATH, embedding_function)
    doc_processor.populate_vectordb(data)

    # Initialize LLM
    llm_engine = LLMQueryEngine(config.CHROMA_PATH, embedding_function, config.MODEL)
    # Return both .txt and .json versions of the output
    results_processor = ResultsProcessor(config.OUTPUT_FILE, OutputFormat.BOTH)

    # Or specify just one format if needed:
    # results_processor = ResultsProcessor(config.OUTPUT_FILE, OutputFormat.TEXT)
    # results_processor = ResultsProcessor(config.OUTPUT_FILE, OutputFormat.JSON)

    # Process questions
    with open(config.RAG_QUESTIONS, "r") as f:
        questions = [q.strip() for q in f.readlines() if q.strip()]

    for i, question in enumerate(questions, 1):
        print(f"Processing question {i} of {len(questions)}: {question}")
        result = llm_engine.query(question)
        results_processor.add_result(question, result)

    results_processor.write_results()

def clear_database():
    if os.path.exists(Config.CHROMA_PATH):
        shutil.rmtree(Config.CHROMA_PATH)

if __name__ == "__main__":
    main()
