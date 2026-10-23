# type: ignore

from lark import Transformer
from typing import List
import functools

import src.lam as lam

# Convert Tree to Prog.
class TreeToConstraints(Transformer):
    def start(self, items): 
        assert len(items) == 2
        return lam.ConstraintProg(items[0], items[1])

    def commands(self, items):
        return tuple(items)

    def constraints(self, items):
        return frozenset(items)

    def check_sat_cmd(self, items):
        assert len(items) == 0
        return lam.CheckSatCommand()

    def saturate_cmd(self, items):
        assert len(items) == 0
        return lam.SaturateCommand()

    def canonicalize_cmd(self, items):
        assert len(items) == 1 
        return lam.CanonicalizeCommand(items[0])

    def constraint(self, items):
        assert len(items) == 2
        return lam.Constraint(items[0], items[1])

    def expr(self, items):
        if len(items) == 1:
            return items[0]
        else:
            assert len(items) == 2
            return lam.FuncTp(items[0], items[1])

    def IDENT(self, s): return lam.TpVar(s)

    def inttp(self, items): 
        assert len(items) == 0
        return lam.IntTp()
