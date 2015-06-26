package AppCluster;

import ClusterUtils.IClusterCalculable;
import Utils.FileUtils;

import java.util.Map;

/**
 * Created by ITTC-Jayvee on 2015/4/9.
 */
public class AppNode implements IClusterCalculable<String> {

    String app_name = null;
    //    String app_intro = null;
    float[] vecValues = null;
    int ID;
    int typeID;


    public AppNode(String app_name, float[] vecValues, int ID) {
        this.app_name = app_name;
        this.vecValues = vecValues;
        this.ID = ID;
    }

    /**
     * 从data、name文件构建AppNode对象数组
     *
     * @param datafilepath
     * @param namefilepath
     * @return
     */
    public static AppNode[] getAppNodesByFile(String datafilepath, String namefilepath,String metavecpath) {
        String data_str = FileUtils.File2str(datafilepath, "utf-8");
        String[] dataline = data_str.split("\n");
        String name_str = FileUtils.File2str(namefilepath, "utf-8");
        String[] nameline = name_str.split("\n");
//        Map<String, Integer> metaVecMap = AnalysisAppIntro.getMetaVecMap("AppChinaProject/data/vecWords.txt");
        Map<String, Integer> metaVecMap = AnalysisAppIntro.getMetaVecMap(metavecpath);
        int vecLen = metaVecMap.get("indexCount");
        AppNode[] nodes = new AppNode[dataline.length];
        for (int i = 0; i < dataline.length; i++) {//
            //读取vec向量值
            float[] vec = new float[vecLen];
            String[] split = dataline[i].split("\t");
            for (int j = 1; j < split.length; j++) {//从1开始，跳过了开头的nameIndex
                String[] sd = split[j].split(":");
                int vecIndex = Integer.valueOf(sd[0]);
                float vecValue = Float.valueOf(sd[1]);
                vec[vecIndex] = vecValue;
            }
            //读取应用名字
            String app_name = nameline[i];
            //创建AppNode对象
            nodes[i] = new AppNode(app_name, vec, i);
        }
        return nodes;
    }

    @Override
    public float[] getVecValues() {
        return this.vecValues;
    }

    @Override
    public int getID() {
        return this.ID;
    }

    @Override
    public int getTypeID() {
        return this.typeID;
    }

    @Override
    public void setTypeID(int typeID) {
        this.typeID = typeID;
    }

    @Override
    public void setVecValues(float[] vecValues) {
        this.vecValues = vecValues;
    }

    @Override
    public void setID(int ID) {
        this.ID = ID;
    }

    @Override
    public String getObj() {
        return this.app_name;
    }
}
