from dataclasses import dataclass
from typing import Iterable, List, Sequence, Dict

### PROGRAMS ###

class Prog:
    pass

@dataclass(frozen=True)
class ProgCons(Prog):
    head: 'Defn'
    tail: Prog

    def __repr__(self) -> str:
        return f'{self.head}\n{self.tail}'

@dataclass(frozen=True)
class ProgEmpty(Prog):
    def __repr__(self) -> str:
        return ''

def get_defns_list(prog: Prog) -> List['Defn']:
    if isinstance(prog, ProgCons):
        return [prog.head] + get_defns_list(prog.tail)
    else:
        return []

# A definition is just a var and an expression
@dataclass(frozen=True)
class Defn:
    s: 'Var'
    e: 'Expr'

    def __repr__(self) -> str: 
        return "def {} = {};".format(self.s, self.e)

### Expressions ###
class Expr:
    pass

# Var also represents constants; see below
@dataclass(frozen=True)
class Var(Expr):
    s: str

    def __repr__(self) -> str: 
        return "{}".format(self.s)

@dataclass(frozen=True)
class Lam(Expr):
    s: Var
    e: Expr

    def __repr__(self) -> str: 
        return "\\{}.{}".format(self.s, self.e)

@dataclass(frozen=True)
class App(Expr):
    e1: Expr
    e2: Expr

    def __repr__(self) -> str: 
        return "({} {})".format(self.e1, self.e2)

@dataclass(frozen=True)
class IntConst(Expr):
    i: int

    def __repr__(self) -> str: 
        return "{}".format(self.i)
    
### Types ###

# Note, Type is an abstract base class; all instances are expected to be one of the cases below.
# Type objects can be compared for structural equality, and thus stored in sets/maps/etc.
# For example, Func(IntType(), IntType()) == Func(IntType(), IntType()) is true, even though the
# actual objects at runtime are different. Note this is *structural equality*, so
# IntType() != TypeVar('x') even if we have an equation somewhere saying TypeVar('x') is IntType().
class Type:
    pass

@dataclass(frozen=True)
class IntTp(Type):
    def __repr__(self) -> str: 
        return "INT"

@dataclass(frozen=True)
class FuncTp(Type):
    a: Type
    b: Type

    def __repr__(self) -> str:
        a = self.a if not isinstance(self.a, FuncTp) else f"({self.a})"
        return f"{a} -> {self.b}"

@dataclass(frozen=True, order=True)
class TpVar(Type):
    s: str

    def __repr__(self) -> str: 
        return self.s

### CONSTANTS ###

# Constants have a fixed type supplied by the following table. Var('x') is a constant
# if 'x' in CONSTS. Otherwise, it is a variable. The parser we have supplied will ensure
# bound variables are never equal to constants.

_I = IntTp()
CONSTS = {
    Var('+'): FuncTp(_I, FuncTp(_I, _I)),
    Var('-'): FuncTp(_I, FuncTp(_I, _I)),
    Var('/'): FuncTp(_I, FuncTp(_I, _I)),
    Var('*'): FuncTp(_I, FuncTp(_I, _I)),
    Var('ifz'): FuncTp(_I, FuncTp(_I, FuncTp(_I, _I)))
}

### CONSTRAINTS ###
@dataclass(frozen=True)
class Constraint:
    l: Type
    r: Type

    def __repr__(self) -> str:
        return f'{self.l} == {self.r}'

### TYPECHECKING ###

# Throw the following error if you detect that the input program is not type-correct:
#   raise TypecheckingError("reason")
# The reason message is optional, but may help you debug your own code  if you get a
# type error when you don't expect it. Don't confuse this with Python's TypeError.
class TypecheckingError(Exception):
    pass

# internal, you can ignore this
class Command:
    pass

@dataclass(frozen=True)
class SaturateCommand(Command):
    pass

@dataclass(frozen=True)
class CheckSatCommand(Command):
    pass

@dataclass(frozen=True)
class CanonicalizeCommand(Command):
    tp: Type

@dataclass(frozen=True)
class ConstraintProg:
    constraints: Sequence[Constraint]
    commands: Sequence[Command]

class TypeNormalizer:
    def __init__(self) -> None:
        self.seen: Dict[TpVar, TpVar] = {}
        self.counter: int = 0

    def normalize(self, tt: Type) -> Type:
        if isinstance(tt, IntTp):
            return IntTp()
        elif isinstance(tt, TpVar):
            if tt not in self.seen:
                self.seen[tt] = TpVar(f"a{self.counter}")
                self.counter += 1
            return self.seen[tt]
        elif isinstance(tt, FuncTp):
            l = self.normalize(tt.a)
            r = self.normalize(tt.b)
            return FuncTp(l, r)
        else:
            raise ValueError(f'Unknown Type {tt}')

