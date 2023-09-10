package tests.tricky;
// This class is a little more tricky.
// It has many dependencies but none to Other :D.
//
// -> dtu.deps.simple.Example
// -> dtu.deps.util.Utils

import tests.simple.*;
import tests.util.*;

// This is never used in the file.
import tests.simple.Other;


public class Tricky implements Comparable {
    Example /* System */ Other = new Example();

    Tricky dtu, deps, simple;

    private <Other> void hello(/*dtu.deps.simple.Other*/ Utils Other) {
        Tricky dtu = new Tricky();
        simple.Other = new Example();
    }
    public int compareTo(Object o){
        return 0;
    }
}
