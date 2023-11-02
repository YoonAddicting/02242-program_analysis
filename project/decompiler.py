import json
import re
import os
import glob


def parse_file_name(file_name) -> (str, str):
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

def parse_condition(str):
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
""" 
        case "is":
           raise
        case "isnot":
            pass
"""

class java_file:
    def __init__(self, json):
        self.json = json
        file_name = json.get('name')
        
        self.package, self.name = parse_file_name(file_name)
        
        self.imports = []
        
        self.java_class = java_class(self)
    
    def add_import(self, import_name : str):
        import_name = import_name.replace("/",".")
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
        if len(self.json.get('interfaces')) != 0:
            raise Exception("Inferfaces are not implemented")
        self.parse_fields()
        self.parse_methods()

    
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
            # TODO: Check if field is not class or if it has args or annotations
            if field_type.get('kind') != "class" or len(field_type.get('args')) != 0 or len(field_type.get('annotations')) != 0:
                raise Exception("Unhandled field situation!")
            # Parse the field path and type
            type_name = f.get('type').get('name')
            field_path, field_type = parse_file_name(type_name)
            # Add an import if the other class isn't in the same folder
            if self.parent.package != field_path:
                self.parent.add_import(type_name)
            
            access = ""
            for a in f.get("access"):
                access = access + " " + a
            
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
        self.parse_arguments(json.get("params"))
        self.code = json.get("code")
        self.annotations = json.get("annotations")
        self.parse_code()

    def generate_variable_name(self) -> str:
        old_number = self.variable_number
        self.variable_number += 1
        return f"n{old_number}"

    def parse_arguments(self, params):
        self.arguments = []
        for param in params:
            if param.get('type').get('kind') == "array":
                name = self.generate_variable_name()
                path, arg_type = parse_file_name(param.get('type').get('type').get('name'))
                self.arguments.append((f"{arg_type}[]", name))
                self.locals.append(name)
                
            elif param.get('type').get('kind') == "class":
                name = self.generate_variable_name()
                path, class_name = parse_file_name(param.get('type').get('name'))
                self.arguments.append(class_name + " " + name)
                self.locals.append(name)

                if path!= self.parent.parent.package:
                    self.parent.parent.add_import(f"{path}/{class_name}")
            else:
                name = self.generate_variable_name()
                self.arguments.append(param.get("type").get("base") + " " + name)
                self.locals.append(name)
                

    def parse_code(self):
        self.method_body = []
        target = 0
        if self.function_name == "<init>":
            # Skip first two instructions if init
            bytecode = self.code.get('bytecode')[2:]
        else:
            bytecode = self.code.get('bytecode')
        for bc in bytecode:
            opr = bc.get('opr')
            match opr:
                case "load":
                    opr_type = bc.get("type")
                    match opr_type:
                        case "ref":
                            index = bc.get("index")
                            if len(self.locals) <= index:
                                self.stack.append("")
                            else:
                                self.stack.append(self.locals[index])
                        case _: 
                            raise Exception(f"Undefined load operation type: {opr_type}")
                    
                case "new":
                    value = self.stack.pop()
                    package_name, class_name = parse_file_name(bc.get('class'))
                    # Add the import
                    if package_name != self.parent.parent.package:
                        self.parent.parent.add_import(f"{package_name}/{class_name}")
                    value += f"new {class_name}"
                    self.stack.append(value)

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
                    out = self.stack.pop()
                    code = ""
                    if index == len(locals):
                        locals.append(self.generate_variable_name)
                        code = bc.get(type)
                    self.method_body.append(f"{code} {locals[index]} = {out}")
                    
                case "push":
                    self.stack.append(bc.get("value"))
                case "binary":
                    type = bc.get("operant")
                    match type:
                        case "add":
                            a = self.stack.pop()
                            b = self.stack.pop()
                            self.stack.append(f"({a}) + ({b})")
                        case "sub":
                            a = self.stack.pop()
                            b = self.stack.pop()
                            self.stack.append(f"({a}) - ({b})")
                        case "mul":
                            a = self.stack.pop()
                            b = self.stack.pop()
                            self.stack.append(f"({a}) * ({b})")
                        case "div":
                            a = self.stack.pop()
                            b = self.stack.pop()
                            self.stack.append(f"({a}) / ({b})")
                        case "rem":
                            a = self.stack.pop()
                            b = self.stack.pop()
                            self.stack.append(f"({a}) % ({b})")
                        case _:
                            raise Exception("Binary operation not recognized")
                case  "negate":
                    a = self.stack.pop()
                    self.stack.append(f"-({a})")
                
                case "invoke":
                    access = bc.get('access')
                    match access:
                        case "static":
                            if bc.get('method').get('ref').get('kind') == "class":
                                package_name, class_name = parse_file_name(bc.get('method').get('ref').get('name'))
                                # Add the import
                                if package_name != self.parent.parent.package:
                                    self.parent.parent.add_import(f"{package_name}/{class_name}")
                                method_name = bc.get('method').get('name')
                                if len(bc.get('method').get('args')) != 0:
                                    raise Exception("Unhandled: Method invokation has arguments")
                                
                                code = f"{class_name}.{method_name}()"
                                self.method_body.append(code)
                        case "special":
                            value = self.stack.pop()
                            value = self.stack.pop()
                            value += "("
                            for arg in bc.get('method').get('args'):
                                raise Exception("Don't handle args for calling new classes")
                            value += ")"
                            self.stack.append(value)
                        case _:
                            raise Exception(f"Unhandled access type: {access}")
                case "put":
                    if not bc.get("static"):
                        field_name = bc.get("field").get("name")
                        field_name_found = False
                        for field in self.parent.fields:
                            if field.name == field_name:
                                field.value = self.stack.pop()
                                field_name_found = True
                        if not field_name_found:
                            raise Exception(f"Could not find field {field_name}")
                    else:
                        raise Exception("Unhandled put, not implemented for static fields")
                case "if":
                    condition = bc.get("condition")
                    target = bc.get("target")
                    a = self.stack.pop()
                    b = self.stack.pop()
                    text = f"if ({a} " + parse_condition(condition) +" " +b +") {"
                    
                case "ifz":
                    condition = bc.get("condition")
                    target = bc.get("target")
                    a = self.stack.pop()
                    text = f"if ({a} " + parse_condition(condition) +" 0) {"
                    
                case "goto":

                    pass
                case "return":
                    continue
                case _:
                    raise Exception(f"Unhandled operation: {opr}")


    
    def export_method(self):
        if self.function_name == "<init>":
            return ""
        res = ""
        res += " ".join(self.access)
        if self.return_type == None:
            res += " void "
        else:
            raise Exception("Unhandled returntype when exporting code")
        
        res += f"{self.function_name}("
        parsed_arguments = []
        for argument in self.arguments:
            parsed_arguments.append(f"{argument[0]} {argument[1]}")
        res += ", ".join(parsed_arguments) + ") {\n\t"
        res += ";\n\t".join(self.method_body)
        res += ";\n}"
        
        return res
    

    
def decompile_file(dep):
    file_object = open(dep, 'r')
    file = json.loads(file_object.read())
    
    try:
        os.mkdir("res")
    except:
        pass

    jfile = java_file(file)

    o_code = jfile.export_code()
    return_path = ".."
    os.chdir("res")
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
   
    
    


def decompile_dir(path):
    
    dir = glob.glob(f'{path}**.json',recursive=True)
    for file in dir:
        decompile_file(file)
    

if __name__ == '__main__':
    os.chdir("project")
    

    #decompile_file('../ass05/course-02242-examples/decompiled/dtu/deps/simple/Example.json')
    #decompile_dir('../ass05/course-02242-examples/decompiled/dtu/deps/simple/')
    decompile_dir('res0/dtu/deps/simple/')
    