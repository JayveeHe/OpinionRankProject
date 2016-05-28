# coding=utf-8
from utils.sentence_utils import get_keywords
import numpy as np

__author__ = 'jayvee'

"""
用于管理句子群并计算相应的群属性
"""


class SentenceNodeManager(object):
    def __init__(self, extra=None):
        self.node_list = []
        self.extra = None

    def add_node(self, sent_node):
        self.node_list.append(sent_node)

    def get_global_keywords(self, topk, keywords_func=None):
        tmp_text = ''
        for node in self.node_list:
            tmp_text += node.sent + '\n'
        return get_keywords(tmp_text, topk, keywords_func)

    def get_global_values(self, tfidf_func=None):
        """
        获取句子群的群属性值
        :return:
        """
        # mean_verb_rate = 0
        # mean_adj_rate = 0
        # mean_noun_rate = 0
        # mean_sent_len = 0
        # list_size = len(self.node_list)
        verb_rate_list = []
        adj_rate_list = []
        noun_rate_list = []
        sent_len_list = []
        for sent in self.node_list:
            vec_value = sent.get_vec()
            verb_rate_list.append(vec_value.get('verb_rate', 0))
            adj_rate_list.append(vec_value.get('adj_rate', 0))
            noun_rate_list.append(vec_value.get('noun_rate', 0))
            sent_len_list.append(vec_value.get('sent_len', 0))
            # mean_verb_rate += vec_value['verb_rate'] / list_size
            # mean_adj_rate += vec_value['adj_rate'] / list_size
            # mean_noun_rate += vec_value['noun_rate'] / list_size
            # mean_sent_len += vec_value['sent_len'] / list_size
        verb_rate_list = np.array(verb_rate_list)
        adj_rate_list = np.array(adj_rate_list)
        noun_rate_list = np.array(noun_rate_list)
        sent_len_list = np.array(sent_len_list)
        std_verb_rate = verb_rate_list.std() if len(verb_rate_list) > 0 else 0.0
        std_adj_rate = adj_rate_list.std() if len(adj_rate_list) > 0 else 0.0
        std_noun_rate = noun_rate_list.std() if len(verb_rate_list) > 0 else 0.0
        std_sent_len = sent_len_list.std() if len(verb_rate_list) > 0 else 0.0
        mean_verb_rate = verb_rate_list.mean() if len(verb_rate_list) > 0 else 0.0
        mean_adj_rate = adj_rate_list.mean() if len(adj_rate_list) > 0 else 0.0
        mean_noun_rate = noun_rate_list.mean() if len(noun_rate_list) > 0 else 0.0
        mean_sent_len = sent_len_list.mean() if len(verb_rate_list) > 0 else 0.0
        # gkeywords = []
        gkeywords = self.get_global_keywords(topk=50, keywords_func=tfidf_func)
        # [{} for word, tfidf in gkeywords]
        if len(gkeywords) < 50:
            for i in range(len(gkeywords), 50):
                gkeywords.append(('tmp', 0.1))

        # for gkey in self.get_global_keywords(10):
        #     gkeywords.append(gkey[0])

        return {
            'mean_verb_rate': mean_verb_rate, 'mean_adj_rate': mean_adj_rate,
            'mean_noun_rate': mean_noun_rate, 'mean_sent_len': mean_sent_len,
            'std_verb_rate': std_verb_rate, 'std_adj_rate': std_adj_rate,
            'std_noun_rate': std_noun_rate, 'std_sent_len': std_sent_len,
            'global_keywords': gkeywords}

    def normalize_all_sentnodes(self, tfidf_func=None):
        global_values = self.get_global_values(tfidf_func=tfidf_func)
        for node in self.node_list:
            node.norm_vec(global_values)

    def get_vec_list(self):
        vec_list = []
        for node in self.node_list:
            vec_dict = node.get_vec()
            vec_list.append(
                [vec_dict['g_verb_rate'], vec_dict['g_noun_rate'],
                 vec_dict['g_adj_rate'], vec_dict['g_sent_len']] + vec_dict['g_tfidf_rate'])
        return vec_list

    def get_sent_list(self):
        sent_list = []
        for node in self.node_list:
            sent_list.append(node.sent)
        return sent_list

    def index2sent(self, index):
        return self.node_list[index].sent
