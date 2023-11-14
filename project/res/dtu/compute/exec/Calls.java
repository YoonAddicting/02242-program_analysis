package dtu.compute.exec;
 class Calls{

public static void helloWorld() {
	System.out.println("Hello, World!\n");
}
public static int fib(int n0) {
	if ((n0) < (2)) {
return 1;
}

	return (Calls.fib((n0) - (1))) * (Calls.fib((n0) - (2)));
}
}