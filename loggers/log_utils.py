# loggers/log_utils.py

import os
from datetime import datetime
from config.settings import LOGFILE
from pprint import pprint
from reasoning.tree_search_core import CallAction
from tabulate import tabulate
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLORAMA = True
except ImportError:
    COLORAMA = False

DEBUG = True

def cprint(msg, color=None, end='\n'):
    """ Colored print for logs """
    if COLORAMA and color:
        print(getattr(Fore, color.upper()) + str(msg) + Style.RESET_ALL, end=end)
    else:
        print(msg, end=end)

def logstep(desc, payload, *, color=None, log_step=False):
    if not DEBUG or not log_step:
        return
    cprint(f"[{desc}]", color or "WHITE")
    if isinstance(payload, dict) or isinstance(payload, list):
        pprint(payload)
    else:
        print(payload)
    print()

def find_action(action_name):
    def wrapper(graph, state):
        return CallAction(graph, state, display=True).__getattribute__(action_name)()
    return wrapper

def build_action_registry(actions):
    registry = {}
    for op, action_method in actions.items():
        registry[op] = find_action(action_method)
    return registry

def summary_table(final_results):
    summary = []
    for rec in final_results:
        standard_candidates = rec.get('standard_candidates', [])
        graph_candidates = rec.get('graph_candidates', [])
        verifications = rec.get('verifications', [])
        summary.append([
            rec['step'],
            rec['sentence'],
            rec.get('parsed', {}).get('op'),
            ', '.join([str(c.get('derived_eq', '')) for c in standard_candidates[:2]]) + \
                (f"...(+{len(standard_candidates)-2} more)" if len(standard_candidates)>2 else ""),
            ', '.join([str(c.get('derived_eq', '')) for c in graph_candidates[:2]]) + \
                (f"...(+{len(graph_candidates)-2} more)" if len(graph_candidates)>2 else ""),
            ', '.join([str(v.get('verified')) for v in verifications[:2]]) + \
                (f"...(+{len(verifications)-2} more)" if len(verifications)>2 else ""),
            str(rec.get('timings'))])
    print(tabulate(summary, headers=['Step','Sentence','ParsedOp','Standard Candidates', 'Graph_Candidates', 'Verification','Timings'], tablefmt="github"))

def log_unknown(sentence, extra=None):
    os.makedirs(os.path.dirname(LOGFILE), exist_ok=True)
    with open(LOGFILE, "a", encoding="utf8") as f:
        f.write(f"{datetime.now(datetime.timezone.utc).isoformat()} | {sentence}\n")
        if extra:
            f.write(f"{extra}\n")

def log_error_if_any(rec_stage, record, final_results, rec_name, log_step):
    if 'error_stage' in rec_stage:
        record['error'] = rec_stage
        final_results.append(record)
        logstep(f"{rec_name} [ERROR]", rec_stage, color="RED", log_step=log_step)
        return True
    return False

def handle_stage(stage_func, *args, record, final_results, stage_name, log_color, log_step):
    """Unified handler for processing, logging, and error checking per stage."""
    result = stage_func(*args)
    if log_error_if_any(result, record, final_results, stage_name, log_step=log_step):
        return None, True
    logstep(desc=stage_name, payload=result, color=log_color, log_step=log_step)
    return result, False

def log_failed_formula(eq, candidate, explanation):
    fail_log = os.path.splitext(LOGFILE)[0] + "_failed_verifications.log"
    os.makedirs(os.path.dirname(fail_log), exist_ok=True)
    with open(fail_log, "a", encoding="utf8") as f:
        timestamp = datetime.now().isoformat()
        msg = (
            f"{timestamp}\n"
            f"Failed Formula: {eq}\n"
            f"Verdict: {candidate.get('verification',{}).get('verdict')}\n"
            f"Reason: {explanation}\n"
            f"Source: {candidate.get('orig_sentence','')}\n"
            f"Step: {candidate.get('source_step','')}\n"
            f"---\n")
        f.write(msg)