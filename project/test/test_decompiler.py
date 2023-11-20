import glob
import unittest
import filecmp
import subprocess
import shutil
import json
import os


class AllTests(unittest.TestCase):
    def compile_source(self, sc_path, files):
        self.files = files
        subprocess.run(["javac", "-cp", sc_path, *self.files], check=True)

    def pretty_print_json(self, file):
        with open(file, "r") as f:
            txt = f.read()
            json_object = json.loads(txt)
        json_formatted_str  = json.dumps(json_object, indent=4)

        with open(file, "w") as f:
            f.write(json_formatted_str)
    
    def generate_json(self, sc_path, out_path = ""):
        files = glob.glob(sc_path+"**/*.class", recursive=True)
        for file in files:
            target = file[:-6]+".json"
            subprocess.run(["jvm2json", "-s", file, "-t", target])
            self.pretty_print_json(target)
            if out_path != "":
                output = target
                target = target.split("/")
                target = '/'.join(target[-4:])
                target = out_path+target
                shutil.move(output, target)
        
    def clean_up_class_files(self, sc_path):
        files = glob.glob(sc_path+"**/*.class", recursive=True)
        for file in files:
            os.remove(file)

    def decompile_dirs(self, dirs, out_dir):
        from project.decompiler import decompile_dir
        for i_dir in dirs:
            decompile_dir(i_dir, out_dir)

    def compare_files(self, dir_a, dir_b, file_names):
        match, mismatch, errors = filecmp.cmpfiles(dir_a, dir_b, file_names)
        print(f"match: {match}")
        print(f"mismatch: {mismatch}")
        print(f"errors: {errors}")
        assert(len(mismatch) == 0)
        assert(len(errors) == 0)


class TestDtuDepsSimpleUtils(AllTests):
    def initial_self_compile_and_decompile(self):
        # Compile simple with java 11
        sc_path = "ass05/course-02242-examples/src/dependencies/java/dtu/deps/"
        self.compile_source(sc_path,
                            [sc_path+"simple/Example.java", 
                            sc_path+"simple/Other.java", 
                            sc_path+"util/Utils.java"]) 
        out_path = "ass05/course-02242-examples/decompiled/"
        self.generate_json(sc_path, out_path)
        self.clean_up_class_files(sc_path)
        self.decompile_dirs(["ass05/course-02242-examples/decompiled/dtu/deps/simple/", 
                             "ass05/course-02242-examples/decompiled/dtu/deps/util/"], 
                             "project/res")
    
    def test_decompile_simple_comp_source(self):
        self.initial_self_compile_and_decompile()
        res_dir = "project/res/dtu/deps/"
        # Compile res_dir
        files = glob.glob(res_dir+"**/*.java", recursive=True)
        self.compile_source(res_dir, files)
        # Create json of res
        self.generate_json(res_dir)
        # decompile res_dir
        self.decompile_dirs([res_dir], "project/res2")
        # compare res_dir and res2_dir
        res2_dir = "project/res2/dtu/deps/"
        files = ["simple/Example.java", "simple/Other.java","util/Utils.java"]
        self.compare_files(res_dir, res2_dir, files)


    def test_decompile_simple_comp_json(self):
        self.initial_self_compile_and_decompile()
        res_dir = "project/res/dtu/deps/"
        # Compile res_dir
        files = glob.glob(res_dir+"**/*.java", recursive=True)
        self.compile_source(res_dir, files)
        # Create json of res
        self.generate_json(res_dir)
        # compare json files
        i_dir = "ass05/course-02242-examples/decompiled/dtu/deps/"
        files = ["simple/Example.json", "simple/Other.json","util/Utils.json"]
        self.compare_files(res_dir, i_dir, files)
        
class TestDtuDepsTricky(AllTests):
    def initial_self_compile_and_decompile(self):
        # Compile tricky with java 11
        sc_path = "ass05/course-02242-examples/src/dependencies/java/dtu/deps/"
        self.compile_source(sc_path,
                               [sc_path+"tricky/Tricky.java", 
                                sc_path+"simple/Example.java", 
                                sc_path+"simple/Other.java", 
                                sc_path+"util/Utils.java"])
        out_path = "ass05/course-02242-examples/decompiled/"
        self.generate_json(sc_path, out_path)
        self.clean_up_class_files(sc_path)
        self.decompile_dirs(["ass05/course-02242-examples/decompiled/dtu/deps/simple/", 
                             "ass05/course-02242-examples/decompiled/dtu/deps/util/",
                             "ass05/course-02242-examples/decompiled/dtu/deps/tricky/"], 
                             "project/res")

    def test_decompile_tricky_source(self):
        self.initial_self_compile_and_decompile()
        res_dir = "project/res/dtu/deps/"
        # Compile res_dir
        files = glob.glob(res_dir+"**/*.java", recursive=True)
        self.compile_source(res_dir, files)
        # Create json of res
        self.generate_json(res_dir)
        # decompile res_dir
        self.decompile_dirs([res_dir], "project/res2")
        # compare res_dir and res2_dir
        res2_dir = "project/res2/dtu/deps/"
        files = ["simple/Example.java", "simple/Other.java","util/Utils.java", "tricky/Tricky.java"]
        self.compare_files(res_dir, res2_dir, files)

    def test_decompile_tricky_json(self):
        self.initial_self_compile_and_decompile()
        res_dir = "project/res/dtu/deps/"
        # Compile res_dir
        files = glob.glob(res_dir+"**/*.java", recursive=True)
        self.compile_source(res_dir, files)
        # Create json of res
        self.generate_json(res_dir)
        # compare json files
        i_dir = "ass05/course-02242-examples/decompiled/dtu/deps/"
        files = ["simple/Example.json", "simple/Other.json","util/Utils.json", "tricky/Tricky.json"]
        self.compare_files(res_dir, i_dir, files)

if __name__ == "__main__":
    unittest.main()

