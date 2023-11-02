import glob
import unittest
import filecmp
import subprocess
pathtodir = "../ass05/"

class TestDtuDeps(unittest.TestCase):
    def test_decompile(self):
        from decompiler import decompile_dir
        
        i_dir = pathtodir+"course-02242-examples/decompiled/dtu/deps/simple/"
        decompile_dir(i_dir, "res")
        i_dir = pathtodir+"course-02242-examples/decompiled/dtu/deps/util/"
        decompile_dir(i_dir, "res")
        res_dir = "res/dtu/deps/"
        # Compile res_dir
        files = glob.glob(res_dir+"**/*.java", recursive=True)
        subprocess.run(["javac", "-cp", res_dir, *files], check=True)
        # Create json of res
        files = glob.glob(res_dir+"**/*.class", recursive=True)
        for file in files:
            target = file[:-6]+".json"
            subprocess.run(["jvm2json", "-s", file, "-t", target])
        
        decompile_dir(res_dir, "res2")
        print("test")
        # compare res_dir and res2_dir
        res2_dir = "res2/dtu/deps/"
        #files = ["normal/Primes.java", "normal/Primes$PrimesIterator.java", 
        #         "simple/Example.java", "simple/Other.java", 
        #         "tricky/Tricky.java", "util/Utils.java"]
        files = ["simple/Example.java", "simple/Other.java","util/Utils.java"]
        match, mismatch, errors = filecmp.cmpfiles(res_dir, res2_dir, files)
        print(f"match: {match}")
        print(f"mismatch: {mismatch}")
        print(f"errors: {errors}")
        assert(len(mismatch) == 0)
        assert(len(errors) == 0)

    # TODO Create test that compares original json with decompiled json


        


if __name__ == "__main__":
    unittest.main()
    '''
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
    ''' 
        


