from __future__ import annotations

from dataclasses import dataclass
from tokens import Token, TokenType
from expr import Expr, Variable

class Stmt:
    pass

@dataclass
class Expression(Stmt):
    expression: Expr 

@dataclass
class Return(Stmt):
    keyword: Token 
    value: Expr 

@dataclass
class Function(Stmt):
    name: Token 
    params: list[Token];
    body: list[Stmt]

@dataclass
class While(Stmt):
    condition: Expr 
    body: Stmt 

@dataclass
class If(Stmt):
    condition: Expr 
    thenBranch: Stmt 
    elseBranch: Stmt 

@dataclass
class Block(Stmt):
    statements: list[Stmt]

@dataclass
class Var(Stmt):
    name: Token 
    initializer: Expr 

@dataclass
class Print(Stmt):
    expression: Expr 

@dataclass
class Class(Stmt):
    name: Token 
    methods: list[Function]