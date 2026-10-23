
# Allow importing student code from parent directory (outside of ./src)
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lark import Lark
import src.constraint_prog as constraint_prog
from typing import FrozenSet
from src.lam import ConstraintProg, SaturateCommand, CanonicalizeCommand, CheckSatCommand, TypecheckingError
from pathlib import Path
from typecheck import saturate_constraints, canonicalize, check_sat

constraint_syntax = Path('./src/constraint_prog.lark').read_text()
constraint_parser = Lark(constraint_syntax, start='start', parser='lalr')

def load_constraint_file(p: Path) -> None:
    try:
        text = p.read_text()
    except Exception as err:
        print(f">>>>> Error occured when reading: '{p}' <<<<<\n")
        print(err)
        exit(0)

    try:
        tree = constraint_parser.parse(text)
        # print(tree.pretty())
    except Exception as err:
        print(f">>>>> Syntax error occured when parsing: '{p}' <<<<<\n")
        print(err)
        exit(0)

    prog: ConstraintProg = constraint_prog.TreeToConstraints().transform(tree)

    saturated = None
    def saturate():
        nonlocal saturated
        if saturated is None:
            saturated = saturate_constraints(prog.constraints)
        assert saturated is not None
        return saturated

    for command in prog.commands:
        if isinstance(command, SaturateCommand):
            saturate()
            print(list(sorted(map(str, saturated))))
        elif isinstance(command, CheckSatCommand):
            saturate()
            try:
                check_sat(saturated)
                print('sat')
            except TypecheckingError as e:
                print('unsat')
        else:
            assert isinstance(command, CanonicalizeCommand)
            saturate()
            result = canonicalize(frozenset(), saturated, command.tp)
            print(f'{command.tp} = {result}')


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("input", nargs='+', type=Path, help="file")
    args = p.parse_args()

    for i in args.input:
        if len(args.input) > 1:
            print(f'# {i}')
        load_constraint_file(i)
