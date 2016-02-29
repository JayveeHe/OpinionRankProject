import codecs

__author__ = 'Jayvee'
import jieba, os
import jieba.posseg as pseg
from gensim import corpora, models, similarities

train_set = []
stoplist = []
for line in open('../data/WordFilter.dic', 'r'):
    stoplist.append(line.strip())
walk = os.walk('D:\CS\Dataset\sogouC')
dcount = 0
fcount = 0
for root, dirs, files in walk:
    print 'dir count = %s' % dcount
    print root
    for name in files:
        print 'file count = %s' % fcount
        print name
        f = codecs.open(os.path.join(root, name), 'r', encoding='gbk')
        raw = f.read()
        word_list = []
        words = pseg.cut(raw)
        for item in words:
            if item.word not in stoplist and item.flag in [u'v', u'vn', u'n', u'ns']:
                word_list.append(item.word)
        # word_list = list(jieba.cut(raw, cut_all=False))
        train_set.append(word_list)
        fcount += 1
    dcount += 1

# fin = open('../data/trainset', 'r').read()
# # word_list = list(jieba.cut(fin, cut_all=False))
# word_list = []
# words = pseg.cut(fin)
# for item in words:
#     # print item
#     # print item.flag
#     # print item.word
#     if item.word not in stoplist and item.flag in [u'v', u'vn', u'n', u'ns']:
#         word_list.append(item.word)
# train_set.append(word_list)

dic = corpora.Dictionary(train_set)
dic.save_as_text('lda_dic')
corpus = [dic.doc2bow(text) for text in train_set]
tfidf = models.TfidfModel(corpus)
corpus_tfidf = tfidf[corpus]
lda = models.LdaModel(corpus_tfidf, id2word=dic, num_topics=10,iterations=100)
lda.save('sogou_reduced_lda.models')
# lda = models.LdaModel.load('sogou_reduced_lda.models')

# lda = models.LdaModel(corpus_tfidf, id2word=dic, num_topics=10)
# corpus_lda = lda[corpus_tfidf]
ti = 0
for t in lda.print_topics(num_words=20):
    print ti, t
    ti += 1
