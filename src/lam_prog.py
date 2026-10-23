# type: ignore

from pathlib import Path

# find lark
import sys
DIR = Path(__file__).resolve().parent
sys.path.append(DIR.parent)

from collections import namedtuple
from lark import Transformer, Lark
from typing import List
import functools

import src.lam as lam

# Convert Tree to Prog.
class TreeToProg(Transformer):
    # start
    def start(self, items): return items[0]
    def prog(self, items): 
        if len(items) == 0:
            return lam.ProgEmpty()
        else:
            return lam.ProgCons(items[0], self.prog(items[1:]))

    def defn(self, items):
        return lam.Defn(lam.Var(items[0]), items[1])

    def IDENT(self, s): return str(s)
    def NUMBER(self, s): return int(s)

    def app(self, items): return lam.App(*items)
    def var(self, items): return lam.Var(*items)
    def lam(self, items):
        if items[0] in lam.CONSTS: raise ValueError("Can't use {} as variable".format(items[0]))
        assert len(items) == 2
        return lam.Lam(lam.Var(items[0]), items[1])
    def num(self, items): return lam.IntConst(int(items[0]))
    def let(self, items): 
        if items[0] in lam.CONSTS: raise ValueError("Can't use {} as variable".format(items[0]))
        return lam.Let(*items)

lam_syntax = (DIR / 'lam_prog.lark').read_text()
lam_parser = Lark(lam_syntax, start='start', parser='lalr')

def load_lam_program(p: Path) -> lam.Prog:
    text = p.read_text()
    tree = lam_parser.parse(text)
    prog: lam.Prog = TreeToProg().transform(tree)
    return prog
