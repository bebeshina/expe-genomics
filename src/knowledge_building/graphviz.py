import re
import networkx as nx
import pandas as pd
from matplotlib import pyplot as plt

def describe_degrees(G: nx.Graph):
    nodes = G.nodes
    degrees = [G.degree(nodes)]

    nd = []
    for d in degrees.pop():
        nd.append([d[0], d[1]])
    temp = pd.DataFrame(nd, columns=["node", "degree"])
    print(temp.describe())



def is_hpo_node(node: str) -> bool:
        """ Check if events starts with Exx """
        return re.match("^HP", node) is not None


def is_omim_node(node: str) -> bool:
    """ Check if events starts with Exx """
    return re.match("^OMIM", node) is not None


def is_orpha_node(node: str) -> bool:
    """ Check if events starts with Exx """
    return re.match("^ORPHA", node) is not None


def is_decipher_node(node: str) -> bool:
    """ Check if events starts with Exx """
    return re.match("^'DECIPHER", node) is not None


def is_maxo_node(node: str) -> bool:
    """ Check if events starts with Exx """
    return re.match("^'MAXO", node) is not None


def is_mondo_node(node: str) -> bool:
    """ Check if events starts with Exx """
    return re.match("^'MONDO", node) is not None


def get_node_color(node: str) -> str:
    """ Get color of the individual node """
    if is_hpo_node(node):
        return "#008000"
    elif is_maxo_node(node):
        return "#800080"
    elif is_decipher_node(node):
        return "#808080"
    elif is_mondo_node(node):
        return "#CD5C5C"
    elif is_omim_node(node):
        return "#46ECD5"
    elif is_orpha_node(node):
        return "#46ECD5"
    else:
        return "##90A1B9"



def plot_connected_components(G: nx.Graph):
    fig = plt.figure("", figsize=(10, 8))
    # Create a gridspec for adding subplots of different sizes
    axgrid = fig.add_gridspec(4, 4)
    ax0 = fig.add_subplot(axgrid[0:3, :])
    G_connected = G.subgraph(nx.connected_components(G))
    # G_connected = G.subgraph(sorted(nx.connected_components(G), key=len, reverse=True)[0])
    attributes = nx.get_node_attributes(G, "color")
    node_color_attrs = [str(attributes[node]) for node in G_connected.nodes()]
    pos = nx.spring_layout(G_connected, seed=10396953)
    nx.draw_networkx(G_connected, pos, ax=ax0, node_color=node_color_attrs, node_size=20)
    # nx.draw_networkx_nodes(G_connected, pos, ax=ax0,  node_size=20)
    # nx.draw_networkx_edges(G_connected, pos, ax=ax0, alpha=0.4)
    ax0.set_title("Connected components and their types")
    ax0.set_axis_off()
    plt.show()