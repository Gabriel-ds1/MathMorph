# models/graph_reasoner.py

import networkx as nx
import sympy as sp
from utils.general_helpers import prime_flag_is_true, prime_flag_is_false, annotate_error
from utils.sympy_helpers import canonicalize_value

def equation_to_graph(parse_dict):
    """
    Converts a parsed equation into a networkx graph.
    Nodes: variables and constants
    Edges: operations (with label: add, mul, etc.)
    """
    try:
        op = parse_dict.get('op')
        lhs = parse_dict.get('lhs', [])
        if isinstance(lhs, list):
            lhs = [canonicalize_value(x) for x in lhs]
        else:
            lhs = [canonicalize_value(lhs)]
        # Safeguard all lhs index access
        lhs_0 = lhs[0] if len(lhs) > 0 and lhs[0] is not None else None
        lhs_1 = lhs[1] if len(lhs) > 1 and lhs[1] is not None else None
        lhs_2 = lhs[2] if len(lhs) > 2 and lhs[2] is not None else None
        lhs_3 = lhs[3] if len(lhs) > 3 and lhs[3] is not None else None

        rhs = canonicalize_value(parse_dict.get('rhs'))
        rhs_0 = _get_nth(rhs, 0)
        rhs_1 = _get_nth(rhs, 1)
        order_obj = canonicalize_value(parse_dict.get('order'))
        local_obj = canonicalize_value(parse_dict.get('local'))
        base_obj = canonicalize_value(parse_dict.get('base'))
        exp_obj = canonicalize_value(parse_dict.get('exp'))
        radicand_obj = canonicalize_value(parse_dict.get('radicand'))
        degree_obj = canonicalize_value(parse_dict.get('degree'))
        dividend_obj = canonicalize_value(parse_dict.get('dividend'))
        divisor_obj = canonicalize_value(parse_dict.get('divisor'))
        remainder_obj = canonicalize_value(parse_dict.get('remainder'))


        g = nx.DiGraph()  # Directed graph
        
        # Add nodes with type/role/meaning
        if isinstance(lhs, list):
            for idx, var in enumerate(lhs):
                if var is not None:
                    _add_node(g, var, role=f"variable{idx+1}")
        else:
            if lhs is not None:
                _add_node(g, lhs, role="variable")


        if isinstance(rhs, list) and rhs:
            _add_node(g, rhs[0], role="result")
        elif rhs is not None:
            _add_node(g, rhs, role="result")

        # --- Arithmetic operators ---
        if op in ['add', 'mul', 'sub', 'div']:
            # Edge from both lhs variables to rhs, labeled with operation
            if lhs_0 is not None and rhs_0 is not None:
                g.add_edge(lhs_0, rhs_0, label=op, operation=op, role="variable1", desc="variable1 is {}".format(lhs_0))
            if lhs_1 is not None and rhs_0 is not None:
                g.add_edge(lhs_1, rhs_0, label=op, operation=op, role="variable2", desc="variable2 is {}".format(lhs_1))
            
        
        # --- Equals ---
        elif op == 'eq' and len(lhs) == 1:
            if lhs_0 is not None and rhs_0 is not None:
                g.add_edge(lhs_0, rhs_0, label='eq', operation='eq', desc="Assignment/equality")

        # --- Primes and Concept Relations ---
        elif op == 'is_prime':
            _add_node(g, lhs_0, is_prime=prime_flag_is_true(lhs_0))
            if lhs_0 is not None:
                g.add_edge(lhs_0, lhs_0, label='is_prime', relation="property", desc="Membership in prime set")
        elif op == 'is_not_prime':
            _add_node(g, lhs_0, is_prime=prime_flag_is_false(lhs_0))
            if lhs_0 is not None:
                g.add_edge(lhs_0, lhs_0, label='is_not_prime', relation="property", desc="Not a member of prime set")
        elif op == 'prime_order':
            _add_node(g, lhs_0, prime_order=order_obj[0])
            _add_node(g, sp.Symbol('prime'), type='concept')
            if lhs_0 is not None:
                g.add_edge(lhs_0, sp.Symbol('prime'), label=f'prime_order_{order_obj[0]}', relation="order", order=order_obj[0])
        # Twin primes
        elif op == 'twin_primes':
            _add_node(g, lhs_0, twin_prime_with=lhs_1)
            _add_node(g, lhs_1, twin_prime_with=lhs_0)
            _add_node(g, sp.Symbol('prime'), type='concept')
            if lhs_0 is not None:
                g.add_edge(lhs_0, sp.Symbol('prime'), label='twin_prime', relation='concept')
            if lhs_1 is not None:
                g.add_edge(lhs_1, sp.Symbol('prime'), label='twin_prime', relation='concept')
            if lhs_0 is not None and lhs_1 is not None:
                g.add_edge(lhs_0, lhs_1, label='twin_prime_pair', relation='twin_pair', desc="Twin prime pair")
        elif op == 'diff_of_primes':
            _add_node(g, lhs_0, is_prime=prime_flag_is_true(lhs_0))
            _add_node(g, lhs_1, is_prime=prime_flag_is_true(lhs_1))
            sym_lhs0 = sp.Symbol(str(lhs_0))
            sym_lhs1 = sp.Symbol(str(lhs_1))
            diff = sym_lhs0 - sym_lhs1
            lhs_2 = diff
            _add_node(g, lhs_2, is_prime=prime_flag_is_true(lhs_2))
            if lhs_0 is not None and lhs_1 is not None:
                g.add_edge(lhs_0, lhs_1, label='difference_of', relation='arithmetic')
            if lhs_2 is not None:
                g.add_edge(lhs_2, sp.Symbol('prime'), label='diff_of_primes', relation='property', desc="Difference of primes")
        elif op == 'sum_of_two_primes':
            _add_node(g, lhs_0, is_prime=prime_flag_is_true(lhs_0))
            _add_node(g, lhs_1, is_prime=prime_flag_is_true(lhs_0))
            _add_node(g, rhs_0, is_prime=prime_flag_is_true(rhs_0))
            if lhs_0 is not None and lhs_1 is not None:
                g.add_edge(lhs_0, lhs_1, label='add', relation='property', desc="First prime")
            if rhs_0 is not None:
                g.add_edge(rhs_0, sp.Symbol('prime'), label='is_prime', relation='property', desc="Second prime")
        elif op == 'prime_factors':
            _add_node(g, lhs_0, is_prime=prime_flag_is_true(lhs_0))
            _add_node(g, lhs_1, is_prime=prime_flag_is_true(lhs_1))
            _add_node(g, lhs_2, is_prime=prime_flag_is_true(lhs_2))
            _add_node(g, rhs_0, is_prime=prime_flag_is_true(rhs_0))
            if lhs_0 is not None and rhs_0 is not None:
                g.add_edge(lhs_0, rhs_0, label='is_prime_factor', relation='property', desc="First prime factor")
            if lhs_1 is not None and rhs_0 is not None:
                g.add_edge(lhs_1, rhs_0, label='is_prime_factor', relation='property', desc="Second prime factor")
            if lhs_2 is not None and rhs_0 is not None:
                g.add_edge(lhs_2, rhs_0, label='is_prime_factor', relation='property', desc="Third prime factor")
        elif op == 'next_prime':
            _add_node(g, lhs_0, is_prime=prime_flag_is_true(lhs_0))
            _add_node(g, rhs_0, role='result', is_prime=prime_flag_is_true(rhs_0))
            if lhs_0 is not None and rhs_0 is not None:
                g.add_edge(lhs_0, rhs_0, label='next_prime', relation='property', desc="Next prime")
        elif op == 'where_is_prime':
            _add_node(g, lhs_0, is_prime=prime_flag_is_true(lhs_0))
            temp_rhs = prime_flag_is_true(lhs_0)
            _add_node(g, temp_rhs, role='result', is_prime=prime_flag_is_true(temp_rhs))
            if lhs_0 is not None and temp_rhs is not None:
                g.add_edge(lhs_0, temp_rhs, label='where_is_prime', relation='property')
        elif op == 'prime_gap':#"The gap between the primes 17 and 23 is 6."
            _add_node(g, lhs_0, is_prime=prime_flag_is_true(lhs_0))
            _add_node(g, lhs_1, is_prime=prime_flag_is_true(lhs_1))
            _add_node(g, rhs_0, is_prime=prime_flag_is_true(rhs_0))
            if lhs_0 is not None and lhs_1 is not None:
                g.add_edge(lhs_0, lhs_1, label='difference_of', relation='arithmetic')
            if lhs_0 is not None and lhs_1 is not None and rhs_0 is not None:
                g.add_edge(rhs_0, (lhs_0, lhs_1), label='is_gap_of_primes', relation='property', desc="Gap of primes")
        elif op == 'quadruplet_primes':
            _add_node(g, lhs_0, is_prime=prime_flag_is_true(lhs_0))
            _add_node(g, lhs_1, is_prime=prime_flag_is_true(lhs_1))
            _add_node(g, lhs_2, is_prime=prime_flag_is_true(lhs_2))
            _add_node(g, lhs_3, is_prime=prime_flag_is_true(lhs_3))
            if lhs_0 is not None:
                g.add_edge(lhs_0, sp.Symbol('prime'), label='is_prime', relation='property')
            if lhs_0 is not None and lhs_1 is not None:
                g.add_edge(lhs_0, lhs_1, label='p+2', relation='property')
            if lhs_1 is not None:
                g.add_edge(lhs_1, sp.Symbol('prime'), label='is_prime', relation='property')
            if lhs_0 is not None and lhs_2 is not None:
                g.add_edge(lhs_0, lhs_2, label='p+6', relation='property')
            if lhs_2 is not None:
                g.add_edge(lhs_2, sp.Symbol('prime'), label='is_prime', relation='property')
            if lhs_0 is not None and lhs_3 is not None:
                g.add_edge(lhs_0, lhs_3, label='p+8', relation='property')
            if lhs_3 is not None:
                g.add_edge(lhs_3, sp.Symbol('prime'), label='is_prime', relation='property')

        elif op == 'triplet_primes':
            _add_node(g, lhs_0, is_prime=prime_flag_is_true(lhs_0))
            _add_node(g, lhs_1, is_prime=prime_flag_is_true(lhs_1))
            _add_node(g, lhs_2, is_prime=prime_flag_is_true(lhs_2))
            if lhs_0 is not None and lhs_1 is not None:
                g.add_edge(lhs_0, lhs_1, label='is_prime', relation='property')
            if lhs_1 is not None and lhs_2 is not None:
                g.add_edge(lhs_1, lhs_2, label='is_prime', relation='property')
            if lhs_2 is not None and lhs_0 is not None:
                g.add_edge(lhs_2, lhs_0, label='is_prime', relation='property')

        elif op == 'prime_exclusion_zone':
            _add_node(g, lhs_0, is_prime=prime_flag_is_true(lhs_0))
            _add_node(g, rhs_0, role='result', is_prime=prime_flag_is_true(rhs_0))
            if lhs_0 is not None and rhs_0 is not None:
                g.add_edge(lhs_0, rhs_0, label='prime_exclusion_zone', operation='prime_exclusion')

        elif op == 'prime_exclusion_zone_range':
            _add_node(g, lhs_0, is_prime=prime_flag_is_true(lhs_0))
            _add_node(g, rhs_0, is_prime=prime_flag_is_true(rhs_0))
            _add_node(g, rhs_1, role='result2', is_prime=prime_flag_is_true(rhs_1))
            if lhs_0 is not None and rhs_0 is not None:
                g.add_edge(lhs_0, rhs_0, label='prime_exclusion_zone_range', operation='prime_exclusion_range')
            if lhs_0 is not None and rhs_1 is not None:
                g.add_edge(lhs_0, rhs_1, label='prime_exclusion_zone_range', operation='prime_exclusion_range')

        elif op == 'prime_exclusion_vals':
            _add_node(g, lhs_0, is_prime=prime_flag_is_true(lhs_0))
            _add_node(g, rhs_0, role='result', order=order_obj[0], local=local_obj[0], is_prime=prime_flag_is_true(rhs_0))
            if lhs_0 is not None and rhs_0 is not None and local_obj[0] is not None and order_obj[0] is not None:
                g.add_edge(lhs_0, rhs_0, label=f'prime_exclusion_{local_obj[0]}_values', order=order_obj[0], operation='prime_exclusion')

        # Divisibility, divides, and factor
        elif op == 'divisible':
            _add_node(g, lhs_0)
            _add_node(g, lhs_1)
            if lhs_0 is not None and lhs_1 is not None:
                g.add_edge(lhs_0, lhs_1, label='divisible_by', relation='arithmetic')
        elif op == 'divides':
            _add_node(g, lhs_0)
            _add_node(g, lhs_1)
            if lhs_0 is not None and lhs_1 is not None:
                g.add_edge(lhs_0, lhs_1, label='divides', relation='arithmetic')
        elif op == 'factor':
            _add_node(g, lhs_0)
            _add_node(g, lhs_1)
            if lhs_0 is not None and lhs_1 is not None:
                g.add_edge(lhs_0, lhs_1, label='factor_of', relation='arithmetic')

        # Power, roots, and exponents
        elif op == 'squared':
            _add_node(g, base_obj[0], role='base')
            _add_node(g, rhs_0)
            if base_obj[0] is not None and rhs_0 is not None:
                g.add_edge(base_obj[0], rhs_0, label='squared', operation='power', exponent=2, desc='base squared')
        elif op == 'cubed':
            _add_node(g, base_obj[0], role='base')
            _add_node(g, rhs_0)
            if base_obj[0] is not None and rhs_0 is not None:
                g.add_edge(base_obj[0], rhs_0, label='cubed', operation='power', exponent=3, desc='base cubed')
        elif op == 'power':
            _add_node(g, base_obj[0], role='base')
            _add_node(g, rhs_0)
            _add_node(g, exp_obj[0], role='exponent')
            if base_obj[0] is not None and rhs_0 is not None:
                g.add_edge(base_obj[0], rhs_0, label=f'power_{exp_obj[0]}', operation='power', exponent=exp_obj[0], desc="base raised to power")
            if exp_obj[0] is not None and rhs_0 is not None:
                g.add_edge(exp_obj[0], rhs_0, label=f'power_{exp_obj[0]}', operation='power', exponent=exp_obj[0], desc="base raised to power")
        elif op == 'sqrt':
            _add_node(g, radicand_obj[0], role="radicand")
            _add_node(g, rhs_0, role="result")
            if radicand_obj[0] is not None and rhs_0 is not None:
                g.add_edge(radicand_obj[0], rhs_0, label='sqrt', operation='root', degree=2, desc="square root")
        elif op == 'cbrt':
            _add_node(g, radicand_obj[0], role="radicand")
            _add_node(g, rhs_0, role="result")
            if radicand_obj[0] is not None and rhs_0 is not None:
                g.add_edge(radicand_obj[0], rhs_0, label='cbrt', operation='root', degree=3, desc="cube root")
        elif op == 'root':
            
            _add_node(g, radicand_obj[0], role="radicand")
            _add_node(g, rhs_0, role="result")
            _add_node(g, degree_obj[0], role="degree")
            if radicand_obj[0] is not None and rhs_0 is not None:
                g.add_edge(radicand_obj[0], rhs_0, label=f'root_{degree_obj[0]}', operation='root', degree=degree_obj[0], desc="nth root")
            if degree_obj[0] is not None and rhs_0 is not None:
                g.add_edge(degree_obj[0], rhs_0, label=f'root', operation='root', degree=degree_obj[0], desc="nth root")

        # Remainder
        elif op == 'remainder':
            _add_node(g, dividend_obj[0], role="dividend")
            _add_node(g, divisor_obj[0], role="divisor")
            _add_node(g, remainder_obj[0], role="remainder")
            if dividend_obj[0] is not None and divisor_obj[0] is not None:
                g.add_edge(dividend_obj[0], divisor_obj[0], label='divided_by', relation='arithmetic')
            if dividend_obj[0] is not None and remainder_obj[0] is not None:
                g.add_edge(dividend_obj[0], remainder_obj[0], label='leaves_remainder', relation='arithmetic')

        else:
            # Unknown operation: create an "unknown_operation" node and an edge
            op_node = f"unknown_op_{op}"
            _add_node(g, op_node, type="unknown_operation", op=op, original_parse=parse_dict)
            
            # Try to connect lhs and rhs for traceability (if they exist)
            # If lhs/rhs are missing, at least attach to op_node
            lhs_nodes = lhs if isinstance(lhs, list) else [lhs] if lhs is not None else []
            for src in lhs_nodes:
                if src is not None:
                    _add_node(g, src)
                    g.add_edge(src, op_node, label="unknown_operation_edge", original_op=op)
            if rhs_0 is not None:
                _add_node(g, rhs_0)
                g.add_edge(op_node, rhs_0, label="unknown_op_result", original_op=op)
            # Optional: tag the graph with the fact it was unknown
            g.graph["unknown_op"] = op

        # You could add the original operation as a graph attribute too, if desired
        g.graph['operation'] = op

        return g
    
    except Exception as e:
        return annotate_error("equation_to_graph", e, parse_dict)
    
def graph_to_parse_dict(graph):
    """
    Inverse utility: Converts a networkx graph back to parse_dict, for roundtrip tests.
    - Reconstructs {op, lhs, rhs,...} where possible.
    - Handles all main math Ops, plus prime attributes/order/local for advanced types.
    - If info loss: yields ('unparsed' or 'ambiguous') fields in result, and a 'trace' field explaining choices.
    """

    graph_parse = {}
    trace = []

    # 1. Operation extraction
    op = graph.graph.get('operation')
    if op:
        graph_parse['op'] = op
        trace.append(f"Operation taken from graph attribute: {op}")
    else:
        # Try to guess from edges if not in attribute
        for u, v, d in graph.edges(data=True): # u -> source node (e.g. lhs node ID), v -> destination node (e.g. rhs node ID), d -> dictionary of attributes
            if 'operation' in d:
                graph_parse['op'] = d['operation']
                trace.append(f"Operation inferred from edge: {u}->{v}: {d['operation']}")
                op = d['operation']
                break

    # 2. Build role-maps and attribute-maps
    role_map = {} # role: [node ids]

    for n, attrs in graph.nodes(data=True):
        role_val = attrs.get('role')
        if role_val is not None:
            if isinstance(role_val, list):
                for role in role_val:
                    role_map.setdefault(role, []).append(n) # set default to not overwrite n (instead append it)
            else:
                role_map.setdefault(role_val, []).append(n)

    
    # 3. Define mapping of graph roles → parse_dict slots
    slots = {
        'variable1': 'lhs',
        'variable2': 'lhs',
        'variable3': 'lhs',
        'variable4': 'lhs',
        'base': 'base',
        'radicand': 'radicand',
        'exponent': 'exp',
        'degree': 'degree',
        'dividend': 'dividend',
        'divisor': 'divisor',
        'remainder': 'remainder',
        'result': 'rhs',
        'result1':'rhs',
        'result2':'rhs'}

    # Initialize
    slot_vals = {v: [] for v in set(slots.values())} # grab list of all field names and remove duplicates with 'set'

    # Assign nodes to parse_dict fields via 'role'
    for role, nodes in role_map.items():
        slot = slots.get(role)
        if slot:
            slot_vals[slot].extend(nodes)
        else:
            # Don't drop, just log/keep as extra
            trace.append(f"Unparsed role: {role} for ndoes {nodes}")

    # 4. Special fields from node or edge attributes
    # (e.g. prime_order, order/local for exclusion ops)
    for n, attrs in graph.nodes(data=True):
        # For prime order (e.g.: prime_order(x))
        if 'prime_order' in attrs:
            graph_parse['order'] = [attrs['prime_order']]
            trace.append(f"prime_order attribute: {attrs['prime_order']} (from node {n})")
        # For order/local (prime_exclusion_vals, etc)
        if 'order' in attrs:
            graph_parse.setdefault('order', []).append(attrs['order'])
            trace.append(f"order from node {n}: {attrs['order']}")
        if 'local' in attrs:
            graph_parse.setdefault('local', []).append(attrs['local'])
            trace.append(f"local from node {n}: {attrs['local']}")
        


        # Prime/Property nodes: handle 'is_prime', 'is_not_prime', etc.
        for n, attrs in graph.nodes(data=True):
            if attrs.get('is_prime', None) is True and not 'prime' in role_map:
                graph_parse['is_prime'] = True
                trace.append(f"Found is_prime True at node {n}")

    # 5. Sometimes, these are on edges (especially for root/power ops)
    for u, v, d in graph.edges(data=True):
        # Exponent for powers
        if 'exponent' in d:
            graph_parse.setdefault('exp', []).append(d['exponent'])
            trace.append(f"exponent on edge {u}->{v}: {d['exponent']}")
        if 'degree' in d:
            graph_parse.setdefault('degree', []).append(d['degree'])
            trace.append(f"degree on edge {u}->{v}: {d['degree']}")
        if 'order' in d:
            graph_parse.setdefault('order', []).append(d['order'])
            trace.append(f"order on edge {u}->{v}: {d['order']}")
        if 'local' in d:
            graph_parse.setdefault('local', []).append(d['local'])
            trace.append(f"local on edge {u}->{v}: {d['local']}")


    # 6. Concept nodes (optional for downstream use)
    for n, attrs in graph.nodes(data=True):
        if attrs.get('type') == 'concept':
            graph_parse.setdefault('concept', []).append(n)
            trace.append(f"Concept node: {n}")


    # 7. Assign values to the parse dict, compressing if possible.
    # Try to compact singleton lists to scalars, except for 'lhs' and 'rhs'
    for field, vals in slot_vals.items():
        # Always keep lhs, rhs as lists (even if singleton); flatten others
        if field in ('lhs', 'rhs'):
            if vals: graph_parse[field] = [v for v in vals]
        else:
            if len(vals) == 1:
                graph_parse[field] = [vals[0]]  # wrap as list for uniformity
            elif len(vals) > 1:
                graph_parse[field] = vals

    # 8. Clean up: Remove empty or None values (but keep trace)
    graph_parse = {k: v for k, v in graph_parse.items() if v not in (None, [], {})}

    # 9. Attach trace
    graph_parse['trace'] = trace

    return graph_parse
    
def _node_type(value):
    """
    Classifies node type as variable, constant, or concept.
    """
    # could be improved, but as a start:
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

def _add_node(g, value, **attrs):
    """
    Adds a node to the graph with attributes.
    """
    if value is None:
        return
    value = canonicalize_value(value)
    node_type = _node_type(value)
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

def _get_nth(val, n=0):
    """Returns nth element if list/tuple, else itself if scalar and n==0, else None, always canonicalized."""
    if isinstance(val, (list, tuple)):
        if len(val) > n:
            return canonicalize_value(val[n])
        return None
    elif n == 0:
        return canonicalize_value(val)
    else:
        return None
    
def print_graph(graph):
    """
    Prints the nodes and edges of the graph for easy debugging.
    """
    print("Nodes:")
    for n, attrs in graph.nodes(data=True):
        print(f"  {n}", dict(attrs) if attrs else "")
    print("Edges:")
    for u, v, d in graph.edges(data=True):
        print(f"  {u} --[{d['label']}]--> {v}")