package LexicalUtils.BasicStructure;

import java.util.ArrayList;
import java.util.Stack;

/**
 * Stanford Parser解析后的自定义基本结点
 * Created by Jayvee on 2015/2/28.
 */
public class ParserNode {
    String type;
    String word;
    ParserNode parent;
    ArrayList<ParserNode> childs = new ArrayList<ParserNode>(0);
    boolean isLeaf;

    public ParserNode(String type, String word, ParserNode parent) {
        this.type = type;
        this.word = word;
        this.parent = parent;
        this.isLeaf = true;

    }

    public ParserNode(String type, ParserNode parent) {
        this.type = type;

        this.parent = parent;
        this.word = null;
        this.isLeaf = false;
    }

    public ParserNode() {
        this.type = "ROOT";
        this.word = null;
        this.isLeaf = false;
        this.parent = null;
    }

    public void addChild(ParserNode childNode) {
        childs.add(childNode);
    }




    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public String getWord() {
        return word;
    }

    public void setWord(String word) {
        this.word = word;
    }

    public ParserNode getParent() {
        return parent;
    }


    public ArrayList<ParserNode> getChilds() {
        return childs;
    }

    public void setChilds(ArrayList<ParserNode> childs) {
        this.childs = childs;
    }

    public boolean isLeaf() {
        return isLeaf;
    }

    public void setLeaf(boolean isLeaf) {
        this.isLeaf = isLeaf;
    }

}
