import re
import glob
import graphviz
import json
from enum import Enum


'''
class TypeFold:
  def visit(self, node, t, results):
    for n in node.children:
      self.visit(n, t, results)
    if hasattr(node, "type"):
        if getattr(node, "type") == t:
            return results.add(self.default(node)) #getattr(self, node.type)(node, results, t)
    else:
        return None   
  def default(self, node):
    return None
  
class Extractor(TypeFold):
  def default(self, node):
    return bytes.decode(node.text, 'utf-8')
    pass

class Dependencies(Enum):
   INHERITANCE = 1
   REALIZATION = 2
   AGGREGATION = 3
   COMPOSITION = 4
   DEPENDENCY = 5


class File:
    def __init__(self, filename, counter):
        self.filename = filename
        self.counter = counter
        self.dependencies = {}
        self.fields = {}
'''

def check_args(args, g, i_name):
  if args:
    for arg in args:
      type_name = arg.get('type').get('name').replace('/','.')
      if type_name != "java.lang.Object":
        if i_name != type_name:
          g.edge(i_name, type_name, "realization")
        #types.append(arg.get('type').get('name'))
        check_args(arg.get('type').get('args'), g, type_name)

def nested_types(type):
  try:
    if type.get('kind') == "typevar":
      res = type.get('bound')
      return res
    else: 
      res=type.get('name')
      return res
  except: 
    t = type.get('type')
    return nested_types(t)
  
  

def make_nodes(dir, g):
  for dep in dir:
    file = json.loads(open(dep).read())

    name = file.get('name').replace('/','.')
    
    # aggregation (fields)
    # if its another class make edge
    fields = set()
    methods = set()
    field_txt = ""
    method_txt = ""
    for field in file['fields']:
      # Add visibility for fields
      if field.get('access'):
        if field.get('access')[0] == 'public':
          field_txt = field_txt + "+ "
        elif field.get('access')[0] == 'private':
          field_txt = field_txt + "- "
        elif field.get('access')[0] == 'protected':
          field_txt = field_txt + "# "
      else: 
        field_txt = field_txt + "~ "
      # Extract type of field
      # If type is not a base (int, float etc.)
      if 'name' in field['type']:
        t = field['type'].get('name')
        res = re.search('(?<=/)[A-Z].*', t).group()
        field_txt = field_txt + res + " "
      else:
        t = field['type'].get('base')
        field_txt = field_txt + t + " "
      

      
      # Extract the name of the field
      field_txt = field_txt + field.get('name') + "\\l"
      
    '''
    private <Other> void hello(/*dtu.deps.simple.Other*/ Utils Other) {
        Tricky dtu = new Tricky();
        simple.Other = new Example();
    }
    '''
    for method in file['methods']:
      # Add visibility for methods 
      if method.get('name') != "<init>":
        if method.get('access'):
          if method.get('access')[0] == 'public':
            method_txt = method_txt + "+ "
          elif method.get('access')[0] == 'private':
            method_txt = method_txt + "- "
          elif method.get('access')[0] == 'protected':
            method_txt = method_txt + "# "
        else:
          method_txt = method_txt + "~ "
        # Extract the name of the method
        method_txt = method_txt + method.get('name') + "\\l"
    '''
    # composition (non-static inner class)
    Extractor().visit(tree.root_node, 'class_declaration')
    '''

    node_txt = "{{ {class_name} \\n |{{ {fields} }}| {methods} }}".format(class_name = name,
                                              fields = field_txt,
                                              methods = method_txt)
    g.node(name, label = node_txt)


def make_edges(dir, g):
   for dep in dir:
      file = json.loads(open(dep).read())
          

      name = file.get('name').replace('/','.')

      
      # inheritance (extends)
      g.attr('edge',style='solid')
      super_name = file['super'].get('name').replace('/','.') 
      if super_name != "java.lang.Object":
        g.edge(name, super_name, "inheritance")
      

      # realization (implements)   
      g.attr('edge',style='dashed')
      g.attr('edge',arrowhead='empty')
      
      for interface in file['interfaces']:
        i_name = interface.get('name').replace('/','.')
        #types = []
        # TODO Make args nested instead of flat
        if name != i_name:
          g.edge(name, i_name, "realization")
        check_args(interface.get('args'), g, i_name)
        #for type in types:
        #  g.edge(name, type, "realization")
      
      
      dependencies = set()
      # dependency (imports and dependecies)
      g.attr('edge',arrowhead='vee')
      #   import_declaration
      #   No....

      #   Types
      for field in file['fields']:
        t = nested_types(field.get('type'))
        dependencies.add(t)
      

      
      #   method invocation
      # params
      for method in file['methods']:
        for p in method['params']:
          type_name = nested_types(p.get('type'))
          dependencies.add(type_name)
          
        
        return_type = method.get('returns').get('type')

        if return_type != None:
          dependencies.add(nested_types(return_type))

        # code > bytecode 
        bc = method.get('code').get('bytecode')
        for code in bc:
          # invoke
          if code.get('opr') == "invoke":
            pass
            bc_method = code.get('method')
            # TODO Is this if-statement neccessary?
            if bc_method.get('is_interface') == False:
                dependencies.add(bc_method.get('ref').get('name'))
          # new
          if code.get('opr') == "new":
            dependencies.add(code.get('class'))

      for dep in dependencies:
        if dep is None:
          continue
        if dep == "java/lang/Object":
          continue
        dep = dep.replace('/','.')
        if dep == name:
          continue
        g.edge(name, dep, "dependency")

if __name__ == "__main__":
    g = graphviz.Digraph()
    g.attr('node',shape='record', style='filled', fillcolor='gray95',fontname='Helvetica,Arial,sans-serif')
    g.attr('edge',fontname='Helvetica,Arial,sans-serif')
    
    dir = glob.glob('./course-02242-examples/src/dependencies/java/dtu/**/*.json',recursive=True)

    make_nodes(dir, g)

    make_edges(dir, g)
    
    #test = json.loads(open(dir[0]).read())
    #print()
    #for method in test['methods']:
    #  print(method['name'])
    #  print(method['params'])
    #  print(method['returns'])
    #  print()

    print(g.source)

