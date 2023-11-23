package eu.bogoe.dtu;
public class Integers{

public static void smallConstant() {
	int n0 = 2;
}
public static void largeConstant() {
	int n0 = 1000;
}
public static void hugeConstant() {
	int n0 = 2147483647;
}
public static void manyConstants() {
	int n0 = 1;
	int n1 = 2;
	int n2 = 3;
	int n3 = 4;
	int n4 = 5;
	int n5 = 6;
	int n6 = 7;
	int n7 = 8;
	int n8 = 9;
}
public static int bitwiseLogic(int n0, int n1) {
	int n2 = (n0) & (n1);
	int n3 = (n0) | (n1);
	int n4 = (n0) ^ (n1);
	int n5 = (n0) << (2);
	int n6 = (n1) >> (2);
	int n7 = (n5) >>> (4);
	int n8 = (n7) ^ (-1);
	return n8;
}
public static int arithmetic(int n0, int n1) {
	int n2 = (n0) + (n0);
	int n3 = (n1) - (n0);
	int n4 = (n2) * (n3);
	int n5 = (n0) / (n1);
	int n6 = (n4) % (n5);
	int n7 = -(n6);
	return n7;
}
public static int[] intArray(int[] n0) {
	int[] n1 = {n0[0], n0[1]};
	int[] n2 = new int[2];
	n2[0] = n1[1];
	n2[1] = n1[0];
	return n2;
}
}