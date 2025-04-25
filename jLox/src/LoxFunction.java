import java.util.List;

public class LoxFunction implements LoxCallable {
    private final Stmt.Function declaration;
    private final Environment closure;
    private final boolean isInitializer;

    LoxFunction(Stmt.Function declaration,
                Environment closure,
                boolean isInitializer){
        this.declaration = declaration;
        this.closure = closure;
        this.isInitializer = isInitializer;
    }

    @Override
    public Object call(Interpreter interpreter, List<Object> arguments) {
        Environment environment = new Environment(closure);

        for (int i = 0; i < declaration.params.size(); i++) {
            environment.define(declaration.params.get(i).lexeme,
                    arguments.get(i));
        }

        try { interpreter.executeBlock(declaration.body, environment); }
        catch (Return returnValue) {
            if (isInitializer)
                return closure.getAt(0, "this");
            return returnValue.value;
        }

        // If the function == "init", just return "this"'s
        // instance.
        if (isInitializer)
            return closure.getAt(0, "this");
        return null;
    }

    /*
     * 1. Create a new environment where the functions parent
     *    is also a parent.
     * 2. Put the "this" LoxInstance in that new environment.
     * 3. Strip the declaration from the old Lox function (this
     *    current one) and place it in a new LoxFunction which
     *    shall be returned.
     * BREF: Temporarily putting { "this": LoxInstance } in the
     * function's scope.
     */
    LoxFunction bind(LoxInstance instance) {
        Environment environment = new Environment(closure);
        environment.define("this", instance);

        return new LoxFunction(declaration,
                environment,
                isInitializer);
    }

    @Override
    public int arity() {
        return declaration.params.size();
    }
}
