# utils/reasoning_helpers.py

from utils import reasoning_arithmetic

# ======== equals ========
def reason_equals(graph, get_node_by_role):
    x = get_node_by_role('variable1')
    result = get_node_by_role('result')
    template = reasoning_arithmetic.equals_templates(x, result)
    return [{"pattern": "assignment", **template}]

# ======== addition ========
def reason_addition(graph, get_node_by_role):
    x = get_node_by_role('variable1')
    y = get_node_by_role('variable2')
    result = get_node_by_role('result')
    template = reasoning_arithmetic.addition_templates(x, y, result)
    return [{"pattern": "addition", **template}]

# ======== multiplication ========
def reason_multiplication(graph, get_node_by_role):
    x = get_node_by_role('variable1')
    y = get_node_by_role('variable2')
    result = get_node_by_role('result')
    template = reasoning_arithmetic.multiplication_templates(x, y, result)
    return [{"pattern": "multiplication", **template}]

# ======== subtraction ========
def reason_subtraction(graph, get_node_by_role):
    x = get_node_by_role('variable1')
    y = get_node_by_role('variable2')
    result = get_node_by_role('result')
    template = reasoning_arithmetic.subtraction_templates(x, y, result)
    return [{"pattern": "subtraction", **template}]

# ======== division ========
def reason_division(graph, get_node_by_role):
    numerator = get_node_by_role('variable1')
    denominator = get_node_by_role('variable2')
    quotient = get_node_by_role('result')
    template = reasoning_arithmetic.division_templates(numerator, denominator, quotient)
    return [{"pattern": "division", **template}]

# ======== squared ========
def reason_squared(graph, get_node_by_role):
    base = get_node_by_role('base')
    result = get_node_by_role('result')
    template = reasoning_arithmetic.squared_templates(base, result)
    return [{"pattern": "squared", **template}]

# ======== divisible ========
def reason_divisible(graph, get_node_by_role):
    x = get_node_by_role('variable1')
    y = get_node_by_role('variable2')
    template = reasoning_arithmetic.divisible_templates(x, y)
    return [{"pattern": "divisible", **template}]

# ======== divides ========
def reason_divides(graph, get_node_by_role):
    x = get_node_by_role('variable1')
    y = get_node_by_role('variable2')
    template = reasoning_arithmetic.divides_templates(x, y)
    return [{"pattern": "divides", **template}]

# ======== factor ========
def reason_factor(graph, get_node_by_role):
    x = get_node_by_role('variable1')
    y = get_node_by_role('variable2')
    template = reasoning_arithmetic.factor_templates(x, y)
    return [{"pattern": "factor", **template}]

# ======== cubed ========
def reason_cubed(graph, get_node_by_role):
    base = get_node_by_role('base')
    result = get_node_by_role('result')
    template = reasoning_arithmetic.cubed_templates(base, result)
    return [{"pattern": "cubed", **template}]

# ======== power ========
def reason_power(graph, get_node_by_role):
    base = get_node_by_role('base')
    exponent = get_node_by_role('exponent')
    result = get_node_by_role('result')
    template = reasoning_arithmetic.power_templates(base, exponent, result)
    return [{"pattern": "power", **template}]

# ======== sqrt ========
def reason_sqrt(graph, get_node_by_role):
    radicand = get_node_by_role('radicand')
    result = get_node_by_role('result')
    template = reasoning_arithmetic.sqrt_templates(radicand, result)
    return [{"pattern": "sqrt", **template}]

# ======== cbrt ========
def reason_cbrt(graph, get_node_by_role):
    radicand = get_node_by_role('radicand')
    result = get_node_by_role('result')
    template = reasoning_arithmetic.cbrt_templates(radicand, result)
    return [{"pattern": "cbrt", **template}]

# ======== root ========
def reason_root(graph, get_node_by_role):
    degree = get_node_by_role('degree')
    radicand = get_node_by_role('radicand')
    result = get_node_by_role('result')
    template = reasoning_arithmetic.root_templates(degree, radicand, result)
    return [{"pattern": "root", **template}]

# ======== remainder ========
def reason_remainder(graph, get_node_by_role):
    dividend = get_node_by_role('dividend')
    divisor = get_node_by_role('divisor')
    remainder = get_node_by_role('remainder')
    template = reasoning_arithmetic.remainder_templates(dividend, divisor, remainder)
    return [{"pattern": "remainder", **template}]

# ======== sum_of_two_primes ========
def reason_sum_of_two_primes(graph, get_node_by_role):
    x = get_node_by_role('variable1')
    y = get_node_by_role('variable2')
    result = get_node_by_role('result')
    template = reasoning_arithmetic.sum_of_two_primes_templates(x, y, result)
    return [{"pattern": "sum_of_two_primes", **template}]

# ======== twin_primes ========
def reason_twin_primes(graph, get_node_by_role):
    x = get_node_by_role('variable1')
    y = get_node_by_role('variable2')
    template = reasoning_arithmetic.twin_primes_templates(x, y)
    return [{"pattern": "twin_primes", **template}]

# ======== prime_gap ========
def reason_prime_gap(graph, get_node_by_role):
    x = get_node_by_role('variable1')
    y = get_node_by_role('variable2')
    result = get_node_by_role('result')
    template = reasoning_arithmetic.prime_gap_templates(x, y, result)
    return [{"pattern": "prime_gap", **template}]

# ======== prime_factors ========
def reason_prime_factors(graph, get_node_by_role):
    result = get_node_by_role('result')
    # Accept any "variable" role (variable1, variable2, ...)
    factors = []
    for n, attrs in graph.nodes(data=True):
        role = attrs.get('role', '')
        if role.startswith('variable') and n != result:
            factors.append(n)
    template = reasoning_arithmetic.prime_factors_templates(result, factors)
    return [{"pattern": "prime_factors", **template}]

# ======== is_prime ========
def reason_is_prime(graph, get_node_by_role):
    constant = get_node_by_role('variable1')
    template = reasoning_arithmetic.is_prime_templates(constant)
    return [{"pattern": "is_prime", **template}]

# ======== is_not_prime ========
def reason_is_not_prime(graph, get_node_by_role):
    constant = get_node_by_role('variable1')
    template = reasoning_arithmetic.is_not_prime_templates(constant)
    return [{"pattern": "is_not_prime", **template}]

# ======== prime_order ========
def reason_prime_order(graph, get_node_by_role):
    attr = next((attr for node, attr in graph.nodes(data=True) if 'prime_order' in attr), None)
    prime_order = attr.get('prime_order') if attr else None
    template = reasoning_arithmetic.prime_order_templates(prime_order)
    return [{"pattern": "prime_order", **template}]

# ======== next_prime ========
def reason_next_prime(graph, get_node_by_role):
    x = get_node_by_role('variable1')
    result = get_node_by_role('result')
    template = reasoning_arithmetic.next_prime_templates(x, result)
    return [{"pattern": "next_prime", **template}]

# ======== where_is_prime ========
def reason_where_is_prime(graph, get_node_by_role):
    x = get_node_by_role('variable1')
    template = reasoning_arithmetic.where_is_prime_templates(x)
    return [{"pattern": "where_is_prime", **template}]

# ======== quadruplet_primes ========
def reason_quadruplet_primes(graph, get_node_by_role):
    a = get_node_by_role('variable1')
    b = get_node_by_role('variable2')
    c = get_node_by_role('variable3')
    d = get_node_by_role('variable4')
    x = [a, b, c, d]
    template = reasoning_arithmetic.quadruplet_primes_templates(x)
    return [{"pattern": "quadruplet_primes", **template}]

# ======== triplet_primes ========
def reason_triplet_primes(graph, get_node_by_role):
    a = get_node_by_role('variable1')
    b = get_node_by_role('variable2')
    c = get_node_by_role('variable3')
    x = [a, b, c]
    template = reasoning_arithmetic.triplet_primes_templates(x)
    return [{"pattern": "triplet_primes", **template}]

# ======== diff_of_primes ========
def reason_diff_of_primes(graph, get_node_by_role):
    x = get_node_by_role('variable1')
    y = get_node_by_role('variable2')
    template = reasoning_arithmetic.diff_of_primes_templates(x, y)
    return [{"pattern": "diff_of_primes", **template}]

# ======== prime_exclusion_zone ========
def reason_prime_exclusion_zone(graph, get_node_by_role):
    x = get_node_by_role('variable1')
    result = get_node_by_role('result')
    template = reasoning_arithmetic.prime_exclusion_zone_templates(x, result)
    return [{"pattern": "prime_exclusion_zone", **template}]

# ======== prime_exclusion_zone_range ========
def reason_prime_exclusion_zone_range(graph, get_node_by_role):
    x = get_node_by_role('variable1')
    result1 = get_node_by_role('result1')
    result2 = get_node_by_role('result2')
    template = reasoning_arithmetic.prime_exclusion_zone_range_templates(x, result1, result2)
    return [{"pattern": "prime_exclusion_zone_range", **template}]

# ======== prime_exclusion_vals ========
def reason_prime_exclusion_vals(graph, get_node_by_role):
    for n, attr in graph.nodes(data=True):
        order = attr.get('order')
        local = attr.get('local')
    x = get_node_by_role('variable1')
    result = get_node_by_role('result')
    template = reasoning_arithmetic.prime_exclusion_vals_templates(x, order, local, result)
    return [{"pattern": "prime_exclusion_vals", **template}]