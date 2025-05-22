# pre_trained/novelty_classification.py

import os
import re
import sys
import json
from openai import OpenAI
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.settings import OPENAI_API_KEY, OPENAI_MODEL
#from .utils.calc_util import scientific_calculator, calculator_function

client = OpenAI(api_key=OPENAI_API_KEY)

def build_novelty_prompt(formula, fewshot=True):
    prompt=""
    if fewshot:
        # Add a few examples to "teach" GPT
        prompt += (
            "Classify each mathematical statement as 'trivial' (routine/arithmetic/simple) or 'nontrivial' (novel/theorem-level/interesting):\n"
            "1. 2 + 2 = 4 | Answer: trivial | Confidence: 0.99"
            "3. a^2 + b^2 = c^2 | Answer: nontrivial | Confidence: 0.95"
            "3. x = x | Answer: trivial | Confidence: 0.99"
            "4. prime(n) > n for n > 1 | Answer: nontrivial | Confidence: 0.85")
        prompt += f"5. {formula} | Answer:"
    return prompt

def chatgpt_novelty_label(formula, openai_model=OPENAI_MODEL, temperature=0):
    system_msg = "You are an expert mathematician. Given a formula or equation, classify if it is 'trivial' (basic, obvious, tautological)\n"
    "or 'nontrivial' (interesting, theorem-like, or surprising). Make sure to add a 'confidence' score on a scale from 0 to 1."
    prompt = build_novelty_prompt(formula, fewshot=True)

    response = client.responses.create(model=openai_model,
                                       #tools=[calculator_function],
                                       input=[{"role": "system", "content": system_msg}, {"role": "user", "content": prompt}],
                                       temperature=temperature)
    response_text = response.output_text.strip().lower()

    #if 'function_call' in response.choices[0].message:
        #function_args = response.choices[0].message['function_call']['arguments']
        # Extract the expression
        #expression = function_args['expression']
       # result = scientific_calculator(expression)
        # to-do: send this result back as a 'function response' message in multi-turn dialogues.
    
    # Extract label and confidence from response
    # Accept "trivial", "nontrivial", or "trivial (confidence:...)" etc.
    label = "nontrivial"  # default
    conf = None
    if "trivial" in response_text and "nontrivial" not in response_text:
        label = "trivial"
    elif "nontrivial" in response_text:
        label = "nontrivial"

    # Extract confidence if given, e.g. "nontrivial (0.97 confidence)"
    conf_match = re.search(r'(\d\.\d{1,2})', response_text)
    if conf_match:
        conf = float(conf_match.group(1))
    else:
        # Optionally, set conservative confidence
        conf = 'unknown'

    return label, conf, response_text

def score_mathiness(formula_text):
    label, conf, llm_response = chatgpt_novelty_label(formula_text)
    return {"novelty_label": label, "confidence": conf, "llm_response": llm_response}

def batch_classify(data_path = "data/formula_novelty.json", ):
    # --- batch classify ---
    if os.path.exists(data_path):
        print(f"\nClassifying file: {data_path}\n")
        with open(data_path) as f:
            formulas = json.load(f)
        for entry in formulas:
            out = score_mathiness(entry["formula"])
            entry.update(out)
            print(f"{entry['formula']:<30} | {entry['novelty_label']:<10} | {entry['confidence']} | {entry['llm_response']}")
        with open("data/formula_novelty_labeled.json", "w") as f:
            json.dump(formulas, f, indent=2)