package Utils;

import LexicalUtils.FudanNLP.FudanUtils;
import org.ansj.domain.Term;
import org.ansj.splitWord.analysis.NlpAnalysis;

import java.util.ArrayList;
import java.util.List;

/**
 * Created by Jayvee on 2015/3/8.
 */
public class SegUtils {
    public static FudanUtils fudanUtils;

    /**
     * 结合ansj_seg的分词和FNLP的词性标注，输出适用于FNLP句法分析的输入数据
     *
     * @param text
     * @return
     */
    public static String[][] seg(String text) {
        List<Term> terms = NlpAnalysis.parse(text);
        String[] words = new String[terms.size()];
        String[] nature = new String[terms.size()];
        List<Integer> quetoIndex = new ArrayList<Integer>(0);
        for (int i = 0; i < terms.size(); i++) {
            words[i] = terms.get(i).getName();
            nature[i] = terms.get(i).getNatureStr();
            //使得Ansj_seg的标点符号与FNLP相适应
            if (terms.get(i).getNatureStr().equals("w")) {
                quetoIndex.add(i);
            }
        }
        String[] pos = FudanUtils.tagText(words);
        for (Integer k : quetoIndex) {
            pos[k] = "标点";
        }
        String[][] result = new String[3][];
        result[0] = words;
        result[1] = pos;
        result[2] = nature;
        return result;
    }

}
