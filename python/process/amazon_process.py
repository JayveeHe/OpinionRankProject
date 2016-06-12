# coding=utf-8
import os
import pickle
from random import shuffle
import math
from gensim import models
import numpy as np
import sys

cur_dir_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(cur_dir_path)
sys.path.append(project_path)

from utils.CommonUtils import PROJECT_PATH, timer
from utils.dao_utils.mongo_utils import get_db_inst
from utils.nltk_utils.nltk_tools import cal_en_tfidf, tag_sents
from utils.node_vec_utils.global_utils import SentenceNodeManager
from utils.node_vec_utils.vec_building_utils import SentenceNode
from utils.textrank_utils.text_rank_utils import text_en_nodelist

__author__ = 'jayvee'


def get_combined_vec(model_lda, tokens, level1_vecs):
    """
    返回lda和level1的组合vector
    :param model_lda:
    :param tokens:
    :param level1_vecs:
    :return:
    """
    lda_vec = get_lda_vec(model_lda, tokens)
    combined_vec = []
    for vi in xrange(len(level1_vecs)):
        vec = level1_vecs[vi]
        lvec = lda_vec[vi]
        combined_vec.append(vec + lvec)
    return combined_vec


def get_lda_vec(model_lda, tokens):
    """
    根据已有的tokenlist获取lda vec
    :param model_lda:
    :param tokens:
    :return:
    """
    lda_vecs = []
    tops = model_lda.get_document_topics(tokens, minimum_probability=0)
    # for t in model_lda[tokens]:
    for t in tops:
        t_vec = [0.0 for i in range(model_lda.num_topics)]
        for tt in t:
            t_vec[tt[0]] = tt[1]
            t_id = tt[0]
            t_prob = tt[1]
            # t_info = model_lda.get_topic_terms(t_id, 1000)
        lda_vecs.append(t_vec)
    return lda_vecs


def train_nb(train_vec, train_label):
    from sklearn.naive_bayes import MultinomialNB as MNB
    nbclf = MNB()
    nbclf.fit(train_vec, train_label)
    return nbclf


def train_rf(train_vec, train_label):
    from sklearn.ensemble.forest import RandomForestClassifier as RFC
    from sklearn.cross_validation import cross_val_score
    # rfrclf = RFR(n_estimators=1001)
    # rfrclf.fit(train_vec, train_label)
    # print rfrclf.feature_importances_
    trfclf = RFC(n_estimators=1001)
    train_vec = np.array(train_vec)
    trfclf.fit(train_vec, train_label)
    cv_value = cross_val_score(trfclf, train_vec, train_label, cv=10, scoring='accuracy').mean()
    # print cv_value
    # print rfclf.feature_importances_
    return trfclf, cv_value


def train_lexical_classifier():
    amazon_preprocess(start=0, end=10)


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


def classify_sent_lexical(sent_node_list, lexical_clf, clf, ldamod, labellist=None):
    """
    根据训练好的clf与ldamod，对输入的nodelist进行重要度分类
    :param sent_node_list:
    :param clf:
    :param labellist:
    :return:
    """
    lexical_vecs = []
    for node in sent_node_list:
        vec_dict = node.get_vec()
        lexical_vecs.append(
            [vec_dict['g_verb_rate'], vec_dict['g_noun_rate'],
             vec_dict['g_adj_rate'], vec_dict['g_sent_len'], vec_dict['g_adv_rate']] + vec_dict['g_tfidf_rate'])
        # lexical_vecs.append([i for i in node.get_vec().values()])
    # lexical_vecs = get_lda_vec(ldamod, tlist)
    tokenlist = []
    for node in sent_node_list:
        tokenlist.append(node.feature2token())
    # lda_vecs = get_lda_vec(ldamod, tokenlist)
    combined_vec = get_combined_vec(ldamod, tokenlist, lexical_vecs)
    res = []
    for i in xrange(len(lexical_vecs)):
        # vec = lda_vecs[i]
        vec = combined_vec[i]
        vec = np.array(vec).reshape((1, -1))
        lexical_vec = lexical_vecs[i]
        lexical_vec = np.array(lexical_vec).reshape((1, -1))
        clf_result = clf.predict_proba(vec)[0]
        lexical_clf_result = lexical_clf.predict_proba(lexical_vec)[0]
        if labellist:
            res.append((
                labellist[i], sent_node_list[i].sent, clf_result[1], sent_node_list[i].extra[1],
                sent_node_list[i].extra[2], lexical_clf_result[1]))
        else:
            # clf_result = clf.predict_proba(vec)[0]
            res.append((
                0 if clf_result[0] > 0.5 else 1, sent_node_list[i].sent, clf_result[1], sent_node_list[i].extra[1],
                sent_node_list[i].extra[2], lexical_clf_result[1]))
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
        if len(a_reviews)<10:
            continue
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


@timer
def amazon_preproc_by_asin(asin, rfclf, lda_model, lexical_rfclf, label_rate=0.65, category_name='AndroidAPP'):
    """
    根据asin直接分析某个商品下的评论
    :param asin:
    :return:
    """
    # review_dicts = {}
    # asin_list = []
    manager_groups = {}
    db_inst = get_db_inst('AmazonReviews', category_name)  # 计算每个APP下的评论
    a_reviews = []
    max_vote = 0  # 常量
    for find_item in db_inst.find({"asin": asin, 'total_vote': {"$gt": 0}}):
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
            # review_rank.append((review, vote_rank_value))
    manager_groups[asin] = snm
    # review_dicts[asin] = review_rank
    # nodelist = []
    # group_nodelist = []
    print 'start normalizing vecs'
    snm.normalize_all_sentnodes(tfidf_func=cal_en_tfidf)
    print 'end normalizing vecs'
    # cal rank errors
    sum_oprank_errors = 0
    sum_textrank_errors = 0
    sum_lexical_errors = 0
    item_rawlist = []
    # manager = manager_groups[asin]
    nodelist = snm.node_list
    try:
        # oprank_res = classify_sent(nodelist, rfclf, lda_model)
        lexical_res = classify_sent_lexical(nodelist, lexical_clf=lexical_rfclf, clf=rfclf, ldamod=lda_model)
        tmp_dict = {}
        for i in lexical_res:
            tmp_dict[i[4]] = {'asin': asin, 'reviewerID': i[4], 'label': i[0], 'sent': i[1],
                              'opinion_rank_value': i[2],
                              'vote_value': i[3], 'lexical_value': i[5]}
            # raw_list.append('%s,%s,%s,%s,%s,%s' % (asin, i[4], i[0], i[1], i[2], i[3]))
        textrank_res = text_en_nodelist(nodelist)
        for i in textrank_res:
            tmp_item = tmp_dict[i.review_id]
            tmp_item['text_rank_value'] = i.weight
            item_rawlist.append(tmp_item)
            # raw_list.append(tmp_item)

        oprank_errors, oprank_d, oprank_ndcg = cal_oprank_error(lexical_res)
        textrank_errors, textrank_d, textrank_ndcg = cal_textrank_error(textrank_res)
        lexical_errors, lexical_d, lexical_ndcg = cal_lexical_error(lexical_res)
        # print info
        sum_oprank_errors += oprank_errors
        sum_lexical_errors += lexical_errors
        sum_textrank_errors += textrank_errors
        info = 'itemID: %s\ttotal reviews: %s\toprank_errors: %s\tlexical_errors: %s\ttextrank_errors: %s\t' \
               'sum_oprank_errors: %s\tsum_lexical_errors: %s\tsum_textrank_errors: %s\t' \
               'oprank_ndcg: %s\ttextrank_ndcg: %s\tlexical_ndcg: %s' % (
                   asin, len(nodelist), oprank_errors, lexical_errors, textrank_errors, sum_oprank_errors,
                   sum_lexical_errors, sum_textrank_errors, oprank_ndcg, textrank_ndcg, lexical_ndcg)
        # info_list.append(info)
        print info
        return info, item_rawlist
        # yield sum_oprank_errors, sum_textrank_errors, info, raw_list
    except Exception, e:
        print '%s raise exceptions, details = %s' % (asin, str(e))
        return None, None


def cal_oprank_error(clf_res):
    """
    计算opinion rank分类算法的rank结果与基于投票的ground truth的rank结果做比较
    :param clf_res:
    :return:
    """
    rank_dict = {}
    ranklist = []
    for _, _, clf_value, rank_value, review_id, lexical_value in clf_res:
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
    nDCG = calc_ndcg_values(ranklist)
    return errors, rank_dict, nDCG


def cal_lexical_error(lexical_clf_res):
    """
    计算opinion rank分类算法的rank结果与基于投票的ground truth的rank结果做比较
    :param lexical_clf_res:
    :return:
    """
    rank_dict = {}
    ranklist = []
    for _, _, clf_value, rank_value, review_id, lexical_value in lexical_clf_res:
        # splits = rv_str.split(',')
        # clf_value = eval(splits[2])
        # rank_value = eval(splits[3])
        # review_id = splits[4]
        ranklist.append((review_id, lexical_value, rank_value))
    # sort
    clf_rank = sorted(ranklist, cmp=lambda x, y: -cmp(x[1], y[1]))
    for i in xrange(len(clf_rank)):
        item = clf_rank[i]
        rank_dict[item[0]] = {'lexical_clf_rank': i}
    value_rank = sorted(ranklist, cmp=lambda x, y: -cmp(x[2], y[2]))
    errors = 0
    for j in xrange(len(value_rank)):
        item = value_rank[j]
        rank_dict[item[0]]['value_rank'] = j
        rank_item = rank_dict[item[0]]
        errors += float(math.fabs(rank_item['lexical_clf_rank'] - rank_item['value_rank'])) / len(lexical_clf_res)
    nDCG = calc_ndcg_values(ranklist)
    return errors, rank_dict, nDCG


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
    nDCG = calc_ndcg_values(ranklist)
    return errors, rank_dict, nDCG

    # rank_dict[review_id]=


def calc_ndcg_values(ranked_list):
    """
    计算排序结果的Discounted cumulative gain (DCG)值
    :param ranked_list: [(review_id, algo_value, rank_value)]
    :return: NDCG值
    """
    # def map_vote_value(vote_value):
    #     if 0<=vote_value<0.2:
    # calc IDCG
    vote_rank = sorted(ranked_list, cmp=lambda x, y: -cmp(x[2], y[2]))
    IDCG = 0.0
    new_rank_with_index = []
    mapping_weight = [5, 4, 3.8, 3.5, 3, 2.5, 2, 1.8, 1.5, 1.3,
                      1.2, 1, 0.9, 0.7, 0.5, 0.3, 0.2, 0.1, 0.1, 0]
    for i in xrange(len(vote_rank)):
        item = vote_rank[i]
        rank_index = i
        mapping_rank = int(math.floor((float(rank_index) / len(vote_rank)) / 0.05))
        # IDCG += (2 ** item[2] - 1) / math.log(2 + i, 2)
        IDCG += (2 ** (mapping_weight[mapping_rank]/2.0) - 1) / math.log(2 + i, 2)
        new_rank_with_index.append((item[0], item[1], item[2], i))

    clf_rank = sorted(new_rank_with_index, cmp=lambda x, y: -cmp(x[1], y[1]))
    # calc DCG
    DCG = 0.0
    for i in xrange(len(clf_rank)):
        item = clf_rank[i]
        rank_index = item[3]
        mapping_rank = int(math.floor((float(rank_index) / len(clf_rank)) / 0.05))
        # DCG += (2 ** item[2] - 1) / math.log(2 + i, 2)
        DCG += (2 ** (mapping_weight[mapping_rank]/2.0) - 1) / math.log(2 + i, 2)

    return DCG / IDCG


def cal_trainset_count_errors(train_start, train_end, test_start, test_end, lda_model, rf_model):
    _, train_sent_list, train_label_list, train_token_list, train_node_list, _ = amazon_preprocess(train_start,
                                                                                                   train_end)


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
    train_veclist, train_sent_list, train_label_list, train_token_list, train_node_list, _ = amazon_preprocess(
        train_start,
        train_end)
    # print 'start lda training'
    # tfidf = models.TfidfModel(train_token_list)
    # corpus_tfidf = tfidf[train_token_list]
    # lda_model = models.LdaModel(corpus_tfidf, num_topics=100, iterations=30,
    #                             passes=10)
    # # print lda_model.print_topics(100)
    # mfile = open('%s/process/models/lda_model_100t.mod' % PROJECT_PATH, 'w')
    # pickle.dump(lda_model, mfile)
    # rfclf = train_rf(get_lda_vec(lda_model, train_token_list), train_label_list)
    # mfile = open('%s/process/models/rf_model_100t.mod' % PROJECT_PATH, 'w')
    # pickle.dump(rfclf, mfile)

    print 'start lda training'
    tfidf = models.TfidfModel(train_token_list)
    corpus_tfidf = tfidf[train_token_list]
    lda_model = models.LdaModel(corpus_tfidf, num_topics=20, iterations=50,
                                passes=10)
    mfile = open('%s/process/models/lda_model_100t.mod' % PROJECT_PATH, 'w')
    pickle.dump(lda_model, mfile)
    print 'start training lexical rf'
    lexical_rfclf, lexical_cv = train_rf(train_veclist, train_label_list)
    print 'lexical rf cross-validation=%s' % lexical_cv
    mfile = open('%s/process/models/lexical_rf_model.mod' % PROJECT_PATH, 'w')
    pickle.dump(lexical_rfclf, mfile)
    print 'start training rf'
    combined_vec = get_combined_vec(lda_model, train_token_list, train_veclist)
    rfclf, rfcv = train_rf(combined_vec, train_label_list)
    print 'latent level rf cross-validation=%s' % rfcv
    mfile = open('%s/process/models/rf_model.mod' % PROJECT_PATH, 'w')
    pickle.dump(rfclf, mfile)
    print 'train done'


if __name__ == '__main__':
    # 2016.5.29 测试lexical feature的分类效果
    # train_veclist, train_sent_list, train_label_list, train_token_list, train_node_list, _ = amazon_preprocess(start=0,
    #                                                                                                            end=500)
    # # # train nb
    # # nbclf = train_nb(get_lda_vec(lda_model, train_token_list), train_label_list)
    # # mfile = open('nb_model.mod', 'w')
    # # pickle.dump(nbclf, mfile)
    #
    train_models(0, 2000)

    pass
    # mfile = open('%s/process/models/lda_model_100t.mod' % PROJECT_PATH, 'r')
    # ldamodel = pickle.load(mfile)
    # # mfile = open('nb_model.mod', 'r')
    # # nbclf = pickle.load(mfile)
    # mfile = open('%s/process/models/rf_model_100t.mod' % PROJECT_PATH, 'r')
    # rfclf = pickle.load(mfile)
    # amazon_main(0, 20, ldamodel, rfclf)
