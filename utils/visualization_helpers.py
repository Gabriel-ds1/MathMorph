# utils/visualization_helpers.py

import matplotlib.pyplot as plt
from collections import defaultdict
import networkx as nx
from utils.sympy_helpers import clean_attributes

def visualize_global_math_graph(scratchpad, fname="math_knowledge_graph.png"):
    # All graphs as networkx objects
    global_graph = nx.DiGraph()
    for rec in scratchpad.get_all():
        g = rec['graph']
        global_graph = nx.compose(global_graph, g)
    plt.figure(figsize=(15,12))
    pos = nx.spring_layout(global_graph, seed=42)
    nx.draw(global_graph, pos, with_labels=True, node_color="skyblue", font_size=10, edge_color="gray")
    # Optionally, highlight edge labels
    edge_labels = dict([((u, v), d.get('label', '')) for u, v, d in global_graph.edges(data=True)])
    nx.draw_networkx_edge_labels(global_graph, pos, edge_labels=edge_labels)
    plt.title("Aggregate Math Knowledge Graph (All Sentences)")
    plt.tight_layout()
    plt.savefig(fname)
    plt.show()

def graph_candidates_across_sentences(candidates):
    contrib = defaultdict(list)
    for cand in candidates:
        if 'graph' in cand['generation_method']:
            contrib[cand['generation_method']].append((cand.get('derived_eq'), cand.get('source_step')))
    print("\n=== Graph Structure Contributions Across Sentences ===")
    for key, lst in contrib.items():
        print(f"\n{key}:")
        for derived_eq, step in lst:
            print(f"Sent #{step}: {derived_eq}")

def build_global_graph(global_graph, scratchpad):

    for rec in scratchpad.get_all():
        g = rec['graph']
        global_graph = nx.compose(global_graph, g)
    #for n in global_graph.nodes():
        #global_graph.nodes[n]['label'] = str(n)
    clean_attributes(global_graph)
    nx.write_graphml(global_graph, "math_knowledge_graph.graphml")
    nx.write_gexf(global_graph, "math_knowledge_graph.gexf")
    nx.write_gml(global_graph, "math_knowledge_graph.gml")