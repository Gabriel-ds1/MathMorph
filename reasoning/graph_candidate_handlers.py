# reasoning/graph_candidate_handlers.py

import networkx as nx
from utils.candidate_helpers import make_candidate
from .graph_candidate_motifs import KNOWN_MOTIFS
from utils.general_helpers import annotate_error

def get_graph_candidates(graph, record, is_correct):
    """
    Generate candidate formulas based on graph topology:
    - cycles (closed formula dependencies)
    - paths of certain depth (chain relations)
    - connected components (subsystems)
    - subgraph isomorphisms (detect known algebraic motifs)
    """
    candidates = []

    if not isinstance(graph, (nx.Graph, nx.DiGraph)):
        return candidates

    # Example: Find all simple cycles up to length 4
    try:
        for cycle in nx.simple_cycles(graph) if graph.is_directed() else nx.cycle_basis(graph):
            if len(cycle) > 1 and len(cycle) <= 4:
                cycle_vars = ', '.join(str(n) for n in cycle)
                formula_str = f"Cycle: {cycle_vars}"
                candidates.append(make_candidate(record, formula_str, 'graph_cycle_discovery', correct=is_correct))
    except Exception:
        pass

    # Example: All paths of length 2 (indicate transitive formula relationships)
    try:
        for n1 in graph.nodes():
            for n2 in graph.nodes():
                if n1 != n2:
                    for path in nx.all_simple_paths(graph, n1, n2, cutoff=2):
                        if len(path) == 3:  # cutoff includes intermediary
                            path_vars = ', '.join(str(x) for x in path)
                            formula_str = f"TransitivePath: {path_vars}"
                            candidates.append(make_candidate(record, formula_str, 'graph_path_discovery', correct=is_correct))
    except Exception as e:
        return [annotate_error("get_graph_candidates", e, str(candidates))]
    
    return candidates

def clique_candidates(graph, record, is_correct):
    """
    Generate candidates from complete subgraphs (cliques)
    For each clique, generates a candidate stating that "All of these nodes are mutually related"
    """
    candidates = []

    if not isinstance(graph, (nx.Graph, nx.DiGraph)):
        return candidates
    G = graph.to_undirected() if graph.is_directed() else graph
    try:
        # Only want maximal cliques of at least 3 nodes
        for clique in nx.find_cliques(G):
            if len(clique) >= 3:
                cli_str = ','.join(str(x) for x in clique)
                formula_str = f"Clique relation among [{cli_str}]"
                note = "All these variables/constants are mutually related (fully connected subgraph)."
                candidates.append(make_candidate(record, formula_str, 'graph_clique_discovery', note, correct=is_correct))
    except Exception as e:
        return [annotate_error("clique_candidates", e, str(candidates))]

    return candidates

def star_candidates(graph, record, is_correct):
    """
    Generate candidates from complete subgraphs (star)
    For each node, check if it has several neighbors. If its neighbors are not connected among each other,
    treat it as the "center" of a star, and create a candidate about its "hub" role.
    """
    candidates = []

    if not isinstance(graph, (nx.Graph, nx.DiGraph)):
        return candidates
    G = graph.to_undirected() if graph.is_directed() else graph
    try:
        # Only want maximal cliques of at least 3 nodes
        for center in G.nodes():
            neighbors = set(G.neighbors(center))
            if len(neighbors) >= 3:
                # Are the neigbors connected to each other?
                subgraph = G.subgraph(neighbors)
                if subgraph.number_of_edges() == 0:
                    # It's a star
                    leaf_str = ', '.join(str(x) for x in neighbors)
                    formula_str = f"Star: Center={center} → [{leaf_str}]"
                    note = f"This resembles a star structure where {center} connects all others, with no mutual connections among leaves."
                    candidates.append(make_candidate(record, formula_str, 'graph_star_discovery', note, correct=is_correct))
    except Exception as e:
        return [annotate_error("star_candidates", e, str(candidates))]

    return candidates

def bipartite_candidates(graph, record, is_correct):
    """
    Generate candidates from complete subgraphs (bipartite)
    Contains two sets of nodes. Edges only run between the sets (not within).
    Captures situations such as "variables vs constants" or "inputs vs outputs"
    """

    candidates = []

    if not isinstance(graph, (nx.Graph, nx.DiGraph)):
        return candidates
    G = graph.to_undirected() if graph.is_directed() else graph

    try:
        if nx.is_bipartite(G):
            set1, set2 = nx.bipartite.sets(G)
            s1 = ', '.join(str(x) for x in set1)
            s2 = ', '.join(str(x) for x in set2)
            formula_str = f"Bipartite relation: [{s1}] <-> [{s2}]"
            note = "These nodes form a bipartite structure: all connections are between sets, not within."
            candidates.append(make_candidate(record, formula_str, 'graph_bipartite_discovery', note, correct=is_correct))
            any_found = True
    except Exception as e:
        return [annotate_error("bipartite_candidates", e, str(candidates))]
    return candidates


# ========= Algebraic Motif Subgraph Isomorphism ============

def flexible_edge_match(eattr1, eattr2):
    # Only require 'label' to be the same (ex: "difference_of", "add", etc.)
    return eattr1.get('label', None) == eattr2.get('label', None)

def flexible_node_match(nattr1, nattr2):
    # Only require both to have same is_prime status, or neither cares.
    is_prime1 = nattr1.get('is_prime', None)
    is_prime2 = nattr2.get('is_prime', None)
    # If neither node restricts by is_prime: match always. If both specify: must match.
    if is_prime1 is None or is_prime2 is None:
        return True
    return is_prime1 == is_prime2

def motif_subgraph_candidates(graph, record, is_correct):
    candidates = []
    G = graph
    for motif_name, motif_graph in KNOWN_MOTIFS.items():
        motif = motif_graph if motif_graph.is_directed() else motif_graph.to_directed()
        matcher = nx.algorithms.isomorphism.DiGraphMatcher(G, motif, node_match = flexible_node_match, edge_match = flexible_edge_match)
        for subiso in matcher.subgraph_isomorphisms_iter():
            mapping = ', '.join(f"{pattern}->{data}" for pattern, data in subiso.items())
            formula_str = f"Motif subgraph matched: {motif_name}, mapping [{mapping}]"
            note = f"This subgraph resembles the {motif_name} algebraic motif."
            candidates.append(make_candidate(record, formula_str, 'graph_motif_subgraph_discovery', note, correct=is_correct))

    return candidates