# models/semantic_parser.py

import re
from utils.text_helpers import normalize_ordinal, convert_int
from utils.general_helpers import annotate_error
from loggers.log_utils import log_unknown
from utils.text_helpers import load_patterns

PATTERNS = load_patterns("config/math_grammar.yml")
def parse_math_sentence(sentence):
    """
    Extracts mathematical expressions from a sentence and returns them in a structured format.
    """
    try:
        matches = []
        for pat in PATTERNS:
            match = re.search(pat.pattern, sentence)
            if match:
                matches.append((match, pat.op))

        if not matches:
            log_unknown(sentence)
            return {'op': 'unknown', 'raw': sentence}

        # Get earliest match
        best_match, op = sorted(matches, key=lambda x: x[0].start())[0]
        g = best_match.groupdict()

        group = lambda k: g.get(k)

        # Map to structured result depending on pattern length
        if op in ['add', 'sub']:
            return {'op': op, 'lhs': [convert_int(group('blhs1')), convert_int(group('blhs2'))], 'rhs': [convert_int(group('brhs'))]}
        elif op == 'mul':
                return {'op': op, 'lhs': [convert_int(group('mlhs1')), convert_int(group('mlhs2'))], 'rhs': [convert_int(group('mrhs'))]}
        elif op == 'div':
            return {'op': op, 'lhs': [convert_int(group('dlhs1')), convert_int(group('dlhs2'))], 'rhs': [convert_int(group('drhs'))]}
        # ------------------- POWERS/ROOTS -------------------
        elif op in ['squared', 'cubed']:
            return {'op': op, 'base': [convert_int(group('base'))], 'rhs': [convert_int(group('rhs'))]}
        elif op == 'power':
            return {'op': op, 'base': [convert_int(group('base'))], 'exp': [convert_int(group('exp'))], 'rhs': [convert_int(group('rhs'))]}
        elif op in ['sqrt', 'cbrt']:
            return {'op': op, 'radicand': [convert_int(group('radicand'))], 'rhs': [convert_int(group('rhs'))]}
        elif op == 'root':
            return {'op': op, 'degree': [convert_int(group('degree'))], 'radicand': [convert_int(group('radicand'))], 'rhs': [convert_int(group('rhs'))]}
        # ------------------- DIVISIBILITY -------------------
        elif op in ['divisible', 'divides', 'factor']: return { 'op': op, 'lhs': [convert_int(group('a')), convert_int(group('b'))]}
        elif op == 'remainder':
            return { 'op': op, 'dividend': [convert_int(group('dividend'))], 'remainder': [convert_int(group('remainder'))], 'divisor': [convert_int(group('divisor'))]}
        # ------------------- PRIMES AND HIGHER STRUCTURE -------------------
        elif op == 'next_prime':
        # For "what number is the next prime after y", we want lhs = result variable!
            if 'lhs' in g and op in ['next_prime'] and 'which' in sentence or 'what' in sentence:
                # The question asks "what number...", assign a generic result variable
                return {'op': op, 'lhs': ['result'], 'rhs': [convert_int(group('lhs'))], 'order': ['next'] }
            else:
                # fallback: "x is the next prime after y"
                return {'op': op, 'lhs': [convert_int(group('lhs'))], 'rhs': [convert_int(group('rhs'))] if convert_int(group('rhs')) else [], 'order': ['next'] }

        elif op == 'prime_factors':
            return {'op': op, 'lhs': [convert_int(group('lhs1')), convert_int(group('lhs2')), convert_int(group('lhs3'))], 'rhs': [convert_int(group('rhs'))]}
        elif op == 'diff_of_primes':
            return {'op': 'diff_of_primes', 'lhs': [convert_int(group('lhs1')), convert_int(group('lhs2'))]}
        elif op == 'sum_of_two_primes':
            return {'op': op, 'lhs': ['prime1', 'prime2'], 'rhs': [convert_int(group('rhs'))] if convert_int(group('rhs')) else [], 'lhs_type': 'prime'}
        elif op == 'twin_primes':
            return {'op': op, 'lhs': [convert_int(group('lhs1')), convert_int(group('lhs2'))]}
        elif op == 'is_prime':
            return {'op': op, 'lhs': [convert_int(group('prime'))]}
        elif op == 'is_not_prime':
            return {'op': op, 'lhs': [convert_int(group('prime'))]}
        elif op == 'prime_order':
            order_val = convert_int(group('order'))
            order_val = normalize_ordinal(order_val) if order_val else None
            lhs_val = convert_int(group('lhs'))
            # If the sentence asks a question ("which"/"what") or explicitly does not specify lhs variable, assign generic.
            if ('which' in sentence or 'what' in sentence):
                return {'op': op, 'lhs': ['result'], 'order': [order_val]}
            else:
                return {'op': op, 'lhs': [lhs_val] if lhs_val else ['result'], 'order': [order_val]}
        elif op == 'where_is_prime':
            order_val = convert_int(group('order'))
            order_val = normalize_ordinal(order_val) if order_val else None
            return {'op': op, 'lhs': [order_val] if order_val else []}
        elif op == 'prime_gap':
            return {'op': op, 'lhs': [convert_int(group('lhs1')), convert_int(group('lhs2'))], 'rhs': [convert_int(group('rhs'))]}
        elif op == 'quadruplet_primes':
            return {'op': op, 'lhs': [convert_int(group('p1')), convert_int(group('p2')), convert_int(group('p3')), convert_int(group('p4'))], 'lhs_type': ['prime']}
        elif op == 'triplet_primes':
            return {'op': op, 'lhs': [convert_int(group('p1')), convert_int(group('p2')), convert_int(group('p3'))], 'lhs_type': ['prime']}
        # ----------- Custom / special prime exclusion patterns -----------
        elif op == 'prime_exclusion_zone':
            return {'op': op, 'lhs': [convert_int(group('n'))], 'rhs': [convert_int(group('v'))]}
        elif op == 'prime_exclusion_zone_range':
            return {'op': op, 'lhs': [convert_int(group('n'))], 'rhs': [convert_int(group('lo')), convert_int(group('hi'))]}
        elif op == 'prime_exclusion_vals':
            return {'op': op, 'lhs': [convert_int(group('n'))], 'rhs': [convert_int(group('val'))], 'order': [convert_int(group('order'))], 'local': [convert_int(group('local'))]}
        #elif op == 'reciprocal_distances_from_one':
            #return { 'op': op, 'lhs': [convert_int(group('n'))], 'rhs': [convert_int(group('d'))]}
        # ---------- Catch-all eq (simple variable assignment) -----------
        elif op == 'eq':
            return {'op': op, 'lhs': [convert_int(group('lhs'))], 'rhs': [convert_int(group('rhs'))]}
        else:
            log_unknown(sentence)
            return {'op': 'unknown', 'raw': sentence}
    
    except Exception as e:
        return annotate_error("semantic_parser", e, sentence)