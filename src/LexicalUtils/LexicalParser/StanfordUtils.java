package LexicalUtils.LexicalParser;

import LexicalUtils.BasicStructure.DataManager;
import LexicalUtils.BasicStructure.ParserManager;
import LexicalUtils.BasicStructure.ParserNode;
import Utils.FileUtils;
import Utils.IDFCaculator;
import Utils.WordNode;
import edu.stanford.nlp.parser.lexparser.LexicalizedParser;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.TypedDependency;
import edu.stanford.nlp.trees.international.pennchinese.ChineseGrammaticalStructure;
import org.ansj.domain.Term;
import org.ansj.splitWord.analysis.NlpAnalysis;
import org.nlpcn.commons.lang.standardization.SentencesUtil;

import java.util.*;


/**
 * Created by Jayvee on 2015/2/12.
 */
public class StanfordUtils {
    static LexicalizedParser lp;

    static {
        String grammar = "./data/chineseFactored.ser.gz";
        String[] options = {"-maxLength", "60", "-MAX_ITEMS", "50000"};
        lp = LexicalizedParser.loadModel(grammar, options);
    }

    public static Tree parseChinese(String text) {
        List<Term> terms = NlpAnalysis.parse(text);
        List<String> lss = new ArrayList<String>();
        for (Term term : terms) {
            lss.add(term.getName());
        }
        Tree parseTree = lp.parseStrings(lss);
        return parseTree;
    }

    public static void main(String a[]) {
//        String text = "何太冲是崆峒派的掌门人。";\
        SentencesUtil su = new SentencesUtil();
        String text = FileUtils.File2str("Knowledge_Graph/data/倚天屠龙记.txt", "utf-8");
        List<String> sentenceList = su.toSentenceList(text);
        Map<String, ArrayList<TypedDependency>> totalMap = new HashMap<String, ArrayList<TypedDependency>>(0);
        IDFCaculator idfCaculator = new IDFCaculator("Knowledge_Graph/data/IDF值.txt");
        ArrayList<WordNode> wordNodes = idfCaculator.CalTFIDF(text);
        DataManager dm = new DataManager();
        for (int i = 0; i < (100 < wordNodes.size() ? 100 : wordNodes.size()); i++) {
//        for (int i = 0; i < wordNodes.size(); i++) {
            WordNode wn = wordNodes.get(i);
            Map<String, Double> tfidf_map = dm.TFIDF_Map;
            if (tfidf_map.get(wn.getWord()) == null) {
                tfidf_map.put(wn.getWord(), wn.tfidf);
            }
//            if (wn.getNature().contains("nr")) {
//            if (wn.getNature().equals("n")||wn.getNature().equals("nw")) {
//            WordNode wn = wordNodes.get(i);
            System.out.println(wn.getWord() + "\ttfidf=" + wn.tfidf + "\tnature=" + wn.getNature());
//            }
        }
        ArrayList<ParserNode> totalROOT = new ArrayList<ParserNode>(0);
        for (int i = 0; i < (10 < sentenceList.size() ? 10 : sentenceList.size()); i++) {
//        for (int i = 0; i < sentenceNodes.size(); i++) {
            String sentence = sentenceList.get(i);
            System.out.println("正在处理第" + i + "个句子\n" + sentence);
            Tree parseTree = parseChinese(sentence);
            ParserNode root = ParserManager.buildParseTree(parseTree.toString());
            totalROOT.add(root);
            ChineseGrammaticalStructure gs = new ChineseGrammaticalStructure(parseTree);
            Collection<TypedDependency> tds = gs.typedDependenciesCollapsed();
            Map<String, ArrayList<TypedDependency>> parserMapByTDs = ParserManager.buildDependencyMapByTDs(tds);
            //进行关系map的合并
            for (String rl : parserMapByTDs.keySet()) {
                if (totalMap.get(rl) != null) {
                    for (TypedDependency td : parserMapByTDs.get(rl)) {
                        totalMap.get(rl).add(td);
                    }
                } else {
                    totalMap.put(rl, parserMapByTDs.get(rl));
                }
//                totalMap.putAll(parserMapByTDs);

            }
//            if (parserMapByTDs.get("nn") != null) {
//                System.out.println(parserMapByTDs.get("nn").get(0).gov().pennString());
//            }
        }
//        System.out.println(pm.getDepdMap().size() + "\t" + pm.getGovMap().size() + "\t" + pm.TFIDF_Map.size());
        System.out.println(totalMap.size() + "\t" + totalROOT.size());

//        System.out.println(parserMapByTDs);
//        System.out.println(parserMapByTDs.get("root").get(0).gov().pennString());
    }


}


