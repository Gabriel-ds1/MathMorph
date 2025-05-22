
import sympy as sp
from utils.sympy_helpers import canonicalize_value

def node_type(value):
    """
    Classifies node type as variable, constant, or concept.
    """
    if value is None:
        return None
    if isinstance(value, str):
        if value.isalpha():
            return "variable"
        elif value.isnumeric():
            return "constant"
        elif value in {"prime", "prime1", "prime2", "prime3", "prime4"}:
            return "concept"
        elif any(op in value for op in ["+", "-", "*", "/", "^"]):
            return "expression"
    # Concept: allow further heuristics
    if isinstance(value, (int, float)):
        return "constant"
    
    if isinstance(value, sp.Basic):
        if value.is_Symbol:
            return "variable"
        if value.is_Number:
            return "constant"
        if value.is_Add:
            return "sum"
        if value.is_Mul:
            return "product"
        if value.is_Pow:
            return "power"
        if value.is_Function:
            return "function"
        return "expression"

    return "unknown"

def add_node(g, value, **attrs):
    """
    Adds a node to the graph with attributes.
    """
    if value is None:
        return
    value = canonicalize_value(value)
    node_type = node_type(value)
    attrs.pop('type', None)
    if value in g:
        for k, v in attrs.items():
            if k in g.nodes[value] and g.nodes[value][k] != v:
                # Always use latest, *or* merge into list if both non-list
                if isinstance(g.nodes[value][k], list):
                    if v not in g.nodes[value][k]:
                        g.nodes[value][k].append(v)
                elif g.nodes[value][k] != v:
                    g.nodes[value][k] = [g.nodes[value][k], v]
            else:
                g.nodes[value][k] = v
        g.nodes[value]['type'] = node_type
        g.nodes[value]['value'] = value
    else:
        g.add_node(value, type=node_type, value=value, **attrs)

def get_nth(val, n=0):
    """Returns nth element if list/tuple, else itself if scalar and n==0, else None, always canonicalized."""
    if isinstance(val, (list, tuple)):
        if len(val) > n:
            return canonicalize_value(val[n])
        return None
    elif n == 0:
        return canonicalize_value(val)
    else:
        return None
    
