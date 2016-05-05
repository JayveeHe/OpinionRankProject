# coding=utf-8
import codecs
import pickle
from random import shuffle
import arrow
import math
from utils.CommonUtils import PROJECT_PATH
from utils.dao_utils.mongo_utils import get_db_inst
from utils.nltk_utils.nltk_tools import cal_tfidf, tag_sents
from utils.node_vec_utils.global_utils import SentenceNodeManager
from utils.node_vec_utils.vec_building_utils import SentenceNode

__author__ = 'jayvee'


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
    trfclf = RFC(n_estimators=1001)
    trfclf.fit(train_vec, train_label)
    # print rfclf.feature_importances_
    return trfclf


def classify_sent(sent_node_list, clf, ldamod, labellist=None):
    tlist = []
    for node in sent_node_list:
        tlist.append(node.feature2token())
    vecs = get_lda_vec(ldamod, tlist)
    res = []
    for i in xrange(len(vecs)):
        vec = vecs[i]
        if labellist:
            clf_result = clf.predict_proba(vec)[0]
            res.append((
                labellist[i], sent_node_list[i].sent, clf_result[1], sent_node_list[i].extra[1],
                sent_node_list[i].extra[2]))
        else:
            clf_result = clf.predict_proba(vec)[0]
            res.append((
                0 if clf_result[0] > 0.5 else 1, sent_node_list[i].sent, clf_result[1], sent_node_list[i].extra[1],
                sent_node_list[i].extra[2]))
    return res


def amazon_test(start=0, end=10, label_rate=0.65):
    # prepare train set
    db_inst = get_db_inst('AmazonReviews', 'AndroidAPP')
    # print len(db_inst.distinct('asin'))
    manager_groups = {}
    limit = 10
    asin_file = open('%s/process/data/asin.list' % PROJECT_PATH, 'r')
    # for asin in db_inst.distinct('asin'):
    #     asin_file.write('%s\n' % asin)
    lines = []
    lines = asin_file.readlines()
    shuffle(lines)
    # for asin in db_inst.distinct('asin'):
    tlines = lines[start:end]
    review_dicts = {}
    for asin in tlines:
        asin = asin.replace('\n', '')
        print 'loading %s' % asin
        # limit -= 1
        # print limit
        # if limit > 0:
        # if asin in manager_groups:
        #     manager_groups[asin].add_node(SentenceNode(splits[4], extra=int(ll)))
        # else:
        snm = SentenceNodeManager()
        # snm.add_node(SentenceNode(splits[4], extra=int(ll)))

        # 计算每个APP下的评论
        a_reviews = []
        max_vote = 0  # 常量
        for find_item in db_inst.find({"asin": asin, 'total_vote': {"$gt": 0}}):
            max_vote = max(find_item['total_vote'], max_vote)
            a_reviews.append(find_item)
        # process item reviews VOTE RANK
        review_rank = []
        print '%s has %s reviews' % (asin, len(a_reviews))
        for review in a_reviews:
            alpha_const = 0
            T = float(review['total_vote']) / max_vote
            V = 1 / (1.0 + math.exp(-0.01 * (2 * review['up_vote'] - review['total_vote'])))
            # V = float(review['up_vote']) / review['total_vote']
            vote_rank_value = 2 * (T + alpha_const) * (V + alpha_const) / (T + V + 2 * alpha_const)
            if vote_rank_value >= label_rate:
                snm.add_node(
                    SentenceNode(review['reviewText'].lower(), extra=(int(1), vote_rank_value, review['reviewerID']),
                                 get_pos_func=tag_sents,
                                 get_keywords_func=cal_tfidf))
            elif vote_rank_value < label_rate:
                snm.add_node(
                    SentenceNode(review['reviewText'].lower(), extra=(int(0), vote_rank_value, review['reviewerID']),
                                 get_pos_func=tag_sents,
                                 get_keywords_func=cal_tfidf))
            review_rank.append((review, vote_rank_value))
        manager_groups[asin] = snm
        review_dicts[asin] = review_rank
        # else:
        #     break
    veclist = []
    sentlist = []
    labellist = []
    tokenlist = []
    nodelist = []
    print 'start normalizing vecs'
    for pid in manager_groups.keys():
        manager = manager_groups[pid]
        # DBSCANcluster(manager, '%s_DBSCANcluster.json' % pid)
        # APcluster(manager, '%s_APcluster.json' % pid)
        manager.normalize_all_sentnodes(tfidf_func=tag_sents)
        veclist.extend(manager.get_vec_list())
        sentlist.extend(manager.get_sent_list())
        for node in manager.node_list:
            labellist.append(node.extra[0])
            tokenlist.append(node.feature2token())
            nodelist.append(node)
    print 'end normalizing vecs'
    return veclist, sentlist, labellist, tokenlist, nodelist


def cal_error(clf_res):
    rank_dict = {}
    ranklist = []
    for _, _, clf_value, rank_value, review_id in clf_res:
        # splits = rv_str.split(',')
        # clf_value = eval(splits[2])
        # rank_value = eval(splits[3])
        # review_id = splits[4]
        ranklist.append((review_id, clf_value, rank_value))
    # sort
    clf_rank = sorted(ranklist, cmp=lambda x, y: -cmp(x[1], y[1]))
    for i in xrange(len(clf_rank)):
        item = clf_rank[i]
        rank_dict[item[0]] = {'clf_rank': i}
    value_rank = sorted(ranklist, cmp=lambda x, y: -cmp(x[2], y[2]))
    errors = 0
    for j in xrange(len(value_rank)):
        item = value_rank[j]
        rank_dict[item[0]]['value_rank'] = j
        rank_item = rank_dict[item[0]]
        errors += float(math.fabs(rank_item['clf_rank'] - rank_item['value_rank'])) / len(clf_res)
    return errors, rank_dict


    # rank_dict[review_id]=


def cal_trainset_count_errors(train_start, train_end, test_start, test_end, lda_model, rf_model):
    _, train_sent_list, train_label_list, train_token_list, train_node_list = amazon_test(train_start, train_end)


def cal_testset_rank_errors(test_start, test_end, lda_model, rf_model):
    pass


def amazon_main(test_start, test_end, lda_model, rfclf):
    # print rfclf.feature_importances_
    _, test_sent_list, _, test_token_list, test_node_list = amazon_test(test_start, test_end)
    test_res = classify_sent(test_node_list, rfclf, lda_model)
    ranked_res = sorted(test_res, cmp=lambda x, y: -cmp(x[3], y[3]))
    print 'done'
    errorsd, rankd = cal_error(test_res)
    print errorsd
    ttt = arrow.utcnow().timestamp
    save_label = 'amazon'
    with open('%s/process/result/%s-%s-rf_lda_feature_as_words_lda.csv' % (PROJECT_PATH, ttt, save_label), 'w') as fout:
        fout.write(codecs.BOM_UTF8)
        # tfout.write(codecs.BOM_UTF8)
        # fout.write('%s,%s\n' % (u'句子', u'可信度'))
        for i in ranked_res:
            fout.write('%s,%s,%s,%s,%s\n' % (i[0], i[1], i[2], i[3], i[4]))
    return errorsd


def train_models(train_start, train_end):
    from gensim import models
    _, train_sent_list, train_label_list, train_token_list, train_node_list = amazon_test(train_start, train_end)
    print 'start lda training'
    tfidf = models.TfidfModel(train_token_list)
    corpus_tfidf = tfidf[train_token_list]
    lda_model = models.LdaModel(corpus_tfidf, num_topics=100, iterations=30,
                                passes=10)
    # print lda_model.print_topics(100)
    mfile = open('%s/process/models/lda_model_100t.mod' % PROJECT_PATH, 'w')
    pickle.dump(lda_model, mfile)
    rfclf = train_rf(get_lda_vec(lda_model, train_token_list), train_label_list)
    mfile = open('%s/process/models/rf_model_100t.mod' % PROJECT_PATH, 'w')
    pickle.dump(rfclf, mfile)
    print 'train done'


if __name__ == '__main__':
    # _, train_sent_list, train_label_list, train_token_list, train_node_list = amazon_test(0, 20)
    #
    # print 'start lda training'
    # tfidf = models.TfidfModel(train_token_list)
    # corpus_tfidf = tfidf[train_token_list]
    # lda_model = models.LdaModel(corpus_tfidf, num_topics=100, iterations=30,
    #                             passes=10)
    # # print lda_model.print_topics(100)
    # mfile = open('lda_model_100t.mod', 'w')
    # pickle.dump(lda_model, mfile)
    # #
    # # # train nb
    # # nbclf = train_nb(get_lda_vec(lda_model, train_token_list), train_label_list)
    # # mfile = open('nb_model.mod', 'w')
    # # pickle.dump(nbclf, mfile)
    # #
    # rfclf = train_rf(get_lda_vec(lda_model, train_token_list), train_label_list)
    # mfile = open('rf_model.mod', 'w')
    # pickle.dump(rfclf, mfile)
    # print 'train done'
    mfile = open('%s/process/models/lda_model_100t.mod' % PROJECT_PATH, 'r')
    ldamodel = pickle.load(mfile)
    # mfile = open('nb_model.mod', 'r')
    # nbclf = pickle.load(mfile)
    mfile = open('%s/process/models/rf_model_100t.mod' % PROJECT_PATH, 'r')
    rfclf = pickle.load(mfile)
    amazon_main(0, 20, ldamodel, rfclf)
