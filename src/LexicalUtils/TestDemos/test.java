package LexicalUtils.TestDemos;

/**
 * Created by Jayvee on 2015/3/12.
 */
public class test {
    public static void main(String a[]){
        int i =0;
        int b = 55;
        i=i++;
        System.out.println(i);
        b = ++i;
        System.out.println(i);
        System.out.println(++i+b+++b+b++);
        System.out.println(b);
    }
}
