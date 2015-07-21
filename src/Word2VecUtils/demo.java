package Word2VecUtils;

/**
 * Created by Jayvee on 2015/6/1.
 */

import ClusterUtils.BasicUtils;
import ClusterUtils.IClusterCalculable;
import ClusterUtils.KMeansCluster;
import Utils.FileUtils;
import Word2VecUtils.vec.Learn;
import Word2VecUtils.vec.Word2VEC;
import Word2VecUtils.vec.domain.WordEntry;
import org.ansj.domain.Term;
import org.ansj.splitWord.analysis.NlpAnalysis;
import org.ansj.splitWord.analysis.ToAnalysis;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Set;



public class demo {

    public static void main(String[] args) throws IOException {
//        final File sportCorpusFile = new File("D:\\CS\\Java\\NLP\\OpinionRankProject\\data\\word2vecData\\word2vec_resultSanguo.txt");
        File projFile = new File("");
        System.out.println(projFile.getAbsolutePath());
        final String proj_path = projFile.getAbsolutePath();
//        File dirfile = new File(proj_path + "\\data\\jianti");
//        File dirfile = new File(args[0]);
//        File[] files = dirfile.listFiles();
////
////        final File fout = new File(proj_path + "\\data\\wikidata\\wiki_result.txt");
//        final File fout = new File(args[1]);
////        构建语料
//        try (FileOutputStream fos = new FileOutputStream(fout)) {
//            int i = 0;
//            for (File file : files) {
////                for (File file : classfile.listFiles()) {
//                Date date = new Date(System.currentTimeMillis());
//                System.out.println(i+++"time:"+date);
//                if (file.canRead() && file.getName().endsWith(".txt")) {
////                    parserFile(fos, file);
//                    String str = FileUtils.File2str(file.getPath(), "utf-8");
//                    List<Term> terms = NlpAnalysis.parse(str);
//                    StringBuilder sb = new StringBuilder();
//                    for (Term term : terms) {
//                        if (!term.getName().equals(" ")) {
//                            sb.append(term.getName() + " ");
//                        }
//                    }
//                    fos.write(sb.toString().getBytes("utf-8"));
//                }
////                }
//            }
//        }
//
//        try (FileOutputStream fos = new FileOutputStream(sportCorpusFile)) {
//            int i = 0;
////            for (File classfile : files) {
//                for (File file : files) {
//                    System.out.println(i++);
//                    if (file.canRead() && file.getName().endsWith(".txt")) {
////                    parserFile(fos, file);
//                        String str = FileUtils.File2str(file.getPath(), "utf-8");
//                        List<Term> terms = NlpAnalysis.parse(str);
//                        StringBuilder sb = new StringBuilder();
//                        for (Term term : terms) {
//                            sb.append(term.getName() + " ");
//                        }
//                        fos.write(sb.toString().getBytes("gbk"));
//                    }
////                }
//            }
//        }


////
////        //进行分词训练
////
//        System.out.println("start training");
//        Learn lean = new Learn();

//        lean.learnFile(fout);
//
////        lean.saveModel(new File(proj_path + "\\data\\word2vecData\\cnwiki.mod"));
//        lean.saveModel(new File(args[2]));
//        System.out.println("model saved at " + args[2]);

        //加载测试

        Word2VEC w2v = new Word2VEC();
//        w2v.loadJavaModel(proj_path + "\\data\\wikidata\\wikimodel.mod");
        w2v.loadJavaModel("e:\\wikimodel_reduced.mod");
//        w2v.loadJavaModel(args[2]);

//        float[] vector = w2v.getWordVector("CBA");
//        System.out.println(w2v.analogy("球队","投篮","CBA"));
//        System.out.println(Arrays.toString(vector));
//        String qury = "喜欢";
//        FileOutputStream fos = new FileOutputStream(
//                new File("D:\\CS\\Git\\NLP\\AppChinaProject\\data\\word2vecData\\" + qury + ".csv"));
////        fos.write("\\xEF\\xBB\\xBF".getBytes());
//        fos.write("词汇,距离\n".getBytes());
//        for (WordEntry we : w2v.distance(qury)) {
//            System.out.println(we.name + "\t" + we.score);
//            fos.write((we.name + "," + we.score + "\n").getBytes());
//        }
        String sent1 = "我喜欢吃西瓜";
        String sent2 = "我讨厌吃西瓜";
//        double cosDist = BasicUtils.calCosDist(VecUtils.sent2vec(w2v, sent1), VecUtils.sent2vec(w2v, sent2));
//        System.out.println(cosDist);
        String quryword = "足球";
        Set<WordEntry> wordEntries = w2v.distance(quryword);
//        w2v.getWordVector()
//        System.out.println(quryword+"===============");
//        for (WordEntry we : wordEntries) {
//            System.out.println(we.name + "\t" + we.score);
//        }
//
//        quryword= "讨厌";
        wordEntries = w2v.distance(quryword);
        System.out.println(quryword + "==============");
        for (WordEntry we : wordEntries) {
            System.out.println(we.name + "\t" + we.score);
        }

        quryword= "学校";
        wordEntries = w2v.distance(quryword);
        System.out.println(quryword + "==============");
        for (WordEntry we : wordEntries) {
            System.out.println(we.name + "\t" + we.score);
        }

//        wordCluster(w2v,20,20);

    }

    public static void wordCluster(Word2VEC w2v, int iterNum, int clusterNum) {
        KMeansCluster kmc = new KMeansCluster(clusterNum, iterNum);
        HashMap<String, float[]> wordMap = w2v.getWordMap();
        //build word cluster nodes
        int wordCount = wordMap.size();
        System.out.println(wordCount);
        WordClusterNode[] dataset = new WordClusterNode[wordCount];
        int i = 0;
        for (String key : wordMap.keySet()) {
            float[] vec = wordMap.get(key);
            dataset[i] = new WordClusterNode(key, i, vec);
            i++;
        }
        IClusterCalculable[][] result = kmc.kmeans(dataset, true);
        try {
            BasicUtils.saveResults(result, "kmeansResult.csv", true);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }





    private static void parseStr(FileOutputStream fos, String title) throws IOException {
        List<Term> parse2 = ToAnalysis.parse(title);
        StringBuilder sb = new StringBuilder();
        for (Term term : parse2) {
            sb.append(term.getName());
            sb.append(" ");
        }
        fos.write(sb.toString().getBytes());
        fos.write("\n".getBytes());
    }
}

