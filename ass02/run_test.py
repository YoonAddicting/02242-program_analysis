import re
import glob
from string import ascii_lowercase as alc
from itertools import count
from tree_sitter import Language, Parser
FILE = "./languages.so" # the ./ is important
Language.build_library(FILE, ["tree-sitter-java"])
JAVA_LANGUAGE = Language(FILE, "java")


parser = Parser()
parser.set_language(JAVA_LANGUAGE)
#with open("./test.java", "rb") as f:
with open("./tests/simple/Example.java", "rb") as f:
    tree = parser.parse(f.read())
# the tree is now ready for analysing




class SyntaxFold:
  def visit(self, node):
    print(node.type)
    for n in node.children:
       self.visit(n)
    if hasattr(self, node.type):
      return getattr(self, node.type)
    else:
      return self.default(node)
  def default(self, node):
    return None



class Printer(SyntaxFold):
  def default(self, node):
    #print(node.type)
    if node.type == 'type_identifier':
       print("hello")
    #print(f"{node} --> {node.text}")


class File:
    def __init__(self, filename, counter):
        self.filename = filename
        self.counter = counter
        self.dependencies = {}



Printer().visit(tree.root_node)
#print(tree.root_node.sexp())
