from enum import Enum, auto
from stmt import *
from expr import *
from tokens import Token

class FunctionType(Enum):
    NONE     = auto()
    FUNCTION = auto()
    METHOD   = auto()

class Resolver:
    scopes         : list[dict[str, bool]]
    currentFunction: FunctionType
    resolutions    : dict[Expr, int]

    def __init__(self):
        self.scopes          = []
        self.currentFunction = FunctionType.NONE
        self.resolutions     = {}
    

def resolve(resolver: Resolver, stmt: Stmt | Expr) -> None:
    assert isinstance(resolver, Resolver)
    assert isinstance(stmt, Stmt | Expr)


    if isinstance(stmt, Var):
        resolveVarStmt(resolver, stmt)
    elif isinstance(stmt, Variable):
        resolveVariableExpr(resolver, stmt)
    elif isinstance(stmt, Function):
        resolveFunctionStmt(resolver, stmt)
    elif isinstance(stmt, Assign):
        resolveAssignExpr(resolver, stmt)
    elif isinstance(stmt, Block):
        resolveBlockStmt(resolver, stmt)
    elif isinstance(stmt, Call):
        resolveCallExpr(resolver, stmt)
    elif isinstance(stmt, Logical):
        resolveLogicalExpr(resolver, stmt)
    elif isinstance(stmt, Binary):
        resolveBinaryExpr(resolver, stmt)
    elif isinstance(stmt, Grouping):
        resolveGroupingExpr(resolver, stmt)
    elif isinstance(stmt, Literal):
        resolveLiteralExpr(resolver, stmt)
    elif isinstance(stmt, Unary):
        resolveUnaryExpr(resolver, stmt)
    elif isinstance(stmt, Expression):
        resolveExpressionStmt(resolver, stmt)
    elif isinstance(stmt, If):
        resolveIfStmt(resolver, stmt)
    elif isinstance(stmt, While):
        resolveWhileStmt(resolver, stmt)
    elif isinstance(stmt, Return):
        resolveReturnStmt(resolver, stmt)
    elif isinstance(stmt, Class):
        resolveClassStmt(resolver, stmt)
    elif isinstance(stmt, Get):
        resolveGetExpr(resolver, stmt)
    elif isinstance(stmt, Set):
        resolveSetExpr(resolver, stmt)
    elif isinstance(stmt, This):
        resolveThisExpr(resolver, stmt)
    else:
        print(f"[resolver-error] unimplemented expression: `{type(stmt)}`")
        exit(1)


def resolveLocal(resolver: Resolver, expr: Expr, name: Token) -> None:
    i =  len(resolver.scopes) - 1

    while i >= 0:
        contains_name = name.lexeme in resolver.scopes[i].keys()

        if contains_name:
            hops = len(resolver.scopes) -1 - i
            resolver.resolutions[expr] = hops
            return

        i-=1

def resolveFunction(resolver: Resolver, fun: Function, type: FunctionType) -> None:
    enclosingFunction: FunctionType = resolver.currentFunction
    resolver.currentFunction = type

    beginScope(resolver)

    for param in fun.params:
        declare(resolver, param)
        define(resolver, param)

    resolveStatements(resolver, fun.body)
    endScope(resolver)

    resolver.currentFunction = enclosingFunction

def resolveStatements(resolver: Resolver, statements: list[Stmt]) -> None:
    assert isinstance(resolver, Resolver)
    assert isinstance(statements, list)

    for stmt in statements:
        resolve(resolver, stmt)


def resolveVarStmt(resolver: Resolver, stmt: Var) -> None:
    declare(resolver, stmt.name)
    if stmt.initializer:
        resolve(resolver, stmt.initializer)

    define(resolver, stmt.name)
    return None


def resolveVariableExpr(resolver: Resolver, expr: Variable) -> None:

    idk = None
    if len(resolver.scopes) > 0:
        idk = resolver.scopes[-1].get(expr.name.lexeme)

    if resolver.scopes != [] and idk == False:
        print(f"[resolver-error] Can't read local variable in it's own initializer: `{expr.name.lexeme}`.")
        exit(1)

    resolveLocal(resolver, expr, expr.name)
    return None

def resolveAssignExpr(resolver: Resolver, expr: Assign) -> None:
    resolve(resolver, expr.value)
    resolveLocal(resolver, expr, expr.name)
    return None

def resolveSetExpr(resolver: Resolver, expr: Set) -> None:
    resolve(resolver, expr.value)
    resolve(resolver, expr.object)
    return None

def resolveGetExpr(resolver: Resolver, expr: Get) -> None:
    resolve(resolver, expr.object)
    return None

def resolveClassStmt(resolver: Resolver, stmt: Class) -> None:
    declare(resolver, stmt.name)
    define(resolver, stmt.name)

    beginScope(resolver)
    resolver.scopes[-1]["this"] = True

    for method in stmt.methods:
        declaration: FunctionType = FunctionType.METHOD
        resolveFunction(resolver, method, declaration)

    endScope(resolver)
    return None

def resolveThisExpr(resolver: Resolver, expr: This) -> None:
    resolveLocal(resolver, expr, expr.keyword)
    
def resolveFunctionStmt(resolver: Resolver, stmt: Function) -> None:
    declare(resolver, stmt.name)
    define(resolver, stmt.name)

    resolveFunction(resolver, stmt, FunctionType.FUNCTION)
    return None

def resolveBlockStmt(resolver: Resolver, stmt: Block) -> None:
    beginScope(resolver)
    resolveStatements(resolver, stmt.statements)
    endScope(resolver)

def resolveCallExpr(resolver: Resolver, expr: Call) -> None:
    resolve(resolver, expr.callee)

    for arg in expr.arguments:
        resolve(resolver, arg)

    return None

def resolveLogicalExpr(resolver: Resolver, expr: Logical) -> None:
    resolve(resolver, expr.left)
    resolve(resolver, expr.right)
    return None

def resolveBinaryExpr(resolver: Resolver, expr: Binary) -> None:
    resolve(resolver, expr.left)
    resolve(resolver, expr.right)

def resolveGroupingExpr(resolver: Resolver, expr: Grouping) -> None:
    resolve(resolver, expr.expression)
    return None

def resolveLiteralExpr(resolver, expr: Literal) -> None:
    return None

def resolveUnaryExpr(resolver: Resolver, expr: Unary) -> None:
    resolve(resolver, expr.right)
    return None

def resolveExpressionStmt(resolver: Resolver, stmt: Expression)  -> None:
    resolve(resolver, stmt.expression)
    return None

def resolveIfStmt(resolver: Resolver, stmt: If) -> None:
    resolve(resolver, stmt.condition)
    resolve(resolver, stmt.thenBranch)
    if stmt.elseBranch:
        resolve(resolver, stmt.elseBranch)
    return None

def resolveWhileStmt(resolver: Resolver, stmt: While) -> None:
    resolve(resolver, stmt.condition)
    resolveStatements(resolver, stmt.body)
    return None

def resolveReturnStmt(resolver: Resolver, stmt: Return) -> None:
    if resolver.currentFunction == FunctionType.NONE:
        print("[resolver-error] Can't return from top-level code.")
        exit(1)

    if stmt.value:
        resolve(resolver, stmt.value)

    return None





def define(resolver: Resolver, name: Token) -> None:
    if resolver.scopes == []:
        return

    resolver.scopes[-1][name.lexeme] = True

def declare(resolver: Resolver, name: Token) -> None:
    if resolver.scopes == []:
        return

    scope: dict[str, bool] = resolver.scopes[-1]

    if name.lexeme in scope:
        print("[resolver-error] Already a variable with this name.")

    resolver.scopes[-1][name.lexeme] = False

def beginScope(resolver: Resolver) -> None:
    resolver.scopes.append({})

def endScope(resolver: Resolver) -> None:
    resolver.scopes.pop()