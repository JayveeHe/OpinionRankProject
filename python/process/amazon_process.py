# coding=utf-8
import pickle
from random import shuffle
import math
import numpy as np
from utils.CommonUtils import PROJECT_PATH, timer
from utils.dao_utils.mongo_utils import get_db_inst
from utils.nltk_utils.nltk_tools import cal_en_tfidf, tag_sents
from utils.node_vec_utils.global_utils import SentenceNodeManager
from utils.node_vec_utils.vec_building_utils import SentenceNode
from utils.textrank_utils.text_rank_utils import text_en_nodelist

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
    """
    根据训练好的clf与ldamod，对输入的nodelist进行重要度分类
    :param sent_node_list:
    :param clf:
    :param ldamod:
    :param labellist:
    :return:
    """
    tlist = []
    for node in sent_node_list:
        tlist.append(node.feature2token())
    vecs = get_lda_vec(ldamod, tlist)
    res = []
    for i in xrange(len(vecs)):
        vec = vecs[i]
        vec = np.array(vec).reshape((1, -1))
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


def amazon_preprocess(start=0, end=10, label_rate=0.65, min_vote=0):
    """

    :param start:
    :param end:
    :param label_rate:
    :return:
    """
    # prepare train set
    db_inst = get_db_inst('AmazonReviews', 'AndroidAPP')
    # print len(db_inst.distinct('asin'))
    manager_groups = {}
    asin_file = open('%s/process/data/asin.list' % PROJECT_PATH, 'r')
    # for asin in db_inst.distinct('asin'):
    #     asin_file.write('%s\n' % asin)
    lines = asin_file.readlines()
    shuffle(lines)
    # for asin in db_inst.distinct('asin'):
    tlines = lines[start:end]
    review_dicts = {}
    asin_list = []
    for asin in tlines:
        asin = asin.replace('\n', '')
        asin_list.append(asin)
        print 'loading %s' % asin
        # snm.add_node(SentenceNode(splits[4], extra=int(ll)))

        # 计算每个APP下的评论
        a_reviews = []
        max_vote = 0  # 常量
        for find_item in db_inst.find({"asin": asin, 'total_vote': {"$gt": min_vote}}):
            max_vote = max(find_item['total_vote'], max_vote)
            a_reviews.append(find_item)
        # process item reviews VOTE RANK
        review_rank = []
        print '%s has %s reviews' % (asin, len(a_reviews))
        snm = SentenceNodeManager()
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
                                 get_keywords_func=cal_en_tfidf))
            elif vote_rank_value < label_rate:
                snm.add_node(
                    SentenceNode(review['reviewText'].lower(), extra=(int(0), vote_rank_value, review['reviewerID']),
                                 get_pos_func=tag_sents,
                                 get_keywords_func=cal_en_tfidf))
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
    group_nodelist = []
    print 'start normalizing vecs'
    for pid in manager_groups.keys():
        manager = manager_groups[pid]
        # DBSCANcluster(manager, '%s_DBSCANcluster.json' % pid)
        # APcluster(manager, '%s_APcluster.json' % pid)
        manager.normalize_all_sentnodes(tfidf_func=tag_sents)
        veclist.extend(manager.get_vec_list())
        sentlist.extend(manager.get_sent_list())
        gnodelist = []
        for node in manager.node_list:
            labellist.append(node.extra[0])
            tokenlist.append(node.feature2token())
            nodelist.append(node)
            gnodelist.append(node)
        group_nodelist.append(gnodelist)
    print 'end normalizing vecs'
    return veclist, sentlist, labellist, tokenlist, nodelist, manager_groups


def cal_oprank_error(clf_res):
    """
    计算opinion rank分类算法的rank结果与基于投票的ground truth的rank结果做比较
    :param clf_res:
    :return:
    """
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


def cal_textrank_error(sorted_sents):
    """
    计算textrank的结果与voterank的差别
    :param sorted_sents:
    :return:
    """
    rank_dict = {}
    ranklist = []
    for sorted_sent in sorted_sents:
        ranklist.append((sorted_sent.review_id, sorted_sent.weight, sorted_sent.vote_value))
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
        errors += float(math.fabs(rank_item['clf_rank'] - rank_item['value_rank'])) / len(sorted_sents)
    return errors, rank_dict

    # rank_dict[review_id]=


def cal_trainset_count_errors(train_start, train_end, test_start, test_end, lda_model, rf_model):
    _, train_sent_list, train_label_list, train_token_list, train_node_list = amazon_preprocess(train_start, train_end)


def amazon_main(test_start, test_end, lda_model, rfclf):
    """
    亚马逊评论的处理main函数，用于统一入口调用
    :param test_start:
    :param test_end:
    :param lda_model:
    :param rfclf:
    :return:
    """
    # print rfclf.feature_importances_
    _, test_sent_list, _, test_token_list, test_node_list, manager_group = amazon_preprocess(test_start, test_end)
    sum_oprank_errors = 0
    sum_textrank_errors = 0
    # info_list = []
    # raw_list = []
    # 根据每个group的nodelist计算rank errors
    for asin in manager_group.keys():
        item_rawlist = []
        manager = manager_group[asin]
        nodelist = manager.node_list
        try:
            oprank_res = classify_sent(nodelist, rfclf, lda_model)
            tmp_dict = {}
            for i in oprank_res:
                tmp_dict[i[4]] = {'asin': asin, 'reviewerID': i[4], 'label': i[0], 'sent': i[1],
                                  'opinion_rank_value': i[2],
                                  'vote_value': i[3]}
                # raw_list.append('%s,%s,%s,%s,%s,%s' % (asin, i[4], i[0], i[1], i[2], i[3]))
            textrank_res = text_en_nodelist(nodelist)
            for i in textrank_res:
                tmp_item = tmp_dict[i.review_id]
                tmp_item['text_rank_value'] = i.weight
                item_rawlist.append(tmp_item)
                # raw_list.append(tmp_item)
            oprank_errors, oprank_d = cal_oprank_error(oprank_res)
            textrank_errors, textrank_d = cal_textrank_error(textrank_res)
            # print info
            sum_oprank_errors += oprank_errors
            sum_textrank_errors += textrank_errors
            info = 'itemID: %s\ttotal reviews: %s\toprank_errors: %s\ttextrank_errors: %s\t' \
                   'sum_oprank_errors: %s\tsum_textrank_errors: %s' % (
                       asin, len(nodelist), oprank_errors, textrank_errors, sum_oprank_errors, sum_textrank_errors)
            # info_list.append(info)
            print info
            yield info, item_rawlist
            # yield sum_oprank_errors, sum_textrank_errors, info, raw_list
        except Exception, e:
            print '%s raise exceptions, details = %s' % (asin, str(e))
        # return sum_oprank_errors, sum_textrank_errors, info_list, raw_list


def train_models(train_start, train_end):
    from gensim import models
    _, train_sent_list, train_label_list, train_token_list, train_node_list, _ = amazon_preprocess(train_start,
                                                                                                   train_end)
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
    pass
    # mfile = open('%s/process/models/lda_model_100t.mod' % PROJECT_PATH, 'r')
    # ldamodel = pickle.load(mfile)
    # # mfile = open('nb_model.mod', 'r')
    # # nbclf = pickle.load(mfile)
    # mfile = open('%s/process/models/rf_model_100t.mod' % PROJECT_PATH, 'r')
    # rfclf = pickle.load(mfile)
    # amazon_main(0, 20, ldamodel, rfclf)
