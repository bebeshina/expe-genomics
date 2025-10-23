import numpy as np
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, OllamaLLM

import __init__


class Retriever:

    @staticmethod
    def cosine_sim_score(v1, v2):
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


    def __init__(self):
        self.log = __init__.get_logger(__class__.__name__)
        self.completion_model = OllamaLLM(model=config.get("models")["completion"])
        self.embed_model = OllamaEmbeddings(model=config.get("models")["embeddings"])
        self.persisted_vectorstore = FAISS.load_local(config.get("resources").get("vectors"), self.embed_model,
                                                      allow_dangerous_deserialization=True)
        self.qa = RetrievalQA.from_chain_type(llm=self.completion_model, chain_type="stuff", retriever=self.persisted_vectorstore.as_retriever())

    def __call__(self):
        self.log = utils.get_logger(__class__.__name__)
        self.completion_model = OllamaLLM(model=config.get("models")["completion"])
        self.embed_model = OllamaEmbeddings(model=config.get("models")["embeddings"])
        self.persisted_vectorstore = FAISS.load_local(config.get("resources").get("vectors"), self.embed_model,
                                                      allow_dangerous_deserialization=True)
        self.qa = RetrievalQA.from_chain_type(llm=self.completion_model, chain_type="stuff", retriever=self.persisted_vectorstore.as_retriever())

    def __run_query__(self, query: str):
        result = self.qa.invoke(templates.response.format(description=query))
        v1 = self.embed_model.embed_query(result["query"])
        v2 = self.embed_model.embed_documents(result["result"])[0]
        score = self.cosine_sim_score(v1, v2)
        return result.get("result"), score

