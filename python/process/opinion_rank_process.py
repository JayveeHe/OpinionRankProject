# coding=utf-8
import codecs
import pickle
import re

import arrow

from utils.node_vec_utils.global_utils import SentenceNodeManager
from utils.node_vec_utils.vec_building_utils import SentenceNode
from utils.textrank_utils.text_rank_utils import analyse_csv

__author__ = 'jayvee'


def feature_lda(save_label):
    # init
    def preprocess(fin_path):
        fin = open(fin_path, 'r')
        manager_groups = {}
        for line in fin:
            splits = line.split(',')
            aa = re.findall('\d+', splits[0])[0]
            pid = int(aa)
            try:
                ll = splits[3].replace('\n', '')
                if pid in manager_groups:
                    manager_groups[pid].add_node(SentenceNode(splits[4], extra=int(ll)))
                else:
                    snm = SentenceNodeManager()
                    snm.add_node(SentenceNode(splits[4], extra=int(ll)))
                    manager_groups[pid] = snm
            except Exception, e:
                print e
                print line
        veclist = []
        sentlist = []
        labellist = []
        tokenlist = []
        nodelist = []
        for pid in manager_groups.keys():
            manager = manager_groups[pid]
            # DBSCANcluster(manager, '%s_DBSCANcluster.json' % pid)
            # APcluster(manager, '%s_APcluster.json' % pid)
            manager.normalize_all_sentnodes()
            veclist.extend(manager.get_vec_list())
            sentlist.extend(manager.get_sent_list())
            for node in manager.node_list:
                labellist.append(node.extra)
                tokenlist.append(node.feature2token())
                nodelist.append(node)
        return veclist, sentlist, labellist, tokenlist, nodelist

    def get_lda_vec(model_lda, tokens):
        """
        根据已有的tokenlist获取lda vec
        :param model_lda:
        :param tokens:
        :return:
        """
        lda_vecs = []
        for t in model_lda[tokens]:
            t_vec = [0.0 for i in range(model_lda.num_topics)]
            for tt in t:
                t_vec[tt[0]] = tt[1]
            lda_vecs.append(t_vec)
        return lda_vecs

    def train_nb(train_vec, train_label):
        from sklearn.naive_bayes import MultinomialNB as MNB
        nbclf = MNB()
        nbclf.fit(train_vec, train_label)
        return nbclf

    def train_rf(train_vec, train_label):
        from sklearn.ensemble.forest import RandomForestClassifier as RFC
        # rfrclf = RFR(n_estimators=1001)
        # rfrclf.fit(train_vec, train_label)
        # print rfrclf.feature_importances_
        rfclf = RFC(n_estimators=1001)
        rfclf.fit(train_vec, train_label)
        print rfclf.feature_importances_
        return rfclf

    def classify_sent(sent_node_list, clf, ldamod, labellist=None):
        tlist = []
        for node in sent_node_list:
            tlist.append(node.feature2token())
        vecs = get_lda_vec(ldamod, tlist)
        res = []
        for i in xrange(len(vecs)):
            vec = vecs[i]
            if labellist:
                res.append('%s,%s,%s' % (labellist[i], sent_node_list[i].sent, clf.predict_proba(vec)[0][1]))
            else:
                clf_result = clf.predict_proba(vec)[0]
                res.append('%s,%s,%s' % (0 if clf_result[0] > 0.5 else 1, sent_node_list[i].sent, clf_result[1]))
        return res

    # start cluster
    # snm.normalize_all_sentnodes()
    # veclist = snm.get_vec_list()

    # _, train_sent_list, train_label_list, train_token_list, train_node_list = preprocess(
    #     '/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/crawler/data/csv/train_set.csv')

    test_path = '/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/crawler/data/csv/1461611102-飘柔护发素高纯度焗油.csv'
    _, test_sent_list, _, test_token_list, test_node_list = preprocess(
        test_path)
    pagerank_c = {'alpha': 0.9}
    key_sents = analyse_csv(test_path, num=len(test_sent_list) - 1, **pagerank_c)


    # gensim textrank
    # gensim_textrank_cn(test_sent_list)

    # lda
    # train lda model
    # print 'start lda training'
    # tfidf = models.TfidfModel(train_token_list)
    # corpus_tfidf = tfidf[train_token_list]
    # lda_model = models.LdaModel(corpus_tfidf, num_topics=100, iterations=30,
    #                             passes=10)
    # # print lda_model.print_topics(100)
    # mfile = open('lda_model_100t.mod', 'w')
    # pickle.dump(lda_model, mfile)
    #
    # # train nb
    # nbclf = train_nb(get_lda_vec(lda_model, train_token_list), train_label_list)
    # mfile = open('nb_model.mod', 'w')
    # pickle.dump(nbclf, mfile)
    #
    # rfclf = train_rf(get_lda_vec(lda_model, train_token_list), train_label_list)
    # mfile = open('rf_model.mod', 'w')
    # pickle.dump(rfclf, mfile)

    mfile = open('lda_model_100t.mod', 'r')
    lda_model = pickle.load(mfile)
    # mfile = open('nb_model.mod', 'r')
    # nbclf = pickle.load(mfile)
    mfile = open('rf_model.mod', 'r')
    rfclf = pickle.load(mfile)
    # print rfclf.feature_importances_

    test_res = classify_sent(test_node_list, rfclf, lda_model)
    test_res = sorted(test_res, cmp=lambda x, y: -cmp(float(x.split(',')[-1]), float(y.split(',')[-1])))
    # res = classify_sent(train_node_list, rfclf, lda_model, labellist=train_label_list)
    # save clf result
    ttt = arrow.utcnow().timestamp
    with open('./result/%s-%s-rf_lda_feature_as_words_lda.csv' % (ttt, save_label), 'w') as fout, open(
                    './result/%s-%s-textrank.csv' % (ttt, save_label), 'w') as tfout:
        fout.write(codecs.BOM_UTF8)
        tfout.write(codecs.BOM_UTF8)
        # fout.write('%s,%s\n' % (u'句子', u'可信度'))
        for i in test_res:
            fout.write(i + '\n')
        for j in key_sents:
            tfout.write('%s,%s\n' % (j.weight, j.sentence))



            # for i in get_lda_vec(lda_model, train_token_list):
            #     print i
            # result = lda_model[test_token_list]
            # for re in result:
            #     print re
            # print lda_model.print_topics()


            # # cluster
            # import sklearn.svm.libsvm as svm
            # import sklearn.cluster as sc
            # #
            # # svm_classifier = svm.fit(veclist, labellist)
            # # print svm.predict_proba(veclist)
            #
            # ap = sc.AffinityPropagation()
            # veclist = get_lda_vec(lda_model, test_token_list)
            # # res = ap.fit(veclist)
            # c_res = ap.fit_predict(veclist)
            # clusters = {}
            # for i in range(len(c_res)):
            #     if clusters.get(c_res[i]):
            #         clusters[c_res[i]].append(test_sent_list[i])
            #     else:
            #         clusters[c_res[i]] = [test_sent_list[i]]
            # open('rf_lda_feature_APcluster111.json', 'w').write(json.dumps(clusters, ensure_ascii=False))


if __name__ == '__main__':
    feature_lda('飘柔护发素高纯度焗油精华400ML')
