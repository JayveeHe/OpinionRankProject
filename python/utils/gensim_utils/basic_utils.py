# coding:utf8
import codecs
import os
from gensim import corpora, models
import gensim
from jieba import posseg as pseg
import jieba

__author__ = 'jayvee'


def travel_all_files(root_path):
    """
    get gensim corpus by travel all files
    :param root_path:
    :return: a list of segmented word_list, where a word_list contains a doc's all word
    """
    stoplist = []
    for stopline in codecs.open('../data/WordFilter.dic', 'r', encoding='utf8'):
        stoplist.append(stopline.strip())
    train_set = []
    walk = os.walk(root_path)
    for root, dirs, files in walk:
        for name in files:
            word_list = []
            print name
            try:
                f = codecs.open(os.path.join(root, name), 'r', encoding='gbk')
                raw = f.read()
                words = pseg.cut(raw)
                # and item.flag in [u'n', u'ns', u'nr', u'nz', u'ng', u'vn']
                for item in words:
                    if item.word not in stoplist and item.flag in [u'n', u'ns', u'nr', u'nz', u'ng', u'vn'] and len(
                            item.word) > 1:
                        word_list.append(item.word)
                        # else:
                        #     print item.word,'\t',item.flag
                train_set.append(word_list)

                # words = jieba.cut(raw)
                # for word in words:
                #     word_list.append(word)
                # train_set.append(word_list)

            except Exception, e:
                print 'error file name = %s' % name
                continue
    return train_set


def get_corpus_by_lists(word_lists):
    dic = corpora.Dictionary(word_lists)
    # dic.save_as_text('lda_dic')
    corpus = [dic.doc2bow(text) for text in word_lists]
    return dic, corpus


if __name__ == '__main__':
    raw_corpus = get_corpus_by_lists(travel_all_files('/Users/jayvee//Downloads/SogouC.reduced/Reduced'))
    # raw_corpus = get_corpus_by_lists(travel_all_files('/Users/jayvee//Desktop/data'))
    dic = raw_corpus[0]
    corpus = raw_corpus[1]
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    print 'start training'
    lda = models.LdaModel(corpus, id2word=dic, num_topics=20, iterations=200, passes=10)
    print 'start training'
    lda_tfidf = models.LdaModel(corpus_tfidf, id2word=dic, num_topics=20, iterations=200, passes=10,
                                minimum_probability=0.001)
    # # for i in lda.print_topics(5):
    # #     print i
    lda.save('../data/lda_models/20topics_reduced.model')
    lda_tfidf.save('../data/lda_models/20topics_reduced_tfidf.model')
    # lda = models.LdaModel.load('../data/lda_models/10topics.model')

    for i in lda.print_topics(50, 100):
        print i
        # lda.get_document_topics()
    print 'tfidf======================'
    for i in lda_tfidf.print_topics(50, 100):
        print i
