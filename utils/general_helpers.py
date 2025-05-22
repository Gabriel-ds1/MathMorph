# utils/general_helpers.py

from collections.abc import Iterable
import sympy as sp

def handle_unregistered_action(graph, state):
    op = graph.graph.get('operation', None)
    return graph, state, f"(No action registered for op {op})"

def annotate_error(stage, err, input_data=None):
    import traceback
    tb = traceback.format_exc()
    return {"error_stage": stage,
        "error_message": str(err),
        "input": str(input_data)[:400],  # preview
        "traceback": tb}

def all_ints_or_float(*args):
    flat = []
    for a in args:
        if isinstance(a, Iterable) and not isinstance(a, (str, bytes)):
            flat.extend(a)
        else:
            flat.append(a)
    return all(isinstance(x, (int, float, sp.Integer, sp.Float)) for x in flat)

def check_template_args(required_args):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for name, val in zip(required_args, args):
                if val is None or val == "":
                    return {
                        "formulas": [],
                        "explanation": f"Cannot construct: {name} is missing."}
            # For keyword arguments too
            for name in required_args[len(args):]:
                if kwargs.get(name) is None or kwargs.get(name) == "":
                    return {
                        "formulas": [],
                        "explanation": f"Cannot construct: {name} is missing."}
            return func(*args, **kwargs)
        return wrapper
    return decorator

def flatten_attr(val):
    """
    Convert complex objects to JSON-serializable primitives.
    """
    # SymPy expressions
    if isinstance(val, sp.Basic):
        if hasattr(val, 'name'):  # Symbols
            return str(val.name)
        return str(val)
    # Tuples/Lists: Flatten each item
    if isinstance(val, (tuple, list)):
        return [flatten_attr(x) for x in val]
    # Dicts: Recursively flatten
    if isinstance(val, dict):
        return {str(k): flatten_attr(v) for k,v in val.items()}
    # Functions/classes
    if callable(val):
        return repr(val)
    # Sets
    if isinstance(val, set):
        return [flatten_attr(x) for x in val]
    # Everything else: fallback to str if not a primitive
    if not isinstance(val, (str, int, float, bool, type(None))):
        return str(val)
    return val

def graph_to_serializable(g):
    """
    Returns data (nodes, edges, attrs) as a JSON-serializable dict.
    """
    return {
        "directed": g.is_directed(),
        "graph": {k: flatten_attr(v) for k, v in g.graph.items()},
        "nodes": [{"id": flatten_attr(n), **{k: flatten_attr(v) for k, v in d.items()}} for n, d in g.nodes(data=True)],
        "edges": [{"source": flatten_attr(u), "target": flatten_attr(v), **{k: flatten_attr(val) for k, val in d.items()}}
            for u, v, d in g.edges(data=True)]}

def prime_flag_is_true(val):
    """
    Returns sp.isprime(val) if val can be interpreted as an integer, else True (unknown/assume candidate for prime).
    """
    try:
        return sp.isprime(int(val))
    except Exception:
        return True
    
def prime_flag_is_false(val):
    """
    Returns sp.isprime(val) if val can be interpreted as an integer, else True (unknown/assume candidate for prime).
    """
    try:
        return not sp.isprime(int(val))
    except Exception:
        return False
    
    