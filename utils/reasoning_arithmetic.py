# utils/reasoning_arithmetic.py

from utils.general_helpers import check_template_args
import sympy as sp

@check_template_args(['x', 'result'])
def equals_templates(x, result):
    return {
        "formulas": [
            f"{x} = {result}",
            f"{result} = {x}"],
        "explanation": (
            f"This is a direct assignment, meaning that {x} is defined to be exactly {result}."
            f" and {result} is defined to be exactly {x}.")}

@check_template_args(['x', 'y', 'result'])
def addition_templates(x, y, result):
    return {
        "formulas": [
            f"{x} + {y} = {result}",
            f"{x} = {result} - {y}",
            f"{y} = {result} - {x}"],
        "explanation": (
            f"The sum of {x} and {y} is {result}. This leads to three useful formulas:"
            f" {x} + {y} = {result} (basic sum)"
            f" {x} = {result} - {y} (solving for {x})"
            f" {y} = {result} - {x} (solving for {y})."
            " Addition is commutative; order does not matter.")}

@check_template_args(['x', 'y', 'result'])
def multiplication_templates(x, y, result):
    return {
        "formulas": [
            f"{x} * {y} = {result}",
            f"{x} = {result} / {y}",
            f"{y} = {result} / {x}"],
        "explanation": (
            f"The product of {x} and {y} is {result}. From this, you have:"
            f" {x} * {y} = {result} (basic multiplication)"
            f" {x} = {result} / {y} (solving for {x})"
            f" {y} = {result} / {x} (solving for {y})"
            " Multiplication is commutative; you can solve for any variable by dividing the result by the other.")}

@check_template_args(['x', 'y', 'result'])
def subtraction_templates(x, y, result):
    return {
        "formulas": [
            f"{x} - {y} = {result}",
            f"{x} = {result} + {y}",
            f"{y} = {x} - {result}"],
        "explanation": (
            f"The difference between {x} and {y} is {result}. Three useful formulas:"
            f" {x} - {y} = {result} (basic subtraction)"
            f" {x} = {result} + {y} (solving for {x})"
            f" {y} = {x} - {result} (solving for {y})."
            f" Subtraction is not commutative: {x} - {y} is not equal to {y} - {x} in general.")}

@check_template_args(['numerator', 'denominator', 'quotient'])
def division_templates(numerator, denominator, quotient):
    return {
        "formulas": [
            f"{numerator} / {denominator} = {quotient}",
            f"{numerator} = {quotient} * {denominator}",
            f"{denominator} = {numerator} / {quotient}"],
        "explanation": (
            f"{numerator} divided by {denominator} is {quotient}. "
            "You can rearrange:"
            f" {numerator} / {denominator} = {quotient} (basic division)"
            f" {numerator} = {quotient} * {denominator} (multiplying both sides by denominator)"
            f" {denominator} = {numerator} / {quotient} (solving for denominator, if quotient is not equal to 0)"
            f" Division is not commutative: {numerator} / {denominator} is not equal to {denominator} / {denominator} in general, and dividing by zero is undefined.")}

@check_template_args(['base', 'result'])
def squared_templates(base, result):
    return {
        "formulas": [
            f"{base}^2 = {result}",
            f"{base} * {base} = {result}",
            f"{base} = {result} / {base}",
            ],
        "explanation": (
            f"{base} squared is {result}."
            "You can rearrange:"
            f" {base}^2 = {result} (basic square root)"
            f" {base} * {base} = {result} (multiplying the base twice)"
            f" {base} = {result} / {base} (solving for base)"
            f" multiplying {base} by itself ({base} * {base}) equals {result}.")}

@check_template_args(['x', 'y'])
def divisible_templates(x, y):
    mod_formula = f"Mod({x}, {y}) = 0"
    return {
        "formulas": [
            f"{x} % {y} = 0 ({y}",
            f"{x} ≡ 0 (mod {y})",
            f"{x} = ({y} * k) for some integer 'k'",
            f"{y} | {x} ({x} divides {y})",
            mod_formula
            ],
        "explanation": (
            f"{x} is divisible by {y} means there exists an integer k such that {x} = {y}*k, or equivalently, the remainder when you divide {x} by {y} is 0 (i.e., {mod_formula})."
            f" {x} is divisible by {y} because {y} fits exactly into {x} {x//y} times (remainder 0)."
            " You can rearrange:"
            f" {x} % {y} = 0 (divides into {x} and leaves a remainder of 0)"
            f" {x} ≡ 0 (mod {y}) ({x} is congruent to 0 modulo {y})"
            f" {x} = ({y} * k) for some integer 'k' ({x} can be written as {y} times some integer k)"
            f" {y} | {x} ({x} divides {y})")}

@check_template_args(['x', 'y'])
def divides_templates(x, y):
    # x divides y means y % x == 0
    mod_formula = f"Mod({y}, {x}) = 0"
    return {
        "formulas": [
            f"{x} | {y}",
            f"{y} % {x} = 0",
            f"{y} ≡ 0 (mod {x})",
            f"{y} = ({x} * k) for some integer k",
            mod_formula,
        ],
        "explanation": (
            f"{x} divides {y} means there exists an integer k such that {y} = {x} * k, "
            f"or the remainder when you divide {y} by {x} is 0 (i.e., {mod_formula})."
            f"In other words: {x} fits exactly into {y} some number of times, with no remainder."
            "This property can be expressed in several mathematically equivalent ways:"
            f" {x} | {y} ({x} divides {y})"
            f" {y} % {x} = 0 (programming/modulus form)"
            f" {y} ≡ 0 (mod {x}) (modular arithmetic)"
            f" {y} = ({x} * k) for some integer k (definition of divisibility)"
            f" {mod_formula} (modulus in symbolic math)")}

@check_template_args(['x', 'y'])
def factor_templates(x, y):
    # x is a factor of y: equivalent to x divides y.
    mod_formula = f"Mod({y}, {x}) = 0"
    return {
        "formulas": [
            f"{x} is a x of {y}",
            f"{x} | {y}",
            f"{y} % {x} = 0",
            f"{y} ≡ 0 (mod {x})",
            f"{y} = ({x} * k) for some integer k",
            mod_formula,
        ],
        "explanation": (
            f"{x} is a x of {y} if there exists an integer k such that {y} = {x} * k,"
            f"meaning dividing {y} by {x} leaves no remainder (i.e., {mod_formula})."
            f"This can be written in several ways:"
            f" {x} is a x of {y}  (plain English)"
            f" {x} | {y} (divides notation)"
            f" {y} % {x} = 0 (modulus form)"
            f" {y} ≡ 0 (mod {x}) (modular arithmetic)"
            f" {y} = ({x} * k) for some integer k (equation definition)"
            f" {mod_formula} (symbolic math notation)")}

@check_template_args(['base', 'result'])
def cubed_templates(base, result):
    return {
        "formulas": [
            f"{base}^3 = {result}",
            f"{base} * {base} * {base} = {result}",
            f"{base} * {base} * {base} = {result}",
            f"{base} = cube root of {result}",
            f"{base} = cubert({result})",
            f"{base} = ∛{result}",
            f"{base} = {result}^(1/3)",
        ],
        "explanation": (
            f"{base} cubed is {result}, meaning you multiply {base} by itself three times."
            f"Common ways to write or interpret this:"
            f" {base}^3 = {result} (exponent notation)"
            f" {base} * {base} * {base} = {result} (repeated multiplication)"
            f" {base} = cube root of {result} (cube root form)"
            f" {base} = cubert({result}) (cube root form)"
            f" {base} = ∛{result} (cube root form)"
            f" {base} = {result}^(1/3) (fractional exponent cube root)"
            f" {result} = {base}^3 (assignment the other way)"
            f" Cubing a number means taking it to the third power: {base} * {base} * {base}.")}

@check_template_args(['base', 'exponent', 'result'])
def power_templates(base, exponent, result):
    return {
        "formulas": [
            f"{base}^{exponent} = {result}",
            f"{' * '.join([str(base)]*int(exponent))} = {result}" if str(exponent).isdigit() and int(exponent) > 1 else f"{base} raised to the {exponent} power = {result}",
            f"{base} = {result}^(1/{exponent})",
            f"log_{base}({result}) = {exponent}",
            f"{result} = {base}^{exponent}"
        ],
        "explanation": (
            f"{base} to the power of {exponent} is {result}, meaning multiply {base} by itself {exponent} times."
            f"Common ways to write or interpret this:"
            f" {base}^{exponent} = {result} (exponent notation)"
            f" {' * '.join([str(base)]*int(exponent))} = {result}" if str(exponent).isdigit() and int(exponent) > 1 else ""
            f" {base} = {result}^(1/{exponent}) (inverse: root form)"
            f" log_{base}({result}) = {exponent} (logarithmic equivalent)"
            f" {result} = {base}^{exponent} (assignment the other way)"
            " To raise a number to a power means multiplying it by itself as many times as the exponent specifies.")}


@check_template_args(['radicand', 'result'])
def sqrt_templates(radicand, result):
    return {
        "formulas": [
            f"sqrt({radicand}) = {result}",
            f"√{radicand} = {result}",
            f"{result}^2 = {radicand}",
            f"{result} * {result} = {radicand}",
            f"{result} = sqrt({radicand})",
            f"{result} = {radicand}^(1/2)",],
        "explanation": (
            f"The square root of {radicand} is {result}, meaning {result} multiplied by itself equals {radicand}."
            "This can be expressed in several equivalent ways:"
            f" sqrt({radicand}) = {result} (function notation)"
            f" square root of {radicand} = {result} (radical notation)"
            f" √{radicand} = {result} (radical notation)"
            f" {result}^2 = {radicand} (power equation)"
            f" {result} * {result} = {radicand} (multiplication form)"
            f" {result} = {radicand}^(1/2) (fractional exponent form)"
            "Finding the square root means finding a value whose square yields the original number.")}

@check_template_args(['radicand', 'result'])
def cbrt_templates(radicand, result):
    return {
        "formulas": [
            f"cbrt({radicand}) = {result}",
            f"∛{radicand} = {result}",
            f"{result}^3 = {radicand}",
            f"{result} * {result} * {result} = {radicand}",
            f"{result} = cbrt({radicand})",
            f"{result} = {radicand}^(1/3)"],
        "explanation": (
            f"The cube root of {radicand} is {result}, meaning {result} multiplied by itself three times equals {radicand}."
            "You can represent this in multiple ways:"
            f" cbrt({radicand}) = {result} (function notation)"
            f" ∛{radicand} = {result} (radical notation)"
            f" {result}^3 = {radicand} (cubed equation)"
            f" {result} * {result} * {result} = {radicand} (repeated multiplication)"
            f" {result} = {radicand}^(1/3) (fractional exponent)"
            "The cube root is the value which, multiplied by itself three times, gives back {radicand}.")}

@check_template_args(['degree', 'radicand', 'result'])
def root_templates(degree, radicand, result):
    return {
        "formulas": [
            f"{degree}th_root({radicand}) = {result}",
            f"root_{degree}({radicand}) = {result}",
            f"√[{degree}]{{{radicand}}} = {result}",
            f"{result}^{degree} = {radicand}",
            f"{result} * ... * {result} = {radicand}  (with {degree} factors)",
            f"{result} = {radicand}^(1/{degree})",
            f"{radicand} = {result}^{degree}",
            f"{result} = exp((1/{degree}) * ln({radicand}))"],
        "explanation": (
            f"The {degree}th root of {radicand} is {result}, meaning {result} to the power of {degree} gives {radicand}."
            "Common equivalent forms:"
            f" {degree}th_root({radicand}) = {result} (function notation)"
            f" root_{degree}({radicand}) = {result} (alternate function notation)"
            f" √[{degree}]{{{radicand}}} = {result} (radical n-th root notation)"
            f" {result}^{degree} = {radicand} (power equation)"
            f" {result} * ... * {result} = {radicand} (product: {result} appears {degree} times)"
            f" {result} = {radicand}^(1/{degree}) (fractional exponent form)"
            f" {result} = exp((1/{degree}) * ln({radicand})) (logarithmic form, for general computation)"
            "These are all valid representations for the root operation.")}

@check_template_args(['dividend', 'divisor', 'remainder'])
def remainder_templates(dividend, divisor, remainder):
    return {
        "formulas": [
            f"{dividend} % {divisor} = {remainder}",
            f"{dividend} mod {divisor} = {remainder}",
            f"{dividend} ≡ {remainder} (mod {divisor})",
            f"{dividend} = {divisor} * q + {remainder}  (where q is an integer quotient, 0 ≤ {remainder} < {divisor})",
            f"Mod({dividend}, {divisor}) = {remainder}"],
        "explanation": (
            f"The remainder when {dividend} is divided by {divisor} is {remainder}."
            "Equivalent forms:"
            f" {dividend} % {divisor} = {remainder} (modulus operator, programming)"
            f" {dividend} mod {divisor} = {remainder} (mathematics 'mod')"
            f" {dividend} ≡ {remainder} (mod {divisor}) (congruence notation: {dividend} and {remainder} leave the same remainder)"
            f" {dividend} = {divisor} * q + {remainder} (q integer, 0 ≤ {remainder} < {divisor}, division algorithm form)"
            f" Mod({dividend}, {divisor}) = {remainder} (symbolic math libraries)"
            f" The remainder is what's left after you remove as many full groups of {divisor} from {dividend} as possible, without going over.")}

@check_template_args(['x', 'y', 'result'])
def sum_of_two_primes_templates(x, y, result):
    return {
        "formulas": [
            f"{x} + {y} = {result}",
            f"{y} + {x} = {result}",  # commutative
            f"{x} = {result} - {y}",
            f"{y} = {result} - {x}",
            f"result = {x} + {y}"],
        "explanation": (
            f"Both {x} and {y} are prime numbers, and their sum is {result}."
            f" For any even {result} > 2, this relates to the famous Goldbach conjecture."
            f" You can write the sum as {x} + {y} = {result},"
            f" or solve for either prime: {x} = {result} - {y}, {y} = {result} - {x}."
            f" Both numbers must be prime for the relationship to count.")}

@check_template_args(['x', 'y'])
def twin_primes_templates(x, y):
    return {
        "formulas": [
            f"abs({x} - {y}) = 2",
            f"{x} = {y} + 2",
            f"{y} = {x} + 2",
            f"{x} - {y} = 2",
            f"{y} - {x} = 2",
            f"isprime({x}) and isprime({y})",
            f"({x}, {y}) are twin primes"],
        "explanation": (
            f"Twin primes are pairs of prime numbers that differ by exactly 2."
            f" For example, if {x} and {y} are twin primes:"
            f" abs({x} - {y}) = 2 (their difference is 2, regardless of order)"
            f" {x} = {y} + 2 or {y} = {x} + 2 (adjacent forms)"
            f" Both numbers must be prime: isprime({x}) and isprime({y})."
            " Well-known examples include (3, 5) or (11, 13)."
            " Twin primes often occur for small primes, but are less common for bigger numbers.")}

@check_template_args(['x', 'y', 'result'])
def prime_gap_templates(x, y, result):
    return {
        "formulas": [
            f"abs({x} - {y}) = {result}",
            f"{x} = {y} + {result}",
            f"{y} = {x} + {result}",
            f"{x} - {y} = {result}",
            f"{y} - {x} = {result}",
            f"{result} = |{x} - {y}|",
            f"isprime({x}) and isprime({y})"],
        "explanation": (
            f"A prime gap is the difference between two prime numbers. "
            f" For {x}, {y}: the gap is {result} if abs({x} - {y}) = {result}."
            f" Both numbers must be prime: isprime({x}) and isprime({y})."
            f" Either {x} = {y} + {result} or {y} = {x} + {result} are valid. "
            f" Prime gaps are often studied between consecutive primes.")}

def prime_factors_templates(result, factors=None):
    # Defensive: if factors is None or empty, clarify in message
    if not factors or len(factors) == 0:
        return {
            "formulas": [],
            "explanation": "Cannot construct: No prime factors provided."}
    # Build formulas (multiplicative, set, separate equations)
    mult_formula = " * ".join(str(i) for i in factors)
    set_formula = "{ " + ", ".join(str(i) for i in factors) + " }"
    return {
        "formulas": [
            f"{mult_formula} = {result}",
            f"{result} = " + " * ".join(str(i) for i in factors),
            f"Prime factors({result}) = {set_formula}",
            *(f"{result} is divisible by {i}" for i in factors),
            *(f"isprime({i})" for i in factors)],
        "explanation": (
            f"The prime factors of {result} are the prime numbers that multiply together to yield {result}."
            f" For {result}: {' * '.join(str(i) for i in factors)} = {result}."
            f" The set notation is Prime factors({result}) = {set_formula}."
            f" Each factor must be prime: " + ", ".join([f"isprime({x})" for x in factors]) + ".")}

@check_template_args(['n'])
def is_prime_templates(n):
    return {
        "formulas": [
            f"isprime({n}) = True",
            f"∀ d ∈ [2, ⎣√{n}⎦], {n} % d ≠ 0",
            f"{n} > 1 and only divisors of {n} are 1 and {n}",
            f"len([d for d in range(1, {n}+1) if {n} % d == 0]) == 2",
            f"∄ k ∈ ℕ, 1 < k < {n}, such that {n} % k == 0",
            f"π({n}) - π({n}-1) = 1",
            # Willans' formula (For completeness, though not practical to compute directly)
            f"primality by Willans' formula: floor((sin^2(π * (factorial({n}-1) + 1)/{n}))) == 0",
            "(j-1)! + 1 is divisible by j if and only if j is prime (for all j ≤ n)",
            "If n is composite, n = a * b for integers 1 < a, b < n"],
        "explanation": (
            f"{n} is prime if and only if its only positive divisors are 1 and itself."
            " Key facts and characterizations include:"
            " A prime number n has exactly two positive divisors: 1 and n."
            " No integer d with 1 < d < n divides n evenly (remainder 0)."
            " To check primality: test division by all integers up to ⎣√n⎦."
            " In programming: count the divisors of n—if exactly 2, then prime."
            " Using the Sieve of Eratosthenes or primality tests can validate larger numbers."
            " Special Characterizations:"
            " If (j-1)! + 1 is divisible by j, then j is prime (Wilson's theorem; for all j ≤ n)."
            " Willans' formula uses trigonometric and factorial expressions to characterize primes, though it is not practical for actual calculation."
            " The prime indication jump: π(n) - π(n-1) = 1, where π is the prime counting function."
            " Symbolically:"
            " isprime(n) == True means n is prime."
            " For a variable n, primality can't be checked until a value is given; use isprime(n) as a condition.")}

@check_template_args(['n'])
def is_not_prime_templates(n):
    return {
        "formulas": [
            f"isprime({n}) = False",
            f"∃ d ∈ [2, ⎣√{n}⎦], {n} % d == 0",
            f"{n} ≤ 1 or {n} has more than two divisors",
            f"len([d for d in range(1, {n}+1) if {n} % d == 0]) > 2",
            f"∃ a, b ∈ ℕ, 1 < a, b < {n}, such that {n} = a * b",
            # Willans' (refuted / failure case):
            f"primality by Willans' formula fails for {n} (not prime)",
            f"({n} - 1)! + 1 is not divisible by {n} (Wilson's theorem fails)"],
        "explanation": (
            f"{n} is not a prime number if it is ≤ 1, or it has any divisors other than 1 and itself."
            " Key facts and characterizations include:"
            " There exists an integer d (2 ≤ d ≤ ⎣√n⎦) such that n % d == 0."
            " n is composite if it can be written as n = a * b for integers 1 < a, b < n."
            " All even numbers greater than 2 are composite (not prime)."
            " Alternatively, if the number of divisors of n is more than 2, n is not prime."
            f" By Wilson's theorem: If ({n} - 1)! + 1 is NOT divisible by {n}, then {n} is not prime."
            " Willans' formula (based on floor/sine/factorials) will indicate non-primality for composite n."
            " Symbolically:"
            " isprime(n) == False means n is not prime."
            " For a variable n, not-primality can't be checked until a value is given; use isprime(n) as a rejection condition.")}

@check_template_args(['order'])
def prime_order_templates(order):
    order_str = str(order).lower()
    # Smallest prime order
    if order_str in ('smallest', 'first', '1'):
        return {
            "formulas": [
                "prime(1) = 2",
                "p₁ = 2",
                "nth_prime(1) = 2",
                "π(2) = 1",  # π(n): number of primes ≤ n — first prime is at π(2)
            ],
            "explanation": (
                "The smallest (first) prime number is always 2."
                "This is because 2 is the only even prime number and all other even numbers greater than 2 are not primes."
                "It is denoted prime(1) = 2 or p₁ = 2."
                "In the sequence of primes: 2, 3, 5, 7, 11, ... — prime(1) = 2.")}
    # Numeric order (n-th prime)
    elif order_str.isdigit():
        n = int(order_str)
        try:
            p = sp.prime(n)
            sequence_str = ", ".join(str(sp.prime(i)) for i in range(1, min(n+1,8)))
        except Exception:
            p = "?"
            sequence_str = "2, 3, 5, 7, 11, ..."
        return {
            "formulas": [
                f"prime({n}) = {p}",
                f"nth_prime({n}) = {p}",
                f"p_{{{n}}} = {p}",
                f"The sequence: {sequence_str}{', ...' if n > 7 else ''}"],
            "explanation": (
                f"The {n}th prime number is {p}."
                f" This is the prime that is {n}th in the ordered sequence of primes."
                f" To compute the nth prime programmatically, you can use libraries like sympy: `sympy.prime({n}) = {p}`."
                f" For reference, the beginning of the prime sequence is: {sequence_str}{', ...' if n>7 else ''}.")}
    # Symbolic argument
    else:
        return {
            "formulas": [
                f"prime({order})",
                f"nth_prime({order})",
                f"p_{{{order}}}",
                "The nth prime is the number in position n in the sequence of all primes."],
            "explanation": (
                f"The nth prime number, where n can be any positive integer, is written as prime(n), nth_prime(n), or pₙ."
                f" For example: prime(1) = 2, prime(2) = 3, prime(3) = 5, and so on."
                f" This remains symbolic until you specify the value of n.")}

@check_template_args(['x'])
def next_prime_templates(x, result):
    # If concrete value
    try:
        x_int = int(x)
        return {
            "formulas": [
                f"nextprime({x_int}) = {result}",
                f"p = min(prime > {x_int}) = {result}",
                f"{result} is the smallest prime number > {x_int}",
                f"isprime({result}) = True, and all n: {x_int} < n < {result} → isprime(n) = False"],
            "explanation": (
                f"The next prime after {x_int} is {result}."
                f" You find this by incrementing from {x_int} and checking each successive number for primality until you hit {result}."
                f" Formally, nextprime({x_int}) = {result}. This can be confirmed by checking isprime({result}) = True and that there are no primes between {x_int} and {result}.")}
    except Exception:
        # Symbolic x
        return {
            "formulas": [
                f"nextprime({x})",
                f"p = min(prime > {x})",
                f"{x}_1 = nextprime({x})",
                f"Find the smallest integer n > {x} such that isprime(n) = True"],
            "explanation": (
                f"The next prime after {x} is defined as the smallest prime greater than {x}."
                f" Symbolically: nextprime({x}) is the standard notation."
                f" To compute it, increment successive integers after {x} and check each for primality (isprime(n)). The first one found is nextprime({x}).")}
    

@check_template_args(['x'])
def where_is_prime_templates(x):
    # Try to resolve n to an integer, if possible
    try:
        n_val = int(x)
        # Get the nth prime
        prime_n = sp.prime(n_val)
        # Show sequence up to n for context (first 10 only, at most)
        sequence_str = ", ".join(str(sp.prime(i)) for i in range(1, min(n_val+1, 11)))
        return {
            "formulas": [
                f"prime({n_val}) = {prime_n}",
                f"nth_prime({n_val}) = {prime_n}",
                f"p_{{{n_val}}} = {prime_n}",
                f"{prime_n} is the {n_val}th prime",
                f"Primes up to index {n_val}: {sequence_str}"],
            "explanation": (
                f"The {n_val}th prime number is {prime_n}."
                f"This means that if you list all the prime numbers in order, the number {prime_n} sits at position {n_val}."
                f"The sequence of primes up to this position is:  {sequence_str}"
                " How to compute:"
                f" Use a mathematical library: `sympy.prime({n_val}) = {prime_n}`."
                f" List all primes in order and count up to the {n_val}th position."
                " In programming, the Sieve of Eratosthenes can efficiently list all primes up to a certain value, but for large n the 'prime-counting function' or prime approximation may be used."
                " Mathematical properties:"
                f" The nth prime is commonly denoted as pₙ or prime(n) or nth_prime(n)."
                f" For example, prime(1)=2, prime(2)=3, prime(3)=5, prime(4)=7, etc."
                " The sequence of primes grows rapidly; there are estimation formulas for the nth prime (e.g., n log n for large n, by the Prime Number Theorem),"
                " but for exact value, enumeration is required."
                " There is no known simple formula to jump directly to the nth prime for arbitrary n;"
                " all fast algorithms generate primes in order or use sieves up to a bound.")}
    except Exception:
        # Symbolic or variable n
        return {
            "formulas": [
                f"prime({x})",
                f"nth_prime({x})",
                f"p_{{{x}}}",
                "The nth prime number (n symbolic/variable).",
                "prime(1) = 2, prime(2) = 3, etc.",
                "prime(n) > n for all n > 1.",
                # Approximations:
                "prime(n) ~ n * log(n) (for large n; by the Prime Number Theorem)",
                "prime(n) < 2n log(n) for n ≥ 1 (Rosser's theorem)"],
            "explanation": (
                f"The nth prime number, written as prime({x}) or nth_prime({x}) or pₙ, refers to the prime in position n when all primes are listed in ascending order."
                " Example: prime(1) = 2, prime(2) = 3, prime(3) = 5, prime(4) = 7, etc."
                " For a symbolic n, this result remains unevaluated until n is given."
                " Estimates and Properties:"
                " It is known that prime(n) > n for all n > 1."
                " Approximate location: For large n, prime(n) ≈ n log(n), by the Prime Number Theorem."
                " Rosser's theorem gives bounds: n log(n) < prime(n) < 2n log(n) for n ≥ 1."
                " Computational notes:"
                " No closed-form formula for arbitrary n is known; numerical algorithms enumerate and count primes to reach the nth."
                " Symbolically, prime(n) defines the operation: Find the nth term in the ordered sequence of prime numbers."
                " Applications:"
                " Used in cryptography, combinatorics, theoretical computer science, and analytic number theory wherever specific primes are indexed or selected.")}
    
@check_template_args(['variables'])
def quadruplet_primes_templates(variables=None):
    if not variables or len(variables) != 4:
        return {"formulas": [], "explanation": "A prime quadruplet requires exactly 4 elements."}

    a, b, c, d = variables
    # Structure for prime quadruplets: [p, p+2, p+6, p+8]
    pattern = f"[{a}, {b}, {c}, {d}]"
    forms = [
        f"{a}, {b}, {c}, {d} are a prime quadruplet.",
        f"{a} = p", f"{b} = p + 2", f"{c} = p + 6", f"{d} = p + 8",
        f"Structure: [{a}, {b}, {c}, {d}] = [p, p+2, p+6, p+8]",
        f"isprime({a}) and isprime({b}) and isprime({c}) and isprime({d})",
        f"quadruplet = [{a}, {b}, {c}, {d}]",
        f"Spacing: {b}-{a}=2, {c}-{b}=4, {d}-{c}=2"]
    return {
        "formulas": forms,
        "explanation": (
            f"A prime quadruplet is a set of four primes in the precise pattern [p, p+2, p+6, p+8]."
            f" For quadruplet {pattern}:"
            f" {a}, {b}, {c}, {d} should all be prime numbers and"
            f" Their differences: {b}-{a}=2, {c}-{b}=4, {d}-{c}=2 (the tightest packing of four primes)"
            f"Common examples: [5, 7, 11, 13]; [11, 13, 17, 19]."
            " This is the densest possible prime constellation of 4 primes. Large prime quadruplets are rare, and their distribution is a subject of deep research in number theory."
            " To verify, check:"
            f" isprime({a}), isprime({b}), isprime({c}), isprime({d})"
            " Are the spacings exactly [2, 4, 2]?"
            f" Do they fit the form: p, p+2, p+6, p+8 for some integer p?")}

@check_template_args(['variables'])
def triplet_primes_templates(variables=None):
    if not variables or len(variables) != 3:
        return {"formulas": [], "explanation": "A prime triplet requires exactly 3 elements."}

    a, b, c = variables
    forms = [
        f"{a}, {b}, {c} are a prime triplet.",
        (f"Pattern: [{a}, {b}, {c}] = [t, t+2, t+6] or [t, t+4, t+6], spacings [2,4] or [4,2]"),
        f"isprime({a}) and isprime({b}) and isprime({c})",
        f"Spacing requirements: either ({b}-{a} = 2 and {c}-{b} = 4), or ({b}-{a} = 4 and {c}-{b} = 2)"]
    return {
        "formulas": forms,
        "explanation": (
            f"A prime triplet is the tightest possible cluster of three odd primes, either in the pattern [t, t+2, t+6] or [t, t+4, t+6]."
            f" For [{a}, {b}, {c}], this means the differences between primes must be [2,4] or [4,2], so the total spread is 6."
            f" Famous examples include [5,7,11] (gaps:2,4) and [7,11,13] (gaps:4,2)."
            f"Any three primes not matching one of those patterns (like [3,5,13]) are not considered a prime triplet."
            " To verify:"
            f" All values are prime."
            f" Spacings are either (2,4) or (4,2)."
            "Triplet primes are important in the study of maximal prime clustering and prime gap theory.")}

@check_template_args(['x', 'y'])
def diff_of_primes_templates(x, y):
    return {
        "formulas": [
            f"|{x} - {y}| = d",
            f"{x} - {y} = d or {y} - {x} = d (depending on which is larger)",
            f"d = |{x} - {y}| (where d is checked for primality: isprime(d))",
            f"isprime({x}), isprime({y}), isprime(|{x} - {y}|)",
            f"Check all: divisors of (|{x} - {y}|) == 2 ⇒ {x}, {y} are primes and their difference is prime",
            f"Difference test: If x, y are primes, their absolute difference can (sometimes) also be prime."],
        "explanation": (
            f"The difference between two primes x and y, written as |{x} - {y}|, can itself sometimes be a prime number."
            " To test this:"
            f"1. Ensure both {x} and {y} are prime numbers."
            f"2. Compute their absolute difference d = |{x} - {y}|."
            "3. Test if d is also prime: isprime(d)."
            " For instance:"
            " |13 - 5| = 8 (not prime)"
            " |13 - 11| = 2 (prime!)"
            " This template is sometimes used in studies of how prime gaps can themselves be prime, and relates to constructible prime constellations."
            " If you know one value (say, x) and want the other prime (y) to differ from x by a prime, you can solve for y:"
            " y = x ± p, (y = x plur or minus p) for some prime p."
            " Note: Not every pair of primes will yield a prime difference, but when it does (especially when the difference is 2), those are twin primes.")}

@check_template_args(['x', 'result'])
def prime_exclusion_zone_templates(x, result):
    forms = [
        f"Prime exclusion zone for {x}: {result}",
        f"pez({x}) = 2 * ({x} - 1) - {x}",
        f"{result} = 2 * ({x} - 1) - {x}",
        f"If {x} == 2, then pez(2) = 0 (minimum exclusion zone case)",
        f"For odd primes > 2: pez({x}) = 2{x} - 2 - {x} = {x} - 2"]
    return {
        "formulas": forms,
        "explanation": (
            f"The prime exclusion zone for {x} is a custom function that, for a prime number x, is calculated as pez({x}) = 2 * (x - 1) - x."
            " For the smallest prime, x = 2:"
            " pez(2) = 2 * (2 - 1) - 2 = 0"
            " For odd primes > 2:"
            " pez(x) = 2 * (x - 1) - x = x - 2 (the result is always even and smaller than x)"
            f" The value {result} defines a symmetric interval of 'possible exclusion': [x - pez(x), x + pez(x)]"
            " Intuition:"
            " This models a ring or halo around x where, by construction, certain divisibility/exclusion properties may hold (ex: based on divisibility or arithmetic constructions for nearby primes)."
            " For practical usage, you can also compute and show the actual exclusion zone interval for x:"
            " [x - pez(x), x + pez(x)]"
            " If x is not a prime number, the concept does not apply or is undefined."
            " This exclusion zone is a unique, user-defined concept meant to study neighborhoods around primes with particular arithmetic properties.")}

@check_template_args(['x', 'result1', 'result2'])
def prime_exclusion_zone_range_templates(x, result1, result2):
    formula_min = f"{x} - (2 * ({x} - 1) - {x})"
    formula_max = f"{x} + (2 * ({x} - 1) - {x})"
    interval_str = f"[{result1}, {result2}]"
    forms = [
        f"Prime exclusion range for {x}: {interval_str}",
        f"pez_range({x}) = ({formula_min}, {formula_max})",
        f"pez_min({x}) = {formula_min} = {result1}, pez_max({x}) = {formula_max} = {result2}",
        f"For x = 2: pez_range(2) = [0, 0] (the trivial case)",
        f"For primes > 2: The range is symmetric about {x}, extending pez({x}) units on either side."]
    return {
        "formulas": forms,
        "explanation": (
            f"The prime exclusion zone range for {x} defines an interval centered at {x},"
            f" spanning from {result1} to {result2}. This interval is given by:"
            f" [{result1}, {result2}] = [{x} - pez({x}), {x} + pez({x})],"
            f" where pez({x}) is the prime exclusion zone calculated as pez({x}) = 2 * ({x} - 1) - {x}."
            " Special case:"
            " If x = 2, the exclusion range collapses to [0, 0]."
            " Intuition:"
            " This range defines a 'halo' or neighborhood around the prime x where certain divisibility or structural exclusion properties may apply (as per your custom theory)."
            " For any prime larger than 2, the interval grows, remaining symmetric around x."
            " Use cases:"
            " Can be used to analyze the density or distribution of composites near primes."
            " May help model local 'gaps' or forbidden zones in advanced number theory questions.")}

@check_template_args(['x', 'order', 'local', 'result'])
def prime_exclusion_vals_templates(x, order, local, result):
    # Construct flexible summaries for order/local cases
    formulas = []
    # Overshoot/undershoot expressions by convention
    if str(order).lower() in ('furthest', 'largest', 'biggest', 'highest', 'second', 'last', 'final'):
        formulas.extend([
            f"Maximum prime exclusion {local}: {x} {'+' if local == 'overshoot' else '-'} pez({x}) = {result}",
            f"{result} = {x} {'+' if local == 'overshoot' else '-'} 2 * ({x} - 1) - {x}"])
        formulas.append("For x = 2, value is always 0 (no exclusion extension).")
    elif str(order).lower() in ('closest', 'smallest', 'nearest', 'lowest', 'first', 'beginning'):
        formulas.extend([f"Minimum prime exclusion {local}: {x} {'+' if local == 'overshoot' else '-'} 1 = {result}"])
        formulas.append("For x = 2, values are 1 or 3 (just outside the prime).")
    else:
        # Catchall description if order is symbolic
        formulas.extend([
            f"Prime exclusion value for {order} {local}: {result}",
            f"Formulas depend on chosen exclusion context (see long form in notes)."])
    return {
        "formulas": formulas,
        "explanation": (
            f"The '{order} {local}' prime exclusion value for {x} gives a special location relative to the prime and its exclusion zone."
            " Maximum/Minimum relates to the farthest or closest extension from x."
            " 'overshoot' means to the right (higher), 'undershoot' means to the left (lower)."
            f" For 'furthest' or 'maximum' with 'overshoot':"
            f" {x} + pez({x}) = {result}, where pez({x}) = 2 * ({x} - 1) - {x}"
            f" For 'furthest' or 'maximum' with 'undershoot':"
            f" {x} - pez({x}) = {result}"
            f" For 'closest' or 'minimum' ones:"
            f" {x} + 1 = {result} or {x} - 1 = {result} (just next to the prime)"
            " Special case: For x = 2, these values always resolve to 0 (no zone) or immediate neighbor values."
            " These values serve as boundary markers for your custom prime exclusion interval, marking the very edge 'just outside' the exclusion ring."
            " They may be useful for custom prime gap, neighborhood, or forbidden-zone models in advanced prime research.")}