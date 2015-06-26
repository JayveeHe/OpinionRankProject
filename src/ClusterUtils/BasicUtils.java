package ClusterUtils;


import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Comparator;

/**
 * Created by Jayvee on 2014/10/8.
 */
public class BasicUtils {
    /**
     * 计算两向量间的余弦距离
     *
     * @param vec1
     * @param vec2
     * @return
     */
    public  static double calCosDist(float[] vec1, float[] vec2) {
        double fenzi = 0;
        double fenmu1 = 0;
        double fenmu2 = 0;
        int dSum = vec1.length;
        for (int i = 0; i < dSum; i++) {
            fenzi += vec1[i] * vec2[i];
            fenmu1 += vec1[i] * vec1[i];
            fenmu2 += vec2[i] * vec2[i];
        }
        double cosDist = fenzi / (Math.sqrt(fenmu1) * Math.sqrt(fenmu2));
        return cosDist > Double.MAX_VALUE ? 1 : cosDist;
    }

    /**
     * 计算两个向量间的欧式距离
     *
     * @param vec1
     * @param vec2
     * @return
     */
    protected static double calDist(float[] vec1, float[] vec2) {
        double dist = 0;
        int dimensionNum = vec1.length;
        for (int i = 0; i < dimensionNum; i++) {
            dist += Math.pow((vec1[i] - vec2[i]), 2);
        }
        return Math.sqrt(dist);
    }

    public static Comparator<IClusterCalculable> typeSorter = new Comparator<IClusterCalculable>() {
        @Override
        public int compare(IClusterCalculable o1, IClusterCalculable o2) {
            return o1.getTypeID() - o2.getTypeID();
        }
    };

    /**
     * 将{@link ClusterUtils.APCluster}或{@link ClusterUtils.KMeansCluster}的聚类结果保存到csv文件中
     *
     * @param data       聚类结果
     * @param resultPath 保存路径
     */
    public static void saveResults(IClusterCalculable[][] data, String resultPath, boolean isWriteObj) throws IOException {
        File resultFile = new File(resultPath);
        FileOutputStream fos = new FileOutputStream(resultFile);
//        fos.write("\\xEF\\xBB\\xBF".getBytes());
        for (IClusterCalculable[] typeNodes : data) {
            StringBuilder sb = new StringBuilder();
            sb.append(typeNodes[0].getTypeID());
            for (IClusterCalculable node : typeNodes) {
                if (isWriteObj) {
                    sb.append("," + node.getObj());
                }
            }
            sb.append("\n");
            fos.write(sb.toString().getBytes("utf-8"));
        }
        System.out.println("结果保存完毕，地址为：" + resultFile.getAbsolutePath());
        fos.close();
    }

}
