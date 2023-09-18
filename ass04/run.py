import glob
from typing import Optional, TextIO
import json

class Program:
    def __init__(self,bytecode):
        self.bytecode = bytecode

class Locals:
    def __init__(self) -> None:
        pass

class OperStack:
    def __init__(self) -> None:
        pass


class ProgramCounter:
    def __init__(self) -> None:
        pass



class Interpreter:


    def __init__(self, program : Program, verbose : Optional[TextIO]):
        self.program = program
        self.verbose = verbose
        self.logfile = None
        self.memory = {}
        self.stack = []

    def run(self, f : tuple[Locals, OperStack, ProgramCounter], method : str):
        self.stack.append(f)
        self.log_start(method)
        self.log_state()
        while self.step():
            self.log_state()
            continue
        self.log_done()
    
    def log_start(self, method):
        self.logfile =  open(f"./tests/{method}.txt",'w')
        
    
    def log_state(self):
        self.logfile.write('\n'.join('{} {} {}'.format(self.stack[-1][0],self.stack[-1][1],self.stack[-1][2])))
        
        self.logfile.write(json.dumps(self.memory))
        

    def log_done(self):
        self.logfile.close()

    def step(self):
        (l, s, pc) = self.stack[-1]
        b = self.program.bytecode[pc]
        if hasattr(self, b["opr"]):
            return getattr(self, b["opr"])(b)
        else:
            return False

    def pop(self, b):
        (l, s, pc) = self.stack.pop(-1)
        # Rule (pop_1)
        if b["words"] == 1:
            if len(s) < 1: return False
            self.stack.append((l, s[:-1], pc + 1))
        # Rule (pop_2)
        elif b["words"] == 2:
            if len(s) < 2: return False
            self.stack.append((l, s[:-2], pc + 1))
        else:
            return False
        
    def invoke(self, b, r):
        l[0] = self.ref(r)
        self.stack.append((l, s, pc + 1))
        return True
        

if __name__ == "__main__":
    dir = glob.glob('./**/Simple.json',recursive=True)
    
    # for all methods in all files
    for dep in dir:
        file = json.loads(open(dep).read())
        for method in file['methods']:
            if "<init>" in method.get("name"):
                continue
            program = Program(method.get('code').get('bytecode'))
            interpreter = Interpreter(program, None)
            interpreter.run(([],[],0), "Simple"+method.get('name'))
