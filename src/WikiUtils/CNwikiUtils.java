package WikiUtils;

import Utils.FileUtils;
import org.nlpcn.commons.lang.jianfan.JianFan;

import java.io.*;

/**
 * Created by Jayvee on 2015/6/25.
 */
public class CNwikiUtils {
    public static void loadCNwikiData() throws IOException {
//用于将繁体的文本转为简体文本
        File root = new File("D:\\CS\\NLPtrainset\\wikidata");
        int i = 0;
        for (File txt : root.listFiles()) {
            if (!txt.isDirectory()) {
                System.out.println(i + ":" + txt.getAbsolutePath());
                String str = FileUtils.File2str(txt.getAbsolutePath(), "utf-8");
                String jstr = JianFan.f2J(str);
                File jtxt = new File("D:\\CS\\NLPtrainset\\wikidata\\jianti\\" + i++ + ".txt");
                FileOutputStream fos = new FileOutputStream(jtxt);
                fos.write(jstr.getBytes("utf-8"));
//            System.out.println(jstr);
            }
        }
    }

    public static void main(String a[]) {
        try {
            loadCNwikiData();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
