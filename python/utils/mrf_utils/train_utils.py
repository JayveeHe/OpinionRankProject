# coding=utf-8
import json

__author__ = 'jayvee'


def cal_p_yk_xi(x_id, k, graph_map):
    """
    计算P(Yk|Xi)
    :param x_id:
    :param k:
    :param graph_map:
    :return:
    """
    return _cal_prior_p_pos(graph_map[x_id]['label'], input_graph_map=graph_map)


def _cal_prior_p_pos(x_label, y_k_value, input_graph_map):
    """
    计算句法丰富度概率的先验，词性大于5种则为1（丰富），否则为0
    :param input_graph_map:
    :param x_label:
    :return:
    """
    count = 0.0
    sum_count = 0.0
    for item in input_graph_map.values():
        if item['label'] == x_label:
            sum_count += 1
            pos_set = set()
            for pos in item['feature']['pos']:
                pos_set.add(pos[1])
            if (y_k_value == '1') == (len(list(pos_set)) > 7):
                count += 1
    if sum_count == 0:
        return 0
    else:
        return count / sum_count


def cal_p_x_ny(x_id, graph_map):
    """
    计算P(X_i|N_i,Y_i)
    :param x_id:
    :param graph_map:
    :return:
    """

    pass


def cal_p_x_n(x_id, n_ids, sim_mat, graph_map):
    """
    计算P(X_i|N_i)
    :param x_id:
    :param n_ids:
    :return:
    """
    sum_f = 0.0
    for n_id in n_ids:
        tao_ij=graph_map[x_id]['datetime']
    pass


if __name__ == '__main__':
    fout = open('../../data/params/mrf_model.json', 'w')
    input_graph = json.loads(open('../../data/trainset/shenqi_train.json', 'r').read())
    params = {'pos': [[0, 0], [0, 0]]}
    params['pos'][1][1] = _cal_prior_p_pos('1', '1', input_graph)
    params['pos'][1][0] = _cal_prior_p_pos('1', '0', input_graph)
    params['pos'][0][1] = _cal_prior_p_pos('0', '1', input_graph)
    params['pos'][0][0] = _cal_prior_p_pos('0', '0', input_graph)
    fout.write(json.dumps(params))

    # 正式函数
