 package dtu.compute.exec;

class Array {

    
    public static int first(int[] vals) {
        if (vals.length == 3){
            vals[2] = 4;
        } else if (vals[0] > 0){
            vals = new int[3];
        }

        return vals[0];
    }

    
    public static int access(int i, int[] vals) {
        int n_vals[][] = {{1, 2}, {3, 4}, {5, 6}};
        return 1;
    }

    
    public static int newArray() {
        int vals[] = {1, 2, 3};
        return vals[0];
    }

    
    public static int newArrayOutOfBounds() {
        int vals[] = {1, 2, 3};
        return vals[4];
    }

    
    public static int accessSafe(int i, int[] vals) {
        return vals[i];
    }

    
    public static void bubbleSort(int[] vals) {
        int n = vals.length;
        while (n > 1) {
            int next_n = 0;
            for (int i = 1; i < n ; i++) {
                if (vals[i - 1] > vals[i]) {
                    int tmp = vals[i - 1];
                    vals[i - 1] = vals[i];
                    vals[i] = tmp;
                    next_n = i;
                }
            }
            n = next_n;
        }
    }

    
    public static int aWierdOneOutOfBounds() {
        int vals[] = {0,1,4};
        return vals[vals[2]];
    }

    
    public static int aWierdOneWithinBounds() {
        int vals[][] = new int[3][3];
        return 1;
    }
}
