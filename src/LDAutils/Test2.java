package LDAutils;

import ansj.lda.LDA;
import ansj.lda.impl.LDAGibbsModel;
import ansj.util.Analysis;
import ansj.util.impl.DicAnalysis;
import com.google.common.base.Charsets;
import com.google.common.io.Files;

import java.io.BufferedReader;
import java.io.File;

public class Test2 {
	public static void main(String[] args) throws Exception {
	
		Analysis dicAnalysis = DicAnalysis.getInstance(new File("library/result_1_3.dic"), "UTF-8");
	
		LDA lda = new LDA(dicAnalysis, new LDAGibbsModel(10, 5, 0.1, 100, Integer.MAX_VALUE, Integer.MAX_VALUE));
		BufferedReader newReader = Files.newReader(new File("/Users/ansj/Documents/temp/computer_300000.txt"), Charsets.UTF_8);
		
		String temp = null;
		int id = 0 ;
		while ((temp = newReader.readLine()) != null) {
			lda.addDoc(String.valueOf(++id),temp);
		}

		lda.trainAndSave("result/computer",50, "utf-8");
	}
}
