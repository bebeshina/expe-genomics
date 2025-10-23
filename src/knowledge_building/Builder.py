import json
from typing import List
from knowledge_building import embeddings

import nltk

from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from ast import literal_eval
from langchain_community.vectorstores import FAISS
from definitions import DATA_DIR, VECTOR_DIR


class Builder:

    def __init__(self):
        self.embed_model = OllamaEmbeddings(model=embeddings)

    @staticmethod
    def __data_to_docs__(file_path: str, seed_size=200) -> list:
        documents = []
        for line in open(file_path, "r").readlines()[:seed_size]:
            # custom structuring
            # @todo structured output with metadata etc.
            text = line.split("\t")[1]
            annot = line.split("\t")[0]
            gene = ""
            for a in literal_eval(annot):
                for e in a:
                    if ":" not in e:
                        gene = e
                        break
            sentences = nltk.sent_tokenize(text, "french")
            for sent in sentences:
                usent = "En lien avec le gene %s: %s" % (gene, sent)
                doc = Document(page_content=usent, metadata={"gene": gene})
                documents.append(doc)
        return documents

    @staticmethod
    def __create_langchain_documents__():
        records = json.load(open(f"{DATA_DIR}/summaries.json", "r"))
        docs: List[Document] = []
        for record in records:
            text = f"""Related to gene {record.get("gene")}:
                    -diseases : {",".join(record.get("diseases"))};
                    -symptoms: {",".join(record.get("symptoms"))};
                    -comment: {record.get("comment")}"""

            doc = Document(page_content=text, metadata=record)
            docs.append(doc)
        return docs


    def __store__(self, documents: list):
        vectorstore = FAISS.from_documents(documents, self.embed_model)
        vectorstore.save_local(f"{VECTOR_DIR}")

b = Builder()
docs = b.__create_langchain_documents__()
b.__store__(docs)