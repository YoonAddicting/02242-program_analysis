import glob
import json
import sys
import math

from dataclasses import dataclass
from typing import NewType, TypeVar

T = TypeVar('T')
INT = NewType('INT', int)
FLOAT = NewType('FLOAT', float)
BOOL = NewType('BOOL', bool)

@dataclass(frozen=True)
class Bounds:
    low: T
    high: T

    @classmethod
    def from_type(cls, typename):
        if typename == 'int':
            return Bounds(-(2**31), 2**31-1)
        if typename == 'float':
            return Bounds(sys.float_info.min,sys.float_info.max)
        if typename == 'boolean':
            return Bounds(0,1)
        else:
            raise Exception(f"Unknown Type: {typename}")

    @classmethod
    def from_value(cls, value):
        if value['type'] == 'integer':
            return cls.from_integer(value['value'])
        else:
            raise Exception("Unknown Value Type")
        
    @classmethod
    def from_integer(cls, value):
        return Bounds(value, value)
    
    @classmethod
    def wide(cls, value1, value2):
        low = None
        if value1.low is not None and value2.low is not None:
            low = min(value1.low, value2.low)
        high = None
        if value1.high is not None and value2.high is not None:
            high = max(value1.high, value2.high)
        return Bounds(low, high)

    @classmethod
    def add(cls, value1, value2):
        def add_m(v1, v2):
            if v1 is None or v2 is None:
                return None
            return v1 + v2
        return Bounds(add_m(value1.low,value2.high), add_m(value1.low, value2.high))
    
    @classmethod
    def sub(cls, value1, value2):
        def sub_m(v1, v2):
            if v1 is None or v2 is None:
                return None
            return v1 - v2
        return Bounds(sub_m(value1.low,value2.high), sub_m(value1.low, value2.high))
    
    @classmethod
    def mul(cls, value1, value2):
        edges = []
        def mul_m(v1, v2):
            if v1 is None or v2 is None:
                return None
            return v1 * v2

        for v1 in [value1.low, value1.high]:
            for v2 in [value2.low, value2.high]:
                edges.append(mul_m(v1, v2))

        return Bounds (None if None in edges else min(edges), None if None in edges else max(edges))
    
    @classmethod
    def div(cls, value1, value2):
        edges = []
        def div_m(v1, v2):
            if v1 is None or v2 is None:
                return None
            return v1 // v2

        for v1 in [value1.low, value1.high]:
            for v2 in [value2.low, value2.high]:
                edges.append(div_m(v1, v2))

        return Bounds (None if None in edges else min(edges), None if None in edges else max(edges))

def get_bytecode_at_offset(bytecode, offset):
    for bc in bytecode:
        if bc.get('offset') == offset:
            return bc
    return None

def merge(old_s, new_s, abstraction):
    if old_s is None:
        return new_s
    olc, os = old_s
    nlc, ls = new_s
    # Wide to be implemented (not yet shown in video)
    mlc = [abstraction.wide(olc[i], nlc[i]) for i in set(olc) | set(nlc)]
    ms = [abstraction.wide(o, n) for o, n in zip(os, ls)]

    return (mlc, ms)

def merge_forward(states, load, locals, stack, abstraction, worklist):
    res = merge(states[load], (locals, stack), abstraction)
    if res != states[load]:
        worklist.append(load)
    states[load] = res


def step(states, load, locals, stack, bytecode, opr, worklist, abstraction, full_bytecode):
    if opr == 'push':
        new_stack = stack + [abstraction.from_value(bytecode.get('value'))]
        new_load = full_bytecode[full_bytecode.index(bytecode) + 1].get('offset')
        merge_forward(states, new_load, locals, new_stack, abstraction, worklist)
    
    elif opr == 'store':
        new_stack = stack[:-1]
        new_locals = locals.copy()
        new_locals[bytecode.get('index')] = stack[-1]
        new_load = full_bytecode[full_bytecode.index(bytecode) + 1].get('offset')

        merge_forward(states, new_load, new_locals, new_stack, abstraction, worklist)

    elif opr == 'load':
        new_stack = stack + [locals[bytecode.get('index')]]
        new_load = full_bytecode[full_bytecode.index(bytecode) + 1].get('offset')

        merge_forward(states, new_load, locals, new_stack, abstraction, worklist)
        
    elif opr == 'if':
        new_stack = stack[:-2]
        a = stack[-1]
        b = stack[-2]

        if bytecode.get('condition') == 'ge':
            # if not a >= b
            new_load = full_bytecode[full_bytecode.index(bytecode) + 1].get('offset')
            merge_forward(states, new_load, locals, new_stack, abstraction, worklist)
            # if a >= b
            new_load = full_bytecode[bytecode.get('target')].get('offset')
            merge_forward(states, new_load, locals, new_stack, abstraction, worklist)
        elif bytecode.get('condition') == 'gt':
            # if not a > b
            new_load = full_bytecode[full_bytecode.index(bytecode) + 1].get('offset')
            merge_forward(states, new_load, locals, new_stack, abstraction, worklist)
            # if a > b
            new_load = full_bytecode[bytecode.get('target')].get('offset')
            merge_forward(states, new_load, locals, new_stack, abstraction, worklist)
        else:
            raise Exception("Not implemented: if")

    
    elif opr == 'ifz':
        new_stack = stack[:-1]
        x = stack[-1]
        if bytecode.get('condition') == 'le':
            # if not 0 <= x
            new_load = full_bytecode[full_bytecode.index(bytecode) + 1].get('offset')
            merge_forward(states, new_load, locals, new_stack, abstraction, worklist)
            # if 0 <= x
            new_load = full_bytecode[bytecode.get('target')].get('offset')
            merge_forward(states, new_load, locals, new_stack, abstraction, worklist)

        elif bytecode.get('condition') == 'ne':
            if x.low == 0 and x.high == 0:
                # if always not 0 != x
                new_load = full_bytecode[full_bytecode.index(bytecode) + 1].get('offset')
                merge_forward(states, new_load, locals, new_stack, abstraction, worklist)
            elif x.low < 0 and x.high < 0 or x.low > 0 and x.high > 0:
                # if always 0 != x
                new_load = full_bytecode[bytecode.get('target')].get('offset')
                merge_forward(states, new_load, locals, new_stack, abstraction, worklist)
            else:
                # if not 0 != x
                new_load = full_bytecode[full_bytecode.index(bytecode) + 1].get('offset')
                merge_forward(states, new_load, locals, new_stack, abstraction, worklist)
                # if 0 != x
                new_load = full_bytecode[bytecode.get('target')].get('offset')
                merge_forward(states, new_load, locals, new_stack, abstraction, worklist)
        elif bytecode.get('condition') == 'gt':
            if x.low <= 0 and x.high <= 0:
                # if always not 0 > x
                new_load = full_bytecode[full_bytecode.index(bytecode) + 1].get('offset')
                merge_forward(states, new_load, locals, new_stack, abstraction, worklist)
            elif x.low > 0 and x.high > 0:
                # if always 0 > x
                new_load = full_bytecode[bytecode.get('target')].get('offset')
                merge_forward(states, new_load, locals, new_stack, abstraction, worklist)
            else:
                # if not 0 > x
                new_load = full_bytecode[full_bytecode.index(bytecode) + 1].get('offset')
                merge_forward(states, new_load, locals, new_stack, abstraction, worklist)
                # if 0 > x
                new_load = full_bytecode[bytecode.get('target')].get('offset')
                merge_forward(states, new_load, locals, new_stack, abstraction, worklist)

        else:
            raise Exception(f"Unhandled condition: {bytecode.get('condition')}")
        
    elif opr == 'incr':
        new_locals = locals.copy()
        new_locals[bytecode.get('index')] = abstraction.add(locals[bytecode.get('index')], abstraction.from_integer(bytecode.get('amount')))
        new_load = full_bytecode[full_bytecode.index(bytecode) + 1].get('offset')

        
        merge_forward(states, new_load, new_locals, stack, abstraction, worklist)
        pass

    elif opr == 'negate':
        new_stack = stack[:-1]
        x = abstraction.mul(stack[-1], abstraction.from_integer(-1))
        new_load = full_bytecode[full_bytecode.index(bytecode) + 1].get('offset')
        merge_forward(states, new_load, locals, new_stack + [x], abstraction, worklist)

    elif opr == 'return':
        # Intentionally left blank
        pass

    elif opr == 'binary':
        if bytecode.get('operant') == 'mul':
            new_stack = stack[:-2]
            x = abstraction.mul(stack[-1], stack[-2])
            new_load = full_bytecode[full_bytecode.index(bytecode) + 1].get('offset')
            merge_forward(states, new_load, locals, new_stack + [x], abstraction, worklist)

        elif bytecode.get('operant') == 'div':
            new_stack = stack[:-2]
            b = stack[-1]
            a = stack[-2]
            if (b.low <= 0 and b.high >= 0) or math.isclose(b.low, .0, abs_tol=1e-50) or math.isclose(b.high, .0, abs_tol=1e-50):
                return "Yes, with exception, ArithmeticException"
            x = abstraction.div(a, b)
            new_load = full_bytecode[full_bytecode.index(bytecode) + 1].get('offset')
            merge_forward(states, new_load, locals, new_stack + [x], abstraction, worklist)

        elif bytecode.get('operant') == 'sub':
            new_stack = stack[:-2]
            b = stack[-1]
            a = stack[-2]
            print(f"b: {b}, a: {a}")
            #TODO Verify contents of a and b to be correct
            x = abstraction.sub(a, b)
            new_load = new_load = full_bytecode[full_bytecode.index(bytecode) + 1].get('offset')
            merge_forward(states, new_load, locals, new_stack + [x], abstraction, worklist)

        else:
            raise Exception(f"Unknown binary operator: {bytecode.get('operant')}")
        
    elif opr == 'get':

        if bytecode.get('field').get('name') == '$assertionsDisabled':
            new_stack = stack + [abstraction.from_integer(0)]
            new_load = full_bytecode[full_bytecode.index(bytecode) + 1].get('offset')
            merge_forward(states, new_load, locals, new_stack, abstraction, worklist)
        else:
            raise(f"Not implemented get: {bytecode.get('field').get('name')}")
        
    elif opr == 'goto':
        new_load = full_bytecode[bytecode.get('target')].get('offset')
        merge_forward(states, new_load, locals, stack, abstraction, worklist)

    elif opr == 'new':
        if bytecode.get('class') == 'java/lang/AssertionError':
            return "Yes, with exception, AssertionError"
        
        else:
            raise Exception(f"Unknown new class: {bytecode.get('class')}")

    else:
        raise Exception(f"Unknown opr: {opr}")


def print_states(states):
    for i, s in enumerate(states):
        if s is None:
            print(f"{i}: None")
        else:
            print(f"{i}: {s}")

def analyse(method, abstraction):
    # Initialize locals and stack
    locals = {}
    for i, p in enumerate(method.get('params')):
        locals[i] = (abstraction.from_type(p.get('type').get('base')))
        #locals[p.get('name')] = ValueExpr(p.get('type').get('base'), set())
    stack = []
    bytecode = method.get('code').get('bytecode')
    # Intialize states
    states = [None for _ in range(bytecode[-1].get('offset')+1)]
    # Intialize worklist and intial state
    worklist = [0]
    states[0] = (locals, stack)

    while worklist:
        load = worklist.pop()
        (lc, s), bc = states[load], get_bytecode_at_offset(bytecode, load)
        print(f"stack: {s}")
        print(f'locals: {lc}')
        print(f"bytecode: {bc}")
        opr = bc.get('opr')
        res = step(states, load, lc, s, bc, opr, worklist, abstraction, bytecode)
        if res is not None:
            print_states(states)
            return res


    print_states(states)


if __name__ == "__main__":
    # Get methods from specified file/path
    dir = glob.glob('./**/Arithmetics.json',recursive=True)
    
    # for all methods in files in dir
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
                print(20*"-")
                print(f"Method {method.get('name')}:")
                res = analyse(method, Bounds)
                if res is not None:
                    print(f"Result: {res}")
                print(20*"-")