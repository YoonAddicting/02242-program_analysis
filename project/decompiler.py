import json
import re
import os
import glob
import copy


def parse_file_name(file_name) -> (str, str):
    if file_name == None:
        return ("", "")
    
    name = ""
    package = ""
    name_opt = re.search('[^/]*$', file_name)
    package_opt = re.search('^.*(?=/)', file_name)
    
    if name_opt is None:
        raise Exception("Could not find name")
    else:
        name = name_opt.group()
    
    if package_opt is None:
        print(f"file {name} has no package")
    else:
        package = package_opt.group()
    
    return package, name


class condition:
    def __init__(self, target, cond, loop, cont):
        self.target = target
        self.cond = cond
        self.loop = loop
        self.cont = cont
        self.body = []

class java_file:
    def __init__(self, json):
        self.json = json
        file_name = json.get('name')

        innerclasses = self.json.get("innerclasses")
        if len(innerclasses) > 0:
            self.is_innerclass = False
            for innerclass in innerclasses:
                if file_name == innerclass.get("class"):
                    self.is_innerclass = True
                    self.name = innerclass.get("name")
                    self.package, _ = parse_file_name(file_name)
        else:
            self.is_innerclass = False


        if not self.is_innerclass:
            self.package, self.name = parse_file_name(file_name)
        
        self.imports = []

        
        self.java_class = java_class(self)
    
    def add_import(self, path, import_name : str):
        if self.package == path or path == "java/lang" or path == "":
            return
        if import_name == None:
            return
        
        import_name = import_name.replace("/",".")
        if import_name not in self.imports:
            self.imports.append(import_name)

    def export_code(self):
        code = ""
        # package declaration
        if self.package != "":
            code = code + "package "+ self.package.replace("/",".") + ";\n"

        # imports
        for i in self.imports:
            code = code + f"import {i};\n"

        # Class
        #   fields
        #   methods  
        # sort file alphabetically?
        code = code + self.java_class.export_class()
        
        return code


class java_class:
    def __init__(self, java_file : java_file):
        self.parent = java_file
        self.json = self.parent.json
        self.class_name = self.parent.name
        self.parse_access()
        if len(self.json.get('typeparams')) != 0:
            raise Exception("Typeparams are not implemented")
        if self.json.get('super').get('name') != "java/lang/Object":
            raise Exception("Non-object super classes not implemented")
        self.parse_interfaces()
        self.parse_fields()
        self.parse_methods()

    def parse_interfaces(self):
        self.interfaces = []
        for i in self.json.get('interfaces'):
            name = i.get('name')
            interface_package, name = parse_file_name(name)
            self.parent.add_import(interface_package, f"{interface_package}/{name}")
            type = None
            try: 
                if i.get('args')[0].get('kind') == "simple":
                    argument_package, type = parse_file_name(i.get('args')[0].get('type').get('name'))
                    self.parent.add_import(argument_package, f"{argument_package}/{type}")
                    self.interfaces.append(java_interface(name, type))
                else:
                    raise Exception("Unhandled interface situation")
            except:
                raise Exception("Unhandled interface situation")

    def parse_access(self):
        # A class itself can only be public or default (no modifier)
        # Source:  https://www.tutorialspoint.com/can-we-declare-a-top-level-class-as-protected-or-private-in-java
        # TODO Not considering inner classes
        if "public" in self.json.get('access'):
            self.access = "public"
        else:
            self.access = ""   
    
    def parse_fields(self):
        self.fields = []
        for f in self.json.get('fields'):
            # Get the name of the field
            field_name = f.get('name')
            field_type = f.get('type')
            # Parse access
            access = " ".join(f.get('access'))
            #for a in f.get("access"):
            #    access = access + " " + a
            # TODO: Check if field is not class or if it has args or annotations
            if "base" in field_type:
                field_type = f.get('type').get('base')
            elif "kind" in field_type and field_type.get("kind") == "class":
                # Parse the field path and type
                type_name = f.get('type').get('name')
                field_path, field_type = parse_file_name(type_name)
                # Add an import if the other class isn't in the same folder
                self.parent.add_import(field_path ,type_name)
            else:
                # TODO Currently doesn't handle field_type without args or annotations
                print("Unhandled field situation!")
        
            # Parse value of field
            val = f.get("value")
            value = ""
            if val is  not None:
                value = val.get("value")
            else:
                value = None

            # Create the field
            field = java_field(field_name, field_type, access, value)
        
            self.fields.append(field)


    def parse_methods(self):
        self.methods = []
        for m in self.json.get("methods"):
            if m.get('name') == "<init >":
                self.parse_init(m)
            else:
                method = java_method(m, self)
                self.methods.append(method)
    
    def export_class(self):
        res = self.access + " class " + self.class_name + "{\n" 
        for f in self.fields:
            res = res + f.export_field() + "\n"
        for m in self.methods:
            res = res + m.export_method() + "\n"

        return res+ "}"
    
class java_interface:
    def __init__(self, name, type = None):
        self.name = name
        self.type = type
    
    def export_interface(self):
        if self.type is not None:
            return f"{self.name}<{self.type}>"
        else:
            return f"{self.name}"
        
class java_field:
    def __init__(self, name, type, access, value):
        self.name = name
        self.type = type
        self.access = access
        self.value = value
    
    def export_field(self):
        end =";"
        if self.value is not None:
            end = f" = {self.value};"
        return f"{self.access} {self.type} {self.name}{end}"
    

class java_method:
    def __init__(self, json, parent : java_class):
        self.function_name = json.get("name")
        self.access = json.get("access")
        self.return_type = json.get("returns").get("type")
        self.variable_number = 0
        self.parent = parent
        self.stack = []
        self.locals = []
        self.parse_typeparams(json.get("typeparams"))
        self.parse_arguments(json.get("params"))
        self.code = json.get("code")
        self.annotations = json.get("annotations")
        self.parse_code()
    
    def parse_type_to_string(self, a):
        res = ""
        t = a.get("kind")
        while t == 'array':
            res += "[]"
            a = a.get("type")
            t = a.get("kind")
        return a.get("base")+res
    
    def parse_to_string(self, v):
        if isinstance(v,str):
            return v
        if isinstance(v, int):
            return v
        
        if isinstance(v, list):
            new = [self.parse_to_string(e) for e in v]
            arr = "{"
            arr += ", ".join([str(a) for a in new])
            arr += "}"
            return arr
            
        t = v.get("type")
        v = v.get("value")
        if t == "string":
            
            v = repr(v)
            v = v.replace("'", '"') 
        return str(v)
    
    def parse_condition(self, str):
        match str:
            case "eq":
                return "!="
            case "ne":
                return "=="
            case "lt":
                return ">="
            case "ge":
                return "<"
            case "gt":
                return "<="
            case "le":
                return ">"
            case _:
                raise Exception(f"condition not defined")
    
    def parse_typ(self, typ):
        match typ:
            case "add":
                return "+"
            case "sub":
                return "-"
            case "mul":
                return "*"
            case "div":
                return "/"
            case "rem":
                return "%"
            case "shl":
                return "<<"
            case "shr":
                return ">>"
            case "ushr":
                return ">>>"
            case "and":
                return "&"
            case "or":
                return "|"
            case "xor":
                return "^"
            case _:
                raise Exception("operation not recognized")

    def generate_variable_name(self) -> str:
        old_number = self.variable_number
        self.variable_number += 1
        return f"n{old_number}"
    
    def parse_typeparams(self, typeparams):
        self.typeparams = []
        for typeparam in typeparams:
            self.typeparams.append(typeparam.get("name"))

    def parse_arguments(self, params):
        self.arguments = []
        for param in params:
            if param.get('type').get('kind') == "array":
                name = self.generate_variable_name()
                if param.get('type').get('type').get('kind') != "class":
                    path, arg_type = parse_file_name(param.get('type').get('type').get('base'))
                else:
                    path, arg_type = parse_file_name(param.get('type').get('type').get('name'))
                self.arguments.append(f"{arg_type}[] {name}")
                self.locals.append(name)
                self.parent.parent.add_import(path, f"{path}/{arg_type}")

            elif param.get('type').get('kind') == "class":
                name = self.generate_variable_name()
                path, class_name = parse_file_name(param.get('type').get('name'))
                self.arguments.append(class_name + " " + name)
                self.locals.append(name)

                self.parent.parent.add_import(path, f"{path}/{class_name}")
            else:
                name = self.generate_variable_name()
                if param.get('type').get('kind') == "typevar":
                    typevar = param.get('type').get('name')
                    self.arguments.append(f"{typevar} {name}")
                else:
                    self.arguments.append(param.get("type").get("base") + " " + name)
                self.locals.append(name)
                

    def parse_code(self):
        self.method_body = []
        # the conditionals currently unfinished
        Cmpopr = []
        # for ease of use
        latest_cmp = None
        arrays = []

        if self.function_name == "<init>":
            # Skip first two instructions of init, unless it's inner method, then five
            if self.parent.parent.is_innerclass:
                bytecode = self.code.get('bytecode')[5:]
            else:
                bytecode = self.code.get('bytecode')[2:]
        else:
            bytecode = self.code.get('bytecode')
           
        for (curpos, bc) in enumerate(bytecode):
            # If the current conditional is done
            if bc == "":
                continue
            if len(Cmpopr) != 0 and latest_cmp.target == curpos:
                # Build the code output
                code = ""
                nest = len(Cmpopr)

                element = Cmpopr.pop()
                if element.cond !="":
                    if element.loop:
                        code += "while "
                    else:
                        code += "if "
                    code += "(" + element.cond + ")"
                code += " {\n"+"\t"*(nest+1)
                code += ("\n"+"\t"*(nest+1)).join(element.body)
                code += "\n"+"\t"*nest+"}"
                if element.cont:
                    code += " else "
                
                # If there are still conditionals load into latest
                if len(Cmpopr) != 0:
                    latest_cmp = Cmpopr[-1]
                    latest_cmp.body.append(code)
                else:
                    latest_cmp = None
                    self.method_body.append(code)

            opr = bc.get('opr')
            match opr:
                case "load":
                    
                    # works for ref at least
                    index = bc.get("index")
                    if len(self.locals) <= index:
                        self.stack.append("")
                    else:
                        self.stack.append(self.locals[index])
                        
                    
                case "new":
                    value = ""
                    try:
                        ref = self.stack.pop()
                    except:
                        ref = ""
                    package_name, class_name = parse_file_name(bc.get('class'))
                    # Add the import
                    
                    self.parent.parent.add_import(package_name, f"{package_name}/{class_name}")
                    value += f"new {class_name}"
                    self.stack.append((ref,value))

                case "dup":
                    if bc.get('words') == 1 or len(self.stack) == 1:
                        self.stack.append(self.stack[-1])
                    elif bc.get('words') == 2:
                        self.stack.append(self.stack[-2])
                        self.stack.append(self.stack[-2])
                    else:
                        raise Exception("Unhandled dup")
                case "dup_x1":
                    if bc.get('words') == 1 or len(self.stack) == 2:
                        self.stack.insert(-2, self.stack[-1])
                    elif bc.get('words') == 2:
                        self.stack.insert(-3, self.stack[-2])
                        self.stack.insert(-3, self.stack[-1])
                    else:
                        raise Exception("Unhandled dup_x1")
                case "dup_x2":
                    if bc.get('words') == 1 or len(self.stack) == 3:
                        self.stack.insert(-3, self.stack[-1])
                    elif bc.get('words') == 2:
                        self.stack.insert(-4, self.stack[-2])
                        self.stack.insert(-4, self.stack[-1])
                    else:
                        raise Exception("Unhandled dup_x2")
                case "store":
                    index = bc.get("index")
                    stack_elem = self.stack.pop()
                    

                    # if the element is ref
                    if bc.get('type') == "ref":
                        if isinstance(stack_elem, int):
                            arr = arrays[stack_elem]                        
                            i = 1
                            a = arr[0]
                            while isinstance(a, list):
                                i += 1
                                a = a[0]
                            bc_idx = bytecode.index(bc)
                            # Get the i'th previous bytecode, and check if it is an array_store
                            prev_bc = bytecode[bc_idx-i]
                            if prev_bc.get('opr') == "array_store":
                                # If it is, get the type from there.
                                typ = f'{prev_bc.get("type")}{"[]"*i}'
                            else:
                                t = str(type(a))
                                t = re.search("(?<=').*(?=')", t).group(0)
                                typ = f'{t}{"[]"*i}'

                            if arr == len(arr)*[0]:
                                value = f"new {t}[{len(arr)}]"
                            elif i > 1 and all(0 in sublist for sublist in arr):
                                # Multi dimensional array
                                brack = i*f"[{len(arr)}]"
                                value = f"new {t}{brack}"
                            else:
                                value = self.parse_to_string(arr)
                            arrays[stack_elem] = None
                                
                        else:
                            if len(stack_elem) == 2:
                                lhs = ""
                                (rhs, ref) = stack_elem
                            elif len(stack_elem) == 3:
                                (lhs, rhs, ref) = stack_elem
                            if lhs != "":
                                raise Exception("Unhandled store, lhs not empty")
                            package_name, class_name = parse_file_name(ref.get('name'))
                            
                            self.parent.parent.add_import(package_name, f"{package_name}/{class_name}")
                    
                            typ = f"{class_name}"
                            value = f"{rhs}"
                        
                    else:
                        typ = bc.get("type")
                        if isinstance(stack_elem,str):
                            value = stack_elem
                        elif len(stack_elem)==3:
                            (_,_,value) = stack_elem
                            if not isinstance(value, str):
                                value = value.get("value")
                        else:
                            value = stack_elem.get('value')

                   
                    new = False
                    while len(self.locals) <= index:
                        self.locals.append(self.generate_variable_name())
                        new = True
                    
                        
                    value = self.parse_to_string(value)
                    if new:
                        text = f"{typ} {self.locals[index]} = {value};"
                    else:
                        text = f"{self.locals[index]} = {value};"
                    
                    if len(Cmpopr) != 0:
                        latest_cmp.body.append(text)
                    else:
                        self.method_body.append(text)
                    
                case "push":
                    self.stack.append(("","", bc.get("value")))
                    #self.stack.append(bc.get("value"))
                case "binary" | "bitopr":
                    typ = bc.get("operant")
                    b = self.stack.pop()
                    a = self.stack.pop()
                    if type(a) is tuple:
                        (_,_,a) = a
                        if type(a) is dict:
                            a = a.get("value")
                    if type(b) is tuple:
                        (_,_,b) = b
                        if type(b) is dict:
                            b = b.get("value")
                    a = self.parse_to_string(a)
                    b = self.parse_to_string(b)
                    typ = self.parse_typ(typ)
                    self.stack.append(f"({a} {typ} {b})")
                    
                case "incr":
                    index = bc.get("index")
                    amount = bc.get("amount")
                    if amount < 0:
                        code = f"{self.locals[index]} -= {abs(amount)};"
                    else:
                        code = f"{self.locals[index]} += {amount};"
                    
                    if len(Cmpopr) != 0:
                        latest_cmp.body.append(code)
                    else:
                        self.method_body.append(code)
                case  "negate":
                    a = self.stack.pop()
                    self.stack.append(f"-{a}")
                case "array_load":
                    index = self.stack.pop()

                    if type(index) is tuple:
                        (_,_,index) = index
                        if type(index) is dict:
                            index = index.get("value")

                    ref = self.stack.pop()
                    index = self.parse_to_string(index)
                    
                    self.stack.append(("","",f"{ref}[{index}]"))
                case "array_store":
                    value = self.stack.pop()
                    if type(value) is tuple:
                        (_,_,value) = value
                    if bc.get('type') == "ref":
                        if type(value) is dict:
                            value = value.get("value")
                        value = arrays[value]
                    elif not isinstance(value, str):
                        value = value.get("value")
                    index = self.stack.pop()
                    if type(index) is tuple:
                        (_,_,index) = index
                        index = index.get("value")
                    ref = self.stack.pop()
                    if isinstance(ref, int):
                        arrays[ref][index] = value
                    else:
                        value = self.parse_to_string(value)
                        index = self.parse_to_string(index)
                        code = f"{ref}[{index}] = {value};"
                        if len(Cmpopr) != 0:
                            latest_cmp.body.append(code)
                        else:
                            self.method_body.append(code)
                case "newarray":
                    dim = bc.get("dim")

                    index = len(arrays)

                    for i in range(dim):
                        (_,_,a) = self.stack.pop()
                        a = a.get("value")
                        if i == 0:
                            arrays.append([0]*a)
                        else:
                            for i in range(len(arrays[index])):
                                arrays[index][i] = [0]*a

                    self.stack.append(index)
                case "arraylength":
                    arr = self.stack.pop()
                    self.stack.append(f"{arr}.length")
                case "invoke":
                    access = bc.get('access')
                    match access:
                        case "static":
                            if bc.get('method').get('ref').get('kind') == "class":
                                # pop potential arguments
                                args = []
                                for i in range(len(bc.get("method").get("args"))):
                                    a = self.stack.pop()
                                    a = self.parse_to_string(a)
                                    args.append(a)

                                package_name, class_name = parse_file_name(bc.get('method').get('ref').get('name'))
                                # Add the import
                                self.parent.parent.add_import(package_name, f"{package_name}/{class_name}")
                                method_name = bc.get('method').get('name')
                                
                                """if len(bc.get('method').get('args')) != 0:
                                    raise Exception("Unhandled: Method invokation has arguments")
                                """
                                code = f"{class_name}.{method_name}("
                                for i, arg in enumerate(args):
                                    if i != 0:
                                        code += ", "
                                    code += arg
                                code += ")"
                                if bc.get("method").get("returns") == None:
                                    code += ";"
                                    if len(Cmpopr) != 0:
                                        latest_cmp.body.append(code)
                                    else:
                                        self.method_body.append(code)
                                else:
                                    self.stack.append(code)
                        case "virtual":
                            # pop potential arguments
                            args = []
                            for i in range(len(bc.get("method").get("args"))):
                                (_,_,a) = self.stack.pop()
                                a = self.parse_to_string(a)
                                args.append(a)
                            ref = self.stack.pop()
                            method_name = bc.get("method").get("name")
                            
                            """arg_name = bc.get("method").get("args")[0].get("name")
                            if arg_name != "java/lang/String":
                                raise Exception(f"Undandled argument type: {arg_name}")
                            """
                            code = f'{ref}.{method_name}('
                            for i, arg in enumerate(args):
                                if i != 0:
                                    code += ", "
                                code += arg
                            code += ");"
                    
                            if len(Cmpopr) != 0:
                                latest_cmp.body.append(code)
                            else:
                                self.method_body.append(code)

                        case "special":
                            (lhs, rhs) = self.stack.pop()
                            (lhs, rhs) = self.stack.pop()
                            rhs += "("
                            for arg in bc.get('method').get('args'):
                                raise Exception("Don't handle args for calling new classes")
                            rhs += ")"
                            self.stack.append((lhs, rhs, bc.get('method').get('ref')))
                        case _:
                            raise Exception(f"Unhandled access type: {access}")
                case "put":
                    if not bc.get("static"):
                        (lhs, rhs, ref) = self.stack.pop()
                        if lhs == "":
                            field_name = bc.get("field").get("name")
                            field_name_found = False
                            if rhs == "":
                                rhs = ref.get('value')
                            for field in self.parent.fields:
                                if field.name == field_name:
                                    field.value = rhs
                                    field_name_found = True
                            if not field_name_found:
                                raise Exception(f"Could not find field {field_name}")
                        else:
                            text = f"{lhs}.{bc.get('field').get('name')} = {rhs};"
                            if len(Cmpopr) != 0:
                                latest_cmp.body.append(text)
                            else:
                                self.method_body.append(text)
                    else:
                        raise Exception("Unhandled put, not implemented for static fields")
                case "if" | "ifz":
                    # Make condition text
                    c = bc.get("condition")
                    a = self.stack.pop()
                    if type(a) is tuple:
                        (_,_,a) = a
                    a = self.parse_to_string(a)
                    b = 0
                    if opr == "if":
                        b = self.stack.pop()
                        if type(b) is tuple:
                            (_,_,b) = b
                        b = self.parse_to_string(b)
                    if opr == "ifz":
                        a, b = b, a
                    cond_text = f"{b} {self.parse_condition(c)} {a}" 

                    # Determine if it is loop or if else
                    loop = False
                    cont = False
                    target = bc.get("target")
                    target_bc = bytecode[target-1]
                    if target_bc.get('opr') == "goto":
                        t = target_bc.get('target')
                        if t < curpos:
                            loop = True
                        else:
                            cont = True
                        bytecode[target-1] = ""
                        

                    cond = condition(target, cond_text, loop, cont)
                    Cmpopr.append(cond)
                    latest_cmp = cond
                case "throw":
                    excp = self.stack[-1]
                    text = "throw " + str(excp)
                    if len(Cmpopr) != 0:
                        latest_cmp.body.append(text)
                    else:
                        self.method_body.append(text)
                case "goto":    
                    target = bc.get("target")

                    if target < curpos:
                        latest_cmp.body.append("continue;")
                    else:
                        latest_cmp.body.append("break;")

                case "get":
                    package_name, class_name = parse_file_name(bc.get('field').get('class'))
                    self.parent.parent.add_import(package_name, f"{package_name}/{class_name}")
                    if bc.get("static"):
                        value = f"{class_name}.{bc.get('field').get('name')}"                        
                        self.stack.append(value)
                    else:
                        value = self.stack.pop()
                        value += f".{bc.get('field').get('name')}"
                        self.stack.append(value)   
                case "return":
                    if bc.get("type") == None:
                        continue
                    text = self.stack.pop()
                    if type(text) is tuple:
                        (_,_,text) = text
                    text = self.parse_to_string(text)
                    text = "return " + text + ";"
                    if len(Cmpopr) != 0:
                        latest_cmp.body.append(text)
                    else:
                        self.method_body.append(text)
                case _:
                    raise Exception(f"Unhandled operation: {opr}")


    
    def export_method(self):
        if self.function_name == "<init>":
            return ""
        res = ""
        res += " ".join(self.access)
        if len(self.typeparams) != 0:
            res += " <"
            res += ", ".join(self.typeparams)
            res += ">"
        if self.return_type == None:
            res += " void "
        else:
            res += " " + self.parse_type_to_string(self.return_type) + " "
        
        res += f"{self.function_name}("
        parsed_arguments = []
        for argument in self.arguments:
            parsed_arguments.append(argument)
        res += ", ".join(parsed_arguments) + ") {\n\t"
        res += "\n\t".join(self.method_body)
        res += "\n}"
        
        return res
    

    
def decompile_file(dep, res_path = "project/res"):
    file_object = open(dep, 'r')
    file = json.loads(file_object.read())
    
    try:
        os.mkdir(res_path)
    except:
        pass

    jfile = java_file(file)

    o_code = jfile.export_code()
    return_path = "../../"
    os.chdir(res_path)
    package = jfile.package +"/"
    path = re.findall('[^/]+(?=/)',package)
    for p in path:
        try:
            os.mkdir(p)
        except:
            pass
        os.chdir(p)
        return_path += "/.."
    
    with open(f"{jfile.name}.java", 'w') as f:
        f.write(o_code)
    
    
    os.chdir(return_path)
    file_object.close()
   
    
    


def decompile_dir(path, res_path = "project/res"):
    
    dir = glob.glob(f'{path}**/*.json',recursive=True)
    for file in dir:
        file = file.replace("\\","/")
        decompile_file(file, res_path)
    

if __name__ == '__main__':
    #os.chdir("project")
    
    
    decompile_file('ass05/course-02242-examples/decompiled/eu/bogoe/dtu/Integers.json')
    #decompile_file('ass05/course-02242-examples/decompiled/dtu/deps/util/Utils.json')
    #decompile_dir('ass05/course-02242-examples/decompiled/dtu/deps/simple/')
    #decompile_dir('ass05/course-02242-examples/decompiled/dtu/deps/util/')
    #decompile_dir('ass05/course-02242-examples/decompiled/dtu/deps/tricky/')
    #decompile_file('ass05/course-02242-examples/decompiled/dtu/compute/exec/Calls.json')
    decompile_file('ass05/course-02242-examples/decompiled/dtu/compute/exec/Array.json')
    
    #decompile_dir('project/res0/dtu/deps/simple/')
    #decompile_file('ass05/course-02242-examples/decompiled/dtu/deps/tricky/Tricky.json')

    