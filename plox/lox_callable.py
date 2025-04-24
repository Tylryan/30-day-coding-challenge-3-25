
import interpreter

class LoxCallable:

    def arity(self) -> int:
        pass
    def call(self, interp: interpreter.Interp, arguments: list[object]) -> object:
        pass