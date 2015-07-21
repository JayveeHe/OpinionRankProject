package LexicalUtils.BasicStructure;

import LexicalUtils.LexicalParser.StanfordUtils;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.TypedDependency;
import edu.stanford.nlp.trees.international.pennchinese.ChineseGrammaticalStructure;
import org.ansj.domain.Term;
import org.ansj.splitWord.analysis.NlpAnalysis;

import java.util.*;

/**
 * 自定义的句子级结点
 * Created by ITTC-Jayvee on 2015/3/6.
 */
public class SentenceNode {
    String sentenceText;
    public Map<String, Map<String, ArrayList<TypedDependency>>> GovMap;//以支配词作为key的map

    public Map<String, Map<String, ArrayList<TypedDependency>>> DepdMap;//以被支配词作为key的map

    public Map<String, ArrayList<TypedDependency>> ParseMap;//以关系描述词作为key的map
    public ParserNode ParseTree;//该句子的解析树
    public String[] natures;
    public Map<String, String> wordMap;//用于存储该句包含的单词与词性

    public SentenceNode(String text) {
        this.sentenceText = text;
        List<Term> terms = NlpAnalysis.parse(text);
        this.natures = new String[terms.size() + 1];
        natures[0] = "ROOT";
        this.wordMap = new HashMap<String, String>(0);
        for (int i = 0; i < terms.size(); i++) {
            Term term = terms.get(i);
            wordMap.put(term.getName(), term.getNatureStr());
            natures[i + 1] = term.getNatureStr();
        }
        this.GovMap = new HashMap<String, Map<String, ArrayList<TypedDependency>>>(0);
        this.DepdMap = new HashMap<String, Map<String, ArrayList<TypedDependency>>>(0);
        Tree tree = StanfordUtils.parseChinese(text);
//        this.ParseTree = ParserManager.buildParseTree(tree.toString());
        ChineseGrammaticalStructure gs = new ChineseGrammaticalStructure(tree);
        Collection<TypedDependency> tds = gs.typedDependenciesCollapsed();
        this.ParseMap = ParserManager.buildDependencyMap(tds, GovMap, DepdMap);
    }
}
