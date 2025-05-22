# reasoning/graph_candidate_motifs.py

import networkx as nx

# ========= Algebraic Motif Subgraph Isomorphism ============

def pythagoras_motif():
    G = nx.Graph()
    # Each squared part:
    G.add_edge('a', 'asq', label='power', exponent=2)
    G.add_edge('b', 'bsq', label='power', exponent=2)
    # The sum of the squares:
    G.add_edge('asq', 'csq', label='addend')
    G.add_edge('bsq', 'csq', label='addend')
    # The result is c squared:
    G.add_edge('c', 'csq', label='power', exponent=2)
    return G

def triangle_sum_motif():
    """
    Motif: x + y = z
    Nodes: x, y, z. Edges indicate both x and y sum to z.
    """
    G = nx.DiGraph()
    G.add_edge('x', 'z', label='addend')
    G.add_edge('y', 'z', label='addend')
    return G

def divides_motif():
    """
    Motif: a divides b (b % a == 0).
    """
    G = nx.DiGraph()
    G.add_node('a')
    G.add_node('b')
    G.add_edge('a', 'b', label='divides', relation='arithmetic')
    return G

def divisible_motif():
    """
    Motif: a is divisible by b (a % b == 0)
    """
    G = nx.DiGraph()
    G.add_node('a')
    G.add_node('b')
    G.add_edge('a', 'b', label='divisible_by', relation='arithmetic')
    return G

def factor_motif():
    """
    Motif: a is a factor of b.
    """
    G = nx.DiGraph()
    G.add_node('a')
    G.add_node('b')
    G.add_edge('a', 'b', label='factor_of', relation='arithmetic')
    return G

def squared_motif():
    """
    Motif: x squared equals y.
    """
    G = nx.DiGraph()
    G.add_node('x')
    G.add_node('y')
    G.add_edge('x', 'y', label='squared', operation='power', exponent=2)
    return G

def cubed_motif():
    """
    Motif: x cubed equals y.
    """
    G = nx.DiGraph()
    G.add_node('x')
    G.add_node('y')
    G.add_edge('x', 'y', label='cubed', operation='power', exponent=3)
    return G

def power_motif():
    """
    Motif: x to the power n equals y.
    """
    G = nx.DiGraph()
    G.add_node('base')
    G.add_node('exp')
    G.add_node('y')
    G.add_edge('base', 'y', label='power_n', operation='power')
    G.add_edge('exp', 'y', label='power_n', operation='power')
    return G

def sqrt_motif():
    """
    Motif: Square root of x is y.
    """
    G = nx.DiGraph()
    G.add_node('radicand')
    G.add_node('y')
    G.add_edge('radicand', 'y', label='sqrt', operation='root', degree=2)
    return G

def cbrt_motif():
    """
    Motif: Cube root of x is y.
    """
    G = nx.DiGraph()
    G.add_node('radicand')
    G.add_node('y')
    G.add_edge('radicand', 'y', label='cbrt', operation='root', degree=3)
    return G

def root_motif():
    """
    Motif: n-th root of x is y.
    """
    G = nx.DiGraph()
    G.add_node('radicand')
    G.add_node('degree')
    G.add_node('y')
    G.add_edge('radicand', 'y', label='root_DEG', operation='root')
    G.add_edge('degree', 'y', label='root', operation='root')
    return G

def remainder_motif():
    """
    Motif: dividend % divisor = remainder.
    """
    G = nx.DiGraph()
    G.add_node('dividend')
    G.add_node('divisor')
    G.add_node('remainder')
    G.add_edge('dividend', 'divisor', label='divided_by', relation='arithmetic')
    G.add_edge('dividend', 'remainder', label='leaves_remainder', relation='arithmetic')
    return G

def equals_motif():
    """
    Motif: x equals y.
    """
    G = nx.DiGraph()
    G.add_node('x')
    G.add_node('y')
    G.add_edge('x', 'y', label='eq', operation='eq')
    return G



# ===== prime motifs =====
def is_prime_motif():
    """
    Motif: 'x' is prime.
    """
    G = nx.DiGraph()
    G.add_node('x', is_prime=True)
    G.add_edge('x', 'x', label='is_prime', relation='property')
    return G

def is_not_prime_motif():
    """
    Motif: 'x' is not prime.
    """
    G = nx.DiGraph()
    G.add_node('x', is_prime=False)
    G.add_edge('x', 'x', label='is_not_prime', relation='property')
    return G

def prime_order_motif():
    """
    Motif: x is the n-th prime.
    """
    G = nx.DiGraph()
    G.add_node('x', prime_order='n')
    G.add_node('prime', type='concept')
    G.add_edge('x', 'prime', label='prime_order_n', relation='order', order='n')
    return G

def twin_primes_motif():
    """
    Motif: x and y are twin primes (abs(x-y)=2, both primes).
    """
    G = nx.DiGraph()
    G.add_node('x', is_prime=True)
    G.add_node('y', is_prime=True)
    G.add_node('prime', type='concept')
    G.add_edge('x', 'prime', label='twin_prime', relation='concept')
    G.add_edge('y', 'prime', label='twin_prime', relation='concept')
    G.add_edge('x', 'y', label='twin_prime_pair', relation='twin_pair')
    return G

def diff_of_primes_motif():
    """
    Motif: Difference of two primes is also prime.
    """
    G = nx.DiGraph()
    G.add_node('x', is_prime=True)
    G.add_node('y', is_prime=True)
    G.add_node('d', is_prime=True)
    G.add_edge('x', 'y', label='difference_of', relation='arithmetic')
    G.add_node('prime', type='concept')
    G.add_edge('d', 'prime', label='diff_of_primes', relation='property')
    return G

def sum_of_two_primes_motif():
    """
    Motif: x + y = z, all primes.
    """
    G = nx.DiGraph()
    G.add_node('x', is_prime=True)
    G.add_node('y', is_prime=True)
    G.add_node('z', is_prime=True)
    G.add_edge('x', 'y', label='add', relation='property')
    G.add_edge('z', 'prime', label='is_prime', relation='property')
    return G

def prime_factors_motif():
    """
    Motif: z = x * y * w, all are primes.
    """
    G = nx.DiGraph()
    G.add_node('x', is_prime=True)
    G.add_node('y', is_prime=True)
    G.add_node('w', is_prime=True)
    G.add_node('z', is_prime=True)
    G.add_edge('x', 'z', label='is_prime_factor', relation='property')
    G.add_edge('y', 'z', label='is_prime_factor', relation='property')
    G.add_edge('w', 'z', label='is_prime_factor', relation='property')
    return G

def next_prime_motif():
    """
    Motif: y = next_prime(x)
    """

    G = nx.DiGraph()
    G.add_node('x', is_prime=True)
    G.add_node('y', is_prime=True)
    G.add_edge('x', 'y', label='next_prime', relation='property')
    return G

def where_is_prime_motif():
    """
    Motif: n-th prime
    """
    G = nx.DiGraph()
    G.add_node('n')
    G.add_node('prime_n', is_prime=True)
    G.add_edge('n', 'prime_n', label='where_is_prime', relation='property')
    return G

def prime_gap_motif():
    """
    Motif: Gap g between two primes x and y (abs(x-y)=g)
    """
    G = nx.DiGraph()
    G.add_node('x', is_prime=True)
    G.add_node('y', is_prime=True)
    G.add_node('g')
    G.add_edge('x', 'y', label='difference_of', relation='arithmetic')
    G.add_edge('g', ('x', 'y'), label='is_gap_of_primes', relation='property')
    return G

def quadruplet_primes_motif():
    """
    Motif: quadruplet primes: p, p+2, p+6, p+8
    """
    G = nx.DiGraph()
    G.add_node('p', is_prime=True)
    G.add_node('p2', is_prime=True)
    G.add_node('p6', is_prime=True)
    G.add_node('p8', is_prime=True)
    G.add_node('prime', type='concept')
    G.add_edge('p', 'prime', label='is_prime', relation='property')
    G.add_edge('p', 'p2', label='p+2', relation='property')
    G.add_edge('p2', 'prime', label='is_prime', relation='property')
    G.add_edge('p', 'p6', label='p+6', relation='property')
    G.add_edge('p6', 'prime', label='is_prime', relation='property')
    G.add_edge('p', 'p8', label='p+8', relation='property')
    G.add_edge('p8', 'prime', label='is_prime', relation='property')
    return G

def triplet_primes_motif():
    """
    Motif: triplet primes p, q, r, all consecutive.
    """
    G = nx.DiGraph()
    G.add_node('p', is_prime=True)
    G.add_node('q', is_prime=True)
    G.add_node('r', is_prime=True)
    G.add_edge('p', 'q', label='is_prime', relation='property')
    G.add_edge('q', 'r', label='is_prime', relation='property')
    G.add_edge('r', 'p', label='is_prime', relation='property')
    return G

def prime_exclusion_zone_motif():
    """
    Motif: prime exclusion zone, lhs -> rhs with label prime_exclusion_zone.
    """
    G = nx.DiGraph()
    G.add_node('a', is_prime=True)
    G.add_node('b', is_prime=True)
    G.add_edge('a', 'b', label='prime_exclusion_zone', operation='prime_exclusion')
    return G

def prime_exclusion_zone_range_motif():
    """
    Motif: prime exclusion zone range, lhs connects to two results
    """
    G = nx.DiGraph()
    G.add_node('a', is_prime=True)
    G.add_node('b1', is_prime=True)
    G.add_node('b2', is_prime=True)
    G.add_edge('a', 'b1', label='prime_exclusion_zone_range', operation='prime_exclusion_range')
    G.add_edge('a', 'b2', label='prime_exclusion_zone_range', operation='prime_exclusion_range')
    return G

def prime_exclusion_vals_motif():
    """
    Motif: Specialized prime exclusion values.
    """
    G = nx.DiGraph()
    G.add_node('a', is_prime=True)
    G.add_node('b', is_prime=True)
    G.add_edge('a', 'b', label='prime_exclusion_LOCAL_values', order='ORDER', operation='prime_exclusion')
    return G

def goldbach_motif():
    """
    Motif: even = p1 + p2, where p1, p2 are primes.
    Nodes: even, p1, p2. Edges: p1/p2 -> even, labeled 'addend'
    """
    G = nx.DiGraph()
    G.add_edge('p1', 'even', label='addend')
    G.add_edge('p2', 'even', label='addend')
    G.nodes['p1']['is_prime'] = True
    G.nodes['p2']['is_prime'] = True
    return G

KNOWN_MOTIFS = {
    "pythagoras": pythagoras_motif(),
    "triangle_sum": triangle_sum_motif(),
    "divides": divides_motif(),
    "divisible": divisible_motif(),
    "factor": factor_motif(),
    "squared": squared_motif(),
    "cubed": cubed_motif(),
    "power": power_motif(),
    "sqrt": sqrt_motif(),
    "cbrt": cbrt_motif(),
    "root": root_motif(),
    "remainder": remainder_motif(),
    "equals": equals_motif(),
    "is_prime": is_prime_motif(),
    "is_not_prime": is_not_prime_motif(),
    "prime_order": prime_order_motif(),
    "twin_primes": twin_primes_motif(),
    "diff_of_primes": diff_of_primes_motif(),
    "sum_of_two_primes": sum_of_two_primes_motif(),
    "prime_factors": prime_factors_motif(),
    "next_prime": next_prime_motif(),
    "where_is_prime": where_is_prime_motif(),
    "prime_gap": prime_gap_motif(),
    "quadruplet_primes": quadruplet_primes_motif(),
    "triplet_primes": triplet_primes_motif(),
    "prime_exclusion_zone": prime_exclusion_zone_motif(),
    "prime_exclusion_zone_range": prime_exclusion_zone_range_motif(),
    "prime_exclusion_vals": prime_exclusion_vals_motif(),
    "goldbach": goldbach_motif(),
}