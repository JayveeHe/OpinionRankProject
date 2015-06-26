package DataProcess;

import Utils.*;
import com.mongodb.BasicDBObject;
import com.mongodb.client.FindIterable;
import com.mongodb.client.MongoCollection;
import org.bson.Document;

import java.io.*;
import java.util.*;

/**
 * Created by ITTC-Jayvee on 2015/4/13.
 */
public class posterProcess {
    public static ArrayList<String> getKeywords(String text, int keyNum) {
        IDFCaculator idfCaculator = new IDFCaculator("AppChinaProject/data/IDF值.txt");
        ArrayList<WordNode> wordNodes = idfCaculator.CalTFIDF(text);
        Collections.sort(wordNodes, TrieTree.TFIDF_dowmSortor);
        int outNum = wordNodes.size() < keyNum ? wordNodes.size() : keyNum;
//        String[] result = new String[outNum];
        List<String> result = new ArrayList<String>();
        int count = 0;
        for (int i = 0; i < outNum; i++) {
            WordNode wn = wordNodes.get(i);
            if (!wn.getNature().equals("w")
                    && !wn.getNature().equals("m")
                    && !wn.getNature().equals("null")) {
                String word = wordNodes.get(i).getWord();
                word = word.replace("\n", "");
                word = word.replace("\r\n", "");
                word = word.replace("\r", "");
                result.add(word);
//                result[count] = wordNodes.get(i).getWord();
                if (count > keyNum) {
                    break;
                }
                count++;
            }
        }
        return (ArrayList<String>) result;
    }

    public static void getClusterKeywords() throws IOException {
        String clusterStr = FileUtils.File2str("AppChinaProject/data/result_kmeans_50_30.csv", "utf-8");
        String[] lines = clusterStr.split("\n");
        String addr = FileUtils.File2str("AppChinaProject/conf/MongoDB_config", "utf-8");
        MongoDBUtils mongoDBUtils = new MongoDBUtils(addr, 27017, "AppChinaData");
        MongoCollection<Document> appInfo = mongoDBUtils.getCollection("AppInfo");

        File output = new File("AppChinaProject/data/clusterKeywords.csv");
        FileOutputStream fos = new FileOutputStream(output);
        int appcount = 0;
        for (int i = 0; i < lines.length; i++) {
            String[] names = lines[i].split(",");
            String typeID = names[0];
//            appcount++;
//            System.out.println("第" + appcount + "个聚类");
            for (int j = 1; j < names.length; j++) {
                appcount++;
                System.out.println("第" + appcount + "个应用");
                StringBuilder sb = new StringBuilder();
                String appname = names[j];
                FindIterable<Document> documents = appInfo.find(new BasicDBObject("app_name", appname));
                for (Document doc : documents) {
                    sb.append(doc.getString("app_intro") + '\n');
                }
                ArrayList<String> keywords = getKeywords(sb.toString(), 10);
                sb = new StringBuilder();
                sb.append(typeID + "," + appname);
                for (String keyword : keywords) {
                    sb.append("," + keyword);
                }
                sb.append("\n");
                fos.write(sb.toString().getBytes("utf-8"));
            }

        }
        fos.close();
        System.out.println("done");
    }

    public void sortKeywords(int keywordNum, String resultPath) {
        String keywordsStr = FileUtils.File2str("AppChinaProject/data/clusterKeywords.csv", "utf-8");
        String[] lines = keywordsStr.split("\n");
        Map<String, Map<String, KeyWordNode>> resultMap = new HashMap<String, Map<String, KeyWordNode>>();
        for (String line : lines) {
            String[] datas = line.split(",");
            String typeID = datas[0];
            String appname = datas[1];
            if (resultMap.containsKey(typeID)) {
                Map<String, KeyWordNode> keyWordNodeMap = resultMap.get(typeID);
                if (datas.length > 3) {
                    for (int i = 2; i < datas.length; i++) {
                        String keyword = datas[i];
                        if (keyWordNodeMap.containsKey(keyword)) {
                            keyWordNodeMap.get(keyword).addValue((float) Math.pow(Math.E, -i));
                        } else {
                            KeyWordNode keyWordNode = new KeyWordNode(keyword, (float) Math.pow(Math.E, -i)/i, appname);
                            keyWordNodeMap.put(keyword, keyWordNode);
                        }
                    }
                }
            } else {
                Map<String, KeyWordNode> keyWordNodeMap = new HashMap<String, KeyWordNode>();
                if (datas.length > 3) {
                    for (int i = 2; i < datas.length; i++) {
                        String keyword = datas[i];
                        KeyWordNode keyWordNode = new KeyWordNode(keyword, (float) Math.pow(Math.E, -i)/i, appname);
                        keyWordNodeMap.put(keyword, keyWordNode);
                    }
                    resultMap.put(typeID, keyWordNodeMap);
                } else {
                    resultMap.put(typeID, new HashMap<String, KeyWordNode>());
                }

            }
        }
        //处理result
        Set<String> keySet = resultMap.keySet();
        File output = new File(resultPath);
        try {
            FileOutputStream fos;
            fos = new FileOutputStream(output);
            for (String key : keySet) {
                Map<String, KeyWordNode> keyWordNodeMap = resultMap.get(key);
                ArrayList<KeyWordNode> keyWordNodes = new ArrayList<KeyWordNode>();
                for (KeyWordNode keyWordNode : keyWordNodeMap.values()) {
                    keyWordNodes.add(keyWordNode);
                }
                try {
                    Collections.sort(keyWordNodes, keyWordNodeComparator);
                } catch (IllegalArgumentException e) {
                    e.printStackTrace();
                }
                //输出该类的top K个关键词
                StringBuilder sb = new StringBuilder();
                sb.append(key );
                int keywordMax = keywordNum < keyWordNodes.size() ? keywordNum : keyWordNodes.size();
                for (int i = 0; i < keywordMax; i++) {
                    sb.append("," + keyWordNodes.get(i).getKeyword());
                }
                sb.append("\n");
                fos.write(sb.toString().getBytes("utf-8"));
            }
            System.out.println("sort keywords done!");
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static Comparator<KeyWordNode> keyWordNodeComparator = new Comparator<KeyWordNode>() {
        @Override
        public int compare(KeyWordNode o1, KeyWordNode o2) {
            if (o1.getValue() - o2.getValue() > 0) {
                return -1;
            } else if (o1.getValue() - o2.getValue() < 0) {
                return 1;
            } else {
                return 0;
            }

        }
    };

    class KeyWordNode {
        String keyword;
        float value;
        String appname;

        public KeyWordNode(String keyword, float value, String appname) {
            this.keyword = keyword;
            this.value = value;
            this.appname = appname;
        }

        public void addValue(float add_value) {
            this.value += add_value;
        }

        public float getValue() {
            return value;
        }

        public String getAppname() {
            return appname;
        }

        public String getKeyword() {
            return keyword;
        }
    }

    public static void main(String a[]) throws IOException {
        posterProcess pp = new posterProcess();
        pp.sortKeywords(30, "AppChinaProject/data/sortedKeywords.csv");
    }
}
