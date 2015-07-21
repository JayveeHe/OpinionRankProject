package LexicalUtils.BasicStructure;

import edu.stanford.nlp.trees.TypedDependency;

import java.util.*;

/**
 * Created by Jayvee on 2015/3/5.
 */
public class ParserManager {

//    private Map<String, Map<String, ArrayList<TypedDependency>>> GovMap;//以支配词作为key的map
//
//    private Map<String, Map<String, ArrayList<TypedDependency>>> DepdMap;//以被支配词作为key的map
//
//    public Map<String, Map<String, ArrayList<TypedDependency>>> getGovMap() {
//        return GovMap;
//    }
//
//    public Map<String, Map<String, ArrayList<TypedDependency>>> getDepdMap() {
//        return DepdMap;
//    }


    public SentenceNode sentenceNode;


    public Map<String, String> natureMap;

    public Map<String, ArrayList<TypedDependency>> DependencyMap;

    public String text;

    //建立句子级的存储结构，包含句子的相关句法分析树、依赖树

    public ParserManager(String text) {
        this.text = text;
        this.sentenceNode = new SentenceNode(text);
//        this.GovMap = new HashMap<String, Map<String, ArrayList<TypedDependency>>>(0);
//        this.DepdMap = new HashMap<String, Map<String, ArrayList<TypedDependency>>>(0);
//        this.natureMap = new HashMap<String, String>(0);
        //计算词性
    }


    /**
     * 根据依赖关系列表创建Map
     *
     * @param tds
     * @param GovMap
     * @param DepdMap
     */
    public static Map<String, ArrayList<TypedDependency>> buildDependencyMap(Collection<TypedDependency> tds,
                                                                             Map<String, Map<String, ArrayList<TypedDependency>>> GovMap,
                                                                             Map<String, Map<String, ArrayList<TypedDependency>>> DepdMap) {
        Map<String, ArrayList<TypedDependency>> rlMap = new HashMap<String, ArrayList<TypedDependency>>(0);

        for (TypedDependency td : tds) {
//            String longname = td.reln().getLongName();
            String shortname = td.reln().getShortName();
            if (rlMap.get(shortname) != null) {
                rlMap.get(shortname).add(td);
            } else {
                ArrayList<TypedDependency> arrayList = new ArrayList<TypedDependency>(1);
                arrayList.add(td);
                rlMap.put(shortname, arrayList);
            }
            //govmap的填充
            String govword = td.gov().value();
            if (GovMap.get(govword) != null) {
                ArrayList<TypedDependency> govrln = GovMap.get(govword).get(td.reln().getShortName());
                if (govrln != null) {
                    govrln.add(td);
                } else {
//                    Map<String, ArrayList<TypedDependency>> govRelatMap
//                            = new HashMap<String, ArrayList<TypedDependency>>(0);//支配词索引后以关系词为key的map
                    ArrayList<TypedDependency> arr_govrln = new ArrayList<TypedDependency>(0);
                    arr_govrln.add(td);
                    GovMap.get(govword).put(td.reln().getShortName(), arr_govrln);
//                    GovMap.get(govword).put(td.reln().getShortName(),td);
                }
            } else {
                Map<String, ArrayList<TypedDependency>> govRelatMap
                        = new HashMap<String, ArrayList<TypedDependency>>(0);//支配词索引后以关系词为key的map
                ArrayList<TypedDependency> arr_govrln = new ArrayList<TypedDependency>(0);
                arr_govrln.add(td);
                govRelatMap.put(td.reln().getShortName(), arr_govrln);
                GovMap.put(govword, govRelatMap);
            }

            //depdmap的填充
            String depdword = td.dep().value();
            if (DepdMap.get(depdword) != null) {
                ArrayList<TypedDependency> depdrln = DepdMap.get(depdword).get(td.reln().getShortName());
                if (depdrln != null) {
                    depdrln.add(td);
                } else {
//                    Map<String, ArrayList<TypedDependency>> govRelatMap
//                            = new HashMap<String, ArrayList<TypedDependency>>(0);//支配词索引后以关系词为key的map
                    ArrayList<TypedDependency> arr_depdrln = new ArrayList<TypedDependency>(0);
                    arr_depdrln.add(td);
                    DepdMap.get(depdword).put(td.reln().getShortName(), arr_depdrln);
//                    GovMap.get(govword).put(td.reln().getShortName(),td);
                }
            } else {
                Map<String, ArrayList<TypedDependency>> depdRelatMap
                        = new HashMap<String, ArrayList<TypedDependency>>(0);//支配词索引后以关系词为key的map
                ArrayList<TypedDependency> arr_depdrln = new ArrayList<TypedDependency>(0);
                arr_depdrln.add(td);
                depdRelatMap.put(td.reln().getShortName(), arr_depdrln);
                DepdMap.put(depdword, depdRelatMap);
            }

        }
        return rlMap;
    }


    ////////////////////暂时不用，集成到sentenceNode的构造函数中

    /**
     * 根据依赖关系列表创建Map
     *
     * @param tds
     */
    public static Map<String, ArrayList<TypedDependency>> buildDependencyMapByTDs(Collection<TypedDependency> tds) {
        Map<String, ArrayList<TypedDependency>> rlMap = new HashMap<String, ArrayList<TypedDependency>>(0);

        for (TypedDependency td : tds) {
            String longname = td.reln().getLongName();
            String shortname = td.reln().getShortName();
            if (rlMap.get(shortname) != null) {
                rlMap.get(shortname).add(td);
            } else {
                ArrayList<TypedDependency> arrayList = new ArrayList<TypedDependency>(1);
                arrayList.add(td);
                rlMap.put(shortname, arrayList);
            }
            /*
            //govmap的填充
            String govword = td.gov().value();
            if (GovMap.get(govword) != null) {
                ArrayList<TypedDependency> govrln = GovMap.get(govword).get(td.reln().getShortName());
                if (govrln != null) {
                    govrln.add(td);
                } else {
//                    Map<String, ArrayList<TypedDependency>> govRelatMap
//                            = new HashMap<String, ArrayList<TypedDependency>>(0);//支配词索引后以关系词为key的map
                    ArrayList<TypedDependency> arr_govrln = new ArrayList<TypedDependency>(0);
                    arr_govrln.add(td);
                    GovMap.get(govword).put(td.reln().getShortName(), arr_govrln);
//                    GovMap.get(govword).put(td.reln().getShortName(),td);
                }
            } else {
                Map<String, ArrayList<TypedDependency>> govRelatMap
                        = new HashMap<String, ArrayList<TypedDependency>>(0);//支配词索引后以关系词为key的map
                ArrayList<TypedDependency> arr_govrln = new ArrayList<TypedDependency>(0);
                arr_govrln.add(td);
                govRelatMap.put(td.reln().getShortName(), arr_govrln);
                GovMap.put(govword, govRelatMap);
            }

            //depdmap的填充
            String depdword = td.dep().value();
            if (DepdMap.get(depdword) != null) {
                ArrayList<TypedDependency> depdrln = DepdMap.get(depdword).get(td.reln().getShortName());
                if (depdrln != null) {
                    depdrln.add(td);
                } else {
//                    Map<String, ArrayList<TypedDependency>> govRelatMap
//                            = new HashMap<String, ArrayList<TypedDependency>>(0);//支配词索引后以关系词为key的map
                    ArrayList<TypedDependency> arr_depdrln = new ArrayList<TypedDependency>(0);
                    arr_depdrln.add(td);
                    DepdMap.get(depdword).put(td.reln().getShortName(), arr_depdrln);
//                    GovMap.get(govword).put(td.reln().getShortName(),td);
                }
            } else {
                Map<String, ArrayList<TypedDependency>> depdRelatMap
                        = new HashMap<String, ArrayList<TypedDependency>>(0);//支配词索引后以关系词为key的map
                ArrayList<TypedDependency> arr_depdrln = new ArrayList<TypedDependency>(0);
                arr_depdrln.add(td);
                depdRelatMap.put(td.reln().getShortName(), arr_depdrln);
                DepdMap.put(depdword, depdRelatMap);
            }
           */
        }

//        this.DependencyMap = rlMap;
        return rlMap;
    }


    /**
     * 根据stanford句法分析给出的字符串结果建立一个树
     *
     * @param text
     * @return
     */
    public static ParserNode buildParseTree(String text) {
        Stack<ParserNode> taskStack = new Stack<ParserNode>();
        ParserNode ROOT = null;
        int i = 0;
        char[] temp = new char[0];
        int count = 0;
        while (i < text.length()) {
            char ch = text.charAt(i);
            switch (ch) {
                case '(': {
                    if (text.charAt(i + 1) >= 'A' && text.charAt(i + 1) <= 'Z') {
                        temp = new char[10];
                        count = 0;
                        char[] newch = new char[10];
                        int j = 0;
                        char chtemp = text.charAt(++i);
                        while (chtemp != ' ') {//提取出的语素描述词
                            newch[j++] = chtemp;
                            chtemp = text.charAt(++i);
                        }
                        String dscr = String.valueOf(newch, 0, j);
                        if (taskStack.size() > 0) {
                            ParserNode newnode = new ParserNode(dscr, taskStack.peek());//待填充的node
                            taskStack.peek().addChild(newnode);
                            taskStack.push(newnode);//将最新的node压入栈中                  }
                        } else {
                            taskStack.push(new ParserNode());
                            ROOT = taskStack.peek();
                        }
                    } else {
                        //否则就认为这个‘(’是一个word
//                        taskStack.peek().setWord(String.valueOf(text.charAt(++i)));
                        temp[count++] = '(';
                        taskStack.peek().setLeaf(true);
                    }
                    i++;
                }
                break;
                case ')': {
                    ParserNode peek = taskStack.peek();
                    if (!peek.isLeaf() && peek.getChilds().size() == 0) {
                        //则说明这个"）"是一个word
//                        peek.setWord(String.valueOf(')'));
                        temp[count++] = ')';
                        peek.setLeaf(true);
                    } else {//正常结束
                        ParserNode pop = taskStack.pop();
                        if (pop.isLeaf()) {
                            pop.setWord(String.valueOf(temp, 0, count));
                        }
//                        pop.setLeaf(true);
                    }
                    i++;
                }
                break;
                case ' ':
                    i++;
                    break;
                default: {//默认情况下就是获取一个节点的word
                    temp[count] = ch;
                    count++;
                    i++;
                    taskStack.peek().setLeaf(true);
                }
            }
        }
        return ROOT;
    }

    @Override
    public boolean equals(Object obj) {
        if(obj instanceof ParserManager){
            return ((ParserManager) obj).text.equals(this.text);
        }else{
            return false;
        }
    }

    class RelationNode {
        String govWord;
        String depdWord;
        String relation;
    }
}
