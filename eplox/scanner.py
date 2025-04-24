
from tokens import Token, TokenType

class ScannerState:
    source: str
    tokens: list[Token]

    start: int
    current: int

    keywords: dict[str, TokenType] = {
        "and"   : TokenType.AND,
        "class" : TokenType.CLASS,
        "else"  : TokenType.ELSE,
        "false" : TokenType.FALSE,
        "for"   : TokenType.FOR,
        "fun"   : TokenType.FUN,
        "if"    : TokenType.IF,
        "or"    : TokenType.OR,
        "return": TokenType.RETURN,
        "super" : TokenType.SUPER,
        "this"  : TokenType.THIS,
        "true"  : TokenType.TRUE,
        "var"   : TokenType.VAR,
        "while" : TokenType.WHILE,
        "nil"   : TokenType.NIL
    }

    def __init__(self, source: str):
        self.source  = source
        self.tokens  = []
        self.start   = 0
        self.current = 0
        self.line    = 1


def scan(source: str):
    scanner = ScannerState(source)

    while not isAtEnd(scanner):
        scanner.start = scanner.current
        scanToken(scanner)

    scanner.tokens.append(Token(TokenType.EOF, "", None, scanner.line))
    return scanner.tokens

def scanToken(scanner: ScannerState):
    c: str = advance(scanner)

    if c == "(": addToken(scanner, TokenType.LEFT_PAREN)
    elif c == ")": addToken(scanner, TokenType.RIGHT_PAREN)
    elif c == "{": addToken(scanner, TokenType.LEFT_BRACE)
    elif c == "}": addToken(scanner, TokenType.RIGHT_BRACE)
    elif c == ",": addToken(scanner, TokenType.COMMA)
    elif c == ".": addToken(scanner, TokenType.DOT)
    elif c == "-": addToken(scanner, TokenType.MINUS)
    elif c == "+": addToken(scanner, TokenType.PLUS)
    elif c == ";": addToken(scanner, TokenType.SEMICOLON)
    elif c == "*": addToken(scanner, TokenType.STAR)
    elif c == "!": 
        tokenType = TokenType.BANG
        if matches(scanner, "="):
            tokenType = TokenType.BANG_EQUAL
        addToken(scanner, tokenType)
    elif c == "=": 
        tokenType = TokenType.EQUAL
        if matches(scanner, "="):
            tokenType = TokenType.EQUAL_EQUAL
        addToken(scanner, tokenType)
    elif c == "<": 
        tokenType = TokenType.LESS
        if matches(scanner, "="):
            tokenType = TokenType.LESS_EQUAL
        addToken(scanner, tokenType)
    elif c == ">": 
        tokenType = TokenType.GREATER
        if matches(scanner, "="):
            tokenType = TokenType.GREATER_EQUAL
        addToken(scanner, tokenType)

    elif c == "/":
        if (matches(scanner, "/")):
            while peek(scanner) != '\n' and not isAtEnd(scanner):
                advance(scanner)
        else:
            addToken(scanner, TokenType.SLASH)
    elif c in [" "]:
        pass
    elif c == "\n":
        scanner.line+=1
    elif c == '"':
        string(scanner)
    else:
        if isDigit(c):
            number(scanner)
        elif isAlpha(c):
            identifier(scanner)
        else:
            print(f"unexpected character: '{c}'")
            exit(1)


def identifier(scanner: ScannerState) -> None:
    while isAlphaNumeric(peek(scanner)):
        advance(scanner)

    text: str = scanner.source[scanner.start: scanner.current]
    type: TokenType  = scanner.keywords.get(text)

    if type == None:
        type = TokenType.IDENTIFIER

    addToken(scanner, type)

def number(scanner: ScannerState) -> None:
    while isDigit(peek(scanner)):
        advance(scanner)

    if peek(scanner) == "." and isDigit(peekNext(scanner)):
        advance(scanner)

        while isDigit(peek(scanner)):
            advance(scanner)

    text: str = scanner.source[scanner.start: scanner.current]
    _addToken(scanner, TokenType.NUMBER, float(text))

    
def string(scanner: ScannerState) -> None:
    while peek(scanner) != '"' and not isAtEnd(scanner):
        if peek(scanner) == "\n":
            scanner.line+=1
        advance(scanner)

    if isAtEnd(scanner):
        print("[scanner-error] unterminated string.")
        exit(1)

    advance(scanner)

    value: str = scanner.source[scanner.start + 1: scanner.current - 1]
    _addToken(scanner, TokenType.STRING, value)

def isDigit(c : str) -> bool:
    return c >= '0' and c <= '9'

def isAlpha(c: str) -> bool:
    return (c >= 'a' and c <= 'z') or\
           (c >= 'A' and c <= 'Z') or\
           (c == '_') or\
           (c in ["?"])

def isAlphaNumeric(c: str) -> bool:
    return isDigit(c) or isAlpha(c)

def addToken(scanner: ScannerState, type: TokenType ):
    _addToken(scanner,type, None)

def _addToken(scanner: ScannerState, type: TokenType,  literal: object) -> None:
    text: str = scanner.source[scanner.start: scanner.current]
    scanner.tokens.append(Token(type, text, literal, scanner.line))

def matches(scanner: ScannerState, expected: str) -> bool:
    if isAtEnd(scanner):
        return False
    if scanner.source[scanner.current] != expected:
        return False
    scanner.current+=1
    return True

def advance(scanner: ScannerState) -> str:
    current = scanner.current
    scanner.current+=1
    return scanner.source[current]

def peek(scanner: ScannerState) -> str:
    if isAtEnd(scanner):
        return "\0"
    return scanner.source[scanner.current]

def peekNext(scanner: ScannerState) -> str:
    if scanner.current + 1 >= len(scanner.source):
        return '\0'
    return scanner.source[scanner.current + 1]

def isAtEnd(scanner: ScannerState) -> bool:
    return scanner.current >= len(scanner.source)


if __name__ == "__main__":
    import sys
    path = sys.argv[1]

    def read_file(path: str) -> str:
        f = open(path)
        contents: str = f.read()
        f.close()
        return contents

    source = read_file(path)
    tokens: list[Token] = scan(source)

    [print(x) for x in tokens]