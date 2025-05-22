# reasoning/reasoning_core.py

from utils.general_helpers import annotate_error
from utils import reasoning_helpers

class Reasoner:
    def __init__(self, upper_bound:int = 100):
        if not upper_bound >= 2:
            raise ValueError("upper_bound should be >= 2")
        self.upper_bound = upper_bound
        
    def _get_node_by_role(self, graph, role):
        for n, attrs in graph.nodes(data=True):
            if attrs.get('role') == role:
                return n
        return None
        
    def process_graph(self, graph):
        """
        Given a graph for a statement, determines which prime pattern applies,
        and performs reasoning/expansion for that operation. 
        Returns: List of inferred facts (dictionaries)
        """
        try:
            op = graph.graph.get('operation')
            operation_map = {
                'eq': lambda g: reasoning_helpers.reason_equals(g, lambda role: self._get_node_by_role(g, role)),
                'add': lambda g: reasoning_helpers.reason_addition(g, lambda role: self._get_node_by_role(g, role)),
                'mul': lambda g: reasoning_helpers.reason_multiplication(g, lambda role: self._get_node_by_role(g, role)),
                'sub': lambda g: reasoning_helpers.reason_subtraction(g, lambda role: self._get_node_by_role(g, role)),
                'div': lambda g: reasoning_helpers.reason_division(g, lambda role: self._get_node_by_role(g, role)),
                'squared': lambda g: reasoning_helpers.reason_squared(g, lambda role: self._get_node_by_role(g, role)),
                'divisible': lambda g: reasoning_helpers.reason_divisible(g, lambda role: self._get_node_by_role(g, role)),
                'divides': lambda g: reasoning_helpers.reason_divides(g, lambda role: self._get_node_by_role(g, role)),
                'factor': lambda g: reasoning_helpers.reason_factor(g, lambda role: self._get_node_by_role(g, role)),
                'cubed': lambda g: reasoning_helpers.reason_cubed(g, lambda role: self._get_node_by_role(g, role)),
                'power': lambda g: reasoning_helpers.reason_power(g, lambda role: self._get_node_by_role(g, role)),
                'sqrt': lambda g: reasoning_helpers.reason_sqrt(g, lambda role: self._get_node_by_role(g, role)),
                'cbrt': lambda g: reasoning_helpers.reason_cbrt(g, lambda role: self._get_node_by_role(g, role)),
                'root': lambda g: reasoning_helpers.reason_root(g, lambda role: self._get_node_by_role(g, role)),
                'remainder': lambda g: reasoning_helpers.reason_remainder(g, lambda role: self._get_node_by_role(g, role)),
                'sum_of_two_primes': lambda g: reasoning_helpers.reason_sum_of_two_primes(g, lambda role: self._get_node_by_role(g, role)),
                'twin_primes': lambda g: reasoning_helpers.reason_twin_primes(g, lambda role: self._get_node_by_role(g, role)),
                'prime_gap': lambda g: reasoning_helpers.reason_prime_gap(g, lambda role: self._get_node_by_role(g, role)),
                'prime_factors': lambda g: reasoning_helpers.reason_prime_factors(g, lambda role: self._get_node_by_role(g, role)),
                'is_prime': lambda g: reasoning_helpers.reason_is_prime(g, lambda role: self._get_node_by_role(g, role)),
                'is_not_prime': lambda g: reasoning_helpers.reason_is_not_prime(g, lambda role: self._get_node_by_role(g, role)),
                'prime_order': lambda g: reasoning_helpers.reason_prime_order(g, lambda role: self._get_node_by_role(g, role)),
                'next_prime': lambda g: reasoning_helpers.reason_next_prime(g, lambda role: self._get_node_by_role(g, role)),
                'where_is_prime': lambda g: reasoning_helpers.reason_where_is_prime(g, lambda role: self._get_node_by_role(g, role)),
                'quadruplet_primes': lambda g: reasoning_helpers.reason_quadruplet_primes(g, lambda role: self._get_node_by_role(g, role)),
                'triplet_primes': lambda g: reasoning_helpers.reason_triplet_primes(g, lambda role: self._get_node_by_role(g, role)),
                'diff_of_primes': lambda g: reasoning_helpers.reason_diff_of_primes(g, lambda role: self._get_node_by_role(g, role)),
                'prime_exclusion_zone': lambda g: reasoning_helpers.reason_prime_exclusion_zone(g, lambda role: self._get_node_by_role(g, role)),
                'prime_exclusion_zone_range': lambda g: reasoning_helpers.reason_prime_exclusion_zone_range(g, lambda role: self._get_node_by_role(g, role)),
                'prime_exclusion_vals': lambda g: reasoning_helpers.reason_prime_exclusion_vals(g, lambda role: self._get_node_by_role(g, role)),
            }
            reasoner = operation_map.get(op)
            if reasoner:
                return(reasoner(graph))
            else:
                return [{"pattern": "unknown_operation", "operation": op,
                    "message": (f"No handler for operation '{op}'. Please check your input or add a handler for this operation."), "graph_summary": str(graph.graph)}]
    
        except Exception as e:
            return [annotate_error("process_graph", e, graph)]
