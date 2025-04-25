import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Interpreter implements Expr.Visitor<Object>, Stmt.Visitor<Object> {
    Environment globals = new Environment();
    Environment environment = globals;
    // this.locals contains AST nodes as the keys and the number
    // of environments away where they are.
    // { BinOp(Tok(+), Lit(1), Lit(2)) : 2 }
    final Map<Expr, Integer> locals = new HashMap<>();

    public Object evaluate(Expr expr) {
        return expr.accept(this);
    }
    public void execute(Stmt stmt) {
        stmt.accept(this);
    }

    // Literally just puts an expression and the hops away
    // it currently is in a new hashmap.
    public void resolve(Expr expr, int depth) {
        locals.put(expr, depth);
    }

    void interpret(List<Stmt> statements) {
        try {
            for (Stmt statement: statements){
                execute(statement);
            }
        } catch (RuntimeError error) {
            Lox.runtimeError(error);
        }
    }

    @Override
    public Object visitThisExpr(Expr.This expr) {
        return lookUpVariable(expr.keyword, expr);
    }

    @Override
    public Object visitSetExpr(Expr.Set expr) {
        Object object = evaluate(expr.object);

        if (!(object instanceof LoxInstance)) {
            throw new RuntimeError(expr.name,
                    "Only instances have fields.");
        }

        Object value = evaluate(expr.value);
        ((LoxInstance)object).set(expr.name, value);
        return value;
    }

    @Override
    public Object visitGetExpr(Expr.Get expr) {
        Object object = evaluate(expr.object);
        if (object instanceof LoxInstance) {
            return ((LoxInstance) object).get(expr.name);
        }

        throw new RuntimeError(expr.name,
                "Only instances have properties.");
    }
    // New
    @Override
    public Void visitClassStmt(Stmt.Class stmt){
        environment.define(stmt.name.lexeme, null);

        Map<String, LoxFunction> methods = new HashMap<>();

        for (Stmt.Function method : stmt.methods) {
            LoxFunction function = new LoxFunction(method,
                    environment,
                    method.name.lexeme.equals("init"));
            methods.put(method.name.lexeme, function);
        }

        LoxClass klass = new LoxClass(stmt.name.lexeme, methods);
        environment.assign(stmt.name, klass);
        return null;
    }

    @Override
    public Void visitReturnStmt(Stmt.Return stmt) {
        Object value = null;
        if (stmt.value != null) {
            value = evaluate(stmt.value);
        }
        throw new Return(value);
    }


    @Override
    public Void visitWhileStmt(Stmt.While stmt) {
        while (isTruthy(evaluate(stmt.condition))){
            execute(stmt.body);
        }

        return null;
    }

    @Override
    public Object visitFunctionStmt(Stmt.Function stmt) {
        LoxFunction function = new LoxFunction(stmt,
                environment,
                false);

        environment.define(stmt.name.lexeme, function);
        return null;
    }

    @Override
    public Object visitIfStmt(Stmt.If stmt) {
        if (isTruthy(evaluate(stmt.condition))) {
            execute(stmt.thenBranch);
        } else if (stmt.elseBranch != null) {
            execute(stmt.elseBranch);
        }
        return null;
    }

    public Void visitBlockStmt(Stmt.Block stmt) {
        executeBlock(stmt.statements, new Environment(environment));
        return null;
    }


    void executeBlock(List<Stmt> statements, Environment environment) {
        Environment previous = this.environment;

        try {
            this.environment = environment;

            for (Stmt statement : statements) {
                execute(statement);
            }
        } finally {
            this.environment = previous;
        }
    }
    // Variable Declarations
    @Override
    public Void visitVarStmt(Stmt.Var stmt) {
        Object value = null;

        if (stmt.initializer != null) {
            value = evaluate(stmt.initializer);
        }

        environment.define(stmt.name.lexeme, value);
        return null;
    }

    @Override
    public Void visitExpressionStmt(Stmt.Expression stmt) {
        evaluate(stmt.expression);
        return null;
    }

    @Override
    public Void visitPrintStmt(Stmt.Print stmt) {
        Object value = evaluate(stmt.expression);
        System.out.println(stringify(value));
        return null;
    }


    @Override
    public Object visitCallExpr(Expr.Call expr) {
        Object callee = evaluate(expr.callee);

        List<Object> arguments = new ArrayList<>();
        for (Expr argument : expr.arguments) {
            arguments.add(evaluate(argument));
        }

        if (!(callee instanceof LoxCallable)){
            throw new RuntimeError(expr.paren, "Can only call functions and classes.");
        }

        LoxCallable function = (LoxCallable) callee;

        return function.call(this, arguments);
    }

    @Override
    public Object visitLogicalExpr(Expr.Logical expr) {
        Object left = evaluate(expr.left);

        if (expr.operator.type == TokenType.OR) {
            if (isTruthy(left))
                return left;
        } else {
            if (!isTruthy(left))
                return left;
        }

        return evaluate(expr.right);
    }

    @Override
    public Object visitBinaryExpr(Expr.Binary expr) {
        Object left = evaluate(expr.left);
        Object right = evaluate(expr.right);

        switch (expr.operator.type) {
            case GREATER:
                return (double)left > (double)right;
            case GREATER_EQUAL:
                return (double)left >= (double)right;
            case LESS:
                return (double)left < (double)right;
            case LESS_EQUAL:
                return (double)left <= (double)right;
            case EQUAL_EQUAL: return isEqual(left, right);
            case BANG_EQUAL : return !isEqual(left, right);

            case MINUS:
                return (double)left - (double)right;
            case SLASH:
                return (double)left / (double)right;
            case STAR:
                return (double)left * (double)right;
            case PLUS:
                if (left instanceof Double && right instanceof Double) {
                    return (double)left + (double)right;
                }
                if (left instanceof String && right instanceof String) {
                    return (String)left + (String)right;
                }
                break;
        }

        // Unreachable
        return null;
    }

    @Override
    public Object visitAssignExpr(Expr.Assign expr) {
        Object value = evaluate(expr.value);

        Integer distance = locals.get(expr);
        // If distance was found statically, use it.
        if (distance != null){ environment.assignAt(distance, expr.name, value); }
        // Else, dynamically assign the expression globally at runtime.
        else { globals.assign(expr.name, value); }

        // environment.assign(expr.name, value); OLD
        return value;
    }

    // Variable References
    @Override
    public Object visitVariableExpr(Expr.Variable expr) {
        //return environment.get(expr.name); OLD
        return lookUpVariable(expr.name, expr);
    }

    @Override
    public Object visitLiteralExpr(Expr.Literal expr) {
        return expr.value;
    }

    @Override
    public Object visitUnaryExpr(Expr.Unary expr) {
        Object right = evaluate(expr.right);

        switch (expr.operator.type) {
            case MINUS:
                return -(double)right;
            case BANG:
                return !isTruthy(right);
        }

        // Unreachable
        return null;
    }

    @Override
    public Object visitGroupingExpr(Expr.Grouping expr) {
        return evaluate(expr.expression);
    }


    // ------------- HELPERS
    private Object lookUpVariable(Token name, Expr expr) {
        Integer distance = locals.get(expr);
        if (distance != null) { return environment.getAt(distance, name.lexeme); }
        // If no distance, then must be a global. Look this value up dynamically.
        // I.e. Dynamic Scoping for Global variables.
        else                  { return globals.get(name); }
    }
    private boolean isEqual(Object a, Object b) {
        if (a == null && b == null) return true;
        if (a == null) return false;

        return a.equals(b);
    }
    private boolean isTruthy(Object object) {
        if (object == null)
            return false;
        if (object instanceof Boolean)
            return (boolean)object;

        return true;
    }

    private String stringify(Object object) {
        if (object == null)
            return "nil";
        if (object instanceof Double){
            String text = object.toString();
            if (text.endsWith(".0")) {
                text = text.substring(0, text.length() - 2);
            }
            return text;
        }

        return object.toString();
    }
}
