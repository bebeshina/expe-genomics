from pprint import pprint

import numpy as np
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings, OllamaLLM

import __init__
from definitions import VECTOR_DIR
from knowledge_building import completion, embeddings
from resources import templates


class Retriever:

    @staticmethod
    def cosine_sim_score(v1, v2):
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


    def __init__(self):
        # self.log = __init__.get_logger(__class__.__name__)
        self.completion_model = OllamaLLM(model=completion)
        self.embed_model = OllamaEmbeddings(model=embeddings)
        self.persisted_vectorstore = FAISS.load_local(f"{VECTOR_DIR}", self.embed_model,
                                                      allow_dangerous_deserialization=True)
        self.qa = RetrievalQA.from_chain_type(llm=self.completion_model, chain_type="stuff", retriever=self.persisted_vectorstore.as_retriever())

    def __call__(self):
        self.completion_model = OllamaLLM(model=completion)
        self.embed_model = OllamaEmbeddings(model=embeddings)
        self.persisted_vectorstore = FAISS.load_local(f"{VECTOR_DIR}", self.embed_model,
                                                      allow_dangerous_deserialization=True)
        self.qa = RetrievalQA.from_chain_type(llm=self.completion_model, chain_type="stuff", retriever=self.persisted_vectorstore.as_retriever())

    def __run_query__(self, query: str):
        result = self.qa.invoke(templates.response.format(description=query))
        v1 = self.embed_model.embed_query(result["query"])
        v2 = self.embed_model.embed_documents(result["result"])[0]
        # @todo improve the scoring function
        score = self.cosine_sim_score(v1, v2)
        return result.get("result"), score


# r = Retriever()
# res = r.__run_query__("")
#
# pprint(res)