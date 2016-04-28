# coding=utf-8
from utils.sentence_utils import get_keywords

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

    def get_global_keywords(self, topk):
        tmp_text = ''
        for node in self.node_list:
            tmp_text += node.sent + '\n'
        return get_keywords(tmp_text, topk)

    def get_global_values(self):
        """
        获取句子群的群属性值
        :return:
        """
        mean_verb_rate = 0
        mean_adj_rate = 0
        mean_noun_rate = 0
        mean_sent_len = 0
        list_size = len(self.node_list)
        for sent in self.node_list:
            vec_value = sent.get_vec()
            mean_verb_rate += vec_value['verb_rate'] / list_size
            mean_adj_rate += vec_value['adj_rate'] / list_size
            mean_noun_rate += vec_value['noun_rate'] / list_size
            mean_sent_len += vec_value['sent_len'] / list_size
        gkeywords = []
        gkeywords = self.get_global_keywords(100)
        # for gkey in self.get_global_keywords(10):
        #     gkeywords.append(gkey[0])

        return {'mean_verb_rate': mean_verb_rate, 'mean_adj_rate': mean_adj_rate,
                'mean_noun_rate': mean_noun_rate, 'mean_sent_len': mean_sent_len, 'global_keywords': gkeywords}

    def normalize_all_sentnodes(self):
        global_values = self.get_global_values()
        for node in self.node_list:
            node.norm_vec(global_values)

    def get_vec_list(self):
        vec_list = []
        for node in self.node_list:
            vec_dict = node.get_vec()
            vec_list.append(
                [vec_dict['g_verb_rate'], vec_dict['g_noun_rate'],
                 vec_dict['g_adj_rate']] + vec_dict['g_tfidf_rate'])
        return vec_list

    def get_sent_list(self):
        sent_list = []
        for node in self.node_list:
            sent_list.append(node.sent)
        return sent_list

    def index2sent(self, index):
        return self.node_list[index].sent
