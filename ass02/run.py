import re
import glob
from string import ascii_lowercase as alc
from itertools import count
from tree_sitter import Language, Parser
FILE = "ass02/languages.so" # the ./ is important
Language.build_library(FILE, ["ass02/tree-sitter-java"])
JAVA_LANGUAGE = Language(FILE, "java")


parser = Parser()
parser.set_language(JAVA_LANGUAGE)
#with open("./test.java", "rb") as f:
with open("ass02/course-02242-examples/src/dependencies/java/dtu/deps/simple/Example.java", "rb") as f:
    tree = parser.parse(f.read())
# the tree is now ready for analysing




class SyntaxFold:
  def visit(self, node):
    results = [ self.visit(n) for n in node.children ]
    if hasattr(self, node.type):
      return getattr(self, node.type)(node, results)
    else:
      return self.default(node, results)
  def default(self, node):
    return None
  

class TypeFold:
  def visit(self, node, t):
    results = [ self.visit(n, t) for n in node.children ]
    if hasattr(node, "type"):
        if getattr(node, "type") == t:
            return self.default(node, results) #getattr(self, node.type)(node, results, t)
    else:
        return None
  def default(self, node):
    return None
      
class Printer(TypeFold):
  def default(self, node, results):
    print(f"{node} --> {node.text}")


class File:
    def __init__(self, filename, counter):
        self.filename = filename
        self.counter = counter
        self.dependencies = {}



# Printer().visit(tree.root_node)
#print(tree.root_node.sexp())


if __name__ == "__main__":
    res="digraph SourceGraph {"
    iterator = count(1)
    
    dir = glob.glob('**/*.java',recursive=True)

    # make a list of classes
    files = {}
    trees = {}
    for dep in dir:
        with open(dep, "rb") as f:
          tree = parser.parse(f.read())
        trees[dep] = tree

        #print(Printer().visit(tree.root_node))
        #print(TypeFold().visit(tree.root_node, 'package_declaration'))
        Printer().visit(tree.root_node, 'package_declaration')



        files[dep] = File(dep,iterator)
        res=res+"\n"+str(files[dep].counter)+" [label=\""+files[dep].filename+"\"];"
        

    # for every file find the dependecies
    for dep in dir:
      tree = trees[dep]

      #Printer().visit(tree.root_note)


      f = open(dep, "r")
      s = f.read()

      # find dependencies
      # inheritance (extends)
      # realization (implements)
      # aggregation (fields)
      # composition (non-static inner class)
      # dependency (imports and dependecies)
         

    print(res+"\n}")

