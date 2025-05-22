# reasoning/candidate_generator.py

import sympy as sp
from .graph_candidate_handlers import get_graph_candidates, clique_candidates, star_candidates, bipartite_candidates, motif_subgraph_candidates
from pre_trained.llm_candidate_generator import generate_auto_candidates
from utils.general_helpers import annotate_error
from utils.candidate_helpers import PRIME_PATTERN_HANDLERS, safe_unwrap_eq_tuple, make_candidate
from utils.sympy_helpers import is_trivial_equation


def commutative_candidates(eq, eq_type, op_context, scratchpad):
    """
    Generate candidates by swapping the left and right sides of the equation.
    This is only valid for commutative operations like addition and multiplication.
    example: x + y = 10 to y + x = 10
    """
    # eq_tuple: (sympy_eq, type), as returend by build_sympy_equation
    candidates = []

    if eq_type != 'equation' or not isinstance(eq, sp.Equality):
        return candidates
    lhs = eq.lhs
    rhs = eq.rhs
    try:
        # Commutative for addition and multiplication
        if isinstance(lhs, sp.Add) or isinstance(lhs, sp.Mul):
            rev_lhs = lhs.func(*reversed(lhs.args), evaluate=False)
            candidates.append(sp.Eq(rev_lhs, rhs, evaluate=False))
    except Exception as e:
        return [annotate_error("commutative_candidates", e, str(candidates))]
    return candidates

def isolating_candidates(eq, eq_type, op_context, scratchpad):
    candidates = []
    if eq_type != 'equation' or not isinstance(eq, sp.Equality):
        return candidates
    for sym in eq.free_symbols:
        try:
            solved = sp.solve(eq, sym)
            if solved:
                # handle both cases: solution is a list or not
                candidate = sp.Eq(sym, solved[0]) if isinstance(solved, list) else sp.Eq(sym, solved)
                candidates.append(candidate)
        except Exception as e:
            return [annotate_error("isolating_candidates", e, str(candidates))]
    return candidates

def prime_candidates(record, op_context, scratchpad):
    """
    Generate candidates for prime-related equations.
    """
    handlers = PRIME_PATTERN_HANDLERS
    op = str(op_context) if op_context else None
    if op and op in handlers:
        return handlers[op](record)
    else:
        # Return a stub/warning candidate dict
        return [{
            'derived_eq': None,
            'generation_method': 'prime_stub_unsupported_pattern',
            'note': f"No handler for prime op='{op}' in candidate_generator. Please implement this handler.",
            'source_step': record.get('step'),
            'orig_sentence': record.get('sentence')}]

def algebraic_candidates(eq, eq_type, record, op_context, scratchpad, correct):
    candidates = []
    if eq_type == 'equation' and isinstance(eq, sp.Equality):
        for sym in eq.free_symbols:
            if isinstance(eq.lhs, sp.Basic):
                try:
                    # Factoring possibilities
                    factored = sp.factor(sp.simplify(eq.lhs))
                    if factored != sp.simplify(eq.lhs):
                        candidates.append(make_candidate(record, sp.Eq(factored, eq.rhs, method='factoring_lhs', evaluate=False, correct=correct)))
                    # Expansion possibilities
                    expanded = sp.expand(sp.simplify(eq.lhs))
                    if expanded != eq.lhs:
                        candidates.append(make_candidate(record, sp.Eq(expanded, eq.rhs, method='expand_lhs', evaluate=False, correct=correct)))
                except Exception as e:
                    return [annotate_error("algebraic_candidates", e, str(candidates))]
    
    return candidates

def modulo_candidates(eq, eq_type, record, op_context, scratchpad, correct):
    """
    Create candidates involving modular arithmetic with respect to primes.
    Example: "If p is an odd prime, p mod 2 = 1"
    """
    candidates = []

    # if the equation involves a single variable and is about primes:
    if eq_type == 'equation' and isinstance(eq, sp.Equality):
        for sym in eq.free_symbols:
            # Basic known prime congruences:
            derived_eq = sp.Eq(sp.Mod(sym, 2), 1, evaluate=False)
            candidates.append(make_candidate(record, derived_eq=derived_eq, method='odd_prime_mod_2', note="if {} is odd prime, then {} mod 2 == 1 (odd)".format(sym, sym), correct=correct))
            # Fermat's little theorem: a^{p-1} congruent to 1 mod p for p prime, a not divisible by p
            if str(sym).startswith('p'):
                a = sp.Symbol('a')
                derived_eq = sp.Eq(sp.Mod(sp.Pow(a, sym - 1), sym), 1, evaluate=False)
                candidates.append(make_candidate(record, derived_eq=derived_eq, method='fermat_little_theorem',
                                                 note="For prime {}, a^({}-1) ≡ 1 mod {} for any a not divisible by {} (i.e., gcd(a, {}) = 1)".format(sym, sym, sym, sym, sym), correct=correct))

    return candidates

def advanced_candidates(eq, eq_type, record, op_context):
    """
    Generating more complex transformations, e.g. function substitutions,
    or mapping to high-level conjectures. Usually custom/experimental.
    """
    candidates = []
    return candidates

def unique_candidates(candidates):
    seen = set()
    out = []
    for cand in candidates:
        # If candidate has an error, always keep it
        if "error_stage" in cand:
            out.append(cand)
            continue
        # Robust key: handle sympy or string equations, fallback to string
        eq_key = cand.get('derived_eq')
        method = cand.get('generation_method', '')
        try:
            if isinstance(eq_key, sp.Equality):
                # Key is: method, frozenset of sides (so Eq(a,b) == Eq(b,a))
                key = (method, frozenset([sp.srepr(eq_key.lhs), sp.srepr(eq_key.rhs)]))
            elif isinstance(eq_key, sp.Basic):
                key = (method, sp.srepr(eq_key))
            else:
                key = (method, str(eq_key))
        except Exception:
            key = (method, str(eq_key))

        if key not in seen:
            seen.add(key)
            out.append(cand)
    return out

def filter_candidates(candidates):
    filtered = []
    for cand in candidates:
        eq = cand.get('derived_eq')
        # 1. Skip None or trivial
        if eq is None or is_trivial_equation(eq):
            continue
        # 2. Non-SymPy eqs: warn, but keep (optional)
        if not hasattr(eq, 'free_symbols'):
            print('WARNING: eq does not have free_symbols:', eq, type(eq))
            continue
        # 3. SymPy eqs with no symbols: skip
        if not eq.free_symbols:
            continue
        filtered.append(cand)
    return filtered

def generate_manual_candidates(scratchpad):
    """
    For each entry in scratchpad, generate commutative, rearranged, algebraic, modulo, or primality equations.
    Also generates graph candidates such as clique, star, bipartite, and motif subgraphs.
    Returns a list of candidate dicts (like step_dict, but 'generated').
    """
    # for each node/edge, try simple manipulations: swap, invert, substitute
    try:
        standard_candidates = []
        graph_candidates = []

        # record contains 'step', 'sentence', 'normalized (sentence)', 'parsed: op, lhs, rhs', '{sympy_eq: eq, type, {meta:op, correct}}, 'graph'
        for record in scratchpad.get_all():
            # only work with those with valid sympy equations
            eq_tuple = record['sympy_eq']['eq']
            eq, eq_type = safe_unwrap_eq_tuple(eq_tuple)
            op = record['parsed'].get('op')
            primality_constraint = record['sympy_eq']['meta'].get('primality_constraint')
            correct_val = str(record['sympy_eq']['meta'].get('correct', ''))
            is_correct = correct_val if correct_val else 'Concept'

            # ======== standard candidates ========
            # add raw sympy_eq as a candidate
            standard_candidates.append(make_candidate(record, eq_tuple[0] if isinstance(eq_tuple, tuple) else eq_tuple, 'direct_sympy', op, note=primality_constraint, correct=is_correct))
            # Commutative and Isolating candidates
            for candidate_eq in commutative_candidates(eq, eq_type, op, scratchpad) + isolating_candidates(eq, eq_type, op, scratchpad):
                candidate = {'source_step': record['step'], 'orig_sentence': record['sentence'], 'derived_eq': candidate_eq, 'generation_method': 'commutativity_or_rearrangement'}
                standard_candidates.append(make_candidate(record, candidate_eq, 'commutativity_or_rearrangement', op, correct=is_correct))
            # Algebraic candidates
            for candidate_eq in algebraic_candidates(eq, eq_type, record, op, scratchpad, correct=is_correct):
                standard_candidates.append(candidate_eq)
            # Modulo candidates
            for candidate_eq in modulo_candidates(eq, eq_type, record, op, scratchpad, correct=is_correct): # cannot access local variable 'sym' where its not associated with a value
                standard_candidates.append(candidate_eq)
            # Prime candidates
            if op and op in PRIME_PATTERN_HANDLERS:
                for candidate in prime_candidates(record, op, scratchpad):
                    note = candidate.get('note', None)
                    standard_candidates.append(make_candidate(record, candidate['derived_eq'], candidate['generation_method'], op, note, correct=is_correct))

            # ======== graph-based candidates ========
            graph = record.get('graph')
            if graph is not None:
                for candidate_eq in get_graph_candidates(graph, record, is_correct):
                    graph_candidates.append(candidate_eq)
                for candidate_eq in clique_candidates(graph, record, is_correct):
                    graph_candidates.append(candidate_eq)
                for candidate_eq in star_candidates(graph, record, is_correct):
                    graph_candidates.append(candidate_eq)
                for candidate_eq in bipartite_candidates(graph, record, is_correct):
                    graph_candidates.append(candidate_eq)
                for candidate_eq in motif_subgraph_candidates(graph, record, is_correct):
                    graph_candidates.append(candidate_eq)

        unique_standard = unique_candidates(standard_candidates)
        unique_graph = unique_candidates(graph_candidates)

        #filtered_standard = filter_candidates(unique_standard)
        #filtered_graph = filter_candidates(unique_graph)

        return unique_standard, unique_graph
    
    except Exception as e:
        return [annotate_error("candidate_generator", e, str(scratchpad))]
    
def generate_candidates(scratchpad, sp_rec, generator_type='manual'):
    """
    Chooses candidate generation backend:
    - 'manual': Calls rule-based generation.
    - 'auto': Calls LLM/neural backend.
    - 'both': Combines both (dedupes, merges provenance etc).
    """
    if generator_type == 'manual':
        return generate_manual_candidates(scratchpad)
    elif generator_type == 'auto':
        
        return generate_auto_candidates(sp_rec)
    elif generator_type == 'both':
        manual_cands, manual_graphs = generate_manual_candidates(scratchpad)
        auto_cands, auto_graphs = generate_auto_candidates(sp_rec)
        return manual_cands + auto_cands, manual_graphs + auto_graphs
    else:
        raise ValueError(f"Unknown generator type: {generator_type}")