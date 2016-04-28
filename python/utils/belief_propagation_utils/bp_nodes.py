# coding=utf-8
import math

__author__ = 'jayvee'

'''
用于置信传播算法的node类
'''


class VarNode(object):
    def __init__(self, node_id, sent_node):
        self.node_id = node_id
        self.neighbors = []
        self.m = [{}, {}]  # mij
        self.px_tuple = []
        self.belief = [0, 1]
        self.sent_node = sent_node
        self.tmp_m = [{}, {}]

    def add_neighbor(self, neighbor_node):
        self.neighbors.append(neighbor_node)
        self.m[0][neighbor_node.node_id] = 1  # init uniform to 1
        self.m[1][neighbor_node.node_id] = 1

    def cal_m_ij(self, node_j, sim):
        tmp = [1, 1]
        for node in self.neighbors:
            if node.node_id != node_j.node_id:
                tmp[0] *= node.m[0][self.node_id]
                tmp[1] *= node.m[1][self.node_id]
        tmp[0] *= self.px_tuple[0] * sim
        tmp[1] *= self.px_tuple[1] * sim
        self.tmp_m[0][node_j.node_id] = tmp[0]
        self.tmp_m[1][node_j.node_id] = tmp[1]

    def cal_bx(self):
        tmp = [1, 1]
        for node in self.neighbors:
            tmp[0] *= node.m[0][self.node_id]
            tmp[1] *= node.m[1][self.node_id]
        self.belief[0] = self.px_tuple[0] * tmp[0] / (self.px_tuple[1] * tmp[1] + self.px_tuple[0] * tmp[0])
        self.belief[1] = self.px_tuple[1] * tmp[1] / (self.px_tuple[1] * tmp[1] + self.px_tuple[0] * tmp[0])

    def on_update(self):
        self.m = self.tmp_m


class ObservNode(object):
    """
    观察节点类
    """

    def __init__(self, node_id):
        self.node_id = node_id
        self.connected_factors = {}
        self.cur_belief = [0.0, 1.0]  # 第一项为x=0的概率,第二项x=1的概率
        self.tmp_belief = [0.0, 1.0]
        self.is_log = False
        self.u_i2alpha = [{}, {}]
        self.tmp_u_i2alpha = [{}, {}]
        self.fai_x = 1

    def cal_bix(self):
        """
        计算该观察点的置信度
        """
        self.is_log = False
        bx = [1, 1]
        for ft_node in self.connected_factors.values():
            bx[0] *= ft_node.cal_u_alpha2i(0, self.node_id)
            bx[1] *= ft_node.cal_u_alpha2i(1, self.node_id)
        self.tmp_belief[0] = bx[0] / (bx[0] + bx[1])
        self.tmp_belief[1] = bx[1] / (bx[0] + bx[1])
        return self.tmp_belief
        # self.tmp_belief = bx

    def cal_log_bx(self, xi):
        """
        计算该观察点的log置信度
        """
        self.is_log = True
        log_bx = 0.0
        for ft_node in self.connected_factors.values():
            log_bx += ft_node.cal_log_f2x(self.node_id)
        self.tmp_belief = log_bx

    def cal_u_i2alpha(self, xi, ft_node_id):
        """
        计算该变量节点i到因子节点的消息值
        :param xi: 该节点是可信(1)还是不可信(0)
        :param ft_node_id: 因子节点在变量节点的链接中的序号
        :return:
        """
        tmp = 1
        for ft_node in self.connected_factors.values():
            if ft_node.node_id != ft_node_id:
                tmp *= ft_node.u_alpha2i[xi][ft_node.node_id]
        self.tmp_u_i2alpha[xi][ft_node_id] = tmp
        return tmp

    def on_update(self, sys_energy):
        """
        每次大循环结束后的置信度更新
        """
        local_energy = self.cur_belief[0] - self.tmp_belief[0]
        self.cur_belief = self.tmp_belief
        self.tmp_belief = [1.0, 1.0]
        self.u_i2alpha = self.tmp_u_i2alpha
        return local_energy


class FactorNode(object):
    """
    因子（约束）节点类
    """

    def __init__(self, node_id):
        self.node_id = node_id
        self.connected_observs = {}
        self.conditions = None
        self.u_alpha2i = [{}, {}]
        self.tmp_u_alpha2i = [{}, {}]

    def cal_u_alpha2i(self, xi, ob_node_id):
        """
        计算该因子节点到变量节点i的消息值
        :param xi: 该节点是可信(1)还是不可信(0)
        :param ob_node_id: 变量节点在因子节点的链接中的序号
        :return:
        """
        tmp = 1.0
        for ob_node in self.connected_observs.values():
            if ob_node.node_id != ob_node_id:
                tmp *= self.connected_observs[ob_node.node_id].cal_u_i2alpha(xi, self.node_id)
        # tmp_result = 1.0
        if xi == 1:
            tmp_result = tmp * self.connected_observs[ob_node_id].cur_belief[xi]  # 省去求和 TODO 此处公式可能很有问题
        else:
            tmp_result = tmp * self.connected_observs[ob_node_id].cur_belief[xi]
        self.tmp_u_alpha2i[xi][ob_node_id] = tmp_result
        return tmp_result

    def cal_f2x(self, x_id):
        """
        计算从因子节点到观察节点的信息值（假设因子函数常为1）
        :param x_id:
        :return:
        """
        f2x = 0.0
        for ob_node in self.connected_observs.values():
            if ob_node.node_id != x_id:
                f2x += ob_node.cur_belief
        return f2x

    def cal_log_f2x(self, x_id):
        f2x = 0.0
        for ob_node in self.connected_observs.values():
            if ob_node.node_id != x_id:
                f2x += math.exp(ob_node.cur_belief)  # TODO 处理0问题
        return f2x

    def on_update(self):
        """
        每次大循环结束后的更新
        """
        self.u_alpha2i = self.tmp_u_alpha2i
        # return local_energy
