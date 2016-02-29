# coding=utf-8
import math
from utils import sentence_utils, lda_utils

__author__ = 'jayvee'


def cal_sim_pos(sent_a, sent_b):
    """
    计算两个句子之间的词性相似度
    :param sent_a:
    :param sent_b:
    :return:
    """

    def __cal_vecmod(pos_dict):
        mod_result = 0.0
        for i in pos_dict.values():
            mod_result += i ** 2
        return math.sqrt(mod_result)

    pos_a = sentence_utils.get_pos(sent_a)
    pos_b = sentence_utils.get_pos(sent_b)
    pos_a_dict = {}
    pos_b_dict = {}
    # 建立句子a的pos词典
    for a in pos_a:
        if a[1] in pos_a_dict.keys():
            pos_a_dict[a[1]] += 1.0 / len(pos_a)
        else:
            pos_a_dict[a[1]] = 1.0 / len(pos_a)
    # 建立句子b的pos词典
    for b in pos_b:
        if b[1] in pos_b_dict.keys():
            pos_b_dict[b[1]] += 1.0 / len(pos_b)
        else:
            pos_b_dict[b[1]] = 1.0 / len(pos_b)
    # 处理二者间的相似度
    # 首先是分子的计算
    fenzi = 0.0
    for key_a in pos_a_dict:
        if key_a in pos_b_dict:
            fenzi += pos_a_dict[key_a] * pos_b_dict[key_a]
    # 计算分母
    fenmu = __cal_vecmod(pos_a_dict) * __cal_vecmod(pos_b_dict)
    if fenmu == 0:
        return 0
    else:
        return fenzi / fenmu


def cal_sim_tfidf(sent_a, sent_b):
    """
    计算两个句子之间的tfidf相似度
    :param sent_a:
    :param sent_b:
    :return:
    """

    def __cal_vecmod(pos_dict):
        mod_result = 0.0
        for i in pos_dict.values():
            mod_result += i ** 2
        return math.sqrt(mod_result)

    tfidf_a = sentence_utils.get_keywords(sent_a, topk=5)
    tfidf_b = sentence_utils.get_keywords(sent_b, topk=5)
    # pos_a = sentence_utils.get_pos(sent_a)
    # pos_b = sentence_utils.get_pos(sent_b)
    tfidf_a_dict = {}
    tfidf_b_dict = {}
    # 建立句子a的pos词典
    for word, tfidf in tfidf_a:
        # print word, tfidf
        tfidf_a_dict[word] = tfidf
    # 建立句子b的pos词典
    for word, tfidf in tfidf_b:
        # print word, tfidf
        tfidf_b_dict[word] = tfidf
    # 处理二者间的相似度
    # 首先是分子的计算
    fenzi = 0.0
    for word_a in tfidf_a_dict:
        if word_a in tfidf_b_dict:
            fenzi += tfidf_a_dict[word_a] * tfidf_b_dict[word_a]
    # 计算分母
    fenmu = __cal_vecmod(tfidf_a_dict) * __cal_vecmod(tfidf_b_dict)
    if fenmu == 0:
        return 0.0
    else:
        return fenzi / fenmu


def cal_sim_lda(sent_a, sent_b):
    vec_a = lda_utils.get_topic_vec_by_model(sent_a)
    vec_b = lda_utils.get_topic_vec_by_model(sent_b)
    fenzi = 0.0
    fenmu1 = 0.0
    fenmu2 = 0.0
    for i in xrange(len(vec_a)):
        fenzi += vec_a[i] * vec_b[i]
        fenmu1 += vec_a[i] ** 2
        fenmu2 += vec_b[i] ** 2
    # 计算分母
    fenmu = math.sqrt(fenmu1 * fenmu2)
    if fenmu == 0:
        return 0.0
    else:
        return fenzi / fenmu


def cal_sim_combine(sent_a, sent_b, alpha=0.5):
    """
    计算综合的相似度
    :param sent_a:
    :param sent_b:
    :return:
    """
    sim_pos = cal_sim_pos(sent_a, sent_b)
    sim_tfidf = cal_sim_tfidf(sent_a, sent_b)
    return alpha * sim_pos + (1 - alpha) * sim_tfidf


if __name__ == '__main__':
    senta = u'火箭队是最好的NBA球队'
    sentb = u'西瓜是最好吃的食物'
    print cal_sim_pos(senta, sentb)
    print cal_sim_tfidf(senta, sentb)
    print cal_sim_lda(senta, sentb)
    # print cal_sim_combine(senta, sentb)
