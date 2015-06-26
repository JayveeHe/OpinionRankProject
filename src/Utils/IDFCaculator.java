package Utils;

import org.ansj.domain.Term;
import org.ansj.splitWord.analysis.NlpAnalysis;

import java.io.UnsupportedEncodingException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * Created by Jayvee on 2014/8/15.
 */
public class IDFCaculator {
    public static void main(String[] args) {
        IDFCaculator idfCaculator = new IDFCaculator("Knowledge_Graph/data/IDF值.txt");
        String text = FileUtils.File2str("Knowledge_Graph/data/sample.txt", "utf-8");
        ArrayList<WordNode> test = idfCaculator.CalTFIDF(text);
        for (WordNode wn : test) {
            if (wn.getNature().equals("n") || wn.getNature().equals("vn"))
                System.out.println(wn.getWord() + "\ttfidf=" + wn.tfidf);
        }
    }

    static int docCount = 0;
    public TrieTree IDFtree;

    public IDFCaculator(String filepath) {
        this.IDFtree = loadIDFtree(filepath);
    }


    public static TrieTree loadIDFtree(String IDFpath) {
        String IDFtext = null;
        TrieTree IDFtree = new TrieTree();
        try {
            IDFtext = new String(FileUtils.File2byte(IDFpath), "utf-8");
            String[] terms = IDFtext.split(System.getProperty("line.separator"));
            for (String term : terms) {
                String[] word = term.split("\t");
                if (word.length == 2) {
                    WordNode wn = IDFtree.addWord(word[0]);
                    wn.obj = Double.valueOf(word[1]);//存入IDF值
                } else System.out.println(term);
            }
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }
        return IDFtree;
    }

    /**
     * 给定的一段文本，返回相应的包含TF-IDF值的wordNode数组.
     *
     * @param text
     */
    public ArrayList<WordNode> CalTFIDF(String text) {
        TrieTree TFIDFtree = new TrieTree();//用于存储TF-IDF信息的树
        List<Term> terms = NlpAnalysis.parse(text);//进行分词
        int wordCount = terms.size();
        for (Term term : terms)//进行词频统计
        {
            TFIDFtree.addWord(term.getName(), term.natrue().natureStr);
        }
        double tfidf = 0;
        ArrayList<WordNode> result = new ArrayList<WordNode>();
        for (WordNode wn : TFIDFtree.word_list) {
//            System.out.println((double) IDFtree.getWordNode(wn.getWord()).obj);
            if (IDFtree.getWordNode(wn.getWord()) != null)//语料IDF数据库中存在该词
            {
                double idf = (Double) IDFtree.getWordNode(wn.getWord()).obj;
//                if (idf != 0) {
//                    System.out.println(wn.getWord());
//                }
                wn.tfidf = (double) wn.getFreq() / wordCount * idf;
            } else {
                wn.tfidf = (double) wn.getFreq() / wordCount * (double) Math.log(400);
            }
            result.add(wn);
        }
        Collections.sort(result, TrieTree.TFIDF_dowmSortor);
        return result;
    }


    /**
     * 给定的包含单词的字典树，返回相应的包含TF-IDF值的字典树实例
     *
     * @param wordTree
     */
    public TrieTree CalTFIDF_ByTT(TrieTree wordTree) {
        for (WordNode wn : wordTree.word_list) {
//            System.out.println((double) IDFtree.getWordNode(wn.getWord()).obj);
            if (IDFtree.getWordNode(wn.getWord()) != null)//语料IDF数据库中存在该词
            {
                double idf = (Double) IDFtree.getWordNode(wn.getWord()).obj;
//                if (idf != 0) {
//                    System.out.println(wn.getWord());
//                }
                wn.tfidf = (double) wn.getFreq() / wn.getFreq() * idf;
            } else {
                wn.tfidf = (double) wn.getFreq() / wn.getFreq() * (double) Math.log(400);
            }
//            result.add(wn);
        }
//        Collections.sort(result, TrieTree.TFIDF_dowmSortor);
        return wordTree;
    }


    /**
     * 给定的一段文本，返回相应的包含TF-IDF值的wordNode树.
     *
     * @param text
     */
    public TrieTree CalTFIDF2Tree(String text) {
        TrieTree TFIDFtree = new TrieTree();//用于存储TF-IDF信息的树
        List<Term> terms = NlpAnalysis.parse(text);//进行分词
        int wordCount = terms.size();
        for (Term term : terms)//进行词频统计
        {
            TFIDFtree.addWord(term.getName(), term.natrue().natureStr);
        }
        double tfidf = 0;
//        ArrayList<WordNode> result = new ArrayList<WordNode>();
        //开始计算TF-IDF值
        for (WordNode wn : TFIDFtree.word_list) {
//            System.out.println((double) IDFtree.getWordNode(wn.getWord()).obj);
            if (IDFtree.getWordNode(wn.getWord()) != null)//语料IDF数据库中存在该词
            {
                double idf = (Double) IDFtree.getWordNode(wn.getWord()).obj;
//                if (idf != 0) {
//                    System.out.println(wn.getWord());
//                }
                wn.tfidf = (double) wn.getFreq() / wordCount * idf;
            } else {
                wn.tfidf = (double) wn.getFreq() / wordCount * (double) Math.log(400);
            }
//            result.add(wn);
        }
//        Collections.sort(result, TrieTree.TFIDF_dowmSortor);
        return TFIDFtree;
    }

}
