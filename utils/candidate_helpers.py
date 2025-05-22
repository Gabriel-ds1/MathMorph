# utils/candidate_helpers.py

import sympy as sp
from utils.sympy_helpers import is_symbolic
from pre_trained.novelty_classification import score_mathiness
from reasoning.symbolic_tools import build_sympy_equation
from models.graph_reasoner import graph_to_parse_dict

PRIME_PATTERN_HANDLERS = {}

def register_prime_handler(op):
    def decorator(func):
        PRIME_PATTERN_HANDLERS[op] = func
        return func
    return decorator

# ======== is_prime ========
@register_prime_handler('is_prime')
def handle_is_prime(record):
    lhs, rhs, op, sympy_eq = extract_vars(record)
    x = lhs[0] if (lhs and len(lhs) > 0) else None
    is_prime = True
    str_eq = f'is_prime({x}) = {is_prime}'
    method = 'primality_assertion'
    note = 'symbolic' if isinstance(x, str) or is_symbolic(x) else None
    return [make_candidate(record, derived_eq=sympy_eq, method=method, str_eq=str_eq, note=note)]

# ======== is_not_prime ========
@register_prime_handler('is_not_prime')
def handle_is_not_prime(record):
    lhs, rhs, op, sympy_eq = extract_vars(record)
    x = lhs[0] if (lhs and len(lhs) > 0) else None
    is_prime = False
    str_eq = f'is_not_prime({x}) = {is_prime}'
    method = 'primality_assertion'
    note = 'symbolic' if isinstance(x, str) or is_symbolic(x) else None
    return [make_candidate(record, derived_eq=sympy_eq, method=method, str_eq=str_eq, note=note)]

# ======== prime_order ========
@register_prime_handler('prime_order')
def handle_prime_order(record):
    lhs, rhs, op, sympy_eq = extract_vars(record)
    nth = lhs[0] if (lhs and len(lhs) > 0) else None
    str_eq = f'nth_prime({nth})'
    method = 'nth_prime_query'
    note = 'symbolic' if isinstance(nth, str) or is_symbolic(nth) else None
    return [make_candidate(record, derived_eq=sympy_eq, method=method, str_eq=str_eq, note=note)]

# ======== twin_primes ========
@register_prime_handler('twin_primes')
def handle_twin_primes(record):
    lhs, rhs, op, sympy_eq = extract_vars(record)
    x, y = lhs if lhs and len(lhs) == 2 else (None, None)
    method = 'twin_prime_assertion'
    str_eq = f'abs({x} - {y}) = 2, is_prime({x}) = True, is_prime({y}) = True'
    note = 'symbolic' if isinstance(x, str) or is_symbolic(x) or isinstance(y, str) or is_symbolic(y) else None
    return [make_candidate(record, derived_eq=sympy_eq, method=method, str_eq=str_eq, note=note)]

# ======== quadruplet_primes ========
@register_prime_handler('quadruplet_primes')
def handle_prime_quadruplets(record):
    lhs, rhs, op, sympy_eq = extract_vars(record)
    if not lhs or len(lhs) < 4:
        return []
    variables = lhs[:4] # [a, b, c, d]
    pattern = f"[{', '.join(map(str, variables))}] structure: [p, p+2, p+6, p+8]"
    method = 'prime_quadruplet_assertion'
    str_eq = f"{pattern}"
    note = 'symbolic' if any(isinstance(item, str) or is_symbolic(item) for item in variables) else None
        
    
    return [make_candidate(record, derived_eq=sympy_eq, method=method, str_eq=str_eq, note=note)]

#================================================
@register_prime_handler('goldbach')
def handle_goldbach(record):
    lhs, rhs, op, sympy_eq = extract_vars(record)
    x = lhs[0] if (lhs and len(lhs) > 0) else None
    method = 'goldbach_assertion'
    str_eq = f"{x} = p1 + p2, where p1, p2 are primes (Goldbach's conjecture)"
    note = 'symbolic' if isinstance(x, str) or is_symbolic(x) else None
    return [make_candidate(record, derived_eq=sympy_eq, method=method, str_eq=str_eq, note=note)]
#=================================================

# ======== next_prime ========
@register_prime_handler('next_prime')
def handle_next_prime(record):
    lhs, rhs, op, sympy_eq = extract_vars(record)
    x = lhs[0] if (lhs and len(lhs) > 0) else None
    result = rhs[0] if (rhs and len(rhs) > 0) else None
    str_eq = f'next_prime({x}) = {result}'
    method = 'next_prime_assertion'
    note = 'symbolic' if isinstance(x, str) or is_symbolic(x) else None
    return [make_candidate(record, derived_eq=sympy_eq, method=method, str_eq=str_eq, note=note)]

# ======== sum_of_two_primes ========
@register_prime_handler('sum_of_two_primes')
def handle_sum_of_two_primes(record):
    lhs, rhs, op, sympy_eq = extract_vars(record)
    x = lhs[0] if (lhs and len(lhs) > 0) else None
    y = lhs[1] if (lhs and len(lhs) > 0) else None
    result = rhs[0] if (rhs and len(rhs) > 0) else None
    str_eq = f'{x} + {y} = {result}'
    method = 'concrete_prime_sum'
    note = 'symbolic' if isinstance(x, str) or is_symbolic(x) or isinstance(y, str) or is_symbolic(y) or isinstance(result, str) or is_symbolic(result) else None
    return [make_candidate(record, derived_eq=sympy_eq, method=method, str_eq=str_eq, note=note)]

# ======== diff_of_primes ========
@register_prime_handler('diff_of_primes')
def handle_diff_of_primes(record):
    lhs, rhs, op, sympy_eq = extract_vars(record)
    x = lhs[0] if (lhs and len(lhs) > 0) else None
    y = lhs[1] if (lhs and len(lhs) > 0) else None
    result = rhs[0] if (rhs and len(rhs) > 0) else None
    str_eq = f'abs({x} - {y}) = {result}, is_prime({result}) = True'
    method = 'prime_difference'
    note = 'symbolic' if isinstance(x, str) or is_symbolic(x) or isinstance(y, str) or is_symbolic(y) or isinstance(result, str) or is_symbolic(result) else None
    return [make_candidate(record, derived_eq=sympy_eq, method=method, str_eq=str_eq, note=note)]

# ======== prime_factors ========
@register_prime_handler('prime_factors')
def handle_prime_factors(record):
    lhs, rhs, op, sympy_eq = extract_vars(record)
    # Ensure variables is always a list, avoiding None
    variables = lhs[:] if (lhs and len(lhs) > 0) else []
    result = rhs[0] if (rhs and len(rhs) > 0) else None

    # Ensure all variables stringified properly
    mult_formula = " * ".join(map(str, variables))
    # Ensure result is pretty for SymPy Symbol, integer, etc.
    result_str = str(result) if result is not None else "?"

    str_eq = f"{mult_formula} = {result_str}"
    method = 'prime_factors'
    note = 'symbolic' if any(isinstance(item, str) or is_symbolic(item) for item in variables) else None
    return [make_candidate(record, derived_eq=sympy_eq, method=method, str_eq=str_eq, note=note)]

# ======== where_is_prime ========
@register_prime_handler('where_is_prime')
def handle_where_is_prime(record):
    lhs, rhs, op, sympy_eq = extract_vars(record)
    # usually where_is_prime: lhs = [n], meaning nth prime
    n = lhs[0] if (lhs and len(lhs) > 0) else None
    str_eq = f"where_is_prime({n}) = prime({n})"
    method = 'where_is_prime_query'
    note = 'symbolic' if isinstance(n, str) or is_symbolic(n) else None
    return [make_candidate(record, derived_eq=sympy_eq, method=method, str_eq=str_eq, note=note)]

# ======== prime_gap ========
@register_prime_handler('prime_gap')
def handle_prime_gap(record):
    lhs, rhs, op, sympy_eq = extract_vars(record)
    x = lhs[0] if (lhs and len(lhs) > 0) else None
    y = lhs[1] if (lhs and len(lhs) > 1) else None
    gap = rhs[0] if (rhs and len(rhs) > 0) else None
    str_eq = f"abs({x} - {y}) = {gap}, isprime({x}) = True, isprime({y}) = True"
    method = 'prime_gap_assertion'
    note = 'symbolic' if (isinstance(x, str) or is_symbolic(x) or isinstance(y, str) or is_symbolic(y) or isinstance(gap, str) or is_symbolic(gap)) else None
    return [make_candidate(record, derived_eq=sympy_eq, method=method, str_eq=str_eq, note=note)]

# ======== triplet_primes ========
@register_prime_handler('triplet_primes')
def handle_triplet_primes(record):
    lhs, rhs, op, sympy_eq = extract_vars(record)
    # triplet should be length 3
    if not lhs or len(lhs) < 3:
        return []
    a, b, c = lhs[:3]
    str_eq = f"{a}, {b}, {c} are triplet primes: isprime({a}), isprime({b}), isprime({c}); spacings: ({b}-{a}), ({c}-{b})"
    method = 'triplet_primes_structure'
    note = 'symbolic' if any(isinstance(x, str) or is_symbolic(x) for x in (a, b, c)) else None
    return [make_candidate(record, derived_eq=sympy_eq, method=method, str_eq=str_eq, note=note)]

# ======== prime_exclusion_zone ========
@register_prime_handler('prime_exclusion_zone')
def handle_prime_exclusion_zone(record):
    lhs, rhs, op, sympy_eq = extract_vars(record)
    x = lhs[0] if (lhs and len(lhs) > 0) else None
    result = rhs[0] if (rhs and len(rhs) > 0) else None
    str_eq = f"prime_exclusion_zone({x}) = {result}"
    method = 'prime_exclusion_zone'
    note = 'symbolic' if (isinstance(x, str) or is_symbolic(x) or isinstance(result, str) or is_symbolic(result)) else None
    return [make_candidate(record, derived_eq=sympy_eq, method=method, str_eq=str_eq, note=note)]

# ======== prime_exclusion_zone_range ========
@register_prime_handler('prime_exclusion_zone_range')
def handle_prime_exclusion_zone_range(record):
    lhs, rhs, op, sympy_eq = extract_vars(record)
    x = lhs[0] if (lhs and len(lhs) > 0) else None
    result1 = rhs[0] if (rhs and len(rhs) > 0) else None
    result2 = rhs[1] if (rhs and len(rhs) > 1) else None
    str_eq = f"prime_exclusion_zone_range({x}) = [{result1}, {result2}]"
    method = 'prime_exclusion_zone_range'
    note = 'symbolic' if (isinstance(x, str) or is_symbolic(x) or isinstance(result1, str) or is_symbolic(result1) or isinstance(result2, str) or is_symbolic(result2)) else None
    return [make_candidate(record, derived_eq=sympy_eq, method=method, str_eq=str_eq, note=note)]

# ======== prime_exclusion_vals ========
@register_prime_handler('prime_exclusion_vals')
def handle_prime_exclusion_vals(record):
    lhs, rhs, op, sympy_eq = extract_vars(record)
    x = lhs[0] if (lhs and len(lhs) > 0) else None
    val = rhs[0] if (rhs and len(rhs) > 0) else None
    order = record.get('parsed', {}).get('order') if 'parsed' in record else record.get('order', None)
    local = record.get('parsed', {}).get('local') if 'parsed' in record else record.get('local', None)
    if (lhs[0] == 2):
         str_eq = f"prime exclusion for 2 is always 0"
    else:
        if order[0] in ('furthest', 'largest', 'biggest', 'highest', 'second', 'last', 'final'):
            if local[0] == 'overshoot':
                str_eq = f"{lhs[0]} + (2 * ({lhs[0]} - 1) - {lhs[0]})"
            elif local[0] == 'undershoot':
                str_eq = f"{lhs[0]} - (2 * ({lhs[0]} - 1) - {lhs[0]})"
        elif order[0] in ('closest', 'smallest', 'nearest', 'lowest', 'first', 'beginning'):
            if local[0] == 'overshoot':
                str_eq = f"{lhs[0]} + 1"
            elif local[0] == 'undershoot':
                str_eq = f"{lhs[0]} - 1"
    method = f"prime_exclusion_val({x}, order={order[0]}, local={local[0]}) = {val}"
    note = 'symbolic' if (isinstance(x, str) or is_symbolic(x) or isinstance(val, str) or is_symbolic(val) or isinstance(order, str) or is_symbolic(order) or isinstance(local, str) or is_symbolic(local)) else None
    return [make_candidate(record, derived_eq=sympy_eq, method=method, str_eq=str_eq, note=note)]

def extract_vars(record):
    """Helper to robustly unpack lhs/rhs/op with [] or None fallback."""
    parsed = record.get('parsed', {}) if 'parsed' in record else record
    lhs = parsed.get('lhs') or record['sympy_eq']['meta']['lhs'] or []
    rhs = parsed.get('rhs') or record.get('sympy_eq', {}).get('meta', {}).get('rhs')
    sympy_eq = record.get('sympy_eq').get('eq')
    op = parsed.get('op')
    return lhs, rhs, op, sympy_eq

def safe_unwrap_eq_tuple(eq_tuple):
    """
    Handles eq_tuple being (eq, eq_type)
    or ([eq1, eq2], eq_type) (system)
    or just a single eq.
    """
    # Eq tuple is a single equation
    if isinstance(eq_tuple, (sp.Equality, sp.Basic)) or eq_tuple is None:
        return eq_tuple, 'equation' if isinstance(eq_tuple, sp.Equality) else None
    elif isinstance(eq_tuple, sp.Basic):
        return eq_tuple, None
    # Eq tuple is (eq, eq_type)
    if isinstance(eq_tuple, (tuple, list)) and len(eq_tuple) == 2 and isinstance(eq_tuple[1], str):
        return eq_tuple
    # Eq tuple is (eq1, eq2, eq_type) or more
    if isinstance(eq_tuple, (tuple, list)) and len(eq_tuple) > 2 and isinstance(eq_tuple[-1], str):
        # treat (eq1, ..., eqN, eq_type)
        return eq_tuple[:-1], eq_tuple[-1]
    # Fallback: treat as not supported
    return None, None

def make_candidate(record, derived_eq, method, str_eq=None, op_context=None, note=None, correct=None):
    cand = {
        'source_step': record['step'],
        'op': record['parsed'].get('op'),
        'orig_sentence': record['sentence'],
        'derived_eq': derived_eq,
        'str_eq': str_eq,
        'generation_method': method}
    if op_context:
        cand['op_context'] = op_context
    if note:
        cand['note'] = note
    if correct:
        cand['is_correct'] = correct
    return cand

def enhance_candidates(candidate_list):
    for cand in candidate_list:
        # ---- Run novelty classifier ----
        string_formula = cand.get('str_eq') or str(cand.get('derived_eq'))
        if string_formula:
            novelty_res = score_mathiness(string_formula)
            cand['novelty_label'] = novelty_res['novelty_label']
            cand['novelty_conf'] = novelty_res['confidence']
            cand['novelty_response'] = novelty_res['llm_response']
        # ---- Graph roundtrip test ----
        if 'graph' in cand and cand['graph'] is not None:
            roundtrip_parse = graph_to_parse_dict(cand['graph'])
            cand['graph_roundtrip_parse'] = roundtrip_parse
            sympy2 = build_sympy_equation(roundtrip_parse)
            cand['sympy_roundtrip'] = sympy2.get('eq') if sympy2 else None
    return candidate_list