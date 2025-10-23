import json
import os
from venv import logger
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import pydantic_core
from ollama import ChatResponse, chat, generate
from pandas.errors import ParserError

from definitions import DATA_DIR, RESOURCE_DIR
from knowledge_building import schemas, kb_templates, completion
from knowledge_building.schemas import Summary, Summaries
from resources import templates


def llm_get_summary(prompt: str) -> str:
    response: ChatResponse = chat(model=completion,  messages=[
        {
            'role': 'system',
            'content': prompt,
        },
        {
            'role': 'user',
            'content': 'What is the gene linked to the symptoms, abnormalities and diseases? ',
        },
    ])
    return response['message']['content']


def llm_get_structured_summary(prompt: str) -> Summary:
    response: ChatResponse = chat(model=completion, messages=[
        {
            'role': 'system',
            'content': prompt,
        },
        {
            'role': 'user',
            'content': 'What is the gene linked to the symptoms, abnormalities and diseases? ',
        },
    ],
    format=schemas.Summary.model_json_schema())
    try:
        formatted_output = schemas.Summary.model_validate_json(response['message']['content'])
        return formatted_output
    except pydantic_core._pydantic_core.ValidationError:
        print("error>>>", response['message']['content'])
        return Summary(gene="", diseases=[], symptoms=[], comment="formatting error")
    return response['message']['content']


def llm_generate_structured_summary(prompt: str) -> Summary:
    response = generate(model=completion,
                        prompt=prompt,
                        format=schemas.Summary.model_json_schema())
    formatted_response = schemas.Summary.model_validate_json(response["response"])
    return formatted_response


def build_lexicalisations(d="../data/overall/") -> dict:
    lexicalisation = dict()
    lex_columns = {"maxo_id": "maxo_name", "hpo_id": "hpo_name", "disease_id": "disease_name", "database_id": "disease_name"}
    d = f"{RESOURCE_DIR}/annotations/"
    for f in os.listdir(d):
        try:
            frame = pd.read_csv("%s%s" % (d, f), sep="\t", low_memory=False)
            for k, v in lex_columns.items():
                if k in frame.columns and v in frame.columns:
                    dic = dict(zip(frame[k].values.tolist(), frame[v].values.tolist()))
                    lexicalisation.update(dic)
        except ParserError as e:
            logger.error(e)
    return lexicalisation


def build_pairs() -> dict:
    rel_columns = {"disease_id": "hpo_id", "hpo_id": "gene_symbol", "database_id": "hpo_id", "maxo_id": "hpo_id"}
    pairs = dict()
    d = f"{RESOURCE_DIR}/annotations/"
    for f in os.listdir(d):
        frame = pd.read_csv("%s/%s" % (d, f), sep="\t", low_memory=False)
        for k, v in rel_columns.items():
            if k in frame.columns and v in frame.columns:
                dic = dict(zip(frame[k].values.tolist(), frame[v].values.tolist()))
                pairs.update(dic)
    return pairs


def data_as_graph(pairs: dict) -> nx.Graph:
    G = nx.Graph()
    node_set = set(pairs.keys()).union(set(pairs.values()))
    G.add_nodes_from(node_set)
    edges = []
    for k, v in pairs.items():
        edges.append((k, v))
    G.add_edges_from(edges)
    # plot_connected_components(G)
    return G


def plot_connected_components(G: nx.Graph):
    fig = plt.figure("", figsize=(10, 8))
    # Create a gridspec for adding subplots of different sizes
    axgrid = fig.add_gridspec(4, 4)
    ax0 = fig.add_subplot(axgrid[0:3, :])
    #@todo fix warning sorted
    G_connected = G.subgraph(sorted(nx.connected_components(G), key=len, reverse=True)[0])
    pos = nx.spring_layout(G_connected, seed=10396953)
    nx.draw_networkx_nodes(G_connected, pos, ax=ax0, node_size=20)
    nx.draw_networkx_edges(G_connected, pos, ax=ax0, alpha=0.4)
    ax0.set_title("Connected components of the Domain Graph")
    ax0.set_axis_off()
    # plt.show()


def get_prefix(term: str) -> str:
    if ":" in term:
        return term.split(":")[0]
    return ""


def lexicalise_graph(G: nx.Graph) -> list:
    logger.info("Edges %s nodes %s", G.number_of_edges(), G.number_of_nodes())
    select = [node for node, degree in dict(G.degree()).items() if degree >= 2]
    lex = build_lexicalisations()
    lexicalized_nodes = []
    for n in select:
        local_in = G.edges(n)
        local_out = []
        for tup in local_in:
            prefix_src = get_prefix(tup[0])
            prefix_tgt = get_prefix(tup[1])
            src = "%s:%s" % (prefix_src, lex.get(tup[0])) if tup[0] in lex.keys() else tup[0]
            tgt = "%s:%s" % (prefix_tgt, lex.get(tup[1])) if tup[1] in lex.keys() else tup[1]
            local_out.append((src, tgt))
        lexicalized_nodes.append(local_out)
    return lexicalized_nodes


def build_summaries(lexicalized_pairs: list) -> list:
    summaries = []
    while lexicalized_pairs:
        elem = lexicalized_pairs.pop()
        rels = "\n".join(["%s, %s" % (t[0], t[1]) for t in elem])
        response = llm_get_summary(templates.summary.format(associations=rels))
        logger.info(response.replace("\n", " ").strip())
        summaries.append(response)
    return summaries


def build_structured_summaries(lexicalized_pairs: list) -> Summaries:
    summaries = []
    while lexicalized_pairs:
        elem = lexicalized_pairs.pop()
        rels = "\n".join(["<association>%s, %s</association>" % (t[0], t[1]) for t in elem])
        response = llm_get_structured_summary(kb_templates.structured_summary.format(associations=rels))
        # logger.info(response.replace("\n", " ").strip())
        summaries.append(response)
    summary_list = Summaries(root=summaries)
    return summary_list


def run():
    pairs = build_pairs()
    graph = data_as_graph(pairs)
    lexicalized_pairs = lexicalise_graph(graph)
    print(len(lexicalized_pairs))
    summaries = build_structured_summaries(lexicalized_pairs[3600:4469])
    with open(f"{DATA_DIR}/summaries_11.json", "a+") as f:
        # dump = summaries.model_dump()
        dump = json.dumps(summaries.model_dump(), indent=4)
        f.write(dump)
        f.flush()
        f.flush()



def refactor():
    s_list = []
    for f in os.listdir(f"{DATA_DIR}/temp"):
        lst = json.load(open(f"{DATA_DIR}/temp/" + f, "r"))
        for elem in lst:
            e = json.loads(elem)
            try:
                s = Summary(gene=e.get("gene"), diseases=e.get("diseases"), symptoms=e.get("symptoms"), comment=e.get("comment"))
                s_list.append(s)
            except pydantic_core._pydantic_core.ValidationError:
                print(e)
    s10 = Summaries.model_validate_json(open(f"{DATA_DIR}/summaries_10.json", "r").read())
    s11 = Summaries.model_validate_json(open(f"{DATA_DIR}/summaries_11.json", "r").read())
    s_list.extend(s10.root)
    s_list.extend(s11.root)
    print("records", len(s_list))
    sums = Summaries(root=s_list)

    with open(f"{DATA_DIR}/summaries.json", "a+") as f:
        dump = sums.model_dump_json(indent=4)
        f.write(dump)
        f.flush()
        f.flush()
