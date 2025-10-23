import nltk

from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from ast import literal_eval
from langchain_community.vectorstores import FAISS

from knowledge_building.knowledge import config


class Builder:

    def __init__(self):
        self.embed_model = OllamaEmbeddings(model=config.get("models")["embeddings"])

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

    def __store__(self, documents: list):
        vectorstore = FAISS.from_documents(documents, self.embed_model)
        vectorstore.save_local(config.get("resources").get("vectors"))
