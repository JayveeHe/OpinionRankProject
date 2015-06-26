package Word2VecUtils;

import ClusterUtils.IClusterCalculable;

/**
 * Created by Jayvee on 2015/6/9.
 */
public class WordClusterNode implements IClusterCalculable {
    float[] vec;
    int ID;
    int typeID;
    String word;

    public WordClusterNode(String word, int ID, float[] vec) {
        this.word = word;
        this.ID = ID;
        this.vec = vec;

    }


    @Override
    public float[] getVecValues() {
        return this.vec;
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
        this.vec = vecValues;
    }

    @Override
    public void setID(int ID) {
        this.ID = ID;
    }

    @Override
    public Object getObj() {
        return this.word;
    }
}
