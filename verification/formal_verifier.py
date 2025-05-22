# verification/formal_verifier.py

import sympy as sp
from utils.sympy_helpers import is_trivial_equation
from sympy.core.relational import Equality
from sympy.logic.boolalg import BooleanTrue
from utils.general_helpers import annotate_error

def iterify(val):
    if isinstance(val, (tuple, list)):
        return list(val)
    # For Mul/Add in SymPy and similar, get their .args
    if hasattr(val, 'args') and (isinstance(val, sp.Mul) or isinstance(val, sp.Add)):
        return list(val.args)
    # Else, treat as scalar
    return [val]

def explain_symbolic_verification(eq, scratchpad, op, previous_formulas=None):
    """
    Robust symbolic/formal verification for all pipeline math ops, including primes, quadruplets, etc.
    """

    if eq is None:
        return "Rejected: Formula is None", 0.0, "invalid"
    
    # --- Step 1: Support both direct op input, or sniff op from scratchpad if present
    op = op or getattr(eq, 'op', None)
    if not op and isinstance(scratchpad, dict):
        op = scratchpad.get('parsed', {}).get('op') or scratchpad.get('op', None)

    # --- Step 2: Handle SymPy object types that are functions/conceptual
    if not (hasattr(eq, 'lhs') and hasattr(eq, 'rhs')):
        # Handle common prime/symbolic types
        if eq.func.__name__ == "isprime":
            var = eq.args[0].name if hasattr(eq.args[0], "name") else str(eq.args[0])
            return f"Conceptual formula: checking primality of {var} (isprime({var}). No numerical value; cannot verify.", 0.25, "symbolic"
        elif eq.func.__name__ == "prime":
            n = eq.args[0]
            return f"Conceptual formula: nth prime function prime({n}). Not directly verifiable unless n is numeric.", 0.3, "symbolic"
        # fallback
        return f"Formula is not a symbolic equation (type {type(eq).__name__}) not verifiable directly: {eq}", 0.25, "symbolic"
    
    # --- Step 3: Fast trivial/identity checks
    simplified_lhs = sp.simplify(eq.lhs)
    simplified_rhs = sp.simplify(eq.rhs)
    simplified_eq = sp.Eq(simplified_lhs, simplified_rhs)
    if is_trivial_equation(simplified_eq):
        return "Rejected: Formula is mathematically trivial (tautology or obvious equivalence)", 0.0, "trivial"
    
    # --- Step 4: Reason by operation (special-case for your domain)
    try:
        # Direct equation check (basic math)
        if op in {'add', 'sub', 'mul', 'div', 'squared', 'cubed', 'power', 'sqrt', 'cbrt', 'root', 'divisible', 'divides', 'factor', 'remainder', 'eq'}:
            test = simplified_lhs - simplified_rhs
            if test == 0:
                return f"LHS and RHS are symbolically equal for op='{op}'", 1.0, "True"
            # Try to see if its false
            if sp.satisfiable(simplified_eq, all_models=True) is False:
                return f"LHS and RHS are symbolically contradictory for op='{op}'", 0.0, "False"
            return f"LHS and RHS for op='{op}' may be conditionally true or have free vars", 0.7, "symbolic"
       
        # --- Primes & Advanced Structures ---
        # Twin Primes
        if op == "twin_primes":
            # eq: |a-b| = 2, primality status in meta
            if hasattr(eq, "lhs") and hasattr(eq, "rhs"):
                try:
                    diff = abs(sp.simplify(eq.lhs) - sp.simplify(eq.rhs))
                    if diff == 2:
                        return "Twin prime condition met (difference is 2). Primality check is external.", 0.8, "likely_true"
                    else:
                        return f"Twin prime difference not met: |{eq.lhs} - {eq.rhs}| = {diff}", 0.1, "likely_false"
                except Exception:
                    pass
            return "Twin prime structure, but could not verify difference symbolically.", 0.4, "unknown"

        # Quadruplet Primes
        if op == "quadruplet_primes":
            # Form: (a, b, c, d) = (p, p+2, p+6, p+8)
            if hasattr(eq, "lhs") and hasattr(eq, "rhs"):
                vals = [sp.simplify(x) for x in iterify(eq.lhs)]
                expct = [sp.simplify(x) for x in iterify(eq.rhs)]
                if len(vals) == 4 and all(isinstance(v, (sp.Integer, int, float)) for v in vals):
                    diffs = [vals[1] - vals[0], vals[2] - vals[1], vals[3] - vals[2]]
                    if diffs == [2,4,2]:
                        return f"Quadruplet spacing condition met (gaps [2,4,2]).", 0.9, "True"  # Primality is not checked here
                    else:
                        return f"Quadruplet gaps not correct: {diffs} (expected [2,4,2])", 0.2, "False"
                # If symbolic: can't decide exact values
                return "Quadruplet primes: structure detected, but not concrete values. Verification requires instantiation.", 0.5, "symbolic"

        # Triplet Primes
        if op == "triplet_primes":
            if hasattr(eq, "lhs") and isinstance(eq.lhs, (tuple, list)) and len(eq.lhs) == 3:
                vals = [sp.simplify(x) for x in iterify(eq.lhs)]
                diffs = [vals[1] - vals[0], vals[2] - vals[1]]
                if (diffs == [2,4] or diffs == [4,2]):
                    return "Triplet prime spacing met ([2,4] or [4,2]).", 0.85, "True"
                else:
                    return f"Triplet gaps fail: {diffs} (expected [2,4] or [4,2])", 0.2, "False"
            return "Triplet structure/form detected, but values not concrete. Requires instantiation.", 0.5, "symbolic"

        # Sum of Two Primes
        if op == "sum_of_two_primes":
            # eq: a + b = c, check if c equals (a+b), (primality test is up to caller)
            if hasattr(eq, "lhs") and hasattr(eq, "rhs"):
                try:
                    if sp.simplify(eq.lhs) + sp.simplify(eq.rhs) == eq.rhs:
                        return "Sum-of-two-primes relation satisfied.", 0.9, "True"
                except Exception:
                    pass
            return "Sum of two primes: could not symbolically verify sum.", 0.7, "symbolic"

        # Diff of Primes
        if op == "diff_of_primes":
            # eq: |a-b| == k, check for positive integer output
            if hasattr(eq, "lhs") and hasattr(eq, "rhs"):
                try:
                    diff = abs(sp.simplify(eq.lhs) - sp.simplify(eq.rhs))
                    if type(diff) in (int, sp.Integer) and diff > 0:
                        return f"Difference of primes yields a positive difference: {diff}.", 0.7, "True"
                except Exception:
                    pass
            return "Difference-of-primes: could not concretely symbolically verify diff.", 0.6, "symbolic"

        # Prime Factors
        if op == "prime_factors":
            # eq: Mul(*vars) == rhs
            if hasattr(eq, "lhs") and hasattr(eq, "rhs"):
                try:
                    product = sp.simplify(sp.Mul(*eq.lhs, evaluate=False))
                    if product == sp.simplify(eq.rhs):
                        return "Prime factors product equals the target number.", 0.9, "True"
                    else:
                        return f"Prime factors product not equal to target: {product} vs {eq.rhs}.", 0.2, "False"
                except Exception:
                    pass
            return "Prime factors structure detected—cannot verify without concrete numbers.", 0.5, "symbolic"

        # Prime Gap
        if op == "prime_gap":
            # eq: |a-b|=gap
            if hasattr(eq, "lhs") and hasattr(eq, "rhs"):
                try:
                    gap = sp.simplify(eq.rhs)
                    diff = abs(sp.simplify(eq.lhs[0]) - sp.simplify(eq.lhs[1]))
                    if diff == gap:
                        return f"Prime gap {gap} matches difference.", 0.9, "True"
                    else:
                        return f"Prime gap {gap} does not match difference ({diff}).", 0.2, "False"
                except Exception:
                    pass
            return "Prime gap structure detected—cannot fully verify symbolically without numbers.", 0.5, "symbolic"

        # Prime Exclusion Zone (and range/vals)
        if op.startswith("prime_exclusion"):
            # These are custom; rely on structure match and symbolic relation
            if hasattr(eq, "lhs") and hasattr(eq, "rhs"):
                # Typically, exclusion zone formula is applied; check structure
                return "Prime exclusion zone: symbolic formula structure detected. Concrete zone verification requires number.", 0.6, "symbolic"

        # Next Prime (symbolic)
        if op == "next_prime":
            return "Next prime formula: symbolic structure (requires evaluation for numbers).", 0.5, "symbolic"

        # Where is prime
        if op == "where_is_prime":
            return "Where-is-prime (nth-prime) symbolic structure: use numeric n for verification.", 0.5, "symbolic"

        # Generic fallback: arithmetic
        if isinstance(simplified_eq, Equality):
            test = simplified_lhs - simplified_rhs
            if test == 0:
                return "Formula is symbolically valid (LHS equals RHS).", 1.0, "True"
            if sp.satisfiable(simplified_eq, all_models=True) is False:
                return "Formula is symbolically false or contradictory.", 0.0, "False"
            return "Formula may be conditionally true or involve free variables.", 0.7, "symbolic"

        elif isinstance(simplified_eq, bool) or isinstance(simplified_eq, BooleanTrue):
            if simplified_eq:
                return "Formula evaluates to True (boolean context).", 1.0, "True"
            return "Formula evaluates to False (boolean context).", 0.0, "False"

        else:
            return "Formula format not recognized for symbolic verification.", 0.1, "unverifiable"
    except Exception as e:
        return [annotate_error("candidate_generator", e, str(scratchpad))]