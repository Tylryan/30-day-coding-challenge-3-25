from tokens import Token, TokenType
from exprs import *

class Interpreter:
    exprs: list[Expr]

global interpreter

def interpreter_init(exprs: list[Expr]) -> None:
    interpreter = Interpreter()
    interpreter.exprs = exprs


def interpret(exprs: list[Expr]) -> object:
    for expr in exprs:
        print(evaluate(expr))

def evaluate(expr: Expr) -> object:
    if is_lit(expr):
        return lit_eval(expr)
    elif is_binop(expr):
        return binop_eval(expr)

    else:
        print(f"[interpreter-error] unimplemented expression: `{expr_to_str(expr)}`")
        exit(1)


def lit_eval(expr: Expr) -> object:
    return expr.tok.literal
    

def binop_eval(expr: Expr) -> object:
    left = evaluate(expr.left)
    right = evaluate(expr.right)

    if expr.op.kind == TokenType.PLUS:
        return left + right
    elif expr.op.kind == TokenType.MINUS:
        return left - right
    elif expr.op.kind == TokenType.STAR:
        return left * right
    elif expr.op.kind == TokenType.SLASH:
        return left / right

    else:
        print(f"[interpreter-error] unimplemented binary operator: {expr.op.lexeme}")
        exit(1)



if __name__ == "__main__":
    from scanner import scan
    from parser import parse

    tokens: list[Token] = scan("1 + 2 * 3")
    exprs: list[Expr] = parse(tokens)
    interpret(exprs)