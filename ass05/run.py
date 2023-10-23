import glob
from typing import Optional, TextIO
import json
from enum import Enum

class VarTypes(Enum):
    INT = 1
    FLOAT = 2
    DOUBLE = 3
    BOOLEAN = 4
    
class ValueExpr:
    def __init__(self, type : VarTypes, value : set) -> None:
        self.type = type
        self.value = value

    def __str__(self) -> str:
        return f"{self.value} : {self.type}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, other : object) -> bool:
        if isinstance(self, other):
            return self.value == other.value and self.type == other.type
        else:
            return False
        
    def __add__(self, other : object) -> object:
        if self.type == 'int' and other.type == self.type:
            
            pass
        elif self.type == 'float' and other.type == self.type:
            pass
        elif self.type == 'double' and other.type == self.type:
            pass
        elif self.type == 'boolean' and other.type == self.type:
            pass
        else:
            pass
    
        
    def union(self, other : object) -> object:
        if self.type == other.type:
            return ValueExpr(self.type, self.value.union(other.value))
        else:
            raise Exception("Type mismatch")
        
    def intersect(self, other : object) -> object:
        if self.type == other.type:
            return ValueExpr(self.type, self.value.difference(other.value))
        else:
            raise Exception("Type mismatch")
    

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
                abstract_args.append(ValueExpr(VarTypes.INT, {'-','0','+'}))
            case 'float':
                abstract_args.append(ValueExpr(VarTypes.FLOAT,{'-','0','+'}))
            case 'double':
                abstract_args.append(ValueExpr(VarTypes.DOUBLE,{'-','0','+'}))
            case 'boolean':
                abstract_args.append(ValueExpr(VarTypes.BOOLEAN,{'true','false'}))
            case "":
                continue
            case _:
                raise Exception(f"Undefined type: {param_type}")
    return abstract_args

def abstract_step(bytecode : list, state : (list, list), pc : int) -> ([(int, list)], bool):
    opr = bytecode[pc].get('opr')

    original_state = (state[0].copy(), state[1].copy())
    new_states = []
    contains_error = False

    print(f"opr: {opr}")
    match opr:
        case 'load':
            index = bytecode[pc].get('index')
            if bytecode[pc].get('type') == 'int':
                original_state[1].append(state[0][index])
                new_states.append((pc+1, original_state))
            elif bytecode[pc].get('type') == 'float':
                original_state[1].append(state[0][index])
                new_states.append((pc+1, original_state))
            else:
                raise Exception("load not defined for type")
            
        case 'store':
            index = bytecode[pc].get('index')
            
            raise Exception("store")
        case 'push':
            # push to stack
            if bytecode[pc].get('value').get('type') == 'integer':
                original_state[1].append(ValueExpr(VarTypes.INT, {'-','0','+'}))
            elif bytecode[pc].get('value').get('type') == 'float':
                original_state[1].append(ValueExpr(VarTypes.FLOAT, {'-','0','+'}))
            else:
                raise Exception("push")
            new_states.append((pc+1, original_state))
        case 'binary': 
            operant = bytecode[pc].get('operant')
            a2 = original_state[1].pop()
            a1 = original_state[1].pop()
            print(f"a1: {a1}, a2: {a2}")
            match operant:
                case 'add':
                    original_state[1]
                    #raise Exception("add")
                case 'sub':
                    raise Exception("sub")
                case 'mul':
                    raise Exception("mul")
                case 'div':
                    original_state[1].append(ValueExpr(VarTypes.INT, {'-','0','+'}))
                    if '0' in a2.value:
                        new_states.append((pc+1, original_state))
                        contains_error == True
                    else:
                        new_states.append((pc+1, original_state))
                    #raise Exception("div")
                case 'rem':
                    raise Exception("rem")
                case _:
                    raise Exception("binary")
        case 'incr':
            index = bytecode[pc].get('index')
            amount = bytecode[pc].get('amount')
            original_state[0][index] = state[0][index] + amount
            new_states.append((pc+1, original_state))
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
        
    
    
    
    
    new_states

    return (new_states, contains_error)



def abstract_join(old_s, new_s):
    #TODO: Finish this method, needs further looping to join the arguments
    res = old_s.copy()
    for (npc, ns) in new_s:
        if npc in old_s.keys():
            # TODO widening of stack
            for i in range(len(old_s[npc][0])):
                # Widening of locals
                old_s[npc][0][i] = old_s[npc][0][i].union(ns[0][i])

            res[npc] = ns
            continue
        #add the state
        res[npc] = ns    
    return res

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
            # new_s is a list of new states and pc
            (new_s, is_error) = abstract_step(bc, s[pc], pc)
            # If the step resulted in an error, return with error
            if is_error:
                return "Has error: " + new_s
            # Join the new state with the next state
            next_s = abstract_join(next_s, new_s)
        # Update the state
        # Check if this is a fixed point
        # TODO: Create function to check if two states are identical
        if s is next_s:
            #fixed point
            return "Has no error"
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
                print(f"Method {method.get('name')}:")
                program = method.get('code').get('bytecode')
                res = bounded_abstract_interpretation(program, method, 10)
                print(res)
                #interpreter = Interpreter(program, None)
                #interpreter.run(([],[],0), "Simple"+method.get('name'))

