package dtu.compute.exec;

/**
 * This class tries to only contain very simple programs.
 */
public class Simple {

    @Case
    public static void noop() {
        return;
    }

    @Case
    public static int zero() {
        return 0;
    }

    @Case
    public static int hundredAndTwo() {
        return 102;
    }

    @Case
    public static int identity(int a) {
        return a;
    }

    @Case
    public static int add(int a, int b) {
        return a + b;
    }

    @Case
    public static int min(int a, int b) {
        if (a <= b) return a;
        else return b;
    }

    @Case
    public static int factorial(int n) {
        int m = n;
        while (n-- > 0) {
            m *= n;
        }
        return m;
    }
}
