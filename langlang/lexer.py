from dataclasses import dataclass
from enum import StrEnum, Enum, auto
from pprint import pprint
from errors import perror
from tokens import Token, TKind


import re
import sys



@dataclass
class LexState:
    index: int
    line : int
    source: str
    tokens: list[Token]
    keywords: dict[str, TKind]
    def __init__(self, source: str):
        self.line   = 0
        self.index  = 0
        self.tokens = []
        self.source = source
        self.keywords = {
        "var"  : TKind.VAR,
        "fun"  : TKind.FUN,
        "return": TKind.RETURN,
        "if"   : TKind.IF,
        "else" : TKind.ELSE,
        "while": TKind.WHILE,
        "break": TKind.BREAK,
        "null" : TKind.NULL,
        "true" : TKind.TRUE,
        "false" : TKind.FALSE,
        "print": TKind.PRINT
    }


def lex(source: str):
    lexer = LexState(source)

    while at_end(lexer) is False:
        char: str = peek(lexer)
        if   char.isdigit(): push(lexer, number(lexer))
        elif char.isalpha(): push(lexer, identifier(lexer))
        elif '"' == char: push(lexer, string(lexer))
        elif "(" == char: push(lexer, Token(TKind.LPAR, char, None)); consume(lexer)
        elif ")" == char: push(lexer, Token(TKind.RPAR, char, None)); consume(lexer)
        elif "=" == char: push(lexer, equals(lexer))
        elif ">" == char: push(lexer, greater(lexer))
        elif "<" == char: push(lexer, less(lexer)); consume(lexer)
        elif "{" == char: push(lexer, Token(TKind.LBRACE, char, None)); consume(lexer)
        elif "}" == char: push(lexer, Token(TKind.RBRACE, char, None)); consume(lexer)
        elif ";" == char: push(lexer, Token(TKind.SEMI, char, None)); consume(lexer)
        elif "," == char: push(lexer, Token(TKind.COMMA, char, None)); consume(lexer)
        elif "." == char: push(lexer, Token(TKind.DOT, char, None)); consume(lexer)
        # TODO(tyler): Eventually this will extend to `--`.
        elif "-" == char: push(lexer, Token(TKind.MINUS, char, None)); consume(lexer)
        elif char in ["\n", "\r"]: lexer.line+=1; consume(lexer)
        elif char in [" ", "\t"]: consume(lexer)
        elif is_binop(char):
            res = binop(lexer)
            if res: push(lexer, res)
        else:
            perror(f"[lexer-error] unimplemented character: `{char}`")


    push(lexer, Token(TKind.EOF, "EOF", None))
    return lexer.tokens

def less(lexer: LexState) -> Token:
    consume(lexer)

    if peek(lexer) != "=":
        consume(lexer)
        return Token(TKind.LESS, "<", None)

    consume(lexer)
    return Token(TKind.LESS_EQUAL, "<=", None)

def greater(lexer: LexState) -> Token:
    consume(lexer)

    if peek(lexer) != "=":
        consume(lexer)
        return Token(TKind.GREATER, ">", None)

    consume(lexer)
    return Token(TKind.GREATER_EQUAL, ">=", None)

def equals(lexer: LexState) -> Token:
    consume(lexer)
    # Currently on "="
    if peek(lexer) != "=":
        return Token(TKind.EQUAL, "=", None)

    consume(lexer)
    return Token(TKind.EQUAL_EQUAL, "==", None)

def string(lexer: LexState) -> Token:
    consume(lexer)

    string = ""
    while '"' != peek(lexer):
        if at_end(lexer):
            perror(f"[lexer-error] unterminated string on line `{lexer.line}`")

        string += consume(lexer)


    consume(lexer)
    lexeme = f'{string}'

    return Token(TKind.STR, lexeme, string)

def identifier(lexer: LexState) -> Token:
    name = ""
    while re.match(r"[a-zA-Z_]+", peek(lexer)):
    #while peek(lexer).isalnum():
        name += consume(lexer)
    
    if name not in lexer.keywords:
        return Token(TKind.IDENT, name, None)

    # Then it's a keyword
    return Token(lexer.keywords[name], name, None)

def binop(lexer: LexState) -> Token | None:
    char = consume(lexer)
    if   char == '+': return Token(TKind.PLUS, char, None)
    elif char == '-': return Token(TKind.MINUS, char, None)
    elif char == '*': return Token(TKind.STAR, char, None)
    elif char == '%': return Token(TKind.MOD, char, None)
    elif char == '/': 
        next_char = peek(lexer)
        if next_char == "*": return comment(lexer)
        else               : return Token(TKind.SLASH, char, None)
    else: perror(f"[lexer-error] unimplemented binary operator: `{char}`")

def comment(lexer: LexState):
    # Should be at the "*"
    consume(lexer)

    while True:
        if at_end(lexer):
            perror(f"[lexer-error] unterminated comment")

        char = peek(lexer)
        next_char = peek_next(lexer)
        if next_char is None:
            perror(f"[lexer-error] unterminated comment")

        if char == "*" and next_char == "/":
            consume(lexer)
            consume(lexer)
            return

        consume(lexer)


def is_binop(char: str) -> bool:
    return char in ['+', '-', '*', '/', '%']

# Right now, it just deals with integers
def number(lexer: LexState) -> Token:
    # 100

    str_number: str = ""

    while at_end(lexer) is False and peek(lexer).isdigit():
        str_number += consume(lexer)

    if peek(lexer) != ".":
        return Token(TKind.INT, str_number, int(str_number))

    str_number += consume(lexer)

    while at_end(lexer) is False and peek(lexer).isdigit():
        str_number += consume(lexer)

    return Token(TKind.FLOAT, str_number, float(str_number))






def peek_at(lexer: LexState, offset: int) -> Token | None:
    if lexer.index + offset >= len(lexer.source):
        return None
    return lexer.source[lexer.index + offset]

def peek_next(lexer: LexState) -> Token | None:
    return peek_at(lexer, 1)

def peek(lexer: LexState):
    return lexer.source[lexer.index]

def consume(lexer: LexState) -> str:
    val = peek(lexer)
    lexer.index+=1
    return val

def at_end(lexer: LexState) -> bool:
    return lexer.index >= len(lexer.source)

# A shorter way to push tokens into the lexer.
def push(lexer: LexState, token: Token):
    lexer.tokens.append(token)


if __name__ == "__main__":

    if len(sys.argv) < 2:
        perror("[lexer-text] lexer requires a file to lex...")

    file_path = sys.argv[1]
    f = open(file_path)
    source = f.read()
    f.close()

    print("*"*75)
    print("\t" * 4 + "LEXER INPUT")
    print("*"*75)
    print(source)
    print("*"*75)
    print("\t" * 4 + "LEXER OUTPUT")
    print("*"*75)
    pprint(lex(source))
    print("*"*75)
    print("*"*75)
