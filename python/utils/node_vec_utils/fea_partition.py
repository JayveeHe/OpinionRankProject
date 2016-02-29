# coding=utf-8
import math

__author__ = 'jayvee'


def divide_fea_rates(interval_rate, fea_list, fea_key):
    '''

    :param interval_rate:
    :param fea_list: 未经过排序的get_vec()后的特征list
    :param fea_key:
    :return:
    '''
    rate_partition = [[] for i in xrange(int(math.floor(1 / interval_rate)) + 1)]
    if fea_key not in ['verb_rate', 'noun_rate', 'adj_rate']:
        return None
    for i in xrange(len(fea_list)):
        cur_fea = fea_list[i]
        rate_partition[int(math.floor(cur_fea.get(fea_key) / interval_rate))].append(i)
    return rate_partition


if __name__ == '__main__':
    pass
