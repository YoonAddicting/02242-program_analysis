import glob
from decompiler import *
pathtodir = "../ass5/"


if __name__ == "__main__":
    
    dir = glob.glob(pathtodir+'**/*.json',recursive=True)
    for dep in dir:
        
        decomp1 = decompile_file(dep)
        # test 1:
        #   compile1
        
        # test 2:
        #   decomp2
        #   compile2
        #   compare compile1 and compile2

        # test 3:
        #   functionality...
        
        


