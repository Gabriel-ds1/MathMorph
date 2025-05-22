# config/settings.py
import os
from pathlib import Path

cache_dir = Path.home()
embedding_cache_file = "embedding_cache.pkl" # path for output cache
LOGFILE = "loggers/logs/unknown_parses.log" # path for output log

CANDIDATE_VERIFICATION_THRESHOLD = 0.85 # threshold for which candidates to keep
PROVENANCE_FILE = "loggers/provenance.log" # provenance

# pre-trained models
OPENAI_MODEL = os.environ.get("OPENAI_MATH_MODEL", "gpt-4.1")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)
DEFAULT_TRANSFORMER_MODEL = 'tbs17/MathBERT'

# list of available candidate graph generators
candidate_graphs = ['direct_sympy', 'commutativity_or_rearrangement', 'factoring_lhs', 'expand_lhs', 'odd_prime_mod_2', 'fermat_little_theorem', 
                        'graph_star_discovery', 'graph_bipartite_discovery', 'graph_motif_subgraph_discovery', 'graph_clique_discovery', 'graph_path_discovery', 'graph_cycle_discovery']

# dict of all available operations and their respective action
action_ops = {'sum_of_two_primes': 'sum_of_two_primes_action', 'twin_primes': 'twin_primes_action',
              'prime_exclusion_vals': 'prime_exclusion_vals_action', 'prime_order': 'prime_order_action',
              'where_is_prime': 'where_is_prime_action', 'next_prime': 'next_prime_action',
              'diff_of_primes': 'diff_of_primes_action', 'prime_factors': 'prime_factors_action',
              'is_prime': 'is_prime_action', 'is_not_prime': 'is_not_prime_action',
              'prime_gap': 'prime_gap_action', 'quadruplet_primes': 'quadruplet_primes_action',
              'triplet_primes': 'triplet_primes_action', 'prime_exclusion_zone': 'prime_exclusion_zone_action',
              'prime_exclusion_zone_range': 'prime_exclusion_zone_range_action', 'squared': 'squared_action',
              'cubed': 'cubed_action', 'power': 'power_action',
              'sqrt': 'sqrt_action', 'cbrt': 'cbrt_action',
              'root': 'root_action', 'divisible': 'divisible_action',
              'divides': 'divides_action', 'factor': 'factor_action',
              'remainder': 'remainder_action', 'div': 'division_action',
              'mul': 'multiplication_action', 'add': 'addition_action',
              'sub': 'subtraction_action', 'eq': 'equals_action'}
  
# list of input sentences
sentences = [
        "The sum of 4 and 6 is 10.",
        "Three times 5 equals 15.",
        "The product of 4 and 8 equals 12.",
        "15 minus 4 is 11.",
        "16 equals 15.",
        "8 divided by 2 is 4.",
        "the quotient of 11 and 5 is 7.",
        "16 is divisible by 2",
        "2 divides 16",
        "4 is a factor of 12",
        "49 squared equals 2401",
        "8 cubed is 512",
        "27 to the 3rd power equals 19683",
        "the square root of 49 is 7",
        "the cube root of 8 equals 2",
        "the 4th root of 16 equals 2",
        "37 leaves a remainder of 1 when divided by 6",

        "25 is a prime number.",
        "49 is not a prime number.",
        "17 is the next prime number after 13",
        "11 and 13 are twin primes",
        "the difference between 13 and 6 is a prime number",
        "the sum of two primes is 24",
        "The prime factors of 30 are 2, 3 and 5.",
        "what number is the next prime after 31",
        "13 is the next prime number after 11",
        "What is the 10th prime number?",
        "Find the hundredth prime.",
        "The gap between the primes 16 and 22 is 6.",
        "what is the smallest prime number?",
        "The quadruplet 5, 7, x, 13 are all primes.",
        "Triplet primes are 3, 5, and 13.",
        "The Prime Exclusion Zone of 9 is 7",
        "the prime exclusion zone of 7 has a range from 2 to 12",
        "the furthest prime exclusion zone overshoot value of 10 is 12",
        "the furthest prime exclusion zone undershoot value of 11 is 2",
        "the closest prime exclusion zone overshoot value of 5 is y",
        "the closest prime exclusion zone undershoot value of 8 is 6",
        #"The product of x and y is 12",
        #"x squared minus 1 equals 0",

    ]