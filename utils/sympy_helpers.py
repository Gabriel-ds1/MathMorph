# utils/sympy_helpers.py

import sympy as sp
from utils.general_helpers import annotate_error

symbols = {}

# Convert all variable names/numbers to sympy objects
def get_sp_obj(name):
    # Try to convert to number, else symbol
    try:
        symp = sp.sympify(name)
        return canonicalize_value(symp)
    except Exception as e:
        if name not in symbols:
            symbols[name] = sp.symbols(name)
        annotate_error("get_sp_obj", e, str(name))
        return symbols[name]
    
def get_field_obj(key, parse_dict, default=None):
    value = parse_dict.get(key, default)
    if isinstance(value, list):
        return [get_sp_obj(x) for x in value]
    elif value is None:
        return None
    else:
        return get_sp_obj(value)

def safe_sympify(value):
    try:
        if isinstance(value, sp.Basic):
            return value
        return sp.sympify(value)
    except Exception as e:
        annotate_error("safe_sympify", e, str(value))
        # fallback for variables
        return sp.Symbol(str(value))
    
def is_symbolic(x):
    # Returns True if x is a sympy symbol or something likely variable
    return (hasattr(x, "is_Symbol") and x.is_Symbol) or (isinstance(x, str) and not str(x).isdigit())

def canonicalize_value(value):
    """
    Forces all values used as node IDs to be SymPy objects:
    """
    if isinstance(value, sp.Basic):
        return value
    if isinstance(value, (int, float)):
        return sp.Integer(value) if isinstance(value, int) else sp.Float(value)
    if isinstance(value, str):
        value = value.replace(',', '')
        for end in ['st', 'nd', 'rd', 'th']:
            if value.endswith(end) and value[:-len(end)].isdigit():
                value = value[:-len(end)]
        if value.isdigit():
            return sp.Integer(value)
        try:
            expr = sp.sympify(value)
            return expr
        except Exception as e:
            annotate_error("canonicalize_value", e, str(value))
            return sp.Symbol(value)
    return value

def is_trivial_equation(eq):
    """
    Returns True if eq is a mathematically trivial equality (e.g. x=x, 0=0, a=a), else False.
    Supports sympy Eq, booleans, and stringified forms.
    """
    if isinstance(eq, sp.Equality):
        lhs, rhs = eq.lhs, eq.rhs
        if isinstance(lhs, (tuple, list)) and isinstance(rhs, (tuple, list)):
            # Must be same length and all elements trivially equal
            if len(lhs) != len(rhs):
                return False
            return all(is_trivial_equation(sp.Eq(l, r, evaluate=False)) for l, r in zip(lhs, rhs))
        # Otherwise, default: try subtracting and simplifying
        # SymPy's canonical test: x == x or numbers equal
        try:
            return sp.simplify(lhs - rhs) == 0
        except Exception as e:
            annotate_error("is_trivial_equation", e, str(eq))
            # If not subtractable but strings equal, allow that as fallback
            return str(lhs) == str(rhs)
    if isinstance(eq, (bool, int, float)):
        return False  # usually not relevant here
    if isinstance(eq, str):
        # crude fallback
        try:
            left, right = eq.split('=')
            return left.strip() == right.strip()
        except Exception as e:
            annotate_error("is_trivial_equation", e, str(eq))
            return False
    return False

def clean_attributes(graph):
    # Fix node attributes
    for n, attrs in list(graph.nodes(data=True)):
        for key, value in attrs.items():
            # Convert SymPy numbers to int/float, everything else to string except basic types
            if isinstance(value, sp.Basic):
                if hasattr(value, 'is_Integer') and value.is_Integer:
                    graph.nodes[n][key] = int(value)
                elif hasattr(value, 'is_Float') and value.is_Float:
                    graph.nodes[n][key] = float(value)
                else:
                    graph.nodes[n][key] = str(value)
            elif key == "label" and key.isdigit:
                graph.nodes[n][key] = int(value)
            elif key == "label" and not key.isdigit:
                graph.nodes[n][key] = str(value)
    # Fix edge attributes
    for u, v, attrs in list(graph.edges(data=True)):
        for key, value in attrs.items():
            if isinstance(value, sp.Basic):
                if hasattr(value, 'is_Integer') and value.is_Integer:
                    graph.edges[u, v][key] = int(value)
                elif hasattr(value, 'is_Float') and value.is_Float:
                    graph.edges[u, v][key] = float(value)
                else:
                    graph.edges[u, v][key] = str(value)
            elif key == "label" and key.isdigit:
                graph.nodes[n][key] = int(value)
            elif key == "label" and not key.isdigit:
                graph.nodes[n][key] = str(value)
