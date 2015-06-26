package LDAutils;

import ansj.lda.LDA;
import ansj.lda.impl.LDAGibbsModel;
import ansj.util.impl.AnsjAnalysis;
import com.google.common.base.Charsets;
import com.google.common.io.Files;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;

public class Test3 {

    public static void main(String[] args) throws IOException {
        LDA lda = new LDA(AnsjAnalysis.DEFAUlT, new LDAGibbsModel(20, 50 / (double) 10, 0.1, 200, Integer.MAX_VALUE, Integer.MAX_VALUE));
        BufferedReader newReader = Files.newReader(new File("D:\\CS\\Git\\NLP\\AppChinaProject\\data\\sanguo.txt"), Charsets.UTF_8);
        String temp = null;
        int i = 0;
        //���Ŀ¼�ļ�
        // ÿһ����һ��doc���ı�
        //��������
//        File dirfile = new File("D:\\CS\\TrainSet\\SogouC_Reduced");
//        File[] files = dirfile.listFiles();
//        for (File classfile : files) {
//            for (File file : classfile.listFiles()) {
//                System.out.println(i);
//                if (file.canRead() && file.getName().endsWith(".txt")) {
////                    parserFile(fos, file);
//                    String str = FileUtils.File2str(file.getPath(), "gbk");
//                    str = str.replaceAll("\n", " ");
//                    lda.addDoc(String.valueOf(++i), str);
//                }
//            }
//        }


        while ((temp = newReader.readLine()) != null) {
            lda.addDoc(String.valueOf(++i), temp);
            if (i > 10000) {
                break;
            }
        }

        lda.trainAndSave("result/news/", 50, "utf-8");
    }
}
