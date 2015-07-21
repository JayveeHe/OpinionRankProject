package LexicalUtils.FudanNLP;

import org.ansj.domain.Term;
import org.ansj.splitWord.analysis.NlpAnalysis;
import org.fnlp.nlp.cn.CNFactory;
import org.fnlp.nlp.parser.dep.DependencyTree;
import org.fnlp.util.exception.LoadModelException;

import java.util.ArrayList;
import java.util.List;

/**
 * Created by Jayvee on 2015/2/26.
 */
public class FudanUtils {
    private static CNFactory factory = null;

    static {
        String modelPath = ".\\models";
        try {
            factory = CNFactory.getInstance(modelPath);
        } catch (LoadModelException e) {
            e.printStackTrace();
        }
    }


    public static void main(String a[]) {
        //            CNFactory factory = CNFactory.getInstance("D:\\CS\\Git\\NLP\\Knowledge_Graph\\models");
////            factory.
//            DependencyTree tree = factory.parse2T("");

        String text = "抢购小米手机的难度很大";
        DependencyTree dependencyTree = FudanUtils.parseText(text);
        System.out.println(dependencyTree);
        System.out.println(dependencyTree.getDepClass());
        ArrayList<List<String>> lists = dependencyTree.toList();
        System.out.println(lists);
//        StanfordUtils.parseChinese(text);

//        System.out.println(factory.parse2T(text));

        System.out.println("done!");
    }

    public static DependencyTree parseText(String text) {
        List<Term> terms = NlpAnalysis.parse(text);
        String[] words = new String[terms.size()];
        List<Integer> quetoIndex = new ArrayList<Integer>(0);
        for (int i = 0; i < terms.size(); i++) {
            words[i] = terms.get(i).getName();
            //使得Ansj_seg的标点符号与FNLP相适应
            if (terms.get(i).getNatureStr().equals("w")) {
                quetoIndex.add(i);
            }
        }
        String[] pos = factory.tag(words);
        for (Integer k : quetoIndex) {
            pos[k] = "标点";
        }
        DependencyTree dependencyTree = factory.parse2T(words, pos);
        return dependencyTree;
    }

    public static String[] tagText(String[] text) {
        return factory.tag(text);
    }
}
