package AppCluster;


import Utils.*;
import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoCollection;
import org.ansj.domain.Term;
import org.ansj.splitWord.analysis.NlpAnalysis;
import org.bson.Document;

import java.io.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.logging.FileHandler;
import java.util.logging.Logger;

/**
 * Created by ITTC-Jayvee on 2015/4/8.
 */
public class AnalysisAppIntro {
    static Logger logger = Logger.getLogger(String.valueOf(AnalysisAppIntro.class));

    public static void calTFIDFbyCategory() {
        File dir = new File("AppChinaProject/data");
        Map<String, Integer> resultMap = new HashMap<String, Integer>();
        StringBuilder sb = new StringBuilder();
        if (dir.isDirectory()) {
            for (File file : dir.listFiles()) {
                String s = FileUtils.File2str(file.getPath(), "utf-8");
//                List<Term> parse = NlpAnalysis.parse(s);
//                TrieTree trieTree = new TrieTree(parse);
                System.out.println(file.getName() + ":");
                IDFCaculator idfCaculator = new IDFCaculator("AppChinaProject/IDF值.txt");
                TrieTree tree = idfCaculator.CalTFIDF2Tree(s);
                ArrayList<WordNode> sortedList = tree.getSortedList(TrieTree.TFIDF_dowmSortor);
                int count = 0;
                for (int i = 0; i < 50; ) {
                    if (count < sortedList.size()) {
                        WordNode wn = sortedList.get(count++);
                        if (!wn.getNature().equals("null")
                                && !wn.getNature().equals("w")
                                && !wn.getNature().equals("m")
                                && !resultMap.containsKey(wn.getWord())
                                && wn.getWord().length() > 1) {
                            System.out.println(wn.getWord() + "\ttfidf=" + wn.tfidf + "\tnature=" + wn.getNature());
                            i++;
                            resultMap.put(wn.getWord(), 1);
                            sb.append(wn.getWord()).append("\n");
                        }
                    } else {
                        break;
                    }
                }
            }
            try {
                FileUtils.byte2File(sb.toString().getBytes("utf-8"), "AppChinaProject", "vecWords.txt");
            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            }
        }
    }


    public static Map<String, Integer> getMetaVecMap(String filepath) {
        String str = FileUtils.File2str(filepath, "utf-8");
        String[] line = str.split("\n");
        Map<String, Integer> indexMap = new HashMap<String, Integer>(0);
        indexMap.put("indexCount", line.length);
        for (int i = 0; i < line.length; i++) {
            indexMap.put(line[i], i);
        }
        return indexMap;
    }

    public static void processIntroVecData() {
        String addr = FileUtils.File2str("AppChinaProject/conf/MongoDB_config", "utf-8");
        MongoDBUtils mongoDBUtils = new MongoDBUtils(addr, 27017, "AppChinaData");
        MongoCollection<Document> appInfo = mongoDBUtils.getCollection("AppInfo");
        FindIterable<Document> documents = appInfo.find();
        IDFCaculator idfCaculator = new IDFCaculator("AppChinaProject/data/IDF值.txt");
        Map<String, Integer> metaVecMap = getMetaVecMap("AppChinaProject/data/vecWords.txt");

        int count = 0;

        try {
            File file_data = new File("AppChinaProject/data/appintro_Vec_50_data.txt");
            FileOutputStream fos_data = new FileOutputStream(file_data);
            File file_name = new File("AppChinaProject/data/appintro_Vec_50_name.txt");
            FileOutputStream fos_name = new FileOutputStream(file_name);
            for (Document doc : documents) {
                StringBuilder sb_data = new StringBuilder();
                StringBuilder sb_name = new StringBuilder();
                sb_data.append(count);
                String app_name = doc.getString("app_name");
                logger.info("正在处理第" + count + "个应用：" + app_name);
                sb_name.append(app_name).append("\n");
                String app_intro = doc.getString("app_intro");
                TrieTree tree = idfCaculator.CalTFIDF2Tree(app_intro);
                ArrayList<WordNode> word_list = tree.word_list;
                for (WordNode wn : word_list) {
                    if (metaVecMap.containsKey(wn.getWord())) {
                        int index = metaVecMap.get(wn.getWord());
                        sb_data.append("\t").append(index).append(":").append(wn.tfidf);
                    }
                }
                sb_data.append("\n");
                fos_data.write(sb_data.toString().getBytes("utf-8"));
                fos_name.write(sb_name.toString().getBytes("utf-8"));
                count++;
            }
//            System.out.println();
            fos_data.close();
            fos_name.close();
            logger.info("处理完毕！输出地址为：\ndata:" + file_data.getAbsolutePath() + "\nname:" + file_name.getAbsolutePath());
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }


    public static void save(){

    }

    public static void main(String a[]) throws IOException {
//AnalysisAppIntro.logger.addHandler(new FileHandler("testlog"));
//        AnalysisAppIntro.logger.
//        AnalysisAppIntro.logger.info("testlogdddd");
//        getCategories();
//        calTFIDFbyCategory();
        processIntroVecData();
    }
}
