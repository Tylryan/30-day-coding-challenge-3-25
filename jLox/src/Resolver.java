import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Stack;

public class Resolver implements Expr.Visitor<Void>, Stmt.Visitor<Void> {
    private final Interpreter interpreter;
    private final Stack<Map<String,Boolean>> scopes = new Stack<>();

    Resolver(Interpreter interpreter) {
        this.interpreter = interpreter;
    }

    void resolve(List<Stmt> statements) {
        for (Stmt statement: statements) {
            resolve(statement);
        }
    }
    private void resolve(Stmt stmt) {
        stmt.accept(this);
    }

    private void resolve(Expr expr) {
        expr.accept(this);
    }

    private void resolveLocal(Expr expr, Token name) {
        for (int i = scopes.size() - 1; i >= 0; i--){
            boolean scope_contains_name = scopes.get(i).containsKey(name.lexeme);
            if (scope_contains_name) {
                // Push the key to interpreter's local hashmap
                // and set the value to "how many hops away"
                // this scope is from whatever scope the
                // interpreter is.
                // { "my_var": 2 }
                int hops = scopes.size() - 1 - i;
                interpreter.resolve(expr, hops);
            }
        }
    }

    private void resolveFunction(Stmt.Function function) {
        beginScope();

        // Declare/Define parameters in the new scope.
        for (Token param : function.params) {
            declare(param);
            define(param);
        }

        // Recurse down to resolve(List<Stmt> statements)
        resolve(function.body);
        endScope();
    }

    // ----------- IMPORTANT VISITORS

    @Override
    public Void visitVarStmt(Stmt.Var stmt) {
        // Variable Declaration
        declare(stmt.name);
        if (stmt.initializer != null) {
            resolve(stmt.initializer);
        }
        define(stmt.name);
        return null;
    }


    @Override
    public Void visitVariableExpr(Expr.Variable expr) {
        // Variable Expressions

        // len(scopes) > 0 and last scope does not contain this variable.
        // This means we have declared it, but not defined it yet (null pointer?).
        if (!scopes.isEmpty() && scopes.peek().get(expr.name.lexeme) == Boolean.FALSE) {
            Lox.error(expr.name, "Can't read local variable in it's own initializer");
        }

        resolveLocal(expr, expr.name);
        return null;
    }

    @Override
    public Void visitAssignExpr(Expr.Assign expr) {
        resolve(expr.value);
        resolveLocal(expr, expr.name);
        return null;
    }

    @Override
    public Void visitFunctionStmt(Stmt.Function stmt) {
        declare(stmt.name);
        define(stmt.name);

        resolveFunction(stmt);
        return null;
    }

    @Override
    public Void visitBlockStmt(Stmt.Block stmt) {
        beginScope();
        resolve(stmt.statements);
        endScope();
        return null;
    }


    // -------------- Other Required Visitors
    @Override
    public Void visitCallExpr(Expr.Call expr) {
        resolve(expr.callee);

        for (Expr arg : expr.arguments) {
            resolve(arg);
        }
        return null;
    }

    @Override
    public Void visitLogicalExpr(Expr.Logical expr) {
        resolve(expr.left);
        resolve(expr.right);
        return null;
    }


    @Override
    public Void visitBinaryExpr(Expr.Binary expr) {
        resolve(expr.left);
        resolve(expr.right);
        return null;
    }

    @Override
    public Void visitGroupingExpr(Expr.Grouping expr) {
        resolve(expr.expression);
        return null;
    }

    @Override
    public Void visitLiteralExpr(Expr.Literal expr) {
        return null;
    }

    @Override
    public Void visitUnaryExpr(Expr.Unary expr) {
        resolve(expr.right);
        return null;
    }


    @Override
    public Void visitPrintStmt(Stmt.Print stmt) {
        resolve(stmt.expression);
        return null;
    }

    @Override
    public Void visitExpressionStmt(Stmt.Expression stmt) {
        resolve(stmt.expression);
        return null;
    }
    @Override
    public Void visitIfStmt(Stmt.If stmt) {
        resolve(stmt.condition);
        resolve(stmt.thenBranch);
        if (stmt.elseBranch != null)
            resolve(stmt.elseBranch);
        return null;
    }

    @Override
    public Void visitWhileStmt(Stmt.While stmt) {
        resolve(stmt.condition);
        resolve(stmt.body);
        return null;
    }


    @Override
    public Void visitReturnStmt(Stmt.Return stmt) {
        return null;
    }

    // ---------- HELPERS
    private void define(Token name){
        if (scopes.isEmpty())
            return;

        // Get the last scope and mark this
        // variable as true regardless of
        // if it was there or not before.
        scopes.peek().put(name.lexeme, true);
    }

    private void declare(Token name) {
        if (scopes.isEmpty())
            return;
        // Push this token name in the last scope
        Map<String, Boolean> scope = scopes.peek();
        scope.put(name.lexeme, false);
    }

    private void beginScope() {
        scopes.push(new HashMap<String, Boolean>());
    }

    private void endScope() {
        scopes.pop();
    }
}
