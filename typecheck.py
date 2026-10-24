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
    saturated_constraints = set(constraints)
    old_size = 0
    while len(saturated_constraints) != old_size:
        old_size = len(saturated_constraints)

        symmetry_candidates = []
        tansitivity_candidates = []
        struct_candidates = []
        for constrint in saturated_constraints:
            if isinstance(constrint.r, TpVar):
                symmetry_candidates.append(constrint)
            if isinstance(constrint.l, TpVar):
                tansitivity_candidates.append(constrint)
            if isinstance(constrint.l, FuncTp) and isinstance(constrint.l, FuncTp):
                struct_candidates.append(constrint)

        _apply_symmetry(symmetry_candidates, saturated_constraints)
        _apply_transitivity(tansitivity_candidates, saturated_constraints)
        _apply_struct(struct_candidates, saturated_constraints)

    return frozenset(saturated_constraints)



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




def _apply_symmetry(symmetry_candidates, saturated_constraints):
    for constraint in symmetry_candidates:
        saturated_constraints.add(Constraint(constraint.r, constraint.l))

def _apply_transitivity(tansitivity_candidates, saturated_constraints):
    for i in range(len(tansitivity_candidates)):
        for j in range(i, len(tansitivity_candidates)):
            contraint_i, constraint_j = tansitivity_candidates[i], tansitivity_candidates[j]
            if contraint_i.l == constraint_j.l:
                saturated_constraints.add(Constraint(contraint_i.r, constraint_j.r))

def _apply_struct(struct_candidates, saturated_constraints):
    for constraint in struct_candidates:
        saturated_constraints.add(Constraint(constraint.l.a, constraint.r.a))
        saturated_constraints.add(Constraint(constraint.l.b, constraint.r.b))