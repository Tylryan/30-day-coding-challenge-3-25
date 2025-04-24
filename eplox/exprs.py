from __future__ import annotations
from tokens import Token


class Expr:
    pass


def lit_init(number: Token) -> Expr:
    assert isinstance(number, Token)
    lit_expr = Expr()
    lit_expr.kind = "Literal"
    lit_expr.tok = number
    return lit_expr


def binop_init(left: Expr, op: Token, right: Expr) -> Expr:
    binop_expr = Expr()
    binop_expr.kind  = "BinOp"
    binop_expr.left  = left
    binop_expr.op    = op
    binop_expr.right = right
    return binop_expr


def is_instance(expr: Expr, kind: str) -> bool:
    assert isinstance(expr, Expr)
    assert isinstance(kind, str)

    return expr.kind == kind

def is_binop(binop_expr: Expr) -> bool:
    assert isinstance(binop_expr, Expr)

    try: return binop_expr.kind == "BinOp"
    except AttributeError: return False

def is_lit(lit_expr: Expr) -> bool:
    assert isinstance(lit_expr, Expr)

    try: return lit_expr.kind == "Literal"
    except AttributeError: return False

def expr_to_str(expr: Expr) -> str:
    assert isinstance(expr, Expr)

    if is_lit(expr):
        return lit_to_str(expr)
    elif is_binop(expr):
        return binop_to_str(expr)

    try:
        print(f"Unimplemented expression: ", expr.kind)
    except Exception:
        print(f"[error] passed the wrong type. expected `expr`, found {type(expr)}")
        exit(1)

def binop_to_str(binop_expr: Expr) -> str:
    assert isinstance(binop_expr, Expr)

    left: str = expr_to_str(binop_expr.left)
    right: str = expr_to_str(binop_expr.right)
    return f"BinOp({left}, {binop_expr.op}, {right})"

def lit_to_str(lit_expr: Expr) -> str:
    assert isinstance(lit_expr, Expr)

    return str(lit_expr.tok.literal)



if __name__ == "__main__":
    from tokens import Token, TokenType

    one_tok = Token(TokenType.NUMBER, "1", 1, 1)
    two_tok = Token(TokenType.NUMBER, "2", 2, 1)
    plus_tok = Token(TokenType.PLUS, "+", None, 1)

    one = lit_init(one_tok)
    two = lit_init(two_tok)

    binop = binop_init(one, plus_tok, two)
    print(expr_to_str(binop))
