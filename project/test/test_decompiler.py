import glob
import unittest
import filecmp
import subprocess
import shutil
import json
import os

def pretty_print_json(file):
        with open(file, "r") as f:
            txt = f.read()
            json_object = json.loads(txt)
        json_formatted_str  = json.dumps(json_object, indent=4)

        with open(file, "w") as f:
            f.write(json_formatted_str)

class CompileTest:
    def __init__(self, sc_path, out_path, files):
        self.sc_path = sc_path
        self.files = files
        self.out_path = out_path
        self.compile()

    def compile(self):
        subprocess.run(["javac", "-cp", self.sc_path, *self.files], check=True)
        self.jvm2json()
    
    def jvm2json(self):
        # Create json of res
        files = glob.glob(self.sc_path+"**/*.class", recursive=True)
        for file in files:
            target = file[:-6]+".json"
            subprocess.run(["jvm2json", "-s", file, "-t", target])
            pretty_print_json(target)
            output = target
            target = target.split("/")
            target = '/'.join(target[-4:])
            target = self.out_path+target
            shutil.move(output, target)
            os.remove(file)


class TestDtuDepsSimpleUtils(unittest.TestCase):
    def test_decompile_simple_comp_source(self):
        pathtodir = "ass05/"
        # Compile simple with java 11
        sc_path = pathtodir+"course-02242-examples/src/dependencies/java/dtu/deps/"
        compiler = CompileTest(sc_path, 
                               pathtodir+"course-02242-examples/decompiled/", 
                               [sc_path+"simple/Example.java", 
                                sc_path+"simple/Other.java", 
                                sc_path+"util/Utils.java"]) 
        from project.decompiler import decompile_dir
        i_dir = pathtodir+"course-02242-examples/decompiled/dtu/deps/simple/"
        decompile_dir(i_dir, "project/res")
        i_dir = pathtodir+"course-02242-examples/decompiled/dtu/deps/util/"
        decompile_dir(i_dir, "project/res")
        res_dir = "project/res/dtu/deps/"
        # Compile res_dir
        files = glob.glob(res_dir+"**/*.java", recursive=True)
        subprocess.run(["javac", "-cp", res_dir, *files], check=True)
        # Create json of res
        files = glob.glob(res_dir+"**/*.class", recursive=True)
        for file in files:
            target = file[:-6]+".json"
            subprocess.run(["jvm2json", "-s", file, "-t", target])
            pretty_print_json(target)
        
        decompile_dir(res_dir, "project/res2")
        # compare res_dir and res2_dir
        res2_dir = "project/res2/dtu/deps/"
        files = ["simple/Example.java", "simple/Other.java","util/Utils.java"]
        match, mismatch, errors = filecmp.cmpfiles(res_dir, res2_dir, files)
        print(f"match: {match}")
        print(f"mismatch: {mismatch}")
        print(f"errors: {errors}")
        assert(len(mismatch) == 0)
        assert(len(errors) == 0)

    def test_decompile_simple_comp_json(self):
        pathtodir = "ass05/"
        # Compile simple with java 11
        sc_path = pathtodir+"course-02242-examples/src/dependencies/java/dtu/deps/"
        compiler = CompileTest(sc_path, 
                               pathtodir+"course-02242-examples/decompiled/", 
                               [sc_path+"simple/Example.java", 
                                sc_path+"simple/Other.java", 
                                sc_path+"util/Utils.java"]) 
        from project.decompiler import decompile_dir
        i_dir = pathtodir+"course-02242-examples/decompiled/dtu/deps/simple/"
        decompile_dir(i_dir, "project/res")
        i_dir = pathtodir+"course-02242-examples/decompiled/dtu/deps/util/"
        decompile_dir(i_dir, "project/res")
        res_dir = "project/res/dtu/deps/"
        # Compile res_dir
        files = glob.glob(res_dir+"**/*.java", recursive=True)
        subprocess.run(["javac", "-cp", res_dir, *files], check=True)
        # Create json of res
        files = glob.glob(res_dir+"**/*.class", recursive=True)
        for file in files:
            target = file[:-6]+".json"
            subprocess.run(["jvm2json", "-s", file, "-t", target])
            pretty_print_json(target)

        i_dir = pathtodir+"course-02242-examples/decompiled/dtu/deps/"
        files = ["simple/Example.json", "simple/Other.json","util/Utils.json"]
        match, mismatch, errors = filecmp.cmpfiles(res_dir, i_dir, files)
        print(f"match: {match}")
        print(f"mismatch: {mismatch}")
        print(f"errors: {errors}")
        assert(len(mismatch) == 0)
        assert(len(errors) == 0)


class TestDtuDepsTricky(unittest.TestCase):
    def test_decompile_tricky_source(self):
        pathtodir = "ass05/"
        # Compile tricky with java 11
        sc_path = pathtodir+"course-02242-examples/src/dependencies/java/dtu/deps/"
        compiler = CompileTest(sc_path, 
                               pathtodir+"course-02242-examples/decompiled/", 
                               [sc_path+"tricky/Tricky.java", 
                                sc_path+"simple/Example.java", 
                                sc_path+"simple/Other.java", 
                                sc_path+"util/Utils.java"])
        from project.decompiler import decompile_dir
        i_dir = pathtodir+"course-02242-examples/decompiled/dtu/deps/simple/"
        decompile_dir(i_dir, "project/res")
        i_dir = pathtodir+"course-02242-examples/decompiled/dtu/deps/util/"
        decompile_dir(i_dir, "project/res")
        i_dir = pathtodir+"course-02242-examples/decompiled/dtu/deps/tricky/"
        decompile_dir(i_dir, "project/res")
        res_dir = "project/res/dtu/deps/"
        # Compile res_dir
        files = glob.glob(res_dir+"**/*.java", recursive=True)
        subprocess.run(["javac", "-cp", res_dir, *files], check=True)
        # Create json of res
        files = glob.glob(res_dir+"**/*.class", recursive=True)
        for file in files:
            target = file[:-6]+".json"
            subprocess.run(["jvm2json", "-s", file, "-t", target])
            pretty_print_json(target)
        
        decompile_dir(res_dir, "project/res2")
        # compare res_dir and res2_dir
        res2_dir = "project/res2/dtu/deps/"
        files = ["simple/Example.java", "simple/Other.java","util/Utils.java", "tricky/Tricky.java"]
        match, mismatch, errors = filecmp.cmpfiles(res_dir, res2_dir, files)
        print(f"match: {match}")
        print(f"mismatch: {mismatch}")
        print(f"errors: {errors}")
        assert(len(mismatch) == 0)
        assert(len(errors) == 0)

    def test_decompile_tricky_json(self):
        pathtodir = "ass05/"
        # Compile simple with java 11
        sc_path = pathtodir+"course-02242-examples/src/dependencies/java/dtu/deps/"
        compiler = CompileTest(sc_path, 
                               pathtodir+"course-02242-examples/decompiled/", 
                               [sc_path+"tricky/Tricky.java", 
                                sc_path+"simple/Example.java", 
                                sc_path+"simple/Other.java", 
                                sc_path+"util/Utils.java"])
        from project.decompiler import decompile_dir
        i_dir = pathtodir+"course-02242-examples/decompiled/dtu/deps/simple/"
        decompile_dir(i_dir, "project/res")
        i_dir = pathtodir+"course-02242-examples/decompiled/dtu/deps/util/"
        decompile_dir(i_dir, "project/res")
        i_dir = pathtodir+"course-02242-examples/decompiled/dtu/deps/tricky/"
        decompile_dir(i_dir, "project/res")
        res_dir = "project/res/dtu/deps/"
        # Compile res_dir
        files = glob.glob(res_dir+"**/*.java", recursive=True)
        subprocess.run(["javac", "-cp", res_dir, *files], check=True)
        # Create json of res
        files = glob.glob(res_dir+"**/*.class", recursive=True)
        for file in files:
            target = file[:-6]+".json"
            subprocess.run(["jvm2json", "-s", file, "-t", target])
            pretty_print_json(target)

        i_dir = pathtodir+"course-02242-examples/decompiled/dtu/deps/"
        files = ["simple/Example.json", "simple/Other.json","util/Utils.json", "tricky/Tricky.json"]
        match, mismatch, errors = filecmp.cmpfiles(res_dir, i_dir, files)
        print(f"match: {match}")
        print(f"mismatch: {mismatch}")
        print(f"errors: {errors}")
        assert(len(mismatch) == 0)
        assert(len(errors) == 0)

if __name__ == "__main__":
    unittest.main()

