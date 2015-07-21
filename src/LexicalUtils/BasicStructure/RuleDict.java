package LexicalUtils.BasicStructure;


import LexicalUtils.LexicalParser.StanfordUtils;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.ling.WordTag;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.trees.TypedDependency;
import edu.stanford.nlp.trees.international.pennchinese.ChineseGrammaticalStructure;
import org.ansj.library.UserDefineLibrary;

import java.util.*;

/**
 * Created by Jayvee on 2015/2/28.
 */
public class RuleDict {
    private static final int ITER_MAX = 10;
    public Map<String, WordMark> wordDict = new HashMap<String, WordMark>(0);
    public List<Rule> ruleList = new ArrayList<Rule>(0);

    public void addWord(String word, String mark) {
        WordMark wordMark = new WordMark(word, mark);
        wordDict.put(word, wordMark);
    }

    /**
     * 添加规则
     *
     * @param coreWord 触发词
     * @param relation 触发词所连接的关系
     * @param isGov    触发词是否为支配词
     */
    public void addRule(String coreWord, String relation, String targetNature, boolean isGov, String mark) {
        ruleList.add(new Rule(coreWord, relation, targetNature, isGov, mark));
    }

    public void analysis(DataManager dataManager) {
        //将wordDict中的词加入分词词典中
        for (String word:wordDict.keySet()){
            UserDefineLibrary.insertWord(word,"nw", 1000);
        }
//        for (int iter = 0; iter < ITER_MAX; iter++) {
        int MAX_ITER = 3;
        int dictCount = ruleList.size();
        int startIndex = 0;
        ArrayList<ParserManager> parserManagerList = new ArrayList<ParserManager>(0);
        do {//每一次迭代对ruledict的所有规则进行查询
            dictCount = ruleList.size();
//            for (int i = 0; i < ruleList.size(); i++) {
            for (int i = startIndex; i < ruleList.size(); i++) {//已经检测过的rule就不再检测了
                Rule rule = ruleList.get(i);
                String coreWord = rule.getCoreWord();
                List<String> sentences = dataManager.qury(coreWord);
                if (sentences != null) {
                    for (String singleSentence : sentences) {
                        //Stanford
                        ParserManager pm = new ParserManager(singleSentence);
                        Tree tree = StanfordUtils.parseChinese(singleSentence);
                        ChineseGrammaticalStructure gs = new ChineseGrammaticalStructure(tree);
                        Collection<TypedDependency> tds = gs.typedDependenciesCollapsed();
                        ParserManager.buildDependencyMapByTDs(tds);
                        if (!parserManagerList.contains(pm)) {
                            parserManagerList.add(pm);
                        }
                        //规则解析阶段
                        if (rule.isGov()) {
                            //如果触发词是支配词，则可以直接查找
                            Map<String, ArrayList<TypedDependency>> relationMap = pm.sentenceNode.GovMap.get(rule.coreWord);
                            if (relationMap != null) {
                                for (ArrayList<TypedDependency> relationList : relationMap.values()) {
                                    for (TypedDependency td : relationList) {
                                        String shortName = td.reln().getShortName();
                                        if (shortName.equals(rule.getRelation())) {
                                            String word = td.dep().value();
                                            if (!wordDict.containsKey(word)) {
                                                if (pm.sentenceNode.natures[td.dep().index()].contains("n")) {
                                                    WordMark wordMark = new WordMark(word, rule.getMark());
                                                    wordDict.put(word, wordMark);
                                                    System.out.println("【发现实体】由  " + rule + "  推出的新实体：" + wordMark);
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        } else {
                            //如果不是支配词，则遍历查找所有指向该点的词
                            Map<String, ArrayList<TypedDependency>> relationMap = pm.sentenceNode.DepdMap.get(rule.coreWord);
                            if (relationMap != null) {
                                for (ArrayList<TypedDependency> relationList : relationMap.values()) {
                                    for (TypedDependency td : relationList) {
                                        String shortName = td.reln().getShortName();
                                        if (shortName.equals(rule.getRelation())) {
                                            String word = td.gov().value();
                                            if (!wordDict.containsKey(word))
                                                if (pm.sentenceNode.natures[td.gov().index()].contains("n")) {

                                                    WordMark wordMark = new WordMark(word, rule.getMark());
                                                    wordDict.put(word, wordMark);
                                                    System.out.println("【发现实体】由  " + rule + "  推出的新实体：" + wordMark);
                                                }
                                        }
                                    }
                                }
                            }
                        }


//                        //Fudan
//                        DependencyTree dt = FudanUtils.parseText(singleSentence);
//                        List<Term> terms = NlpAnalysis.parse(singleSentence);
//                        ArrayList<List<String>> lists = dt.toList();
//                        //规则解析阶段
//                        if (rule.isGov()) {
//                            //如果触发词是支配词，则可以直接查找
//                            for (int j = 0; j < lists.size(); j++) {
//                                List<String> info = lists.get(j);
//                                if (info.get(0).equals(coreWord)
//                                        && info.get(3).equals(rule.getRelation())
//                                        && terms.get(j).getNatureStr().equals(rule.getTargetNature())
//                                        ) {
//                                    int toIndex = Integer.valueOf(info.get(2));
//                                    WordMark wordMark = new WordMark(lists.get(toIndex).get(0),
//                                            rule.getMark());
//                                    wordDict.put(lists.get(toIndex).get(0), wordMark);
//                                }
//                            }
//                        } else {
//                            //如果不是支配词，则遍历查找所有指向该点的词
//                            for (int j = 0; j < lists.size(); j++) {
//                                List<String> info = lists.get(j);
//                                if (
//                                        terms.get(j).getNatureStr().equals(rule.getTargetNature()) &&
//                                                info.get(3).equals(rule.getRelation())) {
//                                    String target = lists.get(Integer.valueOf(info.get(2))).get(0);
//                                    if (target.equals(rule.getCoreWord())) {
//                                        WordMark wordMark = new WordMark(info.get(0), rule.getMark());
//                                        wordDict.put(info.get(0), wordMark);
//                                    }
//
//                                }
//                            }
//                        }
                    }
                }
//                System.out.println("第" + i + "个句子处理完毕");
            }
            //每轮迭代结束前进行规则词典的更新
            System.out.println("正在更新规则……");
            //清空已处理的rule
//            clearRules();
            startIndex = ruleList.size();//防止规则的重复检测
            updateRules(dataManager, parserManagerList);
            printDict();
//            if(dictCount == wordDict.size()){
//                MAX_ITER--;
//            }
        } while (dictCount < ruleList.size());
//        }
//        System.out.println(wordDict.values());
    }


    public void printDict() {
        StringBuilder sb = new StringBuilder("现在词典中共有" + (wordDict.size()) + "个实体\n");
        for (WordMark wm : wordDict.values()) {
            sb.append(wm + "\n");
        }
        System.out.println(sb);
    }

    /**
     * 根据全局数据，对规则词典进行更新
     */
    private void updateRules(DataManager dataManager,
                             ArrayList<ParserManager> parserManagerList) {
        Map<String, List<String[]>> tempMap = new HashMap<String, List<String[]>>(0);
        if (parserManagerList.size() < 1) {
            for (WordMark wm : wordDict.values()) {
                String tempword = wm.getWord();
                List<String> qury = dataManager.qury(tempword);
                if (qury != null) {
                    for (String s : qury) {
                        ParserManager ppp = new ParserManager(s);
                        parserManagerList.add(ppp);
                    }
                }
            }
        }
        //key为mark，value[0]为候选触发词，value[1]为相应的关系，value[2]为是否支配词
        for (WordMark wm : wordDict.values()) {
            String mark = wm.getMark();//用于统计某一标记属性所对应的各词集合中，作为key
            String word = wm.getWord();

            for (ParserManager pm : parserManagerList) {
                if (pm.sentenceNode.wordMap.containsKey(word)) {
                    Map<String, Map<String, ArrayList<TypedDependency>>> govMap = pm.sentenceNode.GovMap;
                    Map<String, Map<String, ArrayList<TypedDependency>>> depdMap = pm.sentenceNode.DepdMap;
                    String[] key = new String[2];

                    //key[0]为已有词典词，key[1]为触发词是否为支配词；
                    //value里的String[0]为候选触发词，String[1]为触发词的关系
                    Map<String, ArrayList<TypedDependency>> govRlnMap = govMap.get(word);
                    if (govRlnMap != null) {
                        String[] value = new String[5];
                        key[0] = word;
//                        key[1] = String.valueOf(false);
                        for (ArrayList<TypedDependency> govList : govRlnMap.values()) {
                            for (TypedDependency td : govList) {
                                value[0] = td.dep().value();
                                value[1] = td.reln().getShortName();
                                value[2] = String.valueOf(false);
                                value[3] = String.valueOf(1);
                                value[4] = pm.sentenceNode.natures[td.dep().index()];
                                if (tempMap.get(mark) != null) {
                                    boolean isAdded = false;
                                    for (String[] temp : tempMap.get(mark)) {
                                        if (temp[0].equals(value[0]) && temp[1].equals(value[1]) && temp[2].equals(value[2])) {
                                            temp[3] = String.valueOf(Integer.valueOf(temp[3]) + 1);//计数+1
                                            isAdded = true;
                                            break;
                                        }
//                                        else {
//                                        }
                                    }
                                    if (!isAdded) {
                                        tempMap.get(mark).add(value);
                                    }
                                } else {
                                    List<String[]> templist = new ArrayList<String[]>(0);
                                    templist.add(value);
                                    tempMap.put(mark, templist);
                                }
                            }
                        }
                    }

                    Map<String, ArrayList<TypedDependency>> depdRlnMap = depdMap.get(word);
                    if (depdRlnMap != null) {
                        String[] value = new String[5];
                        key[0] = word;
//                        key[1] = String.valueOf(false);
                        for (ArrayList<TypedDependency> depdList : depdRlnMap.values()) {
                            for (TypedDependency td : depdList) {
                                value[0] = td.gov().value();
                                value[1] = td.reln().getShortName();
                                value[2] = String.valueOf(true);
                                value[3] = String.valueOf(1);
                                value[4] = pm.sentenceNode.natures[td.gov().index()];
                                if (tempMap.get(mark) != null) {
                                    boolean isAdded = false;
                                    for (String[] temp : tempMap.get(mark)) {
                                        if (temp[0].equals(value[0]) && temp[1].equals(value[1]) && temp[2].equals(value[2])) {
                                            temp[3] = String.valueOf(Integer.valueOf(temp[3]) + 1);//计数+1
                                            isAdded = true;
                                            break;
                                        }
//                                        else {
//                                        }
                                    }
                                    if (!isAdded) {
                                        tempMap.get(mark).add(value);
                                    }
                                } else {
                                    List<String[]> templist = new ArrayList<String[]>(0);
                                    templist.add(value);
                                    tempMap.put(mark, templist);
                                }
                            }
                        }
                    }
                }
            }
        }
//          针对所有mark所连接的词进行排序
        for (String key : tempMap.keySet()) {
            double countMax = 0;
            String[] wordtemp = null;
            Rule tempRule = null;
            for (String[] value : tempMap.get(key)) {
                Double tfidf = dataManager.TFIDF_Map.get(value[0]);
                if (tfidf != null) {
                    tempRule = new Rule(value[0], value[1], value[4], Boolean.valueOf(value[2]), key);
                    if (Integer.valueOf(value[3]) * tfidf >= countMax
                            && !ruleList.contains(tempRule)
                            && (value[4].contains("v") || value[4].contains("n"))
                            && !value[4].equals("null")) {
                        countMax = Integer.valueOf(value[3]) * tfidf;
                        wordtemp = value;
                    }
                }
            }

            if (wordtemp != null) {
                tempRule = new Rule(wordtemp[0], wordtemp[1], wordtemp[4], Boolean.valueOf(wordtemp[2]), key);
                if (!ruleList.contains(tempRule)) {
                    addRule(wordtemp[0], wordtemp[1], wordtemp[4], Boolean.valueOf(wordtemp[2]), key);
                    System.out.println("【新增规则】增加的规则：" + tempRule);
                }
            }
//            RuleDict.Rule newrule = new Rule(wordtemp[0], )
        }
    }


    private void clearRules() {
        this.ruleList.clear();
    }

    private class WordMark {
        private final String word;
        private final String mark;

        public WordMark(String word, String mark) {

            this.word = word;
            this.mark = mark;
        }

        public String getWord() {
            return word;
        }

        public String getMark() {
            return mark;
        }

        @Override
        public String toString() {
            return "实体： " + word + "\t类别： " + mark + "\t";
        }
    }

    private class Rule {
        private final String coreWord;
        private final String relation;
        private final String targetNature;
        private final boolean isGov;
        private final String mark;

        public Rule(String coreWord, String relation, String targetNature, boolean isGov, String mark) {

            this.coreWord = coreWord;
            this.relation = relation;
            this.targetNature = targetNature;
            this.isGov = isGov;
            this.mark = mark;
        }

        public String getRelation() {
            return relation;
        }

        public String getCoreWord() {
            return coreWord;
        }

        public boolean isGov() {
            return isGov;
        }

        public String getMark() {
            return mark;
        }

        public String getTargetNature() {
            return targetNature;
        }

        @Override
        public String toString() {
            return "触发词： " + coreWord + "\t触发关系： " + relation + "\t触发词词性： " + targetNature + "\t是否支配： " + isGov + "\t标注类型： " + mark;
        }

        @Override
        public boolean equals(Object obj) {
            return obj instanceof Rule
                    && ((Rule) obj).getCoreWord().equals(this.coreWord)
                    && ((Rule) obj).getMark().equals(this.mark)
                    && ((Rule) obj).getRelation().equals(this.relation)
                    && ((Rule) obj).getTargetNature().equals(this.targetNature);
        }
    }
}



