# loggers/provenance.py

import os
import json
from config.settings import PROVENANCE_FILE

def log_generation(candidates):
    with open(PROVENANCE_FILE, "a") as f:
        for cand in candidates:
            f.write(json.dumps({
                "method": cand.get('generation_method', 'unknown'),
                "note": cand.get('note', ''),
                "orig_sentence": cand.get('orig_sentence'),
                "step": cand.get('source_step'),
                # Add any more fields you want...
            }) + "\n")