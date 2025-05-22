import math

def scientific_calculator(expression: str) -> float:
    """
    Evaluate a scientific expression safely.
    Supports math functions (e.g., sin, cos, exp, log, pow).
    """
    allowed_names = math.__dict__.copy()
    allowed_names.update({'abs': abs, 'round': round})
    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return result
    except Exception as e:
        return str(e)
    
calculator_function = {
    "type": "function",
    "function": {
        "name": "scientific_calculator",
        "description": "Evaluates a scientific expression using math functions.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate (supports functions like sin, cos, log, etc.)"
                }
            },
            "required": ["expression"]
        }
    }
}