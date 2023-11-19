package dtu.deps.tricky;
import dtu.deps.simple.Example;
import dtu.deps.util.Utils;
public class Tricky{
 Example Other = new Example();
 Tricky dtu;
 Tricky deps;
 Tricky simple;

private <Other> void hello(Utils n0) {
	Tricky n2 = new Tricky();
	n2.deps.simple.Other = new Example();
}
private <Other> void Other(Other n0) {
	
}
}