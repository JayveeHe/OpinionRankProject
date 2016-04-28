# coding=utf-8
import pickle

from process.main_process import get_limit_taobao_comments
from utils.belief_propagation_utils.bp_nodes import FactorNode, ObservNode, VarNode
from utils.node_vec_utils.vec_building_utils import SentenceNode
from utils.similarity_utils import cal_sim_tfidf

__author__ = 'jayvee'
from sklearn.naive_bayes import MultinomialNB as MNB


def cal_p_yi_xi(feature_vec, nbclf):
    return nbclf.predict_proba(feature_vec)[0][1]


def cal_likelihood_rate(feature_vec, nbclf):
    px1yi = nbclf.predict_proba(feature_vec)[0][1]
    px0yi = 1 - px1yi
    return px1yi / px0yi


def train_pyx_nb_clf(fea_vec_list, label_list, model_path):
    """
    根据已有的样本集进行训练，得到一个统计意义上的p(xi=1|Yi)概率

    :return:
    """
    mnb = MNB()
    mnb.fit(fea_vec_list[:-10], label_list[:-10])
    with open(model_path, 'wb') as output_file:
        pickle.dump(mnb, output_file)
        print 'successfully dump model to %s' % model_path


class NodeManager(object):
    """
    用于管理当前图的所有节点操作的管理类
    """

    def __init__(self, sent_vec_list, sent_node_list):
        self.observ_list = [ObservNode(i) for i in xrange(len(sent_vec_list))]
        self.factor_list = []
        self.sent_vec_list = sent_vec_list
        self.sim_matrix = [[1 for i in range(len(sent_vec_list))] for j in range(len(sent_vec_list))]
        self.sent_list = sent_node_list

    def cal_sim_matrix(self):
        if len(self.observ_list) > 0:
            for i in xrange(len(self.sent_vec_list)):
                for j in xrange(i, len(self.sent_vec_list)):
                    self.sim_matrix[i][j] = cal_sim_tfidf(self.sent_list[i], self.sent_list[j])
                    self.sim_matrix[j][i] = self.sim_matrix[i][j]

    def build_factor_graph(self, ft_partition):
        # partition = divide_fea_rates(interval_rate, sent_node_fea_list, fea_key)
        for p in ft_partition:
            if len(p) > 0:
                factor_node = FactorNode(len(self.factor_list))
                for n_id in p:
                    ob_node = self.observ_list[n_id]
                    ob_node.connected_factors[len(self.factor_list)] = factor_node
                    factor_node.connected_observs[n_id] = ob_node
                self.factor_list.append(factor_node)
        print 'build done'

    def start_processing(self, nbclf):
        # 用先验条件初始化各节点的belief
        for node_index in xrange(len(self.observ_list)):
            vec = self.sent_vec_list[node_index]
            # self.observ_list[node_index].cur_belief = cal_p_yi_xi(vec, nbclf)
            px = cal_p_yi_xi(vec, nbclf)
            self.observ_list[node_index].cur_belief = [1 - px, px]
        # start
        sys_energy = 1000
        threshold = 100
        iter_count = 0
        # for i in xrange(10):
        while sys_energy > threshold:
            sys_energy = 0.0
            for ob_node in self.observ_list:
                ob_node.cal_bix()
            # update
            for ob_node in self.observ_list:
                sys_energy += ob_node.on_update(sys_energy)
            for ft_node in self.factor_list:
                ft_node.on_update()
            print '%s times done' % iter_count
            iter_count += 1
        # return result
        result = []
        for ob_node in self.observ_list:
            result.append({'id': ob_node.node_id, 'belief': ob_node.cur_belief})
        return result


class MRFmanager(object):
    def __init__(self, sent_node_list, sent_vec_list):
        # self.graph_map = graph_map
        self.sent_node_list = sent_node_list
        self.sent_vec_list = sent_vec_list
        self.var_node_list = []
        for ii in xrange(len(self.sent_node_list)):
            self.var_node_list.append(VarNode(ii, self.sent_node_list[ii]))
        self.sim_matrix = [[1 for i in range(len(sent_node_list))] for j in range(len(sent_node_list))]
        # cal sim mat
        if len(self.sent_node_list) > 0:
            for q in xrange(len(self.sent_node_list)):

                for j in xrange(q + 1, len(self.sent_node_list)):
                    sm = cal_sim_tfidf(self.sent_node_list[q].sent, self.sent_node_list[j].sent)
                    self.sim_matrix[q][j] = sm
                    self.sim_matrix[j][q] = self.sim_matrix[q][j]
                    if sm > 0.2:
                        self.var_node_list[q].add_neighbor(self.var_node_list[j])
                        self.var_node_list[j].add_neighbor(self.var_node_list[q])

    def cal_sim_matrix(self):
        if len(self.sent_node_list) > 0:
            for i in xrange(len(self.sent_node_list)):
                for j in xrange(i, len(self.sent_node_list)):
                    self.sim_matrix[i][j] = cal_sim_tfidf(self.sent_node_list[i], self.sent_node_list[j])
                    self.sim_matrix[j][i] = self.sim_matrix[i][j]

    def cal_belief(self, nbclf):
        # 用先验条件初始化各节点的belief
        for node_index in xrange(len(self.sent_vec_list)):
            vec = self.sent_vec_list[node_index]
            # self.observ_list[node_index].cur_belief = cal_p_yi_xi(vec, nbclf)
            px = cal_p_yi_xi(vec, nbclf)
            self.var_node_list[node_index].px_tuple = [1 - px, px]
        for i in xrange(10):
            # iter 10 times
            for node in self.var_node_list:
                for nei_node in node.neighbors:
                    node.cal_m_ij(nei_node, self.sim_matrix[node.node_id][nei_node.node_id])
            # update
            for node in self.var_node_list:
                node.on_update()
                node.cal_bx()
        return self.var_node_list


if __name__ == '__main__':
    json_comments = get_limit_taobao_comments(50,
                                              '/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/data/北通阿修罗SE版USB双震动XBOX360架构PS3安卓PC电脑游戏手柄-1410934375464.txt',
                                              is_datetime=True)
    # json_comments.extend(get_limit_taobao_comments(1000,
    #                                                '/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/data/包邮大学生宿舍床头置物架寝室置物架上铺必备挂篮收纳神器-1411148210639.txt',
    #                                                is_datetime=True))
    # json_comments.extend(get_limit_taobao_comments(10000,
    #                                                '/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/data/特价Apple苹果iPhone5c苹果手机港版美V版三网电信移动4G无锁-1411017234827.txt',
    #                                                is_datetime=True))
    # json_comments.extend(get_limit_taobao_comments(10000,
    #                                                '/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/data/飞利浦核心技术佰益莱空气净化器家用除甲醛pm2.5离子杀菌除烟尘-1411211340771.txt',
    #                                                is_datetime=True))
    sent_node_fea_list = []
    sent_node_vec_list = []
    sent_node_belief_list = []
    sent_list = []
    verb_list = []
    noun_list = []
    adj_list = []
    a = {}
    for comm in json_comments:
        comment = comm['comment']
        sent_node = SentenceNode(comment, None)
        sent_list.append(sent_node)
        sent_node_fea_list.append(sent_node.get_vec())
        sent_node_vec_list.append([sent_node.verb_rate, sent_node.noun_rate, sent_node.adj_rate])
        if comm['isBelievable']:
            sent_node_belief_list.append(1)
        else:
            sent_node_belief_list.append(0)
        verb_list.append(sent_node.verb_rate)
        noun_list.append(sent_node.noun_rate)
        adj_list.append(sent_node.adj_rate)

    # ap = sc.AffinityPropagation()
    # res = ap.fit(sent_node_vec_list)
    # c_res = ap.predict(sent_node_vec_list)
    # clusters = {}
    # for i in range(len(c_res)):
    #     if clusters.get(c_res[i]):
    #         clusters[c_res[i]].append(json_comments[i]['comment'])
    #     else:
    #         clusters[c_res[i]] = [json_comments[i]['comment']]
    # open('cluster_result.json', 'w').write(json.dumps(clusters, ensure_ascii=False))
    # node_manager = NodeManager(sent_node_vec_list,sent_list)

    # input_json = json.loads(open(
    #     '/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/visualization/flask_app/static/trainset-taobao-shenqi-0.5-0.3-100-soft.json',
    #     'r').read())
    # graph_map = get_graph_map_by_json(input_json)

    mrf_manager = MRFmanager(sent_list, sent_node_vec_list)


    # 约束条件的建立
    # interval_rate = 0.01
    # fea_key = 'adj_rate'
    # partition = divide_fea_rates(interval_rate, sent_node_fea_list, fea_key)
    # node_manager.build_factor_graph(partition)


    # train_pyx_nb_clf(sent_node_vec_list, sent_node_belief_list,
    #                  '/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/data/bp_data/multiNB.model')
    with open('/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/data/bp_data/multiNB.model',
              'rb') as model_file:
        multinb = pickle.load(model_file)
        mrf_manager.cal_belief(multinb)

        # p_result = node_manager.start_processing(multinb)
        # p_result.sort(lambda x, y: -cmp(x['belief'][1], y['belief'][1]))
        print 'dddd'
        # for i in xrange(10):
        #     vec = sent_node_vec_list[-i]
        #     print sent_node_belief_list[-i], cal_p_yi_xi(vec, multinb)
