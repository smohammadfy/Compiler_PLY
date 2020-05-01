from ply import yacc
import lexer
from errors import error
from ast import *
tokens = lexer.tokens
precedence = (
    ('left', 'LOR'),
    ('left', 'LAND'),
    ('nonassoc', 'GT', 'GTE', 'LT', 'LTE', 'EQ', 'NEQ'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MUL', 'DIVIDE'),
    ('right', 'UNARY'),
)

def p_program_empty(p):
    '''
    program : empty
    '''
    p[0] = Program(None)


def p_program(p):
    '''
    program : basicblock
    '''
    p[0] = Program(p[1])


def p_basicblock(p):
    '''
    basicblock : statements

    '''
    p[0] = p[1]


def p_statements(p):
    '''
    statements : statements statement
    '''
    p[0] = p[1]
    p[0].append(p[2])


def p_statements_1(p):
    '''
    statements : statement
    '''
    p[0] = Statements([p[1]])


def p_statement(p):
    '''
    statement : const_declaration
              |  var_declaration
              |  assign_statement
              |  print_statement
              |  if_statement
              |  if_else_statement
              |  while_statement
              |  return_statement
              |  func_call
              |  func_statement
    '''
    p[0] = p[1]


def p_if_statement(p):
    '''
    if_statement : IF expression LCURL basicblock RCURL
    '''
    p[0] = IfStatement(p[2], p[4], None, lineno=p.lineno(1))


def p_if_else_statement(p):
    '''
    if_else_statement : IF expression LCURL basicblock RCURL ELSE LCURL basicblock RCURL
    '''
    p[0] = IfStatement(p[2], p[4], p[8], lineno=p.lineno(1))


def p_while_statement(p):
    '''
    while_statement : WHILE expression LCURL basicblock RCURL
    '''
    p[0] = WhileStatement(p[2], p[4], lineno=p.lineno(1))


def p_func_call(p):
    '''
    func_call : ID LPAREN arguments RPAREN SEMI
    '''
    p[0] = FuncCall(p[1], p[3], lineno=p.lineno(1))


def p_arguments(p):
    '''
    arguments : argument
    '''
    p[0] = FuncCallArguments([p[1]])


def p_argument(p):
    '''
    argument : expression
    '''
    p[0] = p[1]


def p_arguments_1(p):
    '''
    arguments : arguments COMMA argument
              | empty
    '''
    if p[1] is None:
        return
    p[0] = p[1]
    p[0].append(p[3])


def p_parameter(p):
    '''
    parameter : ID typename
    '''
    p[0] = FuncParameter(p[1], p[2], None)


def p_parameters(p):
    '''
    parameters : parameter
    '''
    p[0] = FuncParameterList([p[1]])


def p_parameters_1(p):
    '''
    parameters : parameters COMMA parameter
            | empty
    '''
    if p[1] is None:
        return
    p[0] = p[1]
    p[0].append(p[3])


def p_func_statement(p):
    '''
    func_statement : FUNC ID typename LPAREN parameters RPAREN LCURL basicblock RCURL
    '''
    p[0] = FuncStatement(p[2], p[3], p[5], p[8], lineno=p.lineno(1))


def p_return_statement(p):
    '''
    return_statement : RETURN expression SEMI
    '''
    p[0] = ReturnStatement(p[2], lineno=p.lineno(1))


def p_const_declaration(p):
    '''
    const_declaration : CONST ID ASSIGN expression SEMI
    '''
    p[0] = ConstDeclaration(p[2], p[4], lineno=p.lineno(1))


def p_var_declaration(p):
    '''
    var_declaration : VAR ID typename SEMI
    '''
    p[0] = VarDeclaration(p[2], p[3], None, lineno=p.lineno(1))


def p_var_declaration_expr(p):
    '''
    var_declaration : VAR ID typename ASSIGN expression SEMI
    '''
    p[0] = VarDeclaration(p[2], p[3], p[5], lineno=p.lineno(1))


def p_assign_statement(p):
    '''
    assign_statement : location ASSIGN expression SEMI
    '''
    p[0] = AssignmentStatement(p[1], p[3], lineno=p.lineno(2))


def p_print_statement(p):
    '''
    print_statement : PRINT expression SEMI
    '''
    p[0] = PrintStatement(p[2], lineno=p.lineno(1))


def p_expression_unary(p):
    '''
    expression : PLUS expression %prec UNARY
               | MINUS expression %prec UNARY
               | NOT expression %prec UNARY
    '''
    p[0] = Unaryop(p[1], p[2], lineno=p.lineno(1))


def p_expression_binary(p):
    '''
    expression : expression PLUS expression
               | expression MINUS expression
               | expression MUL expression
               | expression DIVIDE expression
    '''
    p[0] = Binop(p[2], p[1], p[3], lineno=p.lineno(2))


def p_expression_rel(p):
    '''
    expression : expression GT expression
               | expression GTE expression
               | expression LT expression
               | expression LTE expression
               | expression EQ expression
               | expression NEQ expression
               | expression LAND expression
               | expression LOR expression
    '''
    p[0] = Relop(p[2], p[1], p[3], lineno=p.lineno(2))


def p_expression_group(p):
    '''
    expression : LPAREN expression RPAREN
    '''
    p[0] = p[2]


def p_expression_location(p):
    '''
    expression : location
    '''
    p[0] = LoadLocation(p[1], lineno=p[1].lineno)


def p_expression_literal(p):
    '''
    expression : literal
    '''
    p[0] = p[1]


def p_literal(p):
    '''
    literal : INTEGERNUMBER
            | FLOATNUMBER
            | STRING
            | BOOL
    '''
    p[0] = Literal(p[1], lineno=p.lineno(1))


def p_location(p):
    '''
    location : ID
    '''
    p[0] = Location(p[1], lineno=p.lineno(1))


def p_typename(p):
    '''
    typename : ID
    '''
    p[0] = Typename(p[1], lineno=p.lineno(1))


def p_empty(p):
    '''
    empty :
    '''

def p_error(p):
    if p:
        error(p.lineno, "Syntax error in input at token '%s'" % p.value)
    else:
        error("EOF", "Syntax error. No more input.")


def make_parser():
    parser = yacc.yacc()
    return parser


if __name__ == '__main__':
    import lexer
    import sys
    from errors import subscribe_errors
    lexer = lexer.make_lexer()
    parser = make_parser()
    tests = ["test1", "test2", "test3"]
    with subscribe_errors(lambda msg: sys.stdout.write(msg + "\n")):
        program = parser.parse((open(tests[1] + ".txt").read()), lexer, False)
        for depth, node in flatten(program):
            print("%s%s" % (" " * (4 * depth), node))

