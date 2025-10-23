import json

import langchain_core.documents
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.vectorstores import FAISS
from definitions import RESOURCE_DIR, DATA_DIR

embed_model = OllamaEmbeddings(model="mxbai-embed-large")
completion_model = OllamaLLM(model="llama3.2")


def store():
    # @todo point to the config file
    docs = []
    for document in json.load(open(f"{DATA_DIR}/reports.json", "r")):
        d = langchain_core.documents.Document(document.get("page_content"))
        docs.append(d)
    vectorstore = FAISS.from_documents(docs, embed_model)
    vectorstore.save_local(f"{RESOURCE_DIR}/faiss_idx")


template = """Retrieve and list all distinct medical records related to ADHD from all the documents.
            There may be multiple infant desease records in the same document. A patient record must provide the gender of the patient. 
            Do not give any explanation. No diagnosis. Only medical records. 
            Browse all the documents present in the document vector store to retrieve the medical records."""


def retrieve():
    persisted_vectorstore = FAISS.load_local(f"{RESOURCE_DIR}/faiss_idx",  embed_model, allow_dangerous_deserialization=True)
    qa = RetrievalQA.from_chain_type(llm=completion_model, chain_type="stuff", retriever=persisted_vectorstore.as_retriever())
    result = qa.invoke(template)
    print(result["result"])

retrieve()

