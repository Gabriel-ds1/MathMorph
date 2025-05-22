# reasoning/tree_search_core.py

from utils.general_helpers import handle_unregistered_action, annotate_error

class TreeSearchReasoner:
    def __init__(self, actions=None, max_depth=5):
        """
        Initializes the reasoner.
        actions: a dictionary of action functions ('str' -> 'callable')
        max_depth: limits the tree search for tractability
        """

        self.actions = actions if actions else {}
        self.max_depth = max_depth

    def register_action(self, name, func):
        """
        Dynamically add new action steps
        """
        self.actions[name] = func
        print("self.actions[name] is", self.actions[name])

    def available_actions(self, graph, state):
        """
        Returns a list of applicable actions, possibly based on current graph or scratchpad state.
        """

        op = graph.graph.get('operation', None)
        if op and op in self.actions:
            return [(op, self.actions[op])]
        return [("unknown", handle_unregistered_action)]
    
    def apply_action(self, action_name, graph, state):
        """
        Apply a reasoning step (action).
        :action_name: key of the action to use
        :graph : the semantic/math graph
        :state: scratchpad or current memory state
        """
        # Use fallback if action not registered:
        action_fn = self.actions.get(action_name, handle_unregistered_action(graph, state))
        return action_fn(graph, state)
        
    def search(self, graph, state, goal=None, depth=0, path=None):
        """
        Main search/traversal routine.
        - graph: start graph
        - state: current scratchpad/history
        - goal: an optional function (graph, state) -> True/False for stopping
        Returns a list of (graph, state, reason_sequence) for all found solutions up to depth limit
        """

        path = path or []
        results = []
        # Base case: at depth = 0, apply all actions
        if depth == 0:
            for action_name, action_func in self.available_actions(graph, state):
                new_graph, new_state, desc = self.apply_action(action_name, graph, state)
                # Error propagation logic
                if isinstance(desc, dict) and 'error_stage' in desc:
                    # Error occured: add to results to see error in derivation
                    results.append({
                        'error': desc,
                        'path': path + [(action_name, f'[ERROR] {desc["error_stage"]}: {desc["error_message"]}')]})
                    continue
                # Only append if reasoning (desc) is *not* a skip message
                if desc and not desc.startswith("(Skipped)"):
                    results.append((new_graph, new_state, path + [(action_name, desc)]))

                # if all results are errors, surface this up
                if all(isinstance(res, dict) and 'error' in res for res in results):
                    return results
                # Otherwise, return only the successful chains
                return [r for r in results if not (isinstance(r, dict) and 'error' in r)]
            
        # if there are more complex action-chains, recurse here:
        if goal and goal(graph, state):
            return [(graph, state, list(path))]
        if depth >= self.max_depth:
            return results
        for action_name, action_func in self.available_actions(graph, state):
            new_graph, new_state, desc = self.apply_action(action_name, graph, state)
            
            if isinstance(desc, dict) and 'error_stage' in desc:
                # Annotate error branch, do not descend
                results.append({
                    'error': desc,
                    'path': path + [(action_name, f'[ERROR] {desc["error_stage"]}: {desc["error_message"]}')]})
                continue

            # Only recurse if desc is meaningful, and you want chain-of-reasoning:
            if desc and not desc.startswith("(Skipped)"):
                subresults = self.search(new_graph, new_state, goal, depth+1, path + [(action_name, desc)])
                results.extend(subresults)
            
        # if all results are errors
        if all(isinstance(res, dict) and 'error' in res for res in results):
            return results
        return [r for r in results if not (isinstance(r, dict) and 'error' in r)]


# === actions ===
class CallAction:
    """
        Call an action to do reasoning work on.
        Only runs if the underlying problem in the graph or parse indicates the specified task. e.g. (sum_of_two_primes)
        - graph: the equation graph (from equation_to_graph)
        - state: dict, should include 'reasoner' (instance), and may have 'rhs'
        Returns: (graph, state, result_str)
        """
    def __init__(self, graph, state, display):
        self.graph = graph
        self.state = state
        self.display = display
        self.reasoner = self.state.get('reasoner')

    def display_reasoning(self, action_name):
        """
        Helper to process the graph and optional output display
        """
        try:
            if not self.reasoner:
                return self.graph, self.state, "No Reasoner found"
            # execute reasoner
            reasoning = self.reasoner.process_graph(self.graph)
            # optional display
            if self.display and reasoning:
                explanation = reasoning[0].get('explanation', str(reasoning))
                formulas = reasoning[0]['formulas'] if reasoning and 'formulas' in reasoning[0] else str(reasoning)
                display_output = " | ".join([str(explanation), str(formulas)])
                return self.graph, self.state, display_output
            else:
                return self.graph, self.state, None
        except Exception as e:
            return self.graph, self.state, annotate_error(f"{action_name}_action", e, [self.graph, self.state])
        
    # === Primality actions ===
    def sum_of_two_primes_action(self):
        return self.display_reasoning("sum_of_two_primes")
    
    def prime_order_action(self):
        return self.display_reasoning("prime_order")
    
    def where_is_prime_action(self):
        return self.display_reasoning("where_is_prime")
    
    def next_prime_action(self):
        return self.display_reasoning("next_prime")
    
    def diff_of_primes_action(self):
        return self.display_reasoning("diff_of_primes")
    
    def prime_factors_action(self):
        return self.display_reasoning("prime_factors")
    
    def is_prime_action(self):
        return self.display_reasoning("is_prime")
    
    def is_not_prime_action(self):
        return self.display_reasoning("is_not_prime")
    
    def prime_gap_action(self):
        return self.display_reasoning("prime_gap")
    
    def quadruplet_primes_action(self):
        return self.display_reasoning("quadruplet_primes")
    
    def triplet_primes_action(self):
        return self.display_reasoning("triplet_primes")
    
    def twin_primes_action(self):
        return self.display_reasoning("twin_primes")
    
    def prime_exclusion_zone_action(self):
        return self.display_reasoning("prime_exclusion_zone")
    
    def prime_exclusion_zone_range_action(self):
        return self.display_reasoning("prime_exclusion_zone_range")
    
    def prime_exclusion_vals_action(self):
        return self.display_reasoning("prime_exclusion_vals")
    
    # === Standard Math actions ===
    def squared_action(self):
        return self.display_reasoning("squared")
    
    def cubed_action(self):
        return self.display_reasoning("cubed")
    
    def power_action(self):
        return self.display_reasoning("power")
    
    def sqrt_action(self):
        return self.display_reasoning("sqrt")
    
    def cbrt_action(self):
        return self.display_reasoning("cbrt")
    
    def root_action(self):
        return self.display_reasoning("root")
    
    def divisible_action(self):
        return self.display_reasoning("divisible")
    
    def divides_action(self):
        return self.display_reasoning("divides")
    
    def factor_action(self):
        return self.display_reasoning("factor")
    
    def remainder_action(self):
        return self.display_reasoning("remainder")
    
    # === Basic Operation Actions ===
    def division_action(self):
        return self.display_reasoning("division")
    
    def multiplication_action(self):
        return self.display_reasoning("multiplication")
    
    def addition_action(self):
        return self.display_reasoning("addition")
    
    def subtraction_action(self):
        return self.display_reasoning("subtraction")
    
    def equals_action(self):
        return self.display_reasoning("equals")
