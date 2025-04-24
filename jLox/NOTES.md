# Crafting Interpreters
I'm reading Crafting Interpreters by Robert Nystrom to learn
how to implement programming languages. The book can be found in
various versions [here](https://craftinginterpreters.com/) and the
source code (which also includes the book) can be found 
[here](https://github.com/munificent/craftinginterpreters).

All rights to him, these are just my notes.


# Chapter 6: Parser
> There are evidently several methods of parsing. The book
> uses Recursive Descent. Below are a few other parsing
> techniques:
> 1. LL(k)
> 2. LR(1)
> 3. LALR
> 4. Parser Combinators
> 5. Earley Parser
> 6. Shunting Yard Algorithm
> 7. Packrat Parser

The parser produces a Tree structure that represents the order code 
should be evaluated in, in reverse.

So the precedence level chart below is actually the reverse of
what you might expect.
## Precedence Levels
Each level should call the one higher to keep the parsing machine
from halting at any given level.
- expression()
- assignment()
- logical()
- equality()
- comparison()
- term()
- factor()
- unary()
- primary()
## Grammar
```
expression ::= equality;
assignment ::= IDENT "=" assignment
             | logic_or ;
logic_or   ::= logic_and ( "or" logic_and )* ;
logic_and  ::= equality ( "and" equality )* ;
equality   ::= comparison ( ( "!=" | "==") comparison)* ;
comparison ::= term ( ( ">" | ">=" | "<" | "<=" ) term)* ;
term       ::= factor ( ("-" | "+" ) factor )* ;
factor     ::= unary ( ("/" | "*" ) unary )* ;
unary      ::= ("/" | "*" ) unary
             | primary ;
primary    ::= NUMBER | STRING | "true" | "false" | "nil"
             | "(" expression ")" ;
```

> Note: Every program is just a list of `declarations` such as `if`,
> `while`, `fun`, or an expression statement (which is just an
> expression with a semicolon after it).
## Gotchas
First, each rule needs to match expression at that precedence level or HIGHER.
So in the case of unary expressions, which are right associative, 
we would need to make sure it can continue up the precedence levels
by converting `unary ::= ("!" | "-") unary` into:
```bnf
unary ::= ("!" | "-") unary
       | primary;
```

Second, left associativity produces left-recursive grammars if not careful.
Take factor expressions as an example. The grammar for factor
expressions could simply be:
```bnf
factor ::= factor ("/" | "*") unary
         | unary;
```
This rule is left associative because "factor" is the name of the
rule and the very first a factor can be is itself. This can cause
an infinite loop.

One way to fix this is to update the grammar to:
```bnf
factor ::= unary ( ( "/" | "*") unary )*;
```

This works, but it makes the grammar a little less clear to the
reader. Another way is precedence climbing which I believe is explained
in part III.


# Chapter 8
## Assignment
### Grammar
```
<assign> ::= IDENT "=" <expr>
           | <next_precedence_level>
```
### Examples
Below are two valid assignment expressions:
```
a.b.c = d;
a = b = c = d;
```

Here is an invalid assignment where the left side is not
an l-value.
```
"hello, world!" = 5;
```
### Implementation
1. Evaluate the left side of the expression.
2. While at an equal sign, parse the right side using the **right**
   **associative** rule. 
   - See below for the difference between right and left associativity in code.
3. If the left side is an l-value (such as a Variable), assign the the right expression to the variable.
    - If it is not, throw error.


### Right Associativity
Assignment is right associative. This means an expression like
`a = b = c;` would be evaluated like `(a = (b = c));` instead of
`((a = b) = c)`.

In order to achieve right associativity, you would pretty much
do the same thing as what you'd do for left associativity except
for one thing: when parsing the right side, don't go up a precedence
level.

```python
def assignment():
    left = next_precedence_level()
    
    while match(EQUAL):
        operator = previous()
        right = assignment()
        # If we were to instead go to the next precedence level
        # here, then this would be left associative.
        # right = next_precedence_level()
        left = BinOp(left, operator, right)
    return left
```

# Chapter 11: Resolving And Binding
## The Problem
"A variable usage refers to the preceding declaration with the same name in the **innermost scope**...".
This basically just means that if two variables are declared with the same name, the one that matters
at this moment is the one closest to where it is referenced in code.
> The desired variable can be known at compile time statically.

```
var a = "outer";
{
   // new scope
   var a = "inner";
   // This `a` we're printing should refer to the `a` closest
   // to this `print` statement (i.e. "inner").
   print a;
}
```
However, without resolving or using some other technique such as 
["Persistent Environments"](https://en.wikipedia.org/wiki/Persistent_data_structure)
(which I should definitely look into), the following code would be
valid:
```
var a = "global";
{
   // 1.
   fun showA() {
      print a; // should see "global" above.
   }
   
   // 2.
   showA(); // prints "global"
   
   var a = "block"
   // 3.
   showA(); // prints "block"
}
```
The third `showA()` should ideally always produce the same result as 
the second. Instead though, we've implemented Lox to dynamically
determine the value of `a` **at runtime**. Instead of seeing the
variable `a` where the function was declared, it sees the `a` in
the current environment.

As per Nystrom however, we would like to implement a language where "When a 
function is declared, it captures a reference to the current
environment." and where "The function *should* capture a frozen snapshot of the
environment *as it existed at the moment the function was declared.*"

> In short, I believe our language implementation allows
> [Dynamic Scoping](https://cs.stackexchange.com/questions/52990/what-are-differences-between-static-scope-and-dynamic-scope)
> when we want Lexical/Static Scoping.


## The Solution (Variable Resolution Pass)
"After the parser produces the syntax tree, but before the interpreter
starts executing it, we'll do a single walk over the tree to resolve
all of the variables it contains."
> This is a kind of [Semantic Analysis](https://en.wikipedia.org/wiki/Semantics_(computer_science)). 
> Also, [Type Checking](https://en.wikipedia.org/wiki/Type_system#Static_type_checking)
> and "any work that doesn't rely on state that's only available at 
> runtime can be done in this way."


When resolving variables, we need to handle all of the nodes, but 
the following are the only interesting nodes:
1. **Blocks Statements:** Introduce a new scope for the statement it contains.
2. **Function Declarations:**: Introduce a new scope for their body and bind their parameters in that scope.
3. **Variable Declarations:**: Add a new variable to the current scope.
4. **Variable Expressions:**: Need to have their variables resolved.
   - Variable Assignment Expressions: Same as Variable Expressions.

