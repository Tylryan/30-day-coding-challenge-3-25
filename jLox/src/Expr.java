import java.util.List;

abstract public class Expr {
    abstract <R> R accept(Visitor<R> visitor);
    interface Visitor<R> {
        R visitCallExpr(Call expr);
        R visitLogicalExpr(Logical expr);
        R visitAssignExpr(Assign expr);
        R visitBinaryExpr(Binary expr);
        R visitGroupingExpr(Grouping expr);
        R visitLiteralExpr(Literal expr);
        R visitUnaryExpr(Unary expr);
        R visitVariableExpr(Variable expr);
        R visitGetExpr(Get expr);
        R visitSetExpr(Set expr);
        R visitThisExpr(This expr);
    }

    static class This extends Expr {
        final Token keyword;

        This(Token keyword) {
            this.keyword = keyword;
        }

        <R> R accept(Visitor<R> visitor) {
            return visitor.visitThisExpr(this);
        }
    }

    static class Set extends Expr {
        final Expr object;
        final Token name;
        final Expr value;

        Set(Expr object, Token name, Expr value) {
            this.object = object;
            this.name = name;
            this.value = value;
        }

        <R> R accept(Visitor<R> visitor) {
            return visitor.visitSetExpr(this);
        }
    }

    static class Get extends Expr {
        final Expr object;
        final Token name;

        Get(Expr object, Token name) {
            this.object = object;
            this.name   = name;
        }

        <R> R accept(Visitor<R> visitor) {
            return visitor.visitGetExpr(this);
        }
    }
    static class Call extends Expr {
        final Expr callee;
        final Token paren;
        final List<Expr> arguments;

        Call(Expr callee, Token paren, List<Expr> arguments) {
            this.callee    = callee;
            this.paren     = paren;
            this.arguments = arguments;
        }

        <R> R accept(Visitor<R> visitor) {
            return visitor.visitCallExpr(this);
        }
    }

    static class Logical extends Expr {
        final Expr left;
        final Token operator;
        final Expr right;

        Logical(Expr left, Token operator, Expr right) {
            this.left     = left;
            this.operator = operator;
            this.right    = right;
        }

        <R> R accept(Visitor<R> visitor) {
            return visitor.visitLogicalExpr(this);
        }
    }
    static class Assign extends Expr {
        final Token name;
        final Expr value;

        Assign(Token name, Expr value) {
            this.name = name;
            this.value = value;
        }

        <R> R accept(Visitor<R> visitor) {
            return visitor.visitAssignExpr(this);
        }

        @Override
        public String toString() {
            return String.format("Assign(%s, %s)", name.lexeme, value);
        }
    }
    static class Variable extends Expr {
        final Token name;

        Variable(Token name) {
            this.name = name;
        }

        <R> R accept(Visitor<R> visitor) {
            return visitor.visitVariableExpr(this);
        }

        @Override
        public String toString() {
            return String.format("Variable(%s)", name.lexeme);
        }
    }
    static class Binary extends Expr {
        final Expr left;
        final Token operator;
        final Expr right;

        <R> R accept(Visitor<R> visitor) {
            return visitor.visitBinaryExpr(this);
        }

        Binary(Expr left, Token operator, Expr right) {
            this.left = left;
            this.operator = operator;
            this.right = right;
        }

        public String toString() {
            return String.format("Binary(%s, Token(%s), %s)",
                    left,
                    operator.lexeme,
                    right);
        }
    }

    static class Grouping extends Expr {
        final Expr expression;

        <R> R accept(Visitor<R> visitor) {
            return visitor.visitGroupingExpr(this);
        }
        Grouping(Expr expression) {
            this.expression = expression;
        }
    }

    static class Literal extends Expr {
        final Object value;

        <R> R accept(Visitor<R> visitor) {
            return visitor.visitLiteralExpr(this);
        }
        Literal(Object value) {
            this.value = value;
        }

        @Override
        public String toString() {
            return String.format("Literal(%s)", value.toString());
        }
    }

    static class Unary extends Expr {
        final Token operator;
        final Expr right;

        <R> R accept(Visitor<R> visitor) {
            return visitor.visitUnaryExpr(this);
        }

        Unary(Token operator, Expr right) {
            this.operator = operator;
            this.right = right;
        }
    }
}