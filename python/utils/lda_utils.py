# coding=utf-8
import json
import os
from gensim import corpora, models
import jieba
import jieba.posseg as pseg
from utils.gensim_utils import basic_utils

__author__ = 'jayvee'


def get_topics(text, topic_num=10):
    word_list = []
    words = pseg.cut(text)
    for item in words:
        if item.flag in [u'n', u'ns']:
            word_list.append(item.word)
    train_set = [word_list]
    dic = corpora.Dictionary(train_set)
    # dic.save_as_text('lda_dic')
    corpus = [dic.doc2bow(text) for text in train_set]
    tfidf = models.TfidfModel(corpus)
    corpus_tfidf = tfidf[corpus]
    lda = models.LdaModel(corpus, id2word=dic, num_topics=topic_num, iterations=100)
    # lda.save('sogou_reduced_lda.models')
    return lda.print_topics(topic_num, num_words=30)


def get_topic_by_model(text):
    lda = models.LdaModel.load(
        '/Users/jayvee/github_project/jobs/app.wechat.tagger/data/lda_models/20topics_reduced.model')
    word_list = []
    words = pseg.cut(text)
    for item in words:
        if item.flag in [u'n', u'ns']:
            word_list.append(item.word)
    train_set = [word_list]
    dic = corpora.Dictionary(train_set)
    corpus = [dic.doc2bow(text) for text in train_set]
    # doc_lda = lda.get_document_topics(corpus)
    count = 0
    for j in lda.print_topics(20):
        # print count, j
        count += 1
    # print doc_lda
    for i in lda[corpus]:
        topic_list = []
        for k in i:
            print lda.print_topic(k[0], 7), k[1]


def get_topic_vec_by_model(text,
                           model_path='/Users/jayvee/github_project/jobs/app.wechat.tagger'
                                      '/data/lda_models/20topics_reduced.model'):
    lda = models.LdaModel.load(
        model_path)
    word_list = []
    words = pseg.cut(text)
    for item in words:
        if item.flag in [u'n', u'ns']:
            word_list.append(item.word)
    train_set = [word_list]
    dic = corpora.Dictionary(train_set)
    corpus = [dic.doc2bow(text) for text in train_set]
    # doc_lda = lda.get_document_topics(corpus)
    # count = 0
    # for j in lda.print_topics(20):
    #     # print count, j
    #     count += 1
    # print doc_lda
    topic_vec = []
    for i in lda[corpus]:
        for k in i:
            topic_vec.append(k[1])
            # print lda.print_topic(k[0], 7), k[1]
    return topic_vec


def train_model_by_wordlists(wordlists, num_topics=5, iterations=100, passes=10, is_tfidf=False):
    c_result = basic_utils.get_corpus_by_lists(wordlists)
    dic = c_result[0]
    corpus = c_result[1]
    if is_tfidf:
        tfidf = models.TfidfModel(corpus)
        corpus_tfidf = tfidf[corpus]
        lda_model = models.LdaModel(corpus_tfidf, id2word=dic, num_topics=num_topics, iterations=iterations,
                                    passes=passes)
    else:
        lda_model = models.LdaModel(corpus, id2word=dic, num_topics=num_topics, iterations=iterations, passes=passes)

    return lda_model


def train_model_by_rootpath(root_path, num_topics=5, iterations=100, passes=20, is_tfidf=False):
    flsit = os.listdir(root_path)
    lwordlist = []
    for f in flsit:
        print f
        ftext = open(os.path.join(root_path, f), 'r').read()
        jsonobj = json.loads(ftext)
        pc = jsonobj['post_content']
        wordlist = []
        words = jieba.posseg.cut(pc)
        for item in words:
            if len(item.word) > 1 \
                    and item.flag in [u'v', u'vn', u'n', u'ns'] \
                    and item.word not in [u'关注', u'二维码',
                                          u'公众', u'评论',
                                          u'回复', u'点击', u'信号', u'微信']:
                wordlist.append(item.word)
        lwordlist.append(wordlist)
    lda_model = train_model_by_wordlists(lwordlist, num_topics, iterations, passes, is_tfidf=is_tfidf)
    return lda_model


def loda_ldamodel_by_file(model_path):
    lda_model = models.LdaModel.load(model_path)
    return lda_model


if __name__ == '__main__':
    # tt = open('../data/sample.txt', 'r')
    # get_topic_by_model(tt.read())
    get_topic_vec_by_model(u"我想去大学食堂吃点东西")
    print '========='
    get_topic_vec_by_model(
        u'明天本科宿舍聚餐')
    pass
