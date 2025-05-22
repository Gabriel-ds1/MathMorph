# pipeline.py
from time import perf_counter
import json
import traceback
from models.semantic_parser import parse_math_sentence
from reasoning.symbolic_tools import build_sympy_equation
from models.graph_reasoner import equation_to_graph, graph_to_parse_dict, print_graph
from utils.candidate_helpers import enhance_candidates
from utils.text_helpers import normalize_sentence
from config.settings import action_ops, sentences, CANDIDATE_VERIFICATION_THRESHOLD
from loggers.scratchpad import Scratchpad
from loggers.provenance import log_generation
from reasoning.candidate_generator import generate_candidates
from verification.formal_verifier import explain_symbolic_verification
from utils.general_helpers import handle_unregistered_action, annotate_error
from reasoning.reasoning_core import Reasoner
from reasoning.tree_search_core import TreeSearchReasoner
from models.nlp_encoder import NLPEncoder
from loggers.log_utils import build_action_registry, logstep, cprint, summary_table, handle_stage, log_failed_formula


class SentenceProcessor:
    """
    Processes mathematical sentences through a parser. Extracts SymPy equation, computes graph nodes and edges, candidate generation, 
    verification and tree search.
    Takes as input:
        -stage_val (value from 0-7) 0: runs every step, 7: runs up to reasoning core (does not update record)
            1: runs up to normalization, 2: runs up to parser, 3: runs up to SymPy equation, 4: runs up to graph, 5: runs up to candidate generation, 6: runs up to verification
        -print_val (0-7) 0: prints every step, 7: only prints reasoning core results
    """
    def __init__(self, step_val, stage_val, print_val):
        self.record = {"step": None, "sentence": None, "normalized": None, "parsed": None, "sympy_eq": None, "graph": None, 
                       "standard_candidates": None, "graph_candidates": None,"reasoning": None, "timings": None}
        
        self.step_val = step_val
        self.stage_val = stage_val
        self.print_val = print_val

        self.reasoner = Reasoner(upper_bound=2000)
        self.action_registry = build_action_registry(action_ops)
        self.tree_search = TreeSearchReasoner(actions=self.action_registry)
        self.scratchpad = Scratchpad(capacity=1000)
        self.nlp_encoder = NLPEncoder()

        self.generator_type = 'both' # run either 'manual', 'auto' or 'both' candidate generator

        self.goal = None # Optional function (graph, state) -> True/False for stopping tree search reasoning
        self.verifications = {}
        self.final_results = []
        self.training_pool = []

    
    def run(self):
        """Pipeline for processing a single input sentence."""
        for step, sentence in enumerate(sentences, 1):
            self.record.update({"step": step, "sentence": sentence})
            cprint("="*60, None)
            cprint(f"Step {step} Input", "CYAN")
            print(sentence)
            try:
                t0 = perf_counter()

                embedding = self.nlp_encoder.encode(sentence)

                # ================ Normalize Sentence ================
                rec_norm, error = handle_stage(normalize_sentence, sentence, record=self.record, final_results=self.final_results, stage_name="Normalized", log_color="BLUE", log_step=self.print_val in (0, 1))
                if error or (self.stage_val == 1 and self.step_val == step): return

                # ================ Parse Sentence ================
                rec_parse, error = handle_stage(parse_math_sentence, rec_norm, record=self.record, final_results=self.final_results, stage_name="Parsed", log_color="YELLOW", log_step=self.print_val in (0, 2))
                if error or (self.stage_val == 2 and self.step_val == step): return
                # ================ SymPy equation ================
                rec_eq, error = handle_stage(build_sympy_equation, rec_parse, record=self.record, final_results=self.final_results, stage_name="SymPy Equation", log_color="MAGENTA", log_step=self.print_val in (0, 3))
                if error or (self.stage_val == 3 and self.step_val == step): return
                # ================ Graph ================
                rec_graph, error = handle_stage(equation_to_graph, rec_parse, record=self.record, final_results=self.final_results, stage_name="Graph", log_color="GREEN", log_step=self.print_val in (0, 4))
                if self.print_val in (0, 4):
                    print_graph(rec_graph)
                    pd2 = graph_to_parse_dict(rec_graph)
                    eq2 = build_sympy_equation(pd2)
                    print("orig parse:", rec_parse)
                    print("roundtrip:", pd2)
                    print("back to sympy:", eq2)
                    print("trace:", pd2["trace"])

                if error or (self.stage_val == 4 and self.step_val == step): return
                t1 = perf_counter()
                # Extract step operation
                op = rec_graph.graph.get('operation', None)

                

                sp_record = {"step": step, "sentence": sentence, "normalized": rec_norm, "parsed": rec_parse, "sympy_eq": rec_eq, "graph": rec_graph}
                self.scratchpad.add(sp_record)
                new_records = sp_record

                # ================ Candidate Generation ================
                candidates_data, error = handle_stage(generate_candidates, self.scratchpad, new_records, self.generator_type, record=self.record, final_results=self.final_results, stage_name="Candidates", log_color="CYAN", log_step=self.print_val in (0, 5))
                if error or (self.stage_val == 5 and self.step_val == step): return
                rec_candidates, graph_candidates = candidates_data
                rec_candidates = enhance_candidates(rec_candidates)
                graph_candidates = enhance_candidates(graph_candidates)
                all_candidates = rec_candidates + graph_candidates
                
                if self.print_val in (0, 5):
                    cprint("CANDIDATES FOUND:", "YELLOW")
                    log_generation(rec_candidates + graph_candidates)
                    for candidate in graph_candidates:
                        print(f"Step {step} | Graph Candidate | {candidate.get('orig_sentence')}: {candidate.get('derived_eq')!r} | {candidate.get('generation_method','')} | {candidate.get('note','')} | {candidate.get('is_correct','')}")
                    for candidate in rec_candidates:
                        print(f"Step {step} | Standard Candidate | {candidate.get('orig_sentence')}: {candidate.get('derived_eq')!r} | {candidate.get('generation_method','')} | {candidate.get('note','')} | {candidate.get('is_correct','')}")


                # ======== Verifications ========
                for candidate in rec_candidates:
                    manual_verification = candidate.get('is_correct')
                    derived_eq = candidate.get('derived_eq')
                    # Candidate verification
                    verify, error = handle_stage(explain_symbolic_verification, derived_eq, self.scratchpad, op, record=self.record, final_results=self.final_results, stage_name="Candidate Verification", log_color="GREEN", log_step=self.print_val in (0, 6))
                    explanation, conf, verdict = verify
                    self.verifications.update({'formula': str(derived_eq), "sympy_eq": derived_eq, 'explanation': explanation, 'confidence': conf, 'auto_verification': verdict})
                    # Insert previous (manual) verifications from SymPy parses
                    self.verifications.update({'manual_verification': manual_verification})
                    if verdict in ('false', 'trivial', 'invalid'):
                        log_failed_formula(derived_eq, candidate, explanation)
                        cprint(f"Logged failed candidate: {derived_eq} (verdict={verdict})", "RED")
                    
                    symbolic_score = conf
                    novelty_score = candidate.get('novelty_conf', 0)
                    if symbolic_score > 0.85 and novelty_score > 0.8:
                        self.training_pool.append(candidate)


                logstep("Verifications", self.verifications, color="GREEN", log_step=self.print_val in (0, 6))
                if error or (self.stage_val == 6 and self.step_val == step): return 

                # ================ Reasoning core / tree search ================
                state = {"reasoner": self.reasoner}
                if 'rhs' in rec_parse:
                    state['rhs'] = rec_parse['rhs']

                action_fn = self.action_registry.get(op, handle_unregistered_action)
                result = action_fn(rec_graph, state)
                if self.print_val in (0, 7):
                    cprint("Direct Action Result:" + str(result[2] if len(result) > 2 else result), 'MAGENTA')

                search_results, error = handle_stage(self.tree_search.search, rec_graph, state, self.goal, record=self.record, final_results=self.final_results, stage_name="Reasoning/Tree Search", log_color="CYAN", log_step=self.print_val in (0, 7))
                if error or (self.stage_val == 7 and self.step_val == step): return
                t2 = perf_counter()

                # ================ Update Record ================
                self.record.update({
                    "normalized": rec_norm, "parsed": rec_parse, "sympy_eq": rec_eq, "graph": rec_graph,
                    "standard_candidates": rec_candidates, #"verifications": self.verifications,
                    "verification": self.verifications,
                    "graph_candidates": graph_candidates,
                    "reasoning": search_results,
                    "timings": {"total": round(t2-t0, 4), "pre-candidates": round(t1-t0, 4), "post-candidates": round(t2-t1, 4)}})
                
                if self.verifications['auto_verification'] == "True" and self.verifications['confidence'] > CANDIDATE_VERIFICATION_THRESHOLD:
                    self.training_pool.append(self.verifications)

                self.final_results.append(self.record)

            except Exception as e:
                cprint(f"[ERROR] during processing: {e}", "RED")
                self.record['error'] = annotate_error("main_loop", e, sentence)
                self.final_results.append(self.record)

        cprint("="*60 + "\n", None)

    def print_summary(self):
        # Pipeline summary
        cprint("PIPELINE SUMMARY", "BLUE")
        summary_table(self.final_results)
        last_record = self.final_results[-1] if self.final_results else {}
        if last_record:
            print(f"Final step | {last_record['step']}: Final Sentence: {last_record['sentence']}")
            print("\tParse:", last_record.get('parsed'))
            print("\tStandard Candidates:", last_record.get('standard_candidates', [])[:])
            print("\tGraph Candidates:", last_record.get('graph_candidates', [])[:])
            print("\tVerified:", [v.get('verified') for v in last_record.get('verifications', [])[:]])
            print("\tTiming:", last_record.get('timings'))

    def save_results(self):
        with open("pipeline_results.json", "w") as f:
            json.dump(self.training_pool, f, indent=2, default=str)
        cprint("Results saved to pipeline_results.json", "GREEN")
