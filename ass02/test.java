import ai.serenade.treesitter.*;
import java.nio.file.*;
import java.nio.charset.*;
import java.io.*;
public class Test {
    static {
        System.load("/vagrant/java-tree-sitter/libjava-tree-sitter.so");
    }
    public static void main(String[] main) throws Exception {
        try (Parser parser = new Parser()) {
            parser.setLanguage(Languages.java());
            Path p = FileSystems.getDefault().getPath("src/main/java/Test.java");
            String string = Files.readString(p, StandardCharsets.UTF_16LE);
            try (Tree tree = parser.parseString(string)) {
                Node root = tree.getRootNode();
                System.out.println(root.getChildCount());
            }
} }