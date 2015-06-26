package AppCluster;

import ClusterUtils.*;

import java.io.IOException;

/**
 * Created by ITTC-Jayvee on 2015/4/9.
 */
public class testCluster {
    public static void main(String a[]) {
//        AppNode[] appNodes = AppNode.getAppNodesByFile("AppChinaProject/data/appintro_Vec_50_data.txt",
//                "AppChinaProject/data/appintro_Vec_50_name.txt");
//        System.out.println(appNodes.length);
//        APCluster apCluster = new APCluster(appNodes, 1, 0.6f, 100);
//        AppNode[][] results = (AppNode[][]) apCluster.startCluster();
////        KMeansCluster kMeansCluster = new KMeansCluster(10,10);
////        IClusterCalculable[][] results =  kMeansCluster.kmeans(appNodes);
//        try {
//            BasicUtils.saveResults( results, "AppChinaProject/data/clusterResult" + System.currentTimeMillis() + ".csv", true);
//        } catch (IOException e) {
//            e.printStackTrace();
//        }
        String type = a[0];
        String datafilepath = a[1];
        String namefilepath = a[2];
        String metavecpath = a[3];
        String resultfilepath = a[4];
//        AppNode[] appNodes = AppNode.getAppNodesByFile("AppChinaProject/data/appintro_Vec_50_data.txt",
//                "AppChinaProject/data/appintro_Vec_50_name.txt","AppChinaProject/data/vecWords.txt");
        AppNode[] appNodes = AppNode.getAppNodesByFile(datafilepath,
                namefilepath, metavecpath);
        System.out.println(appNodes.length);
        IClusterCalculable[][] results = null;
        if (type.equals("canopy")) {
//        canopy粗聚类
            results = CanopyCluster.startCluster(appNodes, 0.5f, 0.08f);
        } else if (type.equals("ap")) {
            APCluster apCluster = new APCluster(appNodes, 1, 0.6f, 100);
            results = apCluster.startCluster();
        } else if (type.equals("kmeans")) {
            int clusterNum = Integer.valueOf(a[5]);
            int iterNum = Integer.valueOf(a[6]);
            System.out.println("clusterNum=" + clusterNum + ",iterNum=" + iterNum);
            KMeansCluster kMeansCluster = new KMeansCluster(clusterNum, iterNum);
            results = kMeansCluster.kmeans(appNodes,true);

        }

        //AP聚类
//        AppNode[][] results = (AppNode[][]) apCluster.startCluster();
        try {
//            BasicUtils.saveResults( results, "clusterResult" + System.currentTimeMillis() + ".csv", true);
            BasicUtils.saveResults(results, resultfilepath, true);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
