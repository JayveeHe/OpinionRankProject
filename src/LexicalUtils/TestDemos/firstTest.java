package LexicalUtils.TestDemos;


import LexicalUtils.BasicStructure.DataManager;
import LexicalUtils.BasicStructure.RuleDict;
import Utils.FileUtils;
import Utils.IDFCaculator;
import Utils.WordNode;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.TypedDependency;
import edu.stanford.nlp.trees.international.pennchinese.ChineseGrammaticalStructure;

import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.Map;

/**
 * Created by Jayvee on 2014/12/10.
 */
public class firstTest {

    public static void main(String abs[]) {
//        String text = "我是一个魔兽世界的狂暴战。dota玩家";
//        List<Term> terms = NlpAnalysis.parse(text);
//        System.out.println(terms);
//        static String[] options = {"-MAX_ITEMS", "200000000"};
//        static LexicalizedParser lp = new LexicalizedParser(
//                "grammar/chinesePCFG.ser.gz", options);
//        String[] sent = {"This", "is", "an", "easy", "sentence", "."};
//        LexicalizedParser lp = LexicalizedParser.loadModel("D:\\CS\\Git\\NLP\\Knowledge_Graph\\libs\\stanford-parser-3.4.1-models.jar");
//        List<CoreLabel> rawWords = Sentence.toCoreLabelList(sent);
//        Tree parse = lp.apply(rawWords);
//        parse.pennPrint();
//        IDFCaculator idfCaculator = new IDFCaculator("Knowledge_Graph/data/IDF值.txt");
//        String text = FileUtils.File2str("./Knowledge_Graph/data/sample.txt", "utf-8");
//        ArrayList<WordNode> wordNodes = idfCaculator.CalTFIDF(text);
//        for (WordNode wn : wordNodes) {
////            if (!wn.getNature().equals("null") && (wn.getNature().contains("n") || wn.getNature().contains("v")))
//            System.out.println(wn.getWord() + "\t" + wn.tfidf + "\t" + wn.getNature());
//        }
//        String[] split = text.split("。");
//        ArrayList<ParserManager> pmList = new ArrayList<ParserManager>(0);
//        Map<String, ArrayList<TypedDependency>> totalMap = new HashMap<String, ArrayList<TypedDependency>>(0);
//        for (String s : split) {
//            ParserManager pm = new ParserManager(s);
//            Tree tree = StanfordUtils.parseChinese(s);
////            ParserNode root = ParserManager.buildParseTree(tree.toString());
//            ChineseGrammaticalStructure gs = new ChineseGrammaticalStructure(tree);
//            Collection<TypedDependency> tds = gs.typedDependenciesCollapsed();
//            pm.buildDependencyMapByTDs(tds);
//            pmList.add(pm);
////进行关系map的合并
////            for (String rl : parserMapByTDs.keySet()) {
////                if (totalMap.get(rl) != null) {
////                    for (TypedDependency td : parserMapByTDs.get(rl)) {
////                        totalMap.get(rl).add(td);
////                    }
////                } else {
////                    totalMap.put(rl, parserMapByTDs.get(rl));
////                }
//////                totalMap.putAll(parserMapByTDs);
////
////            }
//        }
        DataManager dataManager = new DataManager();
        dataManager.loadFile("./Knowledge_Graph/data/sample.txt");
        RuleDict ruleDict = new RuleDict();
//        ruleDict.addRule("手机", "nn", "n", true, "手机品牌");
//        ruleDict.addRule("公司", "nn", "n", false, "职务");
//        ruleDict.addWord("武当", "门派");
//        ruleDict.addWord("张无忌", "人物");
//        ruleDict.addWord("张三丰", "人物");
//        ruleDict.addWord("峨嵋派", "门派");
//        ruleDict.addWord("", "");
        ruleDict.addWord("马化腾", "人物");
        ruleDict.addWord("李彦宏", "人物");
        ruleDict.addWord("新浪", "公司");
        ruleDict.addWord("总裁", "职位");
        ruleDict.analysis(dataManager);
//        ruleDict.printDict();
//        String text = "巩俐、胡静等人气明星打造的都市爱情大片《我知女人心》在博纳悠唐国际影城正式首映。";
//        List<Term> terms = NlpAnalysis.parse(text);
//        System.out.println(terms);
////        UserDefineLibrary.insertWord("魅蓝手机", "userDefine", 1);
////        UserDefineLibrary.insertWord("魅蓝", "userDefine", 1);
////        terms = NlpAnalysis.parse(text);
////        System.out.println(terms);
////        terms = IndexAnalysis.parse(text);
////        System.out.println(terms);
//        String[][] seg = SegUtils.seg(text);
//        System.out.println(Arrays.toString(seg[0]));
//        System.out.println(Arrays.toString(seg[1]));
//        System.out.println(Arrays.toString(seg[2]));
//        DependencyTree dt = FudanUtils.parseText(text);
//        System.out.println(dt.toList().toString());
        System.out.println("实体识别结束");


    }
}
