# coding=utf-8
import math
from utils.sentence_utils import get_pos, get_keywords

__author__ = 'jayvee'
'''
用于根据原始文本构建特征向量
'''


class SentenceNode(object):
    def __init__(self, sent, post_datetime=None, extra=None, get_pos_func=get_pos, get_keywords_func=get_keywords):
        """

        :param sent:
        :param post_datetime:
        :param extra:
        :param get_pos_func: 可自定义词性提取
        :param get_keywords_func: 可自定义tfidf提取
        :return:
        """
        self.sent = sent.replace('\n', '')
        self.pos_result = get_pos_func(self.sent)
        self.tfidf_result = {}
        for item in get_keywords_func(self.sent):
            self.tfidf_result[item[0]] = item[1]

        self.noun_rate = 0.0
        self.adj_rate = 0.0
        self.verb_rate = 0.0
        self.adv_rate = 0.0
        self.g_noun_rate = 0.0  # group related feature
        self.g_adj_rate = 0.0
        self.g_verb_rate = 0.0
        self.g_adv_rate = 0.0
        self.g_tfidf_rate = []
        self.sent_len = len(sent)
        self.g_sent_len = 0.0
        self.post_datetime = post_datetime
        self.extra = extra



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
                if pos[1] in ['v', 'vn', 'vd', 'vi', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'VERB']:
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
                if pos[1] in ['n', 'ns', 'nz', 'nr', 'NN', 'NNS', 'NNP', 'NNPS', 'NOUN']:
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
                if pos[1] in ['a', 'ad', 'an', 'ag', 'al', 'JJ', 'JJR', 'JJS', 'ADJ']:
                    tmp_count += 1.0
            return tmp_count / len(self.pos_result)

        def cal_adv_rate():
            """
            计算介词所占的比例
            :return:
            """
            verb_count = 0.0
            if len(self.pos_result) == 0:
                return 0.0
            for pos in self.pos_result:
                if pos[1] in ['ADV']:
                    verb_count += 1.0
            return verb_count / len(self.pos_result)

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
        self.adv_rate = cal_adv_rate()

    def norm_vec(self, group_paras):
        """
        将本句子的feature与全局feature进行归一化处理
        :param group_paras:
        :return:
        """

        def cal_sigmoid(rate, mean_rate, k=2):
            """
            计算sigmoid，即归一化单个feature
            """
            if rate == mean_rate == 0:
                g = 0
            else:
                g = (rate - mean_rate) / (rate+mean_rate)
            return 1 / (1 + math.exp(-k * g))

        def cal_sigmoid_std(rate, mean_rate, std_rate, k=2):
            """
            计算sigmoid，使用std归一化单个feature
            """
            if rate == mean_rate == 0 or std_rate == 0:
                g = 0
            else:
                g = (rate - mean_rate) / (std_rate)
            return 1 / (1 + math.exp(-k * g))

        mean_verb_rate = group_paras['mean_verb_rate']  # 暂时不用mean
        std_verb_rate = group_paras['std_verb_rate']
        # self.g_verb_rate = self.verb_rate / mean_verb_rate
        self.g_verb_rate = cal_sigmoid_std(self.verb_rate, mean_verb_rate, std_verb_rate)
        mean_noun_rate = group_paras['mean_noun_rate']
        std_noun_rate = group_paras['std_noun_rate']
        # self.g_noun_rate = self.noun_rate / mean_noun_rate
        self.g_noun_rate = cal_sigmoid_std(self.noun_rate, mean_noun_rate, std_noun_rate)
        mean_adj_rate = group_paras['mean_adj_rate']
        std_adj_rate = group_paras['std_adj_rate']
        # self.g_adj_rate = self.adj_rate / mean_adj_rate
        self.g_adj_rate = cal_sigmoid_std(self.adj_rate, mean_adj_rate, std_adj_rate)
        mean_adv_rate = group_paras['mean_adv_rate']
        std_adv_rate = group_paras['std_adv_rate']
        # self.g_adj_rate = self.adj_rate / mean_adj_rate
        self.g_adv_rate = cal_sigmoid_std(self.adv_rate, mean_adv_rate, std_adv_rate)
        # sent len
        mean_sent_len = group_paras['mean_sent_len']
        std_sent_len = group_paras['std_sent_len']
        self.g_sent_len = cal_sigmoid_std(self.sent_len, mean_sent_len, std_sent_len)
        # tfidf vec
        global_keywords = group_paras['global_keywords']
        self.g_tfidf_rate = [0.0 for i in range(len(global_keywords))]
        for i in xrange(len(global_keywords)):
            if global_keywords[i][0] in self.tfidf_result:
                # self.g_tfidf_rate[i] = self.tfidf_result[global_keywords[i]]
                self.g_tfidf_rate[i] = cal_sigmoid(self.tfidf_result[global_keywords[i][0]], global_keywords[i][1])

                # for kword in self.tfidf_result:
                #     if kword[0] in global_keywords:
                #         self.g_tfidf_rate += 1
                # self.g_tfidf_rate /= len(global_keywords)

    def get_vec(self):
        """
        获取该句子的特征向量集
        :return: a dict
        """
        return {'verb_rate': self.verb_rate, 'noun_rate': self.noun_rate, 'adj_rate': self.adj_rate,
                'adv_rate': self.adv_rate,
                'g_verb_rate': self.g_verb_rate, 'g_noun_rate': self.g_noun_rate, 'g_adj_rate': self.g_adj_rate,
                'g_adv_rate': self.g_adv_rate,
                'g_tfidf_rate': self.g_tfidf_rate, 'sent_len': self.sent_len, 'g_sent_len': self.g_sent_len}

    def feature2token(self, interval=0.001):
        """
        sent feature转lda的输入token
        :return:
        """
        vec = self.get_vec()
        tokens = []
        i = 0
        RANGE = int(1 / interval)
        for key in vec.keys():
            # if key.__contains__('g'):
            #     rate = vec.get(key)
            #     tokens.append((i * RANGE + int(rate / interval), 1.0))
            #     i += 1
            rate = vec.get(key)
            if key == 'sent_len':
                continue
            if isinstance(rate, list):
                for c in rate:
                    tokens.append((i * RANGE + int(c / interval), 1.0))
                    i += 1
            else:
                tokens.append((i * RANGE + int(rate / interval), 1.0))
                i += 1
        return tokens
