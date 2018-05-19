from mindsetup import *
from argparse import ArgumentParser, Action

modalizer = ArgumentParser(epilog='NB: When using the repl, "-r -c 0 <INPUT>" is a useful format.')

modalizer.add_argument(
  'program',
  help='Filepath to the MindSet program.')
modalizer.add_argument(
  'input', nargs='?',
  help='Filepath to the input.')
modalizer.add_argument(
  '-c', '--code', dest='code', action='store_true',
  help='The program argument is interpreted as literal code instead of a path.')
modalizer.add_argument(
  '-i', '--inputcode', dest='codeinput', action='store_true',
  help='The input argument is interpreted as literal code instead of a path.')
modalizer.add_argument(
  '-s', '--step', dest='step', action='store_true',
  help='Wait for input after each line executes.')
modalizer.add_argument(
  '-r', '--repl', dest='repl', action='store_true',
  help='Currently a nop. In the future, will enter REPL mode after the program is finished. U is set to the result of each evaluated expression. Exits when U is {}.')
modalizer.add_argument(
  '-v', '--verbose', dest='verbose', action='store_true',
  help='Log each step of the execution of the program.')

mode = modalizer.parse_args()

program = mode.program
if not mode.code:
  with open(mode.program) as f: program = f.read()

theinput = mode.input
if not mode.codeinput:
  with open(mode.input) as f: theinput = f.read()

vm = MindSet(program, theinput)
vm.run(mode.verbose, mode.step)
print(vm.result)
