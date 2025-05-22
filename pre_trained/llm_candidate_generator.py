# pre_trained/llm_candidate_generator.py

import json
from utils.candidate_helpers import make_candidate
from config.settings import OPENAI_MODEL, OPENAI_API_KEY
from openai import OpenAI
from utils.general_helpers import annotate_error
#from .utils.calc_util import scientific_calculator, calculator_function


def build_generation_prompt(rec):
    # Given a record, build a simple math-oriented prompt
    parse = rec.get('parsed', {})
    op = parse.get('op', '[unknown]')
    if op != 'unknown':
        description = f"Operation: {op}, LHS: {parse.get('lhs')}, RHS: {parse.get('rhs')}"
    else:
        description = rec.get('sentence', '')
    prompt = (
        "Given the following math structure, fill in the missing outputs/equations/note in the same exact format, and within them, propose at least one new, nontrivial mathematical relationship or formula that could be inferred or conjectured.\n"
        "In the Note: section, place either Symbolic, Concrete, Concept, or Unknown depending on whether theres a variable, known values, or a concept such as isprime(5).\n"
        " Feel free to include any additional equations (they dont have to be specifically related to just commutative/modula like in the examples, include more variety when possible) and make sure each string output has a corresponding SymPy equation.\n"
        "Given the following mathematical structure, produce:\n"
        "- (1) A list of possible string outputs\n"
        "- (2) Their corresponding SymPy equations\n"
        "- (3) At least one NEW, NONTRIVIAL mathematical relationship or conjecture related to the input—clearly marked.\n"
        "STRICT FORMAT:\n"
        "Output as a block of JSONL entries, one line each, like this:\n"
        '{"type": "string", "formula": "c + 6 = 7", "note": "symbolic"}\n'
        '{"type": "sympy", "formula": "Eq(c + 6, 7)", "note": "symbolic"}\n'

        '{"type": "string", "formula": "6 + c = 7", "note": "symbolic"}\n'
        '{"type": "sympy", "formula": "Eq(6 + c, 7)", "note": "symbolic"}\n'

        '{"type": "string", "formula": "7 - 6 = c", "note": "symbolic"}\n'
        '{"type": "sympy", "formula": "Eq(7 - 6, c)", "note": "symbolic"}\n'

        '{"type": "string", "formula": "c = 1", "note": "concrete"}\n'
        '{"type": "sympy", "formula": "Eq(c, 1)", "note": "concrete"}\n'

        '{"type": "string", "formula": "7 - c = 6", "note": "symbolic"}\n'
        '{"type": "sympy", "formula": "Eq(7 - c, 6)", "note": "symbolic"}\n'

        '{"type": "string", "formula": "c ≡ 10 (mod 6)", "note": "symbolic"}\n'
        '{"type": "sympy", "formula": "Eq(Mod(c, 6), Mod(10, 6))", "note": "symbolic"}\n'

        '{"type": "string", "formula": "c ≡ 4 (mod 6)", "note": "symbolic"}\n'
        '{"type": "sympy", "formula": "Eq(Mod(c, 6), 4)", "note": "symbolic"}\n'
        "\n"
        "Only use valid JSON per line. Do NOT include explanation text or ANY other text outside these blocks.\n"

        f"\nInput: {description}\n"
        "Begin output below:\n")
    return prompt

def call_model(prompt, max_tokens=120, temperature=0.8):
    if  not OPENAI_API_KEY:
        # Demo fallback
        return f"(No LLM available. Prompt was: {prompt[:60]}...)"
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.responses.create(model=OPENAI_MODEL,
                                   #tools=[calculator_function],
                                   input=[
                                       {"role": "system", "content": "You are a mathematics research AI who outputs new math conjectures and facts."},
                                       {"role": "user", "content": prompt}],
                                    temperature=temperature)
    
    #if 'function_call' in response.choices[0].message:
        #function_args = response.choices[0].message['function_call']['arguments']
        # Extract the expression
        #expression = function_args['expression']
       # result = scientific_calculator(expression)
        # to-do: send this result back as a 'function response' message in multi-turn dialogues.

    response_text = response.output_text.strip().lower()
    print('response text is', response_text)
    return response_text


def parse_llm_output(output):
    lines = [l.strip() for l in output.splitlines() if l.strip()]
    results = []
    for line in lines:
        try:
            item = json.loads(line)
            results.append(item)
        except Exception as e:
            # Optionally, keep a log of lines that failed (for debugging improvements)
            return [annotate_error("parse_llm_output", e, str(output))]
    print("Parsed results:", results) # {type: 'string', formula: '3*5=15', note: 'concrete}, {type: 'sympy', formula: 'eq(..)', note: 'concrete'}, ...
    return results

def generate_auto_candidates(new_records):
    """
    Calls an LLM to suggest new mathematical formulas based on parse/graph.
    Returns: list of candidate dicts, empty list for graph_cands (for now).
    """
    results = []
    graph_results = []

    # Create a prompt from the parse/graph
    prompt = build_generation_prompt(new_records)
    try:
        llm_output = call_model(prompt)
        candidates = parse_llm_output(llm_output)
    except Exception as e:
        candidates = []
        llm_output = f"Error during LLM call: {str(e)}"
        return [annotate_error("generate_auto_candidates", e, str(new_records))]

    i = 0
    n = len(candidates)
    while i < n:
        cand = candidates[i]
        if cand['type'] == 'string':
            llm_formula_str = cand['formula']
            llm_note = cand.get('note', '').strip().lower()
            # Try to pair with next sympy with same note
            pair_idx = None
            if i+1 < n:
                next_cand = candidates[i+1]
                if next_cand['type'] == 'sympy' and next_cand.get('note', '').strip().lower() == llm_note:
                    pair_idx = i+1
            llm_derived_eq = candidates[pair_idx]['formula'] if pair_idx else None
            results.append(make_candidate(new_records, derived_eq=llm_derived_eq, method='llm_generation', str_eq=llm_formula_str, note=llm_note, correct='unknown'))
            i += 2 if pair_idx else 1  # skip both if paired
        elif cand['type'] == 'sympy':
            # Only add unpaired, non-redundant sympy (e.g., new conjectures), not just "eq(3*5, 15)"
            if i == 0 or candidates[i-1]['type'] != 'string':
                llm_derived_eq = cand['formula']
                llm_note = cand.get('note', '').strip().lower()
                results.append(make_candidate(new_records, derived_eq=llm_derived_eq, method='llm_generation', str_eq=None, note=llm_note, correct='unknown'))
            i += 1
        else:
            # ignore unknown types
            i += 1

    return results, graph_results