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
    
    dir = glob.glob('**/*.java',recursive=True)

    # make a list of classes
    names = []
    files = []
    for dep in dir:
        m = re.search('[A-Za-z]*(?=.java)',dep)
        names.append(m.group(0))
        f = File(dep,0)
        files.append(f)

    # for every file find the dependecies
    for i in range(len(dir)):
        f = open(dir[i], "r")
        s = f.read()
        #g = re.findall('(?<=//)*(?<=import\s)[^;]*(?=;)', s)
        g = re.findall('(?=//).*(?=\n)',s)
        # remove in-line comments
        for smth in g:
            s = s.replace(smth, '')
        f = re.findall('\/\*[^\/]*',s)
        for smth in f:
            s = s.replace(smth, '')

        # find dependencies
        for n in names:
            a = re.search("(?<=new\s)"+n,s)
            if a is not None:
                print(a.group(0)+" -> "+files[i].filename)
        
        n = re.findall('(?<=import\s)[^;]*(?=;)', s)
        print(str(n)+" -> "+ files[i].filename)
        
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
