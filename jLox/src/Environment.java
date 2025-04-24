import java.util.HashMap;
import java.util.Map;

public class Environment {
    // Each time a new environment is created, it starts off
    // with nothing in it.
    private final Map<String, Object> values = new HashMap<>();
    final Environment enclosing;

    Environment() {
        enclosing = null;
    }

    Environment(Environment enclosing) {
        this.enclosing = enclosing;
    }


    void define(String name, Object value) {
        // Currently allows redeclaration of same variable.
        values.put(name, value);
    }

    // Given a distance from the current environment, a name, and a value,
    // assign the expression to the given name k environments back.
    void assignAt(int distance, Token name, Object value){
        ancestor(distance).values.put(name.lexeme, value);
    }

    void assign(Token name, Object value) {
        // If the current scope contains the variable,
        // assign the value to that variable.
        if (values.containsKey(name.lexeme)) {
            values.put(name.lexeme, value);
            return;
        }

        // Try assigning it to the parent environment
        // recursively.
        if (enclosing != null) {
            enclosing.assign(name, value);
            return;
        }

        // If the variable was not found in any scopes,
        // throw an error.
        throw new RuntimeError(name,
                String.format("Undefined variable '%s'.", name.lexeme));
    }

    // Given a variable name and a distance, return a variable
    // with that name located in an environment k hops back.
    Object getAt(int distance, String name){
        return ancestor(distance).values.get(name);
    }

    // Return the environment k hops back.
    Environment ancestor(int distance) {
        Environment environment = this;
        for (int i = 0; i < distance; i++ ){
            environment = environment.enclosing;
        }

        return environment;
    }
    Object get(Token name) {
        // Check the current scope/environment for the
        // variable.
        if (values.containsKey(name.lexeme)) {
            return values.get(name.lexeme);
        }

        // As long as the scope has a parent,
        // recursively try to find the value in
        // the parent environments.
        if (enclosing != null)
            return enclosing.get(name);

        // If variable was never found, throw an error.
        throw new RuntimeError(name, String.format("Undefined variable '%s'.", name.lexeme));
    }
}
