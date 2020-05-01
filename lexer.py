import re
from errors import error
from ply.lex import lex

tokens = [
    'ID', 'CONST', 'VAR', 'PRINT', 'IF', 'ELSE', 'ELIF', 'WHILE', 'FUNC','MAIN',
    'RETURN', 'FLOAT', 'INTEGER', 'VOID',
    'PLUS', 'MINUS', 'MUL', 'DIVIDE', 'MOD',
    'ASSIGN', 'SEMI', 'LPAREN', 'RPAREN', 'COMMA',
    'INTEGERNUMBER', 'FLOATNUMBER', 'STRING', 'BOOL',
    'LT', 'GT', 'LTE', 'GTE', 'EQ', 'NEQ',
    'LAND', 'LOR', 'NOT',
    'LCURL', 'RCURL', 'LSB', 'RSB', 'ERROR',
]

t_ignore = ' \t\r'
t_PLUS = r'\+'
t_MOD = r'\%'
t_MINUS = r'-'
t_MUL = r'\*'
t_DIVIDE = r'/'
t_ASSIGN = r'='
t_SEMI = r';'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LT = r'\<'
t_GT = r'\>'
t_LTE = r'\<='
t_GTE = r'\>='
t_EQ = r'=='
t_NEQ = r'!='
t_LAND = r'&&'
t_LOR = r'\|\|'
t_NOT = r'!'
t_LCURL = r'\{'
t_RCURL = r'\}'
t_LSB = r'\['
t_RSB = r'\]'
t_COMMA = r','



def t_FLOATNUMBER(t):
    r'\d+[eE][-+]?\d+|(\.\d+|\d+\.\d+)([eE][-+]?\d+)?'
    t.value = float(t.value)  # Conversion to Python float
    return t


def t_INTEGERNUMBER(t):
    r'(\d+|0[Xx]\d)'
    # Conversion to a Python int

    if t.value.startswith(('0x', '0X')):
        t.value = int(t.value, 16)
    elif t.value.startswith('0'):
        t.value = int(t.value, 8)
    else:
        t.value = int(t.value)
    return t


def t_BOOL(t):
    r'(true|false)'
    mapping = {"true": True, "false": False}
    t.value = mapping[t.value]
    return t


def _replace_escape_codes(t):
    literals = {
        r"\\n": "\n",
        r"\\r": "\r",
        r"\\t": "\t",
        r"\\\\": r"\\",
        r'\\"': r'"'
    }
    re_byte = r".*\\b(?P<val>[0-9a-fA-F]{2}).*"
    byte_pat = re.compile(re_byte)
    for pattern, repl in literals.items():
        t.value = re.sub(pattern, repl, t.value)
    matcher = byte_pat.match(t.value)
    if matcher:
        val = matcher.groupdict()["val"]
        val = chr(int(val, 16))
        t.value = re.sub(re_byte[2:-2], val, t.value)
    if False:
        error(t.lexer.lineno, "Bad string escape code '%s'" % escape_code)


def t_STRING(t):
    r'\".*?\"'
    t.value = t.value[1:-1]
    _replace_escape_codes(t)
    return t

keywords = {"var", "const", "print",
            "if", "else", "while",
            "func", "return", "float", "int", "void",
            "main", "elif"}

def t_ID(t):
    r'[_A-Za-z][_A-Za-z0-9]*'
    if t.value in keywords:
        t.type = t.value.upper()
    return t

def t_newline(t):
    r'\n'
    t.lexer.lineno += len(t.value)


def t_COMMENT(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')


def t_CPPCOMMENT(t):
    r'//.*\n'
    t.lexer.lineno += 1


def t_error(t):
    error(t.lexer.lineno, "Illegal character %r" % t.value[0])
    t.lexer.skip(1)


def t_COMMENT_UNTERM(t):
    r'/\*(.|\n)*$'
    error(t.lexer.lineno, "Unterminated comment")


def t_STRING_UNTERM(t):
    r'\"(\.|.)*?\n'
    error(t.lexer.lineno, "Unterminated string literal")
    t.lexer.lineno += 1


def make_lexer():
    return lex()


if __name__ == '__main__':
    import sys
    from errors import subscribe_errors
    tests = ["test1", "test2", "test3"]
    resault = []
    lexer = make_lexer()
    with subscribe_errors(lambda msg: sys.stderr.write(msg + "\n")):
        for test in tests:
            lexer.input(open(test + ".txt").read())
            for tok in iter(lexer.token, None):
                resault.append(tok)
            f = open(test + "res.txt", "w+")
            print("\n------------------****" + "\t" + test + "\t" + "****------------------\n")
            for res in resault:
                f.write(str(res) + "\n")
                print(res)
            f.close()
