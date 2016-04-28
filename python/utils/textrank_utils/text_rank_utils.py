# coding=utf-8
import math
from textrank4zh.util import AttrDict, get_similarity
from utils.node_vec_utils.global_utils import SentenceNodeManager
from utils.node_vec_utils.vec_building_utils import SentenceNode

__author__ = 'jayvee'
import sys

import networkx as nx
import numpy as np

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass

import codecs

from textrank4zh import TextRank4Keyword, TextRank4Sentence

tr4s = TextRank4Sentence()


def analyse_csv(csv_path, num=3, **pagerank_config):
    fin = codecs.open(csv_path, 'r', 'utf-8')
    all_text = ''
    for line in fin:
        eles = line.split(',')
        try:
            all_text += eles[4].replace('\n', '') + '。'
        except:
            continue
    tr4s.analyze(all_text, lower=True, source='all_filters', pagerank_config=pagerank_config)
    return tr4s.get_key_sentences(num=num, sentence_min_len=1)


def text_rank(sentences, num=10, sim_func=get_similarity, pagerank_config={'alpha': 0.85, }):
    """将句子按照关键程度从大到小排序

    Keyword arguments:
    sentences         --  列表，元素是句子
    words             --  二维列表，子列表和sentences中的句子对应，子列表由单词组成
    sim_func          --  计算两个句子的相似性，参数是两个由单词组成的列表
    pagerank_config   --  pagerank的设置
    """

    def cal_cos(vec1, vec2):
        def __cal_vecmod(vec):
            mod_result = 0.0
            for i in vec:
                mod_result += i ** 2
            return math.sqrt(mod_result)

        # 首先是分子的计算
        fenzi = 0.0
        for i in xrange(len(vec1)):
            fenzi += vec1[i] * vec2[i]
        # 计算分母
        fenmu = __cal_vecmod(vec1) * __cal_vecmod(vec2)
        if fenmu == 0:
            return 0
        else:
            return fenzi / fenmu

    sorted_sentences = []
    snm = SentenceNodeManager()
    for sent in sentences:
        snode = SentenceNode(sent)
        snm.add_node(snode)
    snm.normalize_all_sentnodes()
    vlist = snm.get_vec_list()
    # _source = words
    sentences_num = len(vlist)
    graph = np.zeros((sentences_num, sentences_num))

    for x in xrange(sentences_num):
        for y in xrange(x, sentences_num):
            similarity = cal_cos(vlist[x], vlist[y])
            graph[x, y] = similarity
            graph[y, x] = similarity

    nx_graph = nx.from_numpy_matrix(graph)
    scores = nx.pagerank(nx_graph, **pagerank_config)  # this is a dict
    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)

    for index, score in sorted_scores:
        item = AttrDict(sentence=sentences[index], weight=score)
        sorted_sentences.append(item)

    return sorted_sentences[:num]


if __name__ == '__main__':
    fin = codecs.open(
        '/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/crawler/data/csv/1461606416-机器学习.csv',
        'r', 'utf-8')
    all_text = ''
    sents = []
    for line in fin:
        eles = line.replace('\n', '').split(',')
        try:
            all_text += eles[4] + '。'
            sents.append(eles[4])
        except:
            continue
    for i in text_rank(sents, num=100):
        print '%s\t%s' % (i.weight, i.sentence)
