package OpinonRankUtils;

import ClusterUtils.BasicUtils;
import Utils.FileUtils;
import Word2VecUtils.VecUtils;
import Word2VecUtils.vec.Word2VEC;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;

/**
 * Created by Jayvee on 2015/6/29.
 */
public class OpinionRankDemo {
    public static void main(String args[]) throws JSONException, IOException {
        Word2VEC w2v = new Word2VEC();
        try {
            System.out.println("loading model");
            w2v.loadJavaModel("e:\\wikimodel_reduced.mod");
            System.out.println("model loaded!");
        } catch (IOException e) {
            e.printStackTrace();
        }
        String txt = FileUtils.File2str("./data/rates.txt", "utf-8");
        String[] rates = txt.split("\r\n");
//        double[][] similarityMat = calSimilarityMat(w2v, rates);
//        System.out.println(similarityMat.length);
//        JSONObject root = new JSONObject();
//        JSONArray smat = new JSONArray();
//        for (double[] row : similarityMat) {
//            JSONArray rowdata = new JSONArray();
//            for (double k : row) {
//                rowdata.put(k);
//            }
//            smat.put(rowdata);
//        }
//        root.put("similarityMatrix", smat);
//        FileOutputStream fos = new FileOutputStream(new File("./data/smat.json"));
//        fos.write(smat.toString().getBytes("utf-8"));
        System.out.println("loading similarity matrix");
        double[][] smat = loadSimilarityMat("./data/smat.json");
        System.out.println("loading similarity matrix done!");
        iterTrustness(smat, rates, 5, 1000);
    }

    public static double[][] calSimilarityMat(Word2VEC w2v, String[] sent_list) throws IOException {
        double[][] Smat = new double[sent_list.length][sent_list.length];
        for (int i = 0; i < sent_list.length; i++) {
            for (int j = 0; j < sent_list.length; j++) {
                Smat[i][j] = BasicUtils.calCosDist(VecUtils.sent2vec(w2v, sent_list[i]), VecUtils.sent2vec(w2v, sent_list[j]));
                System.out.println(i * sent_list.length + j + ":\t" + Smat[i][j]);
            }
        }
        return Smat;
    }

    public static double[][] loadSimilarityMat(String path) throws JSONException {
        String matstr = FileUtils.File2str(path, "utf-8");
        JSONTokener tokener = new JSONTokener(matstr);
        JSONArray rows = (JSONArray) tokener.nextValue();
        int len = rows.length();
        double[][] smat = new double[len][len];
        for (int i = 0; i < len; i++) {
            JSONArray row = rows.getJSONArray(i);
            for (int j = 0; j < len; j++) {
                smat[i][j] = row.getDouble(j);
            }
        }
        return smat;
    }

    public static void iterTrustness(double[][] smat, String[] sent_list, int iternum, int topk) {
        int len_sent = smat[0].length;
        double[] trustVec = new double[len_sent];
        double[][] supporty = new double[len_sent][len_sent];
        //可信度、支撑度初始赋值
        for (int i = 0; i < len_sent; i++) {
            trustVec[i] = 1;
            for (int j = 0; j < len_sent; j++) {
                supporty[i][j] = 1;
            }
        }
        //进行迭代
        for (int iterIndex = 0; iterIndex < iternum; iterIndex++) {
            double[] temp_trustVec = new double[len_sent];
            double[][] temp_supporty = new double[len_sent][len_sent];
            for (int i = 0; i < len_sent; i++) {
                for (int j = 0; j < len_sent; j++) {
                    temp_supporty[i][j] =  smat[i][j]*trustVec[i];
                    temp_trustVec[i] += supporty[i][j];
                }
            }
            trustVec = temp_trustVec;
            supporty = temp_supporty;
        }
        ArrayList<SentNode> sentArray = new ArrayList<>();
        for (int i = 0; i < len_sent; i++) {
            sentArray.add(i, new SentNode(sent_list[i], trustVec[i]));
        }
        Collections.sort(sentArray);
        for (int k = 0; k < topk; k++) {
            SentNode sentNode = sentArray.get(k);
            System.out.println(sentNode.sent + "\t" + sentNode.getTrustNess());
        }
    }


}
