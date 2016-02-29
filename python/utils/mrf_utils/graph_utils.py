# coding=utf-8
import json
import random
import arrow
from dateutil import tz
from utils.sentence_utils import get_pos

__author__ = 'jayvee'


def get_links_by_matrix_and_time(sim_matrix, comments, output_path, window_count=3, time_range=1 * 3600):
    # 首先根据相似矩阵
    last_comment = comments[0]
    data_json = {'nodes': [], 'edges': []}
    for i in xrange(len(comments)):
        data_json['nodes'].append(
            {'id': '%s' % i, "label": '%s-' % i + comments[i]['comment'][:40], 'x': random.random() * 100,
             'y': random.random() * 100,
             'size': 1})
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


def get_graph_map_by_json(data_json, is_train=False):
    graph_map = {}
    for edge in data_json['edges']:
        source = edge['source']
        target = edge['target']
        if source in graph_map:
            graph_map[source]['neighbors'].append(target)
        else:
            graph_map[source] = {'content': data_json['nodes'][int(source)]['label'].split('-')[1],
                                 'neighbors': [target], 'label': random.choice(['0', '1']),
                                 'datetime': arrow.get(data_json['datetimes'][source], u'YYYY年MM月DD日 HH:mm',
                                                       tzinfo=tz.tzlocal()),
                                 'feature': {'pos': get_pos(data_json['nodes'][int(source)]['label'].split('-')[1])}}

        if target in graph_map:
            graph_map[target]['neighbors'].append(source)
        else:
            graph_map[target] = {'content': data_json['nodes'][int(target)]['label'].split('-')[1],
                                 'neighbors': [source], 'label': random.choice(['0', '1']),
                                 'datetime': arrow.get(data_json['datetimes'][source], u'YYYY年MM月DD日 HH:mm'),
                                 'feature': {'pos': get_pos(data_json['nodes'][int(source)]['label'].split('-')[1])}}
    return graph_map


if __name__ == '__main__':
    input_json = json.loads(open(
        '/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/visualization/flask_app/static/trainset-taobao-shenqi-0.5-0.3-100-soft.json',
        'r').read())
    graph_map = get_graph_map_by_json(input_json)
    output_json = json.dumps(graph_map)
    open('../../data/trainset/shenqi_train.json', 'w').write(output_json)
