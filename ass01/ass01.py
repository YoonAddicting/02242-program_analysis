import re
import glob
#import graphviz
from string import ascii_lowercase as alc
from itertools import count


class File:
    def __init__(self, filename, counter):
        self.filename = filename
        self.counter = counter
        self.dependencies = {}

'''
def generate_viz_text(files_dict):
    with open("source-graph.dot",'w') as f:
        f.write("digraph SourceGraph {")
        for label in files_dict.values():
            
        
        

        f.write("}")
    return 0

    '''


if __name__ == "__main__":

    iterator = count(1)
    
    dir = glob.glob('**/*.java')
    names = []
    for dep in dir:
        m = re.search('[A-Za-z]*(?=.java)',dep)

        names.append(m.group(0))
        

    for path in dir:
        f = open(path, "r")
        s = f.read()
        #g = re.findall('(?<=//)*(?<=import\s)[^;]*(?=;)', s)
        #print(g)
        g = re.findall('(?=//).*(?=\n)',s)
        for smth in g:
            s = s.replace(smth, '')

        n = re.findall('(?<=import\s)[^;]*(?=;)', s)
        print(n)
        #m= re.findall('(?<=//).*import.*(?=;\n)', s)
        
        #print(m)
        '''
        for dep in n:
            d = File(dep)
        
        '''
        # for dep in dir:
        #     #print(m.group(0))
        #     n = re.search('(?<=import\s).*(?=;)', s)
        #     #print(n.group(0))
