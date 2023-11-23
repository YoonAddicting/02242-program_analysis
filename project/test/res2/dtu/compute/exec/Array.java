package dtu.compute.exec;
 class Array{

public static int first(int[] n0) {
	if (n0.length == 3) {
		n0[2] = 4;
	} else 
	if (n0[0] > 0) {
		n0 = new int[3];
	}
	return n0[0];
}
public static int access(int n0, int[] n1) {
	int[][] n2 = {{1, 2}, {3, 4}, {5, 6}};
	return 1;
}
public static int newArray() {
	int[] n0 = {1, 2, 3};
	return n0[0];
}
public static int newArrayOutOfBounds() {
	int[] n0 = {1, 2, 3};
	return n0[4];
}
public static int accessSafe(int n0, int[] n1) {
	return n1[n0];
}
public static void bubbleSort(int[] n0) {
	int n1 = n0.length;
	while (n1 > 1) {
		int n2 = 0;
		int n3 = 1;
		while (n3 < n1) {
			if (n0[(n3 - 1)] > n0[n3]) {
				int n4 = n0[(n3 - 1)];
				n0[(n3 - 1)] = n0[n3];
				n0[n3] = n4;
				n2 = n3;
			}
			n3 += 1;
		}
		n1 = n2;
	}
}
public static int aWierdOneOutOfBounds() {
	int[] n0 = {0, 1, 4};
	return n0[n0[2]];
}
public static int aWierdOneWithinBounds() {
	int[][] n0 = new int[3][3];
	return 1;
}
}