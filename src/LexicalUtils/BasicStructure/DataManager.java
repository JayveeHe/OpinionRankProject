package LexicalUtils.BasicStructure;

import Utils.FileUtils;
import Utils.IDFCaculator;
import Utils.SegUtils;
import Utils.WordNode;
import org.ansj.domain.Term;
import org.ansj.splitWord.analysis.IndexAnalysis;
import org.ansj.util.MyStaticValue;
import org.nlpcn.commons.lang.standardization.SentencesUtil;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 全局的数据管理器
 * Created by Jayvee on 2015/3/7.
 */
public class DataManager {
    private Map<String, List<Integer>> indexMap;
    //    private List<SentenceNode> sentenceNodes;
    private List<String> sentenceList;

    public Map<String, Double> TFIDF_Map;

    public DataManager() {
        MyStaticValue.userLibrary = "./Knowledge_Graph/seg_dict/myDict.dic";
        this.indexMap = new HashMap<String, List<Integer>>(0);
//        this.sentenceNodes = new ArrayList<SentenceNode>(0);
        this.sentenceList = new ArrayList<String>(0);
        this.TFIDF_Map = new HashMap<String, Double>(0);
    }

    public void addSentence(String sentence) {
        int index = sentenceList.size();
//        SentenceNode sentenceNode = new SentenceNode(sentence);
//        sentenceNodes.add(sentenceNode);
        sentenceList.add(sentence);
        List<Term> terms = IndexAnalysis.parse(sentence);

        //添加索引
        for (Term term : terms) {
            if (indexMap.get(term.getName()) != null) {
                if (!indexMap.get(term.getName()).contains(index)) {
                    indexMap.get(term.getName()).add(index);
                }
            } else {
                ArrayList<Integer> templist = new ArrayList<Integer>(0);
                templist.add(index);
                indexMap.put(term.getName(), templist);
            }
        }
//        return sentenceNode;
    }

    public Map<String, List<Integer>> getIndexMap() {
        return indexMap;
    }

    public List<String> getSentenceList() {
        return sentenceList;
    }

    /**
     * 根据查询词返回包含该词的所有句子的列表
     *
     * @param word
     * @return
     */
    public List<String> qury(String word) {
        List<Integer> indexs = indexMap.get(word);
        List<String> result = null;
        if (indexs != null) {
            result = new ArrayList<String>(0);
            for (Integer index : indexs) {
                result.add(sentenceList.get(index));
            }
        }
        return result;
    }

    /**
     * 根据文件路径读取文件内容，并分句
     *
     * @param filepath
     */
    public void loadFile(String filepath) {
        String text = FileUtils.File2str(filepath, "utf-8");
        //首先针对全文进行tfidf计算
        IDFCaculator idfCaculator = new IDFCaculator("Knowledge_Graph/data/IDF值.txt");
        ArrayList<WordNode> wordNodes = idfCaculator.CalTFIDF(text);
        TFIDF_Map.put("ROOT",0.0);
        for (WordNode wn : wordNodes) {
//            double temp = wn.tfidf;
            TFIDF_Map.put(wn.getWord(), wn.tfidf);
//            if()
//            TFIDF_Map
        }
        SentencesUtil su = new SentencesUtil();
        List<String> sentenceList = su.toSentenceList(text);
//        DataManager dm = new DataManager();
        int i = 0;
        for (String sentence : sentenceList) {
            if (sentence.length() > 50) {
                System.out.println("分割句子:\n"+sentence);
                String[] split = sentence.split(",|，");
                for (String s : split) {
                    addSentence(s);
                }
            } else {
                addSentence(sentence);
            }
            i++;
        }
        System.out.println("成功读取" + i + "个句子");
    }

    public static void main(String a[]) {
        SentencesUtil su = new SentencesUtil();
        String text = FileUtils.File2str("Knowledge_Graph/data/sample.txt", "utf-8");
        List<String> sentenceList = su.toSentenceList(text);

        DataManager dm = new DataManager();
        int i = 0;
        for (String sentence : sentenceList) {
            System.out.println("正在处理第" + (i++) + "句");
            String[][] seg = SegUtils.seg(sentence);
            for (int j = 0; j < seg[0].length; j++) {
                if (seg[1][j].equals("人名")
                        || seg[1][j].equals("地名")
                        || seg[1][j].equals("机构")
                        || seg[1][j].equals("名词")) {
                    if (seg[2][j].contains("n")) {
                        System.out.println(seg[0][j] + "\t" + seg[1][j] + "\t" + seg[2][j]);
                    }
                }
            }
            if (sentence.length() > 50) {
                System.out.println("句子过长：\n" + sentence + "\n进行拆分处理……");
                String[] split = sentence.split("，");
                for (String s : split) {
                    dm.addSentence(s);
                }
            } else {
                dm.addSentence(sentence);
            }
        }
        System.out.println("done!");
    }
}
