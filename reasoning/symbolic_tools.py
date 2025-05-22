# reasoning/symbolic_tools.py

import sympy as sp
from utils.sympy_helpers import get_field_obj
from utils.general_helpers import prime_flag_is_true, prime_flag_is_false, annotate_error, all_ints_or_float

def build_sympy_equation(parse_dict):
    """
    Converts parsed math/logic representation to a SymPy equation or concept.
    
    Returns:
        dict containing:
            - 'eq': sympy object, or bool, or None
            - 'type': type of relation ('equation', 'concept', 'boolean', ...)
            - 'meta': dict with additional info (operation, operands, details, etc.)
    """
    try:
            
        # Short alias for safer access
        g = lambda k: get_field_obj(k, parse_dict)
        result = {'eq': None, 'type': None, 'meta': {}}
        op = parse_dict.get('op')
        result['meta'] = {'op': op}
        lhs_obj = g('lhs')
        rhs_obj = g('rhs')
        base_obj = g('base')
        exp_obj = g('exp')
        radicand_obj = g('radicand')
        dividend_obj = g('dividend')
        divisor_obj = g('divisor')
        remainder_obj = g('remainder')
        degree_obj = g('degree')
        order_obj = g('order')
        local_obj = g('local')

        if op == 'add':
            expr = sp.Add(lhs_obj[0], lhs_obj[1], evaluate=False)
            eq = sp.Eq(expr, rhs_obj[0], evaluate=False)
            result.update({'eq': eq, 'type': 'equation'})
            if all_ints_or_float(lhs_obj[0], lhs_obj[1], rhs_obj[0]):
                correct = (lhs_obj[0] + lhs_obj[1] == rhs_obj[0])
                result['meta']['correct'] = correct

        elif op == 'mul':
            expr = sp.Mul(lhs_obj[0], lhs_obj[1], evaluate=False)
            eq = sp.Eq(expr, rhs_obj[0], evaluate=False)
            result.update({'eq': eq, 'type': 'equation'})
            if all_ints_or_float(lhs_obj[0], lhs_obj[1], rhs_obj[0]):
                correct = (lhs_obj[0] * lhs_obj[1] == rhs_obj[0])
                result['meta']['correct'] = correct

        elif op == 'sub':
            expr = sp.Add(lhs_obj[0], sp.Mul(-1, lhs_obj[1], evaluate=False), evaluate=False)
            eq = sp.Eq(expr, rhs_obj[0], evaluate=False)
            result.update({'eq': eq, 'type': 'equation'})
            if all_ints_or_float(lhs_obj[0], lhs_obj[1], rhs_obj[0]):
                correct = (lhs_obj[0] - lhs_obj[1] == rhs_obj[0])
                result['meta']['correct'] = correct

        elif op == 'div':
            expr = sp.Mul(lhs_obj[0], sp.Pow(lhs_obj[1], -1, evaluate=False), evaluate=False)
            eq = sp.Eq(expr, rhs_obj[0], evaluate=False)
            result.update({'eq': eq, 'type': 'equation'})
            if all_ints_or_float(lhs_obj[0], lhs_obj[1], rhs_obj[0]):
                correct = (lhs_obj[1] != 0 and lhs_obj[0] / lhs_obj[1] == rhs_obj[0])
                result['meta']['correct'] = correct

        elif op == 'squared':
            expr = sp.Pow(base_obj[0], 2, evaluate=False)
            eq = sp.Eq(expr, rhs_obj[0], evaluate=False)
            result.update({'eq': eq, 'type': 'equation'})
            if all_ints_or_float(base_obj[0], rhs_obj[0]):
                correct = (base_obj[0] ** 2 == rhs_obj[0])
                result['meta']['correct'] = correct

        elif op == 'cubed':
            expr = sp.Pow(base_obj[0], 3, evaluate=False)
            eq = sp.Eq(expr, rhs_obj[0], evaluate=False)
            result.update({'eq': eq, 'type': 'equation'})
            if all_ints_or_float(base_obj[0], rhs_obj[0]):
                correct = (base_obj[0] ** 3 == rhs_obj[0])
                result['meta']['correct'] = correct

        elif op == 'power':
            expr = sp.Pow(base_obj[0], exp_obj[0], evaluate=False)
            eq = sp.Eq(expr, rhs_obj[0], evaluate=False)
            result.update({'eq': eq, 'type': 'equation'})
            if all_ints_or_float(base_obj[0], exp_obj[0], rhs_obj[0]):
                correct = (base_obj[0] ** exp_obj[0] == rhs_obj[0])
                result['meta']['correct'] = correct

        elif op == 'sqrt':
            expr = sp.Pow(radicand_obj[0], sp.Rational(1, 2), evaluate=False)
            eq = sp.Eq(expr, rhs_obj[0], evaluate=False)
            result.update({'eq': eq, 'type': 'equation'})
            if all_ints_or_float(radicand_obj[0], rhs_obj[0]):
                correct = rhs_obj[0] == sp.sqrt(radicand_obj[0]) or rhs_obj[0] == -sp.sqrt(radicand_obj[0])
                result['meta']['correct'] = correct

        elif op == 'cbrt':
            expr = sp.Pow(radicand_obj[0], sp.Rational(1, 3), evaluate=False)
            eq = sp.Eq(expr, rhs_obj[0], evaluate=False)
            result.update({'eq': eq, 'type': 'equation'})
            if all_ints_or_float(radicand_obj[0], rhs_obj[0]):
                correct = (rhs_obj[0] == sp.cbrt(radicand_obj[0]))
                result['meta']['correct'] = correct

        elif op == 'divisible':
            expr = sp.Mod(lhs_obj[0], lhs_obj[1], evaluate=False)
            eq = sp.Eq(expr, 0, evaluate=False)
            result.update({'eq': eq, 'type': 'equation'})
            if all_ints_or_float(lhs_obj[0], lhs_obj[1]):
                correct = (lhs_obj[1] != 0 and lhs_obj[0] % lhs_obj[1] == 0)
                result['meta']['correct'] = correct

        elif op in ['divides', 'factor']:
            expr = sp.Mod(lhs_obj[1], lhs_obj[0], evaluate=False)
            eq = sp.Eq(expr, 0, evaluate=False)
            result.update({'eq': eq, 'type': 'equation'})
            if all_ints_or_float(lhs_obj[0], lhs_obj[1]):
                correct = (lhs_obj[0] != 0 and lhs_obj[1] % lhs_obj[0] == 0)
                result['meta']['correct'] = correct

        elif op == 'remainder':
            expr = sp.Mod(dividend_obj[0], divisor_obj[0], evaluate=False)
            eq = sp.Eq(expr, remainder_obj[0], evaluate=False)
            result.update({'eq': eq, 'type': 'equation'})
            if all_ints_or_float(dividend_obj[0], divisor_obj[0], remainder_obj[0]):
                correct = (divisor_obj[0] != 0 and dividend_obj[0] % divisor_obj[0] == remainder_obj[0])
                result['meta']['correct'] = correct

        elif op == 'root':
            expr = sp.Pow(radicand_obj[0], sp.Rational(1, degree_obj[0]), evaluate=False)
            eq = sp.Eq(rhs_obj[0], expr, evaluate=False)
            result.update({'eq': eq, 'type': 'equation'})
            if all_ints_or_float(rhs_obj[0], radicand_obj[0], degree_obj[0]):
                correct = (rhs_obj[0] ** degree_obj[0] == radicand_obj[0])
                result['meta']['correct'] = correct


        elif op == 'eq':
            eq = sp.Eq(lhs_obj[0], rhs_obj[0], evaluate=False)
            result.update({'eq': eq, 'type': 'equation'})
            if all_ints_or_float(lhs_obj[0], rhs_obj[0]):
                correct = (lhs_obj[0] == rhs_obj[0])
                result['meta']['correct'] = correct

        elif op == 'is_prime':
            expr = sp.Function("isprime")(lhs_obj[0])  # symbolic function
            # Symbolic function for display/formal reasoner
            eq = sp.Eq(expr, True, evaluate=False)
            # The boolean value for this input:
            is_prime = prime_flag_is_true(lhs_obj[0])
            result.update({'eq': eq, 'type': 'boolean'})
            result['meta'].update({'lhs': lhs_obj[0], 'primality_constraint': f'isprime({lhs_obj[0]})', 'correct': is_prime, 'op': 'is_prime'})
            if all_ints_or_float(lhs_obj[0]):
                result['meta']['correct'] = is_prime

        elif op == 'is_not_prime':
            expr = sp.Function("isprime")(lhs_obj[0])
            # Symbolic function for display/formal reasoner
            eq = sp.Eq(expr, False, evaluate=False)
            # The boolean value for this input:
            is_not_prime = prime_flag_is_false(lhs_obj[0])
            result.update({'eq': eq, 'type': 'boolean'})
            result['meta'].update({'lhs': lhs_obj[0], 'primality_constraint': f'isprime({lhs_obj[0]})', 'correct': is_not_prime, 'op': 'is_not_prime'})
            if all_ints_or_float(lhs_obj[0]):
                result['meta']['correct'] = is_not_prime

        elif op == 'prime_order':
            # Numeric order
            if lhs_obj[0] and all_ints_or_float(lhs_obj[0], order_obj[0]):
                prime_val = sp.prime(int(order_obj[0]))
                primes_constraint = f'isprime({int(lhs[0])})'
                eq = sp.Eq(lhs_obj[0], prime_val, evaluate=False)
                result.update({'eq': eq, 'type': 'equation'})
                result['meta'].update({'lhs': lhs_obj[0], 'order': order_obj[0]})
                correct = (lhs_obj[0] == prime_val)
                result['meta']['correct'] = correct
                result['meta']['primality_constraint'] = primes_constraint
            if not lhs_obj[0] and all_ints_or_float(order_obj[0]):
                prime_val = sp.prime(int(order_obj[0]))
                eq = sp.Eq(sp.Function("prime")(order_obj[0]), prime_val, evaluate=False)  # prime(n) = 11
                result.update({'eq': eq, 'type': 'equation'})
                result['meta'].update({'order': order_obj[0]})
            # Symbolic order (e.g., variable n)
            else:
                eq = sp.Function("prime")(order_obj[0])
                result.update({'eq': eq, 'type': 'concept'})
                result['meta'].update({'order': order_obj[0]})
            return result
        
        elif op == 'diff_of_primes':
            diff_expr = sp.Abs(lhs_obj[0] - lhs_obj[1], evaluate=False)
            diff_value = abs(lhs_obj[0] - lhs_obj[1])
            # symbolic equation
            eq = sp.Eq(diff_expr, diff_value, evaluate=False)
            # Symbolic primality requirement
            primality_constraint = f"isprime({diff_value})"
            # Check if the result is actually a prime
            is_prime = prime_flag_is_true(diff_value)
            result.update({'eq': eq, 'type': 'equation'})
            result['meta'].update({ 'lhs': [lhs_obj[0], lhs_obj[1]], 'diff': diff_value, 'rhs':[diff_expr], 'primality_constraint': primality_constraint, 'is_diff_prime': is_prime})
            if all_ints_or_float(lhs_obj[0], lhs_obj[1], diff_value):
                result['meta']['correct'] = is_prime

        elif op == 'sum_of_two_primes':
            expr = sp.Add(lhs_obj[0], lhs_obj[1], evaluate=False)
            eq = sp.Eq(expr, rhs_obj[0], evaluate=False)
            result.update({'eq': eq, 'type': 'equation'})
             # Concrete check (if all are ints)
            all_prime = all(prime_flag_is_true(p) for p in lhs_obj)
            primes_constraint = [f'isprime({p})' for p in lhs_obj]
            result['meta']['all_prime'] = all_prime
            result['meta']['primality_constraint'] = primes_constraint
            if all_ints_or_float(lhs_obj[0], lhs_obj[1], rhs_obj[0]):
                correct_product = (lhs_obj[0] + lhs_obj[1]) == rhs_obj[0]
                result['meta']['correct_product'] = correct_product
                result['meta']['correct'] = all_prime and correct_product

        elif op == 'twin_primes':
            diff_expr = sp.Abs(lhs_obj[0] - lhs_obj[1], evaluate=False)
            eq = sp.Eq(diff_expr, 2, evaluate=False)
            result.update({'eq': eq, 'type': 'equation'})
            # Primality constraints as strings
            primes_constraint = [f'isprime({p})' for p in lhs_obj]
            result['meta']['primality_constraint'] = primes_constraint
             # Concrete check (if all are ints)
            all_prime = all(prime_flag_is_true(p) for p in lhs_obj)
            result['meta']['all_prime'] = all_prime
            if all_ints_or_float(lhs_obj[0], lhs_obj[1]):
                correct_product = sp.Abs(lhs_obj[0] - lhs_obj[1]) == 2
                result['meta']['correct_product'] = correct_product
                result['meta']['correct'] = all_prime and correct_product

        elif op == 'prime_factors':
            # The symbolic equation for display: product of all lhs = rhs
            expr = sp.Mul(*lhs_obj, evaluate=False)
            eq = sp.Eq(expr, rhs_obj[0], evaluate=False)
            result.update({'eq': eq, 'type': 'equation'})
            # Primality constraints as strings
            primes_constraint = [f'isprime({p})' for p in lhs_obj]
            result['meta']['primality_constraint'] = primes_constraint
            # Concrete check (if all are ints)
            all_prime = all(prime_flag_is_true(p) for p in lhs_obj)
            result['meta']['all_prime'] = all_prime

            if all_ints_or_float(*lhs_obj, rhs_obj[0]):
                correct_product = sp.Mul(*lhs_obj) == rhs_obj[0]
                result['meta']['correct_product'] = correct_product
                result['meta']['correct'] = all_prime and correct_product

        elif op == 'next_prime':
            lhs = lhs_obj[0]
            rhs = rhs_obj[0] if isinstance(rhs_obj, list) else rhs_obj

            # If both are numbers (not variables)
            if all_ints_or_float(lhs_obj[0], rhs):
                is_nextprime = (sp.nextprime(rhs) == lhs)
                primes_constraint = f'isprime({sp.nextprime(rhs)})'
                eq = sp.Eq(lhs, sp.nextprime(rhs), evaluate=False)
                
                result.update({'eq': eq, 'type': 'equation'})
                result['meta'].update({ 'lhs': lhs, 'rhs': rhs, 'is_nextprime': is_nextprime})
                result['meta']['primality_constraint'] = primes_constraint
                result['meta']['correct'] = is_nextprime
            # If one or both are variables / symbolic
            else:
                # Return a symbolic Eq expression: lhs = nextprime(rhs)
                eq = sp.Eq(lhs, sp.Function('nextprime')(rhs), evaluate=False)
                result.update({'eq': eq, 'type': 'equation'})
                result['meta'].update({ 'lhs': lhs, 'rhs': rhs, 'is_nextprime': 'symbolic'})

        elif op == 'where_is_prime':
            # lhs_obj[0] should always be the n "th"
            n = lhs_obj[0]
            # If n is a number, give the nth prime (numeric result)
            if all_ints_or_float(n):
                nth_prime = sp.prime(int(n))
                eq = sp.Eq(sp.Function("prime")(n), nth_prime, evaluate=False)
                primes_constraint = f'isprime({nth_prime})'
                # sp.prime returns the nth prime (e.g., sp.prime(1) == 2)
                result.update({'eq': eq, 'type': 'equation'})
                result['meta']['primality_constraint'] = primes_constraint
            # If n is a symbol (symbolic variable), just return the symbolic function (prime(n))
            else:
                eq = sp.Function("prime")(n)
                result.update({'eq': eq, 'type': 'symbolic'})
        
        elif op == 'prime_gap':
            gap = rhs_obj[0] if isinstance(rhs_obj, (list, tuple)) else rhs_obj
            # Always use the absolute gap
            abs_expr = sp.Abs(lhs_obj[0] - lhs_obj[1], evaluate=False)
            eq = sp.Eq(abs_expr, gap, evaluate=False)
            # Symbolic constraints:
            primality_constraints = f'isprime({lhs_obj[0]})', f'isprime({lhs_obj[1]})'
            # Evaluate primality
            is_a_prime = prime_flag_is_true(lhs_obj[0])
            is_b_prime = prime_flag_is_true(lhs_obj[1])
            # Both must be prime and gap correct
            all_prime = is_a_prime and is_b_prime if (is_a_prime is not None and is_b_prime is not None) else None
            result.update({'eq': eq, 'type': 'equation'})
            result['meta'].update({ 'op': op, 'lhs': [lhs_obj[0], lhs_obj[1]], 'gap': gap, 'primality_constraints': primality_constraints, 'is_a_prime': is_a_prime, 
                                   'is_b_prime': is_b_prime, 'all_prime': all_prime})
            # Evaluate gap
            if all_ints_or_float(lhs_obj[0], lhs_obj[1], gap):
                correct_gap = (abs(lhs_obj[1] - lhs_obj[0]) == gap)
                correct = all_prime and correct_gap if (all_prime is not None and correct_gap is not None) else None
                result['meta']['correct_gap'] = correct_gap
                result['meta']['correct'] = correct
            
        
        elif op == 'quadruplet_primes':
        # If all are integers, do full numeric analysis
            if all_ints_or_float(*lhs_obj):
                vals = [int(x) for x in lhs_obj]
                is_prime = all(prime_flag_is_true(x) for x in vals)
                primes_constraint = [f'isprime({p})' for p in vals]
                is_consecutive = all(vals[i] == sp.nextprime(vals[i-1]) for i in range(1, 4))
                expected = [vals[0], vals[0]+2, vals[0]+6, vals[0]+8]
                eq = sp.Eq(tuple(vals), tuple(expected), evaluate=False)
                is_expected = vals == expected
                result['eq'] = eq
                result['meta'].update({'lhs': vals, 'all_prime': is_prime, 'is_consecutive': is_consecutive, 'correct_spacing': is_expected})
                result['meta']['primality_constraint'] = primes_constraint
                result['type'] = 'concrete'
                correct = is_prime and is_consecutive and expected
                result['meta']['correct'] = correct
            # If symbolic, just output the primality conditions symbolically
            else:
                p = sp.symbols('p')
                quadruplet = (p, p+2, p+6, p+8)
                eq = sp.Eq(tuple(lhs_obj), quadruplet, evaluate=False)
                constraints = " and ".join([f"isprime({v})" for v in lhs_obj])
                result['eq'] = eq
                result['meta'].update({ 'lhs': lhs_obj, 'symbolic': True, 'primality_constraint': constraints})
                result['type'] = 'concept'

        elif op == 'triplet_primes':
            # If all numeric
            if all_ints_or_float(*lhs_obj):
                vals = [int(x) for x in lhs_obj]
                is_prime = all(prime_flag_is_true(x) for x in vals)
                primes_constraint = [f'isprime({p})' for p in vals]
                is_consecutive = all(vals[i] == sp.nextprime(vals[i - 1]) for i in range(1, 3))
                spacing_valid = all((vals[i] - vals[i - 1]) <= 6 for i in range(1, 3))
                # Tuple equality
                eq_tuple = sp.Eq(tuple(vals), tuple(vals), evaluate=False)
                # Spacing constraints
                gap1 = vals[1] - vals[0]
                gap2 = vals[2] - vals[1]
                eq_gaps = sp.And(gap1 <= 6, gap2 <= 6)
                # Combined equation with AND
                eq = sp.And(eq_tuple, eq_gaps)

                result['eq'] = eq
                result['meta'].update({'lhs': vals, 'all_prime': is_prime, 'is_consecutive': is_consecutive, 'correct_spacing': spacing_valid, 'gap1': gap1, 'gap2': gap2})
                result['meta']['primality_constraint'] = primes_constraint
                result['type'] = 'concrete'
                correct = is_prime and is_consecutive and spacing_valid
                result['meta']['correct'] = correct
            # If variables/symbolic
            else:
                # Symbolic variables: use p, q, r
                p, q, r = lhs_obj
                eq_tuple = sp.Eq((p, q, r), (p, q, r), evaluate=False)  # Just show the triplet
                spacing = sp.And((q - p) <= 6, (r - q) <= 6)
                # Primality constraints
                constraints = [sp.Eq(sp.Function('isprime')(p), True, evaluate=False), sp.Eq(sp.Function('isprime')(q), True, evaluate=False), sp.Eq(sp.Function('isprime')(r), True, evaluate=False)]
                eq = sp.And(eq_tuple, spacing, *constraints)
                result['eq'] = eq
                result['meta'].update({'lhs': lhs_obj, 'symbolic': True, 'primality_constraint': " and ".join([f"isprime({v})" for v in lhs_obj]), 'gap1': f"{q} - {p}", 'gap2': f"{r} - {q}"})
                result['type'] = 'concept'
        
        elif op == 'prime_exclusion_zone':
            # If lhs is 2, the "zone" is always 0
            # but still wrap in Eq for symbolic consistency:
            if lhs_obj[0] == 2:
                eq = sp.Eq(0, rhs_obj[0], evaluate=False)
                # Prime check for '2'
                is_prime = prime_flag_is_true(lhs_obj[0])
                primes_constraint = f'isprime({lhs_obj[0]})'
                result.update({'eq': eq, 'type': 'equation', 'meta': {'op': op, 'lhs': lhs_obj[0], 'rhs': rhs_obj[0], 'is_prime': is_prime}})
                if all_ints_or_float(rhs_obj[0]):
                    correct = rhs_obj[0] == 0
                    result['meta']['correct'] = correct
            else:
                # Compute the exclusion zone
                pez = 2 * (lhs_obj[0] - 1) - lhs_obj[0]
                eq = sp.Eq(pez, rhs_obj[0], evaluate=False)
                is_prime = prime_flag_is_true(lhs_obj[0])
                primes_constraint = f'isprime({lhs_obj[0]})'
                result.update({'eq': eq, 'type': 'equation', 'meta': {'op': op, 'lhs': lhs_obj[0], 'rhs': rhs_obj[0], 'is_prime': is_prime}})
                if all_ints_or_float(lhs_obj[0], rhs_obj[0]):
                    correct = (pez == rhs_obj[0])
                    result['meta']['correct'] = correct
            result['meta']['primality_constraint'] = primes_constraint
        
        elif op == 'prime_exclusion_zone_range':
            primes_constraint = None
            if lhs_obj[0] == 2:
                # For 2, range is always [0, 0]
                eq_min = sp.Eq(0, rhs_obj[0], evaluate=False)
                eq_max = sp.Eq(0, rhs_obj[1], evaluate=False)
                eq = sp.And(eq_min, eq_max)
                is_prime = prime_flag_is_true(lhs_obj[0])
                primes_constraint = f'isprime({lhs_obj[0]})'
                result.update({'eq': eq, 'type': 'equation', 'meta': {'op': op, 'lhs': lhs_obj[0], 'rhs': rhs_obj, 'is_prime': is_prime}})
                if all_ints_or_float(rhs_obj[0], rhs_obj[1]):
                    correct = (rhs_obj[0] == 0) and (rhs_obj[1] == 0)
                    result['meta']['correct'] = correct
            else:
                pez = 2 * (lhs_obj[0] - 1) - lhs_obj[0]
                pez_range_min = lhs_obj[0] - pez
                pez_range_max = lhs_obj[0] + pez
                eq_min = sp.Eq(pez_range_min, rhs_obj[0], evaluate=False)
                eq_max = sp.Eq(pez_range_max, rhs_obj[1], evaluate=False)
                eq = sp.And(eq_min, eq_max)
                is_prime = prime_flag_is_true(lhs_obj[0])
                result.update({'eq': eq, 'type': 'equation', 'meta': {'op': op, 'lhs': lhs_obj[0], 'rhs': rhs_obj, 'is_prime': is_prime, 'pez_min': pez_range_min, 'pez_max': pez_range_max}})
                if all_ints_or_float(rhs_obj[0], rhs_obj[1]):
                    correct = (pez_range_min == rhs_obj[0]) and (pez_range_max == rhs_obj[1])
                    result['meta']['correct'] = correct
            if primes_constraint is not None:
                result['meta']['primality_constraint'] = primes_constraint
            
        elif op == 'prime_exclusion_vals':
            is_prime = prime_flag_is_true(lhs_obj[0])
            primes_constraint = f'isprime({lhs_obj[0]})'
            pez = 2 * (lhs_obj[0] - 1) - lhs_obj[0]
            pez_str = f"(2 * ({lhs_obj[0]} - 1) - {lhs_obj[0]})"

            eq = None
            info = None
            correct = None
            order = order_obj[0].name
            local = local_obj[0].name
            val = None

            if (lhs_obj[0] == 2):
                # Always 0 for 2
                eq = sp.Eq(0, rhs_obj[0], evaluate=False)
                info = 0
                if all_ints_or_float(rhs_obj[0]):
                    correct = (rhs_obj[0] == 0)

            else:
                if order in ('furthest', 'largest', 'biggest', 'highest', 'second', 'last', 'final'):
                    if local == 'overshoot':
                        val = lhs_obj[0] + pez
                        val_str = f"{lhs_obj[0]} + {pez_str}"
                    elif local == 'undershoot':
                        val = lhs_obj[0] - pez
                        val_str = f"{lhs_obj[0]} - {pez_str}"

                elif order in ('closest', 'smallest', 'nearest', 'lowest', 'first', 'beginning'):
                    if local == 'overshoot':
                        val = lhs_obj[0] + 1
                        val_str = f"{lhs_obj[0]} + 1"
                    elif local == 'undershoot':
                        val = lhs_obj[0] - 1
                        val_str = f"{lhs_obj[0]} - 1"

                if val is not None:
                    eq = sp.Eq(val, rhs_obj[0], evaluate=False)
                    info = val
                    if all_ints_or_float(lhs_obj[0], rhs_obj[0]):
                        correct = (val == rhs_obj[0])   

            result.update({'eq': eq, 'type': 'equation', 'meta': {'op': op, 'lhs': lhs_obj[0], 'rhs': rhs_obj[0], 'is_prime': is_prime}})
            result['meta']['primality_constraint'] = primes_constraint

            if correct is not None:
                result['meta']['correct'] = correct
            if val_str:
                result['meta']['pez_val_formula'] = val_str 
            if info is not None:
                result['meta']['pez_val'] = info
            

        if isinstance(result['eq'], bool):
            result['type'] = 'boolean'
        return result

    except Exception as e:
        # Return error in the same dict format
        return {'eq': None, 'type': 'error', 'meta': {'error': annotate_error("build_sympy_equation", e, parse_dict), 'input': parse_dict}}
    
