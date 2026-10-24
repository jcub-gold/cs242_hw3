from src.lam import *
from typing import FrozenSet, Mapping, Tuple, Dict
import sys

COUNT = 0

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
        for constraint in saturated_constraints:
            if isinstance(constraint.r, TpVar):
                symmetry_candidates.append(constraint)
            if isinstance(constraint.l, TpVar):
                tansitivity_candidates.append(constraint)
            if isinstance(constraint.l, FuncTp) and isinstance(constraint.r, FuncTp):
                struct_candidates.append(constraint)

        _apply_symmetry(symmetry_candidates, saturated_constraints)
        _apply_transitivity(tansitivity_candidates, saturated_constraints)
        _apply_struct(struct_candidates, saturated_constraints)

    return frozenset(saturated_constraints)



def canonicalize(X: FrozenSet[Type], S: FrozenSet[Constraint], t: Type) -> Type:
    if isinstance(t, IntTp):
        return t
    if t in X:
        raise TypecheckingError("Cycle discovered during canonicalization...")

    X_new = set(X)
    X_new.add(t)
    X_new = frozenset(X_new)
    if isinstance(t, FuncTp):
        return FuncTp(canonicalize(X_new, S, t.a), canonicalize(X_new, S, t.b))

    if isinstance(t, TpVar):
        T = _find_T(t, S)
        if T is not None:
            return canonicalize(X_new, S, T)
        B = _find_B(t, S)
        if B is not None:
            return canonicalize(X_new, S, B)        
    return t

def check_sat(S: FrozenSet[Constraint]) -> None:
    for constraint in S:
        l_canonicalized, r_canonicalized = canonicalize(frozenset(), S, constraint.l), canonicalize(frozenset(), S, constraint.r)
        if (isinstance(l_canonicalized, FuncTp) and isinstance(r_canonicalized, IntTp)) or (isinstance(r_canonicalized, FuncTp) and isinstance(l_canonicalized, IntTp)):
            raise TypecheckingError("Invalid form (FuncTp equal to IntTp)...")

def generate_constraints_for_expr(A: Mapping[Var, Type], e: Expr) -> Tuple[Type, FrozenSet[Constraint]]:
    global COUNT
    
    if e in CONSTS:
        return (CONSTS[e], frozenset())
    if isinstance(e, IntConst):
        return (IntTp(), frozenset())
    if isinstance(e, Var):
        if e not in A:
            raise TypecheckingError(f"Undefined variable: {e}")
        return (A[e], frozenset())
    if isinstance(e, Lam):
        alpha = TpVar(f"a{COUNT}")
        COUNT += 1
    
        A_new = dict(A)
        A_new[e.s] = alpha
        T, constraints = generate_constraints_for_expr(A_new, e.e)
        return (FuncTp(alpha, T), constraints)
    if isinstance(e, App):
        beta = TpVar(f"a{COUNT}")
        COUNT += 1

        T, constraints = generate_constraints_for_expr(A, e.e1)
        T_prime, constraints_prime = generate_constraints_for_expr(A, e.e2)

        constraints = set(constraints) | set(constraints_prime) | {Constraint(T, FuncTp(T_prime, beta))}
        constraints = frozenset(constraints)
        return (beta, constraints)

def generate_constraints_for_program(prog: Prog, A: Mapping[Var, Type]) -> Tuple[Mapping[Var, Type], FrozenSet[Constraint]]:
    A_new, constraints = dict(A), set()
    defns_list = get_defns_list(prog)
    for defn in defns_list:
        T, frozen_constraints = generate_constraints_for_expr(A_new, defn.e)
        A_new[defn.s] = T
        constraints |= set(frozen_constraints)

    return (A_new, frozenset(constraints))



def typecheck(prog: Prog) -> Dict[Var, Type]:
    A, constraints = generate_constraints_for_program(prog, {})
    S = saturate_constraints(constraints)
    check_sat(S)
    A_canonicalized = {}
    for var, t in A.items():
        A_canonicalized[var] = canonicalize({}, S, t)

    return A_canonicalized



def _find_B(alpha, S):
    possible_Bs = []
    for constraint in S:
        if constraint.l == alpha and isinstance(constraint.r, TpVar):
            possible_Bs.append(constraint.r)

    possible_Bs.sort()
    if len(possible_Bs) > 0 and possible_Bs[-1] != alpha:
        return possible_Bs[-1]
    return None

def _find_T(alpha, S):
    for constraint in S:
        if constraint.l == alpha and not isinstance(constraint.r, TpVar):
            return constraint.r
    return None

def _apply_symmetry(symmetry_candidates, saturated_constraints):
    for constraint in symmetry_candidates:
        saturated_constraints.add(Constraint(constraint.r, constraint.l))

def _apply_transitivity(tansitivity_candidates, saturated_constraints):
    for i in range(len(tansitivity_candidates)):
        for j in range(i, len(tansitivity_candidates)):
            constraint_i, constraint_j = tansitivity_candidates[i], tansitivity_candidates[j]
            if constraint_i.l == constraint_j.l:
                saturated_constraints.add(Constraint(constraint_i.r, constraint_j.r))

def _apply_struct(struct_candidates, saturated_constraints):
    for constraint in struct_candidates:
        saturated_constraints.add(Constraint(constraint.l.a, constraint.r.a))
        saturated_constraints.add(Constraint(constraint.l.b, constraint.r.b))