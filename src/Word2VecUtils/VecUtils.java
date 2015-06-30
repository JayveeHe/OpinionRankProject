package Word2VecUtils;

import LexicalUtils.BasicStructure.ParserManager;
import LexicalUtils.BasicStructure.ParserNode;
import LexicalUtils.LexicalParser.StanfordUtils;
import Utils.IDFCaculator;
import Utils.WordNode;
import Word2VecUtils.vec.Word2VEC;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.TypedDependency;
import edu.stanford.nlp.trees.international.pennchinese.ChineseGrammaticalStructure;
import org.ansj.domain.Term;
import org.ansj.splitWord.analysis.NlpAnalysis;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;

/**
 * Created by Jayvee on 2015/6/29.
 */
public class VecUtils {
    public static float[] sent2vec(Word2VEC w2v, String sent) {
        List<Term> parse = NlpAnalysis.parse(sent);
        float[] result = new float[w2v.getWordVector("男人").length];
        for (Term t : parse) {
            float[] wordVector = w2v.getWordVector(t.getName());
            if (wordVector != null) {
                for (int i = 0; i < wordVector.length; i++) {
                    float val = wordVector[i];
                    result[i] += val;
                }
            }
        }
        return result;
    }

    /**
     * 计算两个句子的TFIDF相似度
     * @param w2v
     * @param sent1
     * @param sent2
     */
    public static void calWordsSimilarity(Word2VEC w2v,String sent1,String sent2){
        IDFCaculator idfc = new IDFCaculator("./data/IDF值.txt");
        ArrayList<WordNode> tfidf1 = idfc.CalTFIDF(sent1);
        ArrayList<WordNode> tfidf2 = idfc.CalTFIDF(sent2);
    }

    public static void main(String args[]) {
        String sent1 = "我喜欢吃苹果";
        String sent2 = "我不喜欢吃苹果";
        Tree t1 = StanfordUtils.parseChinese(sent1);
        Tree t2 = StanfordUtils.parseChinese(sent2);
        ChineseGrammaticalStructure gs1 = new ChineseGrammaticalStructure(t1);
        Collection<TypedDependency> tds1 = gs1.typedDependenciesCollapsed();
        ChineseGrammaticalStructure gs2 = new ChineseGrammaticalStructure(t2);
        Collection<TypedDependency> tds2 = gs1.typedDependenciesCollapsed();
        System.out.println(gs1);
        System.out.println(t1);
        System.out.println(tds1);
        System.out.println(tds2);
        ParserNode p1 = ParserManager.buildParseTree(t1.toString());
        ParserNode p2 = ParserManager.buildParseTree(t2.toString());
        Map<String, ArrayList<TypedDependency>> mapByTDs = ParserManager.buildDependencyMapByTDs(tds1);
        System.out.println();
    }
}
