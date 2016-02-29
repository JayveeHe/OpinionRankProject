# coding=utf-8
from utils.sentence_utils import get_pos, get_keywords

__author__ = 'jayvee'


class SentenceNode(object):
    def __init__(self, sent, post_datetime):
        self.sent = sent
        self.pos_result = get_pos(self.sent)
        self.tfidf_result = get_keywords(self.sent)
        self.noun_rate = 0.0
        self.adj_rate = 0.0
        self.verb_rate = 0.0
        self.post_datetime = post_datetime

        # define cal rates func
        def cal_verb_rate():
            """
            计算动词所占的比例
            :return:
            """
            verb_count = 0.0
            if len(self.pos_result) == 0:
                return 0.0
            for pos in self.pos_result:
                if pos[1] in ['v', 'vn', 'vd', 'vi']:
                    verb_count += 1.0
            return verb_count / len(self.pos_result)

        def cal_noun_rate():
            """
            计算名词所占的比例
            :return:
            """
            tmp_count = 0.0
            if len(self.pos_result) == 0:
                return 0.0
            for pos in self.pos_result:
                if pos[1] in ['n', 'ns', 'nz', 'nr']:
                    tmp_count += 1.0
            return tmp_count / len(self.pos_result)

        def cal_adj_rate():
            """
            计算形容词所占的比例
            :return:
            """
            tmp_count = 0.0
            if len(self.pos_result) == 0:
                return 0.0
            for pos in self.pos_result:
                if pos[1] in ['a', 'ad', 'an', 'ag', 'al']:
                    tmp_count += 1.0
            return tmp_count / len(self.pos_result)

        # def cal_pos_rate():


        # def cal_unknown_rate():
        #     tmp_count = 0.0
        #     for pos in self.pos_result:
        #         if pos[1] in ['a', 'ad', 'an', 'ag', 'al']:
        #             tmp_count += 1.0
        #     return tmp_count / len(self.pos_result)

        # start building vec
        self.verb_rate = cal_verb_rate()
        self.noun_rate = cal_noun_rate()
        self.adj_rate = cal_adj_rate()

    def get_vec(self):
        """
        获取该句子的特征向量集
        :return: a dict
        """
        return {'verb_rate': self.verb_rate, 'noun_rate': self.noun_rate, 'adj_rate': self.adj_rate}
