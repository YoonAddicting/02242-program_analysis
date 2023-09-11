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

def make_nodes(dir, g):
  for dep in dir:
    file = json.loads(open(dep).read())

    name = file.get('name')
    
    # aggregation (fields)
    # if its another class make edge
    fields = set()
    methods = set()
    field_txt = ""
    method_txt = ""
    for field in file['fields']:
      # Add visibility for fields
      if field.get('access') == 'public':
        field_txt = field_txt + "+ "
      elif field.get('access') == 'private':
        field_txt = field_txt + "- "
      elif field.get('access') == 'protected':
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
      if method.get('access') == 'public':
        method_txt = method_txt + "+ "
      elif method.get('access') == 'private':
        method_txt = method_txt + "- "
      elif method.get('access') == 'protected':
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
          

      name = file.get('name')

      dependencies = set()
      # inheritance (extends)
      g.attr('edge',style='solid')
      for dep in file['super']:
        s = file.get('name')
        if name != s:
          g.edge(name, s, "inheritance")
      dependencies = set()

      # realization (implements)   
      g.attr('edge',style='dashed')
      g.attr('edge',arrowhead='empty')
      
      for dep in file['interfaces']:
        s = file.get('name')
        if name != s:
          g.edge(name, s, "realization")
      dependencies = set()
      
      # dependency (imports and dependecies)
      g.attr('edge',arrowhead='vee')
      #   import_declaration
      #   No....

      #   type_identifier
      
      for dep in dependencies:
        if name != dep:
          g.edge(name, dep, "dependency")

      dependencies = set()
      #   method_invocation
      for dep in dependencies:
        s0 = re.search('[A-Z].*(?=\.)', dep)
        if s0 is None:
          continue
        s = s0.group()   
        if name != s:
          g.edge(name, s, "dependency")

if __name__ == "__main__":
    g = graphviz.Digraph()
    g.attr('node',shape='record', style='filled', fillcolor='gray95',fontname='Helvetica,Arial,sans-serif')
    g.attr('edge',fontname='Helvetica,Arial,sans-serif')
    g.attr('node',fontname='Helvetica,Arial,sans-serif')
    
    dir = glob.glob('./course-02242-examples/src/dependencies/java/dtu/**/*.json',recursive=True)

    make_nodes(dir, g)

    #make_edges(dir, g)
    
    #test = json.loads(open(dir[0]).read())
    #print()
    #for method in test['methods']:
    #  print(method['name'])
    #  print(method['params'])
    #  print(method['returns'])
    #  print()

    print(g.source)

