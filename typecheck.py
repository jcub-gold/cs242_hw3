from src.lam import *
from typing import FrozenSet, Mapping, Tuple, Dict
import sys

def log(*args) -> None:
    """
    The grader for this assignment will ignore stderr when running your code, 
    so you can use this function for debugging and not worry about making sure 
    it's deleted when you submit.
    """
    print(*args, file=sys.stderr, flush=True)

def saturate_constraints(constraints: FrozenSet[Constraint]) -> FrozenSet[Constraint]:
    raise NotImplementedError()

def canonicalize(X: FrozenSet[Type], S: FrozenSet[Constraint], t: Type) -> Type:
    raise NotImplementedError()

def check_sat(S: FrozenSet[Constraint]) -> None:
    raise NotImplementedError()

def generate_constraints_for_expr(A: Mapping[Var, Type], e: Expr) -> Tuple[Type, FrozenSet[Constraint]]:
    raise NotImplementedError()

def generate_constraints_for_program(prog: Prog, A: Mapping[Var, Type]) -> Tuple[Mapping[Var, Type], FrozenSet[Constraint]]:
    raise NotImplementedError()

def typecheck(prog: Prog) -> Dict[Var, Type]:
    raise NotImplementedError()
