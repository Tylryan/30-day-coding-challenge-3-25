
from tokens import Token, TokenType
from expr import *
from stmt import *

class ParseState:
    tokens : list[Token]
    current: int

    def __init__(self, tokens: list[Token]):
        self.tokens  = tokens
        self.current = 0


def parse(tokens: list[Token]) -> list[Stmt]:
    parser = ParseState(tokens)

    statements: list[Stmt] = []

    while not isAtEnd(parser):
        statements.append(declaration(parser))

    return statements


# --------- Statements
def declaration(parser: ParseState) -> Stmt:
    if matches(parser, TokenType.VAR):
        return varDeclaration(parser)
    if matches(parser, TokenType.FUN):
        return fun(parser)
    if matches(parser, TokenType.CLASS):
        return classDeclaration(parser)
    
    return statement(parser)

def statement(parser: ParseState) -> Stmt:
    if matches(parser, TokenType.LEFT_BRACE):
        return Block(block(parser))

    if matches(parser, TokenType.IF):
        return ifStatement(parser)
    
    if matches(parser, TokenType.WHILE):
        return whileStatement(parser)

    if matches(parser, TokenType.RETURN):
        return returnStatement(parser)

    return expressionStatement(parser)
    

def block(parser: ParseState) -> list[Stmt]:
    statements: list[Stmt] = []
    while not check(parser, TokenType.RIGHT_BRACE) and not isAtEnd(parser):
        statements.append(declaration(parser))

    consume(parser, TokenType.RIGHT_BRACE, "Expect '}' after block.")
    return statements


def classDeclaration(parser: ParseState) -> Stmt:
    name: Token = consume(parser, TokenType.IDENTIFIER, "Expect class name.")
    consume(parser, TokenType.LEFT_BRACE, "Expect '{' before class body.")

    methods: list[Function] = []

    while (not check(parser, TokenType.RIGHT_BRACE)) and (not isAtEnd(parser)):
        methods.append(fun(parser))

    consume(parser, TokenType.RIGHT_BRACE, "Expect '}' after class body.")
    return Class(name, methods)

def fun(parser: ParseState) -> Function:
    name: Token = consume(parser, TokenType.IDENTIFIER,
                          "Expect function name")
    consume(parser, TokenType.LEFT_PAREN, "Expect '(' after function name")

    parameters: list[Token] = []
    if not check(parser, TokenType.RIGHT_PAREN):
        parameters.append(consume(parser, TokenType.IDENTIFIER,
                                  "Expect parameter name"))
        
        while matches(parser, TokenType.COMMA):
            parameters.append(consume(parser, TokenType.IDENTIFIER,
                                    "Expect parameter name"))


    consume(parser, TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
    consume(parser, TokenType.LEFT_BRACE, "Expect '{' before function body.")

    body: list[Stmt] = block(parser)
    return Function(name, parameters, body)

def varDeclaration(parser: ParseState) -> Stmt:
    name: Token = consume(parser, TokenType.IDENTIFIER, "Expect variable name.")

    initializer: Expr = None

    if matches(parser, TokenType.EQUAL):
        initializer = expression(parser)


    consume(parser, TokenType.SEMICOLON, "Expect ';' after variable declaration")
    return Var(name, initializer)
    
    
def returnStatement(parser: ParseState) -> Stmt:
    keyword: Token = previous(parser)
    value: Expr = None

    if not check(parser, TokenType.SEMICOLON):
        value = expression(parser)

    consume(parser, TokenType.SEMICOLON, "Expect ';' after return value.")
    return Return(keyword, value)

def whileStatement(parser: ParseState) -> Expr:
    consume(parser, TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
    condition: Expr = expression(parser)
    consume(parser, TokenType.RIGHT_PAREN, "Expect ')' after while condition.")

    body: Stmt = statement(parser)
    return While(condition, body)

def ifStatement(parser: ParseState) -> Expr:
    consume(parser, TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
    cond: Expr = expression(parser)
    consume(parser, TokenType.RIGHT_PAREN, "Expect ')' after if condition.")

    thenBranch: Stmt = statement(parser)
    elseBranch: Stmt = None

    if matches(parser, TokenType.ELSE):
        elseBranch = statement(parser)
    return If(cond, thenBranch, elseBranch)

def expressionStatement(parser: ParseState) -> Expr:
    expr: Expr = expression(parser)
    consume(parser, TokenType.SEMICOLON, "Expect ';' after expression")
    return Expression(expr)

# ------- Expressions
def expression(parser: ParseState) -> Expr:
    return assignment(parser)

def assignment(parser: ParseState) -> Expr:
    expr: Expr = _or(parser)

    if matches(parser, TokenType.EQUAL):
        equals: Token = previous(parser)
        # Right Associative
        value: Expr = assignment(parser)

        # var a = value
        if isinstance(expr, Variable):
            name: Token = expr.name
            return Assign(name, value)
        # class.field = value
        elif isinstance(expr, Get):
            return Set(expr.object, expr.name, value)

        print("[parser-error] invalid assignment target: `{expr}`")
        exit(1)

    return expr

def _or(parser: ParseState) -> Expr:
    expr: Expr = _and(parser)

    while matches(parser, TokenType.OR):
        operator: Token = previous(parser)
        right: Expr = _and(parser)
        expr = Binary(expr, operator, right)

    return expr

def _and(parser: ParseState) -> Expr:
    expr: Expr = equality(parser)

    while matches(parser, TokenType.AND):
        operator: Token = previous(parser)
        right: Expr = equality(parser)
        expr = Binary(expr, operator, right)

    return expr

def equality(parser: ParseState) -> Expr:
    expr: Expr = comparison(parser)

    while matches(parser, 
                  TokenType.BANG_EQUAL, 
                  TokenType.EQUAL_EQUAL):

        operator: Token = previous(parser)
        right: Expr = comparison(parser)
        expr = Binary(expr, operator, right)

    return expr


def comparison(parser: ParseState) -> Expr:
    expr: Expr = term(parser)

    while matches(parser, 
                  TokenType.LESS, 
                  TokenType.LESS_EQUAL,
                  TokenType.GREATER,
                  TokenType.GREATER_EQUAL):

        operator: Token = previous(parser)
        right: Expr = term(parser)
        expr = Binary(expr, operator, right)

    return expr

def term(parser: ParseState) -> Expr:
    expr: Expr = factor(parser)

    while matches(parser, TokenType.PLUS, TokenType.MINUS):
        operator: Token = previous(parser)
        right: Expr = factor(parser)
        expr = Binary(expr, operator, right)
    return expr

def factor(parser: ParseState) -> Expr:
    expr: Expr = unary(parser)

    while matches(parser, TokenType.STAR, TokenType.SLASH):
        operator: Token = previous(parser)
        right: Expr = unary(parser)
        expr = Binary(expr, operator, right)
    return expr

def unary(parser: ParseState) -> Expr:
    if matches(parser, TokenType.BANG, TokenType.MINUS):
        operator: Token = previous(parser)
        # Right Associative recursion
        right: Expr = unary(parser)
        return Unary(operator, right)

    return call(parser)

def call(parser: ParseState) -> Expr:
    expr: Expr = primary(parser)

    def finishCall(parser: ParseState, callee: Expr) -> Expr:
        arguments: list[Expr] = []

        if not check(parser, TokenType.RIGHT_PAREN):
            arguments.append(expression(parser))
            while matches(parser, TokenType.COMMA):
                arguments.append(expression(parser))

        paren: Token = consume(parser, TokenType.RIGHT_PAREN,
                               "Expect ')' after arguments.")
        
        return Call(callee, paren, arguments)

    while True:
        if matches(parser, TokenType.LEFT_PAREN):
            expr = finishCall(parser, expr)
        elif matches(parser, TokenType.DOT):
            name: Token = consume(parser, TokenType.IDENTIFIER,
                                  "Expect property name after '.'.")
            expr = Get(expr, name)
        else:
            break

    return expr

def primary(parser: ParseState) -> Expr:
    if matches(parser, TokenType.FALSE): return Literal(False)
    if matches(parser, TokenType.TRUE) : return Literal(True)
    if matches(parser, TokenType.NIL)  : return Literal(None)

    if matches(parser, TokenType.NUMBER, TokenType.STRING):
        return Literal(previous(parser).literal)

    if matches(parser, TokenType.THIS):
        return This(previous(parser))

    if matches(parser, TokenType.IDENTIFIER):
        return Variable(previous(parser))

    if matches(parser, TokenType.LEFT_PAREN):
        expr: Expr = expression(parser)
        consume(parser, TokenType.RIGHT_PAREN, "Expect ')' after expression")
        return Grouping(expr)

    print(f"[parser-error] unimplemented primary token: `{peek(parser).lexeme}`")
    exit(1)

# ----------- HELPERS

def consume(parser, type: TokenType, message: str) -> Token:
    if check(parser, type):
        return advance(parser)
    print(f"[parser-error] {message}")
    exit(1)

def matches(parser, *types: TokenType) -> bool:
    for type in types:
        if check(parser, type):
            advance(parser)
            return True
    return False

def check(parser: ParseState, type: TokenType) -> bool:
    if isAtEnd(parser):
        return False

    return peek(parser).type == type
    
def advance(parser: ParseState) -> bool:
    if not isAtEnd(parser):
        parser.current+=1
    return previous(parser)

def isAtEnd(parser: ParseState) -> bool:
    return peek(parser).type == TokenType.EOF

def peek(parser: ParseState) -> Token:
    return parser.tokens[parser.current]

def previous(parser: ParseState) -> Token:
    return parser.tokens[parser.current - 1]



if __name__ == "__main__":
    from scanner import scan
    from pprint import pprint

    def readFile(path: str) -> str:
        f = open(path)
        c = f.read()
        f.close()
        return c

    source: str = readFile("tests/test-script.txt")
    tokens: list[Token] = scan(source)
    stmts : list[Stmt]  = parse(tokens)

    [pprint(x) for x in stmts]