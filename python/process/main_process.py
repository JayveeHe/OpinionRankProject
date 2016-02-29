# coding=utf-8
import hashlib
import random
import sys
import math
import arrow
from dateutil import tz
from utils.node_vec_utils.vec_building import SentenceNode
from utils.sentence_utils import remove_illegal_characters

reload(sys)
sys.setdefaultencoding('utf-8')
import json
from utils.similarity_utils import cal_sim_combine

__author__ = 'jayvee'


def make_network_by_similarity():
    pass


def get_limit_appchina_comments(limit, json_path):
    weixin_json_str = open(
        json_path, 'r').read()
    weixin_json_root = json.loads(weixin_json_str)
    comments = weixin_json_root['comments']
    result = []
    temp_dict = {}
    for i in xrange(limit):
        refined_str = remove_illegal_characters(json.dumps(comments[i]))
        refined_comment = json.loads(refined_str)
        # md5标记去重
        comment_md5 = hashlib.md5(refined_comment['comment'] + refined_comment['nickname']).hexdigest()
        if comment_md5 not in temp_dict:
            refined_comment[u'datetime'] = arrow.get(refined_comment['date'])
            result.append(refined_comment)
            temp_dict[comment_md5] = 1
    return result


def get_limit_taobao_comments(limit, json_path, is_datetime=True):
    taobao_json_str = open(
        json_path, 'r').read()
    taobao_json_root = json.loads(taobao_json_str)
    comments = taobao_json_root['rateList']
    result = []
    temp_dict = {}
    limit = min(limit, len(comments))
    for i in xrange(limit):
        refined_str = remove_illegal_characters(json.dumps(comments[i]))
        refined_comment = json.loads(refined_str)
        com_content = refined_comment.get('content', '')
        if not com_content:
            com_content = ''
        # md5标记去重
        comment_md5 = hashlib.md5(
            str(com_content) + str(refined_comment['user']['nick'])).hexdigest()
        if comment_md5 not in temp_dict:
            if is_datetime:
                refined_comment[u'datetime'] = arrow.get(refined_comment['date'], u'YYYY年MM月DD日 HH:mm',
                                                         tzinfo=tz.tzlocal())
                result.append(
                    {'comment': com_content, 'datetime': refined_comment['datetime']})
            else:
                result.append(
                    {'comment': com_content, 'datetime': refined_comment['date'],
                     'isBelievable': random.choice([True, False])})
            temp_dict[comment_md5] = 1
            if not refined_comment['content']:
                print refined_str
    return result


def cal_similarity_matrix(comments, output_path, sim_rate=0.8, alpha=0.6, time_window=24):
    sim_matrix = [[1.0 for x in xrange(len(comments))] for x in xrange(len(comments))]
    # 根据时间进行排序
    sorted_comments = sorted(comments, cmp=(lambda x, y: cmp(x['datetime'], y['datetime'])))
    # output = open(output_path, 'w')
    # data_json = {'nodes': [], 'edges': []}
    for i in xrange(len(sorted_comments)):
        i_edge_count = 0
        print i
        for j in xrange(i + 1, len(sorted_comments)):
            # print i, j
            sim_matrix[i][j] = cal_sim_combine(sorted_comments[i]['comment'], sorted_comments[j]['comment'],
                                               alpha=alpha)
            sim_matrix[j][i] = sim_matrix[i][j]
            # if i != j and sim_matrix[i][j] > sim_rate:
            #     # if i != j:
            #     # 进行软连接
            #     smd = sim_matrix[i][j]
            #     rd = random.random()
            #     sd = sim_matrix[i][j] ** 2
            #     if rd < sd:
            #         print 'rd=%s, sd=%s, smd=%s|||index=%s【content】:%s----------index=%s【content】%s' % (rd, sd, smd,
            #                                                                                             i,
            #                                                                                             sorted_comments[
            #                                                                                                 i][
            #                                                                                                 'comment'],
            #                                                                                             j,
            #                                                                                             sorted_comments[
            #                                                                                                 j][
            #                                                                                                 'comment'])
            #         data_json['edges'].append({'id': '%s-%s' % (i, j), 'source': '%s' % i, 'target': '%s' % j})
            #         i_edge_count += 1
    # data_json['nodes'].append(
    #         {'id': '%s' % i, "label": sorted_comments[i]['comment'][:40], 'x': random.random() * 100,
    #          'y': random.random() * 100,
    #          'size': 1.1 ** i_edge_count})
    # output.write(json.dumps(data_json))
    return sim_matrix


def get_links_by_matrix_and_time(sim_matrix, comments, output_path, window_count=3, time_range=1 * 3600):
    # 首先根据相似矩阵
    last_comment = comments[0]
    data_json = {'nodes': [], 'edges': [], 'datetimes': {}}
    for i in xrange(len(comments)):
        data_json['nodes'].append(
            {'id': '%s' % i, "label": '%s-' % i + comments[i]['comment'][:40], 'x': random.random() * 100,
             'y': random.random() * 100,
             'size': 1})
        data_json['datetimes']['%s' % i] = comments[i]['datetime']
        # cur_comment = comments[i]
        # 首先连接前后两点
        j = 1
        if i - j >= 0:
            data_json['edges'].append({'id': '%s-%s' % (i, i - j), 'source': '%s' % i, 'target': '%s' % (i - j)})
        # 进行其他点的连接
        j = 2
        t = (comments[i - j]['datetime'] - comments[i]['datetime'])
        while (j < window_count) and (i - j > 0) and (
                not (not ((comments[i]['datetime'] - comments[i - j]['datetime']).seconds < time_range) and not (
                                random.random() ** 2 < sim_matrix[i][i - j]))
        ):
            data_json['edges'].append({'id': '%s-%s' % (i, i - j), 'source': '%s' % i, 'target': '%s' % (i - j)})
            j += 1
    open(output_path, 'w').write(json.dumps(data_json))
    return data_json


if __name__ == '__main__':
    # json_comments = get_limit_appchina_comments(200,
    #                                             '/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/data/appchina_qq.json')
    json_comments = get_limit_taobao_comments(100,
                                              '/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/data/包邮大学生宿舍床头置物架寝室置物架上铺必备挂篮收纳神器-1411148210639.txt',
                                              is_datetime=True)
    # open('../data/trainset/shenqi.json', 'w').write(json.dumps(json_comments, ensure_ascii=False))
    # for i in json_comments:
    #     print i
    # sm = cal_similarity_matrix(json_comments,
    #                            output_path='/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/visualization/flask_app/'
    #                                        'static/trainset-taobao-shenqi-0.5-0.3-100-soft.json',
    #                            sim_rate=0.5,
    #                            alpha=0.3)
    sent_node_list = []
    for comm in json_comments:
        comment = comm['comment']
        sent_node = SentenceNode(comment, None)
        sent_node_list.append(sent_node)
    print len(sent_node_list)

    sm = json.loads(open('../data/params/sim_mat_shenqi.json', 'r').read())
    djson = get_links_by_matrix_and_time(sm, json_comments, window_count=20, time_range=2 * 3600,
                                         output_path='/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/visualization/flask_app/'
                                                     'static/trainset-taobao-shenqi-0.5-0.3-100-soft.json')

    # open('../data/params/sim_mat_shenqi.json', 'w').write(json.dumps(djson))

    # sm = cal_similarity_matrix(json_taobao, output_path='taobao-iphone-0.8-0.7-300-soft.json', sim_rate=0.8, alpha=0.7)
    # print len(sm)
    # open('sim_mat.json', 'w').write(json.dumps(sm))
