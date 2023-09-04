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
    res="digraph SourceGraph {"
    iterator = count(1)
    
    dir = glob.glob('**/*.java',recursive=True)

    # make a list of classes
    names = []
    files = []
    
    j=0
    for dep in dir:
        
        m = re.search('[A-Za-z]*(?=.java)',dep)
        names.append(m.group(0))
        f = File(dep,j)
        files.append(f)
        d=dep.replace('\\','\\\\')
        res=res+"\n"+str(j)+" [label=\""+d+"\"];"
        j=j+1

    # for every file find the dependecies
    for i in range(len(dir)):
        f = open(dir[i], "r")
        s = f.read()
        #g = re.findall('(?<=//)*(?<=import\s)[^;]*(?=;)', s)
        # Removed "?=" and (?=\n) as this seemed unnecessary. Before was: g = re.findall('(?=//).*(?=\n)',s) 
        g = re.findall('//.*',s)
        # remove in-line comments
        for smth in g:
            s = s.replace(smth, '')
        # remove multiline comments
        # changed .* in the middle of '/\*.*\*/' to .+?
        f = re.findall('/\*.+?\*/',s,flags=re.DOTALL)
        for smth in f:
            s = s.replace(smth, '')

        # find dependencies
        for n in names:
            a = re.search("(?<=new\s)"+n,s)
            if a is not None:
                l = a.group()
                res=res+"\n"+str(j)+" [label=\""+l+"\"];"
                res=res+"\n"+str(j)+" -> "+str(files[i].counter)+";"
                j=j+1
        
        n = re.findall('(?<=import\s)[^;]*(?=;)', s)
        for l in n:
            res=res+"\n"+str(j)+" [label=\""+l+"\"];"
            res=res+"\n"+str(j)+" -> "+ str(files[i].counter)+";"
            j=j+1
        
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
    """
    f=open("graph.dot","w")
    f.write(res)
    f.write("}")
    f.write("% well done")
    f.close
    """
    print(res+"\n}")

    
