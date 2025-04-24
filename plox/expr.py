
from tokens import Token, TokenType
from dataclasses import dataclass

class Expr:
    pass

@dataclass
class This(Expr):
    keyword: Token

    def __hash__(self):
        return hash(f"__builtin_this{self.keyword.line}")

@dataclass
class Set(Expr):
    object: object
    name  : Token
    value : Expr

@dataclass
class Get(Expr):
    object: object
    name  : Token

@dataclass
class Call(Expr):
    callee: Expr
    paren    : Token
    arguments: list[Expr]

    def __hash__(self):
        return hash(f"__builtin_call.{self.paren.line}")

@dataclass
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr

    def __hash__(self):
        return hash(f"__builtin_logical.{self.operator.line}")

@dataclass
class Assign(Expr):
    name: Token
    value: Expr

    def __hash__(self):
        return hash(f"__builtin_assign.{self.name.line}")

@dataclass
class Variable(Expr):
    name: Token

    def __repr__(self):
        return f"Variable({self.name.lexeme})"

    def __hash__(self):
        return hash(f"__builtin_variable.{self.name.line}")

@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def __hash__(self):
        return hash(f"__builtin_binary.{self.operator.line}")

@dataclass
class Grouping(Expr):
    expression: Expr

    def __hash__(self):
        # NOTE(tyler): Probably doesn't pass mustard
        return hash(f"__builtin_grouping")

@dataclass
class Literal(Expr):
    value: object

    def __hash__(self):
        # NOTE(tyler): Probably doesn't pass mustard
        return hash(f"__builtin_literal.{self.value}")

@dataclass
class Unary(Expr):
    operator: Token
    expr: Expr