from __future__ import annotations
from pprint import pprint

from environment import Environment
from expr import *
from stmt import *
from tokens import Token, TokenType
from resolver import resolveStatements, Resolver
import libffi

class Interp:
    globals    : Environment
    environment: Environment
    # From resolver
    locals     : dict[Expr, int]

    def __init__(self):
        self.environment = Environment(None)
        self.globals     = self.environment

class LoxCallable:
    def arity(self) -> int:
        pass
    def call(self, interp: Interp, arguments: list[object]) -> object:
        pass


class LoxReturn(RuntimeError):
    value: object

    def __init__(self, value: object):
        self.value = value


class LoxInstance:
    klass: LoxClass
    fields: dict[str, object]

    def __init__(self, klass: LoxClass):
        self.klass  = klass
        self.fields = {}

    def __repr__(self):
        return f"<{self.klass.name} instance>"

    def get(self, name: Token) -> object:
        if name.lexeme in self.fields:
            return self.fields.get(name.lexeme)
        
        method: LoxFunction = self.klass.findMethod(name.lexeme)
        if method: 
            return method.bind(self)

        print(f"[interpreter-error] Undefined property `{name.lexeme}`")
        exit(1)

    def set(self, name: Token, value: object) -> None:
        self.fields[name.lexeme] = value


@dataclass
class LoxClass(LoxCallable):
    name: str
    methods: dict[str, LoxFunction]

    def __repr__(self):
        return f"<class `{self.name}`>"

    def arity(self) -> int:
        initializer: LoxFunction = self.findMethod("init")
        if initializer is None:
            return 0
        return initializer.arity()

    def call(self, interp: Interp, arguments: list[object]) -> object:
        instance: LoxInstance = LoxInstance(self)

        initializer: LoxFunction = self.findMethod("init")
        if initializer:
            initializer.bind(instance).call(interp, arguments)
        return instance

    def findMethod(self, name: str) -> LoxFunction:
        if name in self.methods.keys():
            return self.methods[name]

        return None

def interpret(stmts: list[Stmt]) -> None:
    interp = Interp()
    interp.globals.define("print", libffi.LoxPrint())


    resolver = Resolver()

    resolveStatements(resolver, stmts)

    interp.locals = resolver.resolutions.copy()
    pprint(interp.locals)

    for stmt in stmts:
        evaluate(interp, stmt)

def evaluate(interp: Interp, stmt: Stmt) -> object:
    if isinstance(stmt, Literal):
        return eval_literal(interp, stmt)
    elif isinstance(stmt, Unary):
        return eval_unary(interp, stmt)
    elif isinstance(stmt, Binary):
        return eval_binary(interp, stmt)
    elif isinstance(stmt, Grouping):
        return eval_grouping(interp, stmt)
    elif isinstance(stmt, Variable):
        return eval_variable(interp, stmt)
    elif isinstance(stmt, Assign):
        return eval_assign(interp, stmt)
    elif isinstance(stmt, Grouping):
        return eval_grouping(interp, stmt)
    elif isinstance(stmt, Logical):
        return eval_logical(interp, stmt)
    elif isinstance(stmt, Block):
        return eval_block_stmt(interp, stmt)
    elif isinstance(stmt, If):
        return eval_if_stmt(interp, stmt)
    elif isinstance(stmt, While):
        return eval_while_stmt(interp, stmt)
    elif isinstance(stmt, Var):
        return eval_var_stmt(interp, stmt)
    elif isinstance(stmt, Expression):
        return eval_expr_stmt(interp, stmt)
    elif isinstance(stmt, Return):
        return eval_return_stmt(interp, stmt)
    elif isinstance(stmt, Function):
        return eval_fun_stmt(interp, stmt)
    elif isinstance(stmt, Call):
        return eval_call_expr(interp, stmt)
    elif isinstance(stmt, Class):
        return eval_class_stmt(interp, stmt)
    elif isinstance(stmt, Get):
        return eval_get_expr(interp, stmt)
    elif isinstance(stmt, Set):
        return eval_set_expr(interp, stmt)
    elif isinstance(stmt, This):
        return eval_this_expr(interp, stmt)
    
    else:
        pprint(f"[interpreter-error] unimplemented expression:`{stmt}`")
        exit(1)


def eval_set_expr(interp: Interp, stmt: Set) -> object:
    object: object = evaluate(interp, stmt.object)
    if not isinstance(object, LoxInstance):
        print("[interpreter-error] Only instances have fields.")
        exit(1)

    value: object = evaluate(interp, stmt.value)
    object.set(stmt.name, value)
    return value

def eval_get_expr(interp: Interp, stmt: Get) -> object:
    object: object = evaluate(interp, stmt.object)
    if isinstance(object, LoxInstance):
        return object.get(stmt.name)

    print(f"[interpreter-error] only instances have properties: `{object}`")
    exit(1)

def eval_class_stmt(interp: Interp, stmt: Class) -> object:
    interp.environment.define(stmt.name.lexeme, None)

    methods: dict[str, LoxFunction] = {}
    for method in stmt.methods:
        fun: LoxFunction = LoxFunction(method, 
                                       interp.environment,
                                       method.name.lexeme == "init")
        methods[method.name.lexeme] = fun

    klass: LoxClass = LoxClass(stmt.name.lexeme, methods)
    interp.environment.assign(stmt.name, klass)
    return None

def eval_this_expr(interp: Interp, expr: This)  -> object:
    return interp.environment.get(expr.keyword)

def eval_call_expr(interp: Interp, expr: Call) -> object:
    callee: object = evaluate(interp, expr.callee)

    arguments: list[object] = []
    for argument in expr.arguments:
        arguments.append(evaluate(interp, argument))

    # NOTE(tyler): Python's `isinstance` is not working for ffis
    # so I'm removing the fucker. Not great for production code,
    # but this isn't production and I hate python, soo...

    # if not isinstance(callee, LoxCallable):
    #     print("[interpreter-error] Can only call functions. type: ", type(callee))
    #     exit(1)

    return callee.call(interp, arguments)

def eval_fun_stmt(interp: Interp, stmt: Function) -> None:
    fun: LoxFunction = LoxFunction(stmt, 
                                   interp.environment, 
                                   False)
    interp.environment.define(stmt.name.lexeme, fun)
    return None

def eval_return_stmt(interp: Interp, stmt: Return) -> None:
    value: object = None
    if stmt.value is not None:
        value = evaluate(interp, stmt.value)

    raise LoxReturn(value)

def eval_while_stmt(interp: Interp, stmt: While) -> None:
    while isTruthy(evaluate(interp, stmt.condition)):
        evaluate(interp, stmt.body)
    return None

def eval_if_stmt(interp: Interp, stmt: If) -> None:
    if isTruthy(evaluate(interp, stmt.condition)):
        evaluate(interp, stmt.thenBranch)
    elif stmt.elseBranch is not None:
        evaluate(interp, stmt.elseBranch)
    return None

def eval_block_stmt(interp: Interp, stmt: Block) -> None:
    execute_block(interp, stmt.statements, Environment(interp.environment))
    return None

def execute_block(interp: Interp, statements: list[Stmt], environment: Environment) -> None:
    previous: Environment = interp.environment

    try:
        interp.environment = environment

        for statement in statements:
            evaluate(interp, statement)
    finally:
        interp.environment = previous

def eval_var_stmt(interp: Interp, stmt: Var) -> None:
    value: object = None
    if stmt.initializer is not None:
        value = evaluate(interp, stmt.initializer)

    interp.environment.define(stmt.name.lexeme, value)
    return None

def eval_expr_stmt(interp: Interp, stmt: Expression) -> None:
    evaluate(interp, stmt.expression)
    return None

def eval_logical(interp: Interp, expr: Logical) -> object:
    left: object = evaluate(expr.left)

    if expr.operator.type == TokenType.OR:
        if isTruthy(left):
            return left
    else:
        if not isTruthy(left):
            return left

    return evaluate(interp, expr.right)

def eval_assign(interp: Interp, expr: Assign) -> object:
    value: object = evaluate(interp, expr.value)
    interp.environment.assign(expr.name, value)
    return value

def eval_variable(interp: Interp, expr: Variable) -> object:
    # Try to find in the environment stack
    return interp.environment.get(expr.name)


def eval_grouping(interp: Interp, expr: Grouping) -> object:
    return evaluate(interp, expr.expression)

def eval_binary(interp: Interp, expr: Binary) -> object:
    left : object = evaluate(interp, expr.left)
    right: object = evaluate(interp, expr.right)

    match expr.operator.type:
        case TokenType.GREATER:
            return float(left) > float(right)
        case TokenType.GREATER_EQUAL:
            return float(left) >= float(right)
        case TokenType.LESS:
            return float(left) < float(right)
        case TokenType.LESS_EQUAL:
            return float(left) <= float(right)
        case TokenType.EQUAL_EQUAL:
            return left == right
        case TokenType.BANG_EQUAL:
            return float(left) != float(right)
        case TokenType.MINUS:
            return float(left) - float(right)
        case TokenType.SLASH:
            return float(left) / float(right)
        case TokenType.STAR:
            return float(left) * float(right)
        case TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return float(left) + float(right)
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
        case _:
            print(f"[interpreter-error] unknown token type for binary expressions: `{expr.operator.lexeme}`")

def eval_unary(interp: Interp, expr: Unary) -> object:
    right: object = evaluate(interp, expr.expr)

    match expr.operator.type:
        case TokenType.MINUS:
            return -float(right)
        case TokenType.BANG:
            return not isTruthy(right)
        case _:
            print(f"[interpret-error] unknown unary operator: `{expr.operator.lexeme}`")
            exit(1)

def eval_literal(interp: Interp, expr: Literal) -> object:
    return expr.value


# Functions
@dataclass
class LoxFunction(LoxCallable):
    declaration  : Function
    closure      : Environment
    isInitializer: bool

    def arity(self) -> int:
        return len(self.declaration.params)

    def call(self, interp: Interp, arguments: list[object]) -> object:
        environment = Environment(self.closure)

        for i, param in enumerate(self.declaration.params):
            environment.define(self.declaration.params[i].lexeme,
                               arguments[i])

        try:
            execute_block(interp, 
                          self.declaration.body,
                          environment)
        except LoxReturn as rv:
            if self.isInitializer:
                return self.closure.gets("this")
            return rv.value

        # If the function name is "init", return
        # the class instance it refers to.
        if self.isInitializer:
            return self.closure.gets("this")

        return None

    def bind(self, instance: LoxInstance) -> LoxFunction:
        environment: Environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment,
                           self.isInitializer)
        

# ------------- Helpers

def stringify(obj: object) -> str:
    if obj is None:
        return "nil"
    if isinstance(obj, float):
        text: str = str(obj)
        if text.endswith(".0"):
            text = text[:-2]
        return text

    return str(obj)

def isEqual(a: object, b: object) -> bool:
    if a is None and b is None:
        return True
    if a is None:
        return False

    return a == b

def isTruthy(obj: object) -> bool:
    if obj is None:
        return False
    if isinstance(obj, bool):
        return obj

    return True


if __name__ == "__main__":
    from scanner import scan
    from parser import parse

    def readFile(path: str) -> str:
        f = open(path)
        c = f.read()
        f.close()
        return c
    
    source: str = readFile("tests/test-script.txt")
    tokens: list[Token] = scan(source)
    stmts: list[Stmt]   = parse(tokens)
    interpret(stmts)