# Allow importing student code from parent directory (outside of ./src)
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
import argparse

from src.lam_prog import load_lam_program
import src.lam as lam
from src.eval import eval_lam
from typing import List

def lam_to_prog(fname: Path, normalize: bool, type_check: bool, execute: bool, echo_name: bool = False) -> None:
    try:
        prog = load_lam_program(fname)
    except Exception as err:
        print(f">>>>> Error occured while loading: '{fname}' <<<<<\n")
        print(err)
        exit(0)

    if echo_name:
        print('---', fname, '---')

    # type-check
    if type_check:
        print("type-checking... ", file=sys.stderr)
        from typecheck import typecheck
        try:
            types = typecheck(prog)
            normalizer = lam.TypeNormalizer()
            if not isinstance(types, dict):
                raise lam.TypecheckingError("Result types not of correct form")
            print("Typings:", file=sys.stderr)
            for defn in lam.get_defns_list(prog):
                type_ = types[defn.s]
                if normalize:
                    type_ = normalizer.normalize(type_)
                print(f"def {defn.s}: {type_}")
        except lam.TypecheckingError as e:
            print("Typechecking failed")
            print(f'Error message: {e}', file=sys.stderr)
            execute = False
    # execute
    if execute:
        print("executing...", file=sys.stderr)
        try:
            eval_lam(prog)
        except lam.TypecheckingError as e:
            print(f">>> Warning: file {fname} runtime produced an error: {e} <<<")
            

        
    
if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("input", nargs='+', type=Path, help="file")
    argparser.add_argument("--no-type-check", dest='type_check', action='store_false', default=True, help="don't perform typechecking")
    argparser.add_argument("--no-execute", dest='execute', action='store_false', default=True, help="don't execute any expressions")
    argparser.add_argument("--normalize", action='store_true', help="normalize type variable names")
    args = argparser.parse_args()

    for i in args.input:
        lam_to_prog(i, normalize=args.normalize, type_check=args.type_check, execute=args.execute, echo_name=len(args.input) > 1)
