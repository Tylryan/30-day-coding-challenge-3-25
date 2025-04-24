from __future__ import annotations

from tokens import Token, TokenType
from exprs import *


global parser

class Parser:
    index : int
    tokens: list[Token]

def parser_init(tokens: list[Token]):
    global parser
    parser = Parser()
    parser.tokens = tokens
    parser.index = 0
    parser.len = len(tokens)


def parse(tokens: list[Token]) -> list[Expr]:
    parser_init(tokens)

    exprs = []
    while is_at_end() == False:
        expr = parse_term()
        exprs.append(expr)

    return exprs


def parse_term() -> Expr:
    left: Expr = parse_fact()

    while matches(TokenType.PLUS, TokenType.MINUS):
        op: Token = prev()
        right: Expr = parse_fact()
        left = binop_init(left, op, right)

    return left

def parse_fact() -> Expr:
    left: Expr = parse_primary()

    while matches(TokenType.STAR, TokenType.SLASH):
        op: Token = prev()
        right: Expr = parse_primary()
        left = binop_init(left, op, right)

    return left

def parse_primary() -> Expr:
    
    if matches(TokenType.NUMBER):
        return lit_init(prev())

    print(f"[parser-error] unimplemented token: '{peek()}")
    exit(1)


def advance() -> bool:
    global parser
    parser.index+=1

def is_at_end() -> bool:
    eof = parser.tokens[parser.index].kind == TokenType.EOF
    past = parser.index >= parser.len

    if past or eof:
        return True

    return False

def peek() -> Token:
    if is_at_end() == True:
        return None
    return parser.tokens[parser.index]

def prev() -> Token:
    assert parser.index != 0
    return parser.tokens[parser.index - 1]

def check(kind: TokenType) -> bool:
    assert isinstance(kind, TokenType)
    if is_at_end():
        return False
    return peek().kind == kind

def matches(*kinds: TokenType) -> bool:
    for kind in kinds:
        if check(kind):
            advance()
            return True
    return False



if __name__ == "__main__":
    from scanner import scan
    tokens = scan("1 + 2 - 3")
    exprs = parse(tokens)
    [ expr_to_str(x) for x in exprs ]
