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
        raise "Could not find name"
    else:
        name = name_opt.group()
    
    if package_opt is None:
        print(f"file {name} has no package")
    else:
        package = package_opt.group()
    
    return package, name

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
            code = code + i + "\n"

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
            raise "Typeparams are not implemented"
        if self.json.get('super').get('name') != "java/lang/Object":
            raise "Non-object super classes not implemented"
        if len(self.json.get('interfaces')) != 0:
            raise "Inferfaces are not implemented"
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
                raise "Unhandled field situation!"
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
                
    def parse_init(self, init):
        bc = init.get('code').get('bytecode')
        # Skip the initial load and invoke operations
        bc = bc[2:]
        field_index = None
        for code in bc:
            opr = code.get('opr')
            match opr:
                case 'load':
                    field_index = code.get('index')
                case 'new':
                    field = self.fields[field_index-1]
                    _, field_type = parse_file_name(code.get('class'))
                    field.value = f"new {field_type}" 
                case 'dup':
                    continue
                case 'invoke':
                    field = self.fields[field_index-1]
                    field_args = "("
                    for arg in code.get('method').get('args'):
                        raise "Don't handle args for calling new classes"
                    field_args += ")"
                    field.value += field_args
                case 'put':
                    continue
                case 'return':
                    continue
                case '_':
                    raise f"Unhandled opr: {opr}, in init"

    def parse_methods(self):
        self.methods = []
        for m in self.json.get("methods"):
            if m.get('name') == "<init>":
                self.parse_init(m)
            else:
                method = java_method(m)
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
    def __init__(self, json):
        self.function_name = json.get("name")
        self.access = json.get("access")
        self.return_type = json.get("returns").get("type")
        self.variable_number = 0
        self.parse_arguments(json.get("params"))
        self.stack = None
        self.locals = None
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
                _, arg_type = parse_file_name(param.get('type').get('type').get('name'))
                self.arguments.append((f"{arg_type}[]", self.generate_variable_name()))
            else:
                raise f"Non array parameter: {param.get('type').get('kind')}"

    def parse_code(self):
        self.method_body = []
        bytecode = self.code.get('bytecode')
        for bc in bytecode:
            opr = bc.get('opr')
            match opr:
                case "invoke":
                    if bc.get('method').get('ref').get('kind') == "class":
                        _, class_name = parse_file_name(bc.get('method').get('ref').get('name'))
                        method_name = bc.get('method').get('name')
                        if len(bc.get('method').get('args')) != 0:
                            raise "Unhandled: Method invokation has arguments"
                        code = f"{class_name}.{method_name}()"
                        self.method_body.append(code)
                case "return":
                    continue
                case "_":
                    raise f"Unhandled operation: {opr}"


    
    def export_method(self):
        res = ""
        res += " ".join(self.access)
        if self.return_type == None:
            res += " void "
        else:
            raise "Unhandled returntype when exporting code"
        
        res += f"{self.function_name}("
        parsed_arguments = []
        for argument in self.arguments:
            parsed_arguments.append(f"{argument[0]} {argument[1]}")
        res += ", ".join(parsed_arguments) + ") {\n    "
        res += ";\n    ".join(self.method_body)
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
    

    decompile_file('../ass05/course-02242-examples/decompiled/dtu/deps/simple/Example.json')
    decompile_dir('../ass05/course-02242-examples/decompiled/dtu/deps/simple/')
    