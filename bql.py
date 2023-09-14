import re
import csv

# Regular expression matching optional whitespace followed by a token
# (if group 1 matches) or an error (if group 2 matches).
TOKEN_RE = re.compile(r'\s*(?:([A-Za-z01()~∧∨→↔])|(\S))')

# Special token indicating the end of the input string.
TOKEN_END = '<end of input>'

def tokenize(s):
    """Generate tokens from the string s, followed by TOKEN_END."""
    for match in TOKEN_RE.finditer(s):
        token, error = match.groups()
        if token:
            yield token
        else:
            raise SyntaxError("Unexpected character {!r}".format(error))
    yield TOKEN_END

from collections import namedtuple

Constant = namedtuple('Constant', 'value')
Variable = namedtuple('Variable', 'name')
UnaryOp = namedtuple('UnaryOp', 'op operand')
BinaryOp = namedtuple('BinaryOp', 'left op right')

import operator
from string import ascii_lowercase, ascii_uppercase

# Tokens representing Boolean constants (0=False, 1=True).
CONSTANTS = '01'

# Tokens representing variables.
VARIABLES = set(ascii_lowercase) | set(ascii_uppercase)

# Map from unary operator to function implementing it.
UNARY_OPERATORS = {
    '~': operator.not_,
}

# Map from binary operator to function implementing it.
BINARY_OPERATORS = {
    '∧': operator.and_,
    '∨': operator.or_,
    '→': lambda a, b: not a or b,
    '↔': operator.eq,
}

def parse(s):
    """Parse s as a Boolean expression and return the parse tree."""
    tokens = tokenize(s)        # Stream of tokens.
    token = next(tokens)        # The current token.

    def error(expected):
        # Current token failed to match, so raise syntax error.
        raise SyntaxError("Expected {} but found {!r}"
                          .format(expected, token))

    def match(valid_tokens):
        # If the current token is found in valid_tokens, consume it
        # and return True. Otherwise, return False.
        nonlocal token
        if token in valid_tokens:
            token = next(tokens)
            return True
        else:
            return False

    def term():
        # Parse a <Term> starting at the current token.
        t = token
        if match(VARIABLES):
            return Variable(name=t)
        elif match(CONSTANTS):
            return Constant(value=(t == '1'))
        elif match('('):
            tree = disjunction()
            if match(')'):
                return tree
            else:
                error("')'")
        else:
            error("term")

    def unary_expr():
        # Parse a <UnaryExpr> starting at the current token.
        t = token
        if match('~'):
            operand = unary_expr()
            return UnaryOp(op=UNARY_OPERATORS[t], operand=operand)
        else:
            return term()

    def binary_expr(parse_left, valid_operators, parse_right):
        # Parse a binary expression starting at the current token.
        # Call parse_left to parse the left operand; the operator must
        # be found in valid_operators; call parse_right to parse the
        # right operand.
        left = parse_left()
        t = token
        if match(valid_operators):
            right = parse_right()
            return BinaryOp(left=left, op=BINARY_OPERATORS[t], right=right)
        else:
            return left

    def implication():
        # Parse an <Implication> starting at the current token.
        return binary_expr(unary_expr, '→↔', implication)

    def conjunction():
        # Parse a <Conjunction> starting at the current token.
        return binary_expr(implication, '∧', conjunction)

    def disjunction():
        # Parse a <Disjunction> starting at the current token.
        return binary_expr(conjunction, '∨', disjunction)

    tree = disjunction()
    if token != TOKEN_END:
        error("end of input")
    return tree

def evaluate(tree, env):
    """Evaluate the expression in the parse tree in the context of an
    environment mapping variable names to their values.

    """
    if isinstance(tree, Constant):
        return tree.value
    elif isinstance(tree, Variable):
        return env[tree.name]
    elif isinstance(tree, UnaryOp):
        return tree.op(evaluate(tree.operand, env))
    elif isinstance(tree, BinaryOp):
        return tree.op(evaluate(tree.left, env), evaluate(tree.right, env))
    else:
        raise TypeError("Expected tree, found {!r}".format(type(tree)))
    
def replace_logical_operators(input_string):
    # replace 'and', 'or', 'then', 'iff' with boolean operator characters
    pattern = r"(?<!['])\b(and|or|then|iff|not)\b(?!')(?=(?:[^']*'[^']*')*[^']*$)"
    operator_mapping = {
        'and': '∧',
        'or': '∨',
        'then': '→',
        'iff': '↔',
        'not': '~'
    }
    result = re.sub(pattern, lambda match: operator_mapping.get(match.group(0), match.group(0)), input_string)
    
    return result

def escape_parentheses_inside_quotes(input_string):
    # Escape parentheses inside single quotes for the split_statement function to work properly
    input_string = input_string + " "
    pattern = r"([^']+)\((?=[^']*' |$)"
    result = re.sub(pattern, r"\1\(", input_string)
    result = result[:-1]

    pattern = r"(\)([^')]*?)(?=[^']*'$|[^']*' ))"
    result = re.sub(pattern, r"\\\1", result)

    return result

def split_statement(input_string):
    # Split the input string into a list of strings, each containing a single proposition
    pattern = r"(?<![\\])[\(\)]|∧|∨|→|↔|~" # Matches boolean operators and non-escaped parentheses
    propositions = re.split(pattern, input_string)
    propositions = [x.strip() for x in propositions if x.strip()] # Remove empty strings and trim whitespace
    propositions = list(dict.fromkeys(propositions)) # Remove duplicates

    # Unscape parentheses
    propositions = [x.replace("\(", "(") for x in propositions]
    propositions = [x.replace("\)", ")") for x in propositions]

    return propositions

alphabet = "pqrstuvwxyzabcdefghijklmno"

def set_boolean_aliases(original_input, propositions):
    # Set boolean aliases for each proposition in the statement

    # Create a dictionary that maps each proposition to a letter of the alphabet, starting with 'a'
    alphabet_index = 0
    proposition_mapping = {}
    for proposition in propositions:
        proposition_mapping[alphabet[alphabet_index]] = proposition
        alphabet_index += 1
    
    # Replace each proposition with its corresponding letter
    statement = original_input
    for letter, proposition in proposition_mapping.items():
        statement = statement.replace(proposition, letter)

    # Replace each boolean operator with its corresponding symbol
    statement = replace_logical_operators(statement)

    return (statement, proposition_mapping)

def print_logo():
    print(
    """
    dP                dP 
    88                88 
    88d888b. .d8888b. 88 
    88'  `88 88'  `88 88 
    88.  .88 88.  .88 88 
    88Y8888' `8888P88 dP 
                88    
                dP    

    boolean query language

    """
    )

def main():
    print_logo()

    import glob
    print("Archivos .csv en directorio:")
    for file in glob.glob("**/*.csv", recursive=True):
        print(".\t" + file)

    file_path = input("\nInsertar ruta del archivo .csv\n> ")

    try:
        open(file_path)
    except:
        print("Error: No se pudo abrir el archivo")
        exit()

    with open(file_path) as csv_file:
        # Get header info
        csv_reader = csv.reader(csv_file, delimiter=',')
        header = next(csv_reader)
        print("\nCampos disponibiles:")
        field_indexes = {}
        for i in range(len(header)):
            print(str(i) + ".\t" + header[i])
            field_indexes[header[i]] = "row[" + str(i) + "]"

        # Get pickers
        pickers = input("\nInsertar formato de salida (ej. 0, 3, 4)\n> ")

        import random

        # Get the input string
        rand1 = random.randint(0, len(header) - 1)
        rand2 = random.randint(0, len(header) - 1)
        while rand1 == rand2:
            rand2 = random.randint(0, len(header) - 1)
        filters = input("\nInsertar filtros (ej. " + header[rand1] + " ?= 'regex' and " + header[rand2] + " != 'valor')\n> ")

        # Ask to save output to file
        save_output = input("\n¿Guardar salida en un archivo? (s/n)\n> ")
        if save_output == "s":
            output_name = input("\nInsertar nombre del archivo de salida\n> ")
            output_file = open(output_name, "w")

        # Format the input string
        formatted_input = escape_parentheses_inside_quotes(replace_logical_operators(filters))
        propositions = split_statement(formatted_input)
        statement, proposition_mapping = set_boolean_aliases(filters, propositions)

        # Format input propositions as python code
        l_equal_pattern = r"(\S+)\s*(?= ==| !=)"
        l_regex_pattern = r"(\S+)\s*(?= \?=)"
        r_pattern = r"(?<=(== |\?= )')[\s\S]+?(?=')"

        code_propositions = propositions[:]
        for i in range(len(code_propositions)):
            for j in range(len(header)):
                try:
                    if re.search(l_equal_pattern, code_propositions[i]).group(0) == header[j]:
                        code_propositions[i] = code_propositions[i].replace(header[j], field_indexes[header[j]])
                except: pass
                try:
                    if re.search(l_regex_pattern, code_propositions[i]).group(0) == header[j]:
                        field_index = field_indexes[header[j]]
                        r_val = str(re.search(r_pattern, code_propositions[i]).group(0))
                        code_propositions[i] = "re.search(r\"" + r_val + "\", " + field_index + ", re.IGNORECASE) is not None"
                except: pass

        proposition_mapping = {}
        for i in range(len(code_propositions)):
            proposition_mapping[alphabet[i]] = code_propositions[i]

        output = ""
        for picker in pickers.split(","):
            output += header[int(picker)] + ","
        print("\n" + output[:-1])
        if save_output == "s":
            output_file.write(output[:-1] + "\n")

        # Evaluate the statement for each row in the csv file
        for row in csv_reader:
            try:
                truth_mapping = {}
                for letter, proposition in proposition_mapping.items():
                    proposition_value = (eval(proposition_mapping[letter]))
                    truth_mapping.update({letter: proposition_value})
                answer = evaluate(parse(statement), truth_mapping)
                if answer == True:
                    output = ""
                    for picker in pickers.split(","):
                        if row[int(picker)] == "":
                            output += "null,"
                        elif "," in row[int(picker)]:
                            output += "\"" + row[int(picker)] + "\","
                        else:
                            output += row[int(picker)] + ","
                    print(output[:-1])
                    if save_output == "s":
                        output_file.write(output[:-1] + "\n")
            except: pass

if __name__ == '__main__':
    main()