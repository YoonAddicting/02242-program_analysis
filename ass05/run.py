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

def get_type(t):
    try:
        type=t.get('type')
        k=t.get('kind')
        return k+ " " +get_type(type)
    except:
        return t.get('base')
    
def abstract_args(method):
    abstract_args = []
    for param in method.get('params'):
        # type = get_type(p.get('type'))
        param_type=""
        try:
            param_type=param.get('type').get('base')
        except:
            # nested type
            raise Exception("nested type")
        match param_type:
            case 'int':
                abstract_args.append(('int',{'-','0','+'}))
            case 'float':
                abstract_args.append(('float',{'-','0','+'}))
            case 'double':
                abstract_args.append(('double',{'-','0','+'}))
            case 'boolean':
                abstract_args.append(('boolean',{'true','false'}))
            case "":
                continue
            case _:
                raise Exception(f"Undefined type: {param_type}")
    return abstract_args

def abstract_step(bytecode, state, pc):
    opr = bytecode[pc].get('opr')

    match opr:
        case 'load':
            if bytecode[pc].get('type') == 'int':
                raise Exception("load int")
            elif bytecode[pc].get('type') == 'float':
                raise Exception("load float")
            else:
                raise Exception("load")
        case 'store':
            raise Exception("store")
        case 'push':
            if bytecode[pc].get('value').get('type') == 'integer':
                state[1].append(('int',{'-','0','+'}))
            elif bytecode[pc].get('value').get('type') == 'float':
                state[1].append(('float',{'-','0','+'}))
            else:
                raise Exception("push")
            return (state, pc+1, False)
        case 'binary': 
            operant = bytecode[pc].get('operant')
            a2 = state[1].pop()
            a1 = state[1].pop()
            print(f"a1: {a1}, a2: {a2}")
            match operant:
                case 'add':
                    raise Exception("add")
                case 'sub':
                    raise Exception("sub")
                case 'mul':
                    raise Exception("mul")
                case 'div':
                    state[1].append(('int',{'-','0','+'}))
                    if a2[1].contains('0'):
                        return (state, pc+1, True)
                    else:
                        return (state, pc+1, False)
                    raise Exception("div")
                case 'rem':
                    raise Exception("rem")
                case _:
                    raise Exception("binary")
        case 'incr':
            raise Exception("incr")
        case 'negate':
            raise Exception("negate")
        case 'put':
            raise Exception("put")
        case 'get':
            raise Exception("get")
        case 'ifz':
            cond = bytecode[pc].get('condition')
            match cond:
                case 'eq':
                    raise Exception("eq")
                case 'ne':
                    raise Exception("ne")
                case 'lt':
                    raise Exception("lt")
                case 'le':
                    raise Exception("le")
                case 'gt':
                    raise Exception("gt")
                case 'ge':
                    raise Exception("ge")
                case _:
                    raise Exception("ifz")
        case 'if':
            cond = bytecode[pc].get('condition')
            match cond:
                case 'eq':
                    raise Exception("eq")
                case 'ne':
                    raise Exception("ne")
                case 'lt':
                    raise Exception("lt")
                case 'le':
                    raise Exception("le")
                case 'gt':
                    raise Exception("gt")
                case 'ge':
                    raise Exception("ge")
                case _:
                    raise Exception("if")
        case 'new':
            raise Exception("new")
        case 'dup':
            raise Exception("dup")
        case 'throw':
            raise Exception("throw")
        case 'goto':
            raise Exception("goto")
        case 'negate':
            raise Exception("negate")
        case 'incr':
            raise Exception("incr")
        
        case 'invoke':
            raise Exception("invoke")
        case 'return':
            raise Exception("return")
        case 'array_store':
            raise Exception("array store")
        case 'array_load':
            raise Exception("array load")
        case _:
            raise Exception()
        
    
    
    
    
   

    return (None, None)



def abstract_join(a1, a2, npc):
    #TODO: Finish this method, needs further looping to join the arguments
    res = a1.copy()
    notfound = True
    for arg2 in a2[npc][0]:
        for arg1 in a1[npc][0]:
            if arg1[0] is arg2[0]:
                # Do set join on    
                # res[npc][0][1] and arg2[1]
                
                notfound = False
                break
        if notfound:
            res[npc][0].append(arg2)
        
    a1[npc] = a1 + a2 # Join a1 og a2 somehow

    
    
    
    return a1

def is_error(res):
    return True


def bounded_abstract_interpretation(bc, m, k):
    # {(abstract_args(m), [])} is the intial state
    s = {0 : (abstract_args(m), [])}
    # Perform steps up to k times
    for _ in range(0, k):
        # Copy the current state
        next_s = s.copy()
        # For each pc in the current state
        for pc in s:
            # Perform the abstract step
            (new_s, npc, is_error) = abstract_step(bc, s[pc], pc)
            # If the step resulted in an error, return with error
            if is_error:
                return "Has error: " + new_s
            # Join the new state with the next state
            next_s = abstract_join(next_s, new_s, npc)
        # Update the state
        s = next_s 
    return "Has no error"
 

if __name__ == "__main__":
    dir = glob.glob('./**/Arithmetics.json',recursive=True)
    
    # for all methods in all files
    for dep in dir:
        file = json.loads(open(dep).read())
        for method in file['methods']:
            is_case = False
            for annotation in method.get('annotations'):
                if annotation.get('type') == "dtu/compute/exec/Case":
                    is_case = True
                    break
            if not is_case:
                continue
            else:
                program = method.get('code').get('bytecode')
                res = bounded_abstract_interpretation(program, method, 10)
                print(res)
                #interpreter = Interpreter(program, None)
                #interpreter.run(([],[],0), "Simple"+method.get('name'))

