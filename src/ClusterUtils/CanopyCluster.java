package ClusterUtils;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Canopy算法的工具类
 * Created by ITTC-Jayvee on 2015/4/10.
 */
public class CanopyCluster {

    /**
     * 进行Canopy聚类
     *
     * @param clusterNodes
     * @param T1
     * @param T2
     */
    public static IClusterCalculable[][] startCluster(IClusterCalculable[] clusterNodes, float T1, float T2) {
        List<IClusterCalculable> nodelist = new ArrayList<IClusterCalculable>(0);
        for (IClusterCalculable node : clusterNodes) {
            nodelist.add(node);
        }
        List<IClusterCalculable> canopyList = new ArrayList<IClusterCalculable>(0);
        Map<Integer, List<IClusterCalculable>> canopyMap = new HashMap<Integer, List<IClusterCalculable>>(0);
        while (nodelist.size() != 0) {
//            System.out.println(nodelist.size());
            System.out.println("nodelist_size = " + nodelist.size() + "canopy_size = " + canopyList.size());

            List<IClusterCalculable> newlist = new ArrayList<IClusterCalculable>();
            int count = 0;
            for (IClusterCalculable node : nodelist) {
                System.out.println(count++);
                if (canopyMap.size() == 0) {
                    //选出第一个canopy
                    List<IClusterCalculable> fellows = new ArrayList<IClusterCalculable>(0);
                    canopyMap.put(node.getID(), fellows);
                    canopyList.add(node);
                } else {
                    int i_offset = 0;
                    int nodeLen = nodelist.size();
                    //计算node与所有canopy的距离
                    int j_offset = 0;
                    int canopyLen = canopyList.size();
                    boolean isAssign = false;
                    for (int j = 0; j < canopyLen; j++) {
                        IClusterCalculable canopy = canopyList.get(j);
                        double dist = BasicUtils.calDist(node.getVecValues(), canopy.getVecValues());
                        if (dist < T1) {
                            if (!canopyMap.get(canopy.getID()).contains(node)) {
                                canopyMap.get(canopy.getID()).add(node);
                            }
                            if (dist < T2) {
                                isAssign = true;
                                break;
                            }
                        } else {
                            //作为新的canopy
                            canopyList.add(node);
                            canopyMap.put(node.getID(), new ArrayList<IClusterCalculable>(0));
                            isAssign = true;
                            break;
                        }
                    }
                    if (!isAssign) {
                        newlist.add(node);
                    }
                }
            }
            nodelist = newlist;
        }
        //构建结果
        IClusterCalculable[][] result = new IClusterCalculable[canopyList.size()][];
        int index = 0;
        for (List<IClusterCalculable> fellows : canopyMap.values()) {
            int count = 0;
//            result[index] = (IClusterCalculable[]) fellows.toArray();
            if (fellows.size() > 0) {
                result[index] = new IClusterCalculable[fellows.size()];
                for (IClusterCalculable node : fellows) {
                    result[index][count++] = node;
                }
                index++;
            }
        }
        return result;
    }

    public static void main(String a[]) {
        ArrayList<String> s = new ArrayList<String>();
        for (int i = 0; i < 10; i++) {
            s.add(String.valueOf(i));
        }

        for (int i = 0; i < s.size(); i++) {
            System.out.println("index = " + i + "value: " + s.get(i));
            if (i % 5 == 3) {
                s.remove(i);
//            System.out.println(s.get(i));
                i--;
            }
            System.out.println("size=" + s.size());
        }
    }
}