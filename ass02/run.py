import re
import glob
import graphviz
from string import ascii_lowercase as alc
from itertools import count
from tree_sitter import Language, Parser
from enum import Enum
FILE = "./languages.so" # the ./ is important
Language.build_library(FILE, ["tree-sitter-java"])
JAVA_LANGUAGE = Language(FILE, "java")


parser = Parser()
parser.set_language(JAVA_LANGUAGE)

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

def make_nodes(dir, g):
  for dep in dir:
    with open(dep, "rb") as f:
        tree = parser.parse(f.read())

    name = re.search('([A-Z].*)(?=.java)',dep).group()
    
    # aggregation (fields)
    fields = set()
    methods = set()
    field_txt = ""
    method_txt = ""
    Extractor().visit(tree.root_node, 'field_declaration', fields)
    Extractor().visit(tree.root_node, 'method_declaration', methods)
    for field in fields:
      #remove comments from both fields and methods
      q = re.findall('/\*.+?\*/',field,flags=re.DOTALL)
      for smth in q:
          field = field.replace(smth, '')

      res = re.search('([^=^;]*)',field).group()
      field_txt = field_txt + res + "\\l"

    '''
    private <Other> void hello(/*dtu.deps.simple.Other*/ Utils Other) {
        Tricky dtu = new Tricky();
        simple.Other = new Example();
    }
    '''
    for method in methods:
      q = re.findall('/\*.+?\*/',method,flags=re.DOTALL)
      for smth in q:
          method = method.replace(smth, '')
      res = re.search('([^{]*)',method).group()
      res = re.search('[^\s]*\(.*\)', res).group()
      method_txt = method_txt + res + "\\l"
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
      with open(dep, "rb") as f:
          tree = parser.parse(f.read())

      name = re.search('([A-Z].*)(?=.java)',dep).group()

      f = open(dep, "r")
      s = f.read()
      dependencies = set()
      # inheritance (extends)
      Extractor().visit(tree.root_node, 'super_classes', dependencies)
      for dep in dependencies:
         s = re.search('(?<=extends\s).*', dep).group()
         if name != s:
          g.edge(name, s, "inheritance")
      dependencies = set()

      # realization (implements)   
      Extractor().visit(tree.root_node, 'super_interfaces', dependencies)
      for dep in dependencies:
         s = re.search('(?<=implements\s).*', dep).group()
         if name != s:
          g.edge(name, s, "realization")
      dependencies = set()
      
      # dependency (imports and dependecies)
      #   import_declaration
      '''Extractor().visit(tree.root_node, 'import_declaration',dependencies)
      for d in dependencies:
        res = re.search('(?<=import\s).*', d)'''
      #   type_identifier
      Extractor().visit(tree.root_node, 'type_identifier', dependencies)
      for dep in dependencies:
        if name != dep:
          g.edge(name, dep, "dependency")

      dependencies = set()
      #   method_invocation
      Extractor().visit(tree.root_node, 'method_invocation', dependencies)
      for dep in dependencies:
        s = re.search('[A-Z].*(?=\.)', dep).group()
        if name != s:
          g.edge(name, s, "dependency")

if __name__ == "__main__":
    g = graphviz.Digraph()
    g.attr('node',shape='record')
    
    dir = glob.glob('./tests/**/*.java',recursive=True)

    make_nodes(dir, g)

    make_edges(dir, g)

    print(g.source)

