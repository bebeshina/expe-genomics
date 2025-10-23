import json
import requests
from langchain_community.document_loaders import PyPDFLoader
from bs4 import BeautifulSoup
from definitions import DATA_DIR


def get_ann_case_links():
    res = requests.post('https://www.anncaserep.com')
    soup = BeautifulSoup(res.content, 'html.parser')
    links = {link.get("href") for link in soup.find_all("a", class_="btn btn-outline-success btn-sm px-1 py-0 border-0")}
    global_docs = []
    for link in links:
        docs = get_ann_case_report(link)
        global_docs.extend(docs)
    with open(f"{DATA_DIR}/reports.json", "w+") as f:
        f.write(json.dumps(global_docs, indent=4))


def get_ann_case_report(page_url):
    print(f"processing {page_url}")
    loader = PyPDFLoader(page_url)
    pages = []
    data = loader.lazy_load()
    for page in data:
        pages.append({"metadata": page.metadata, "page_content": page.page_content})
    print(type(pages))
    return pages


get_ann_case_links()


