# coding=utf-8
from process.main_process import get_limit_taobao_comments
from utils.node_vec_utils.fea_partition import divide_fea_rates
from utils.node_vec_utils.vec_building import SentenceNode
import matplotlib.pyplot as plt

__author__ = 'jayvee'

if __name__ == '__main__':
    json_comments = get_limit_taobao_comments(1000,
                                              '/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/data/北通阿修罗SE版USB双震动XBOX360架构PS3安卓PC电脑游戏手柄-1410934375464.txt',
                                              is_datetime=True)
    json_comments.extend(get_limit_taobao_comments(1000,
                                                   '/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/data/包邮大学生宿舍床头置物架寝室置物架上铺必备挂篮收纳神器-1411148210639.txt',
                                                   is_datetime=True))
    json_comments.extend(get_limit_taobao_comments(10000,
                                                   '/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/data/特价Apple苹果iPhone5c苹果手机港版美V版三网电信移动4G无锁-1411017234827.txt',
                                                   is_datetime=True))
    json_comments.extend(get_limit_taobao_comments(10000,
                                                   '/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/data/飞利浦核心技术佰益莱空气净化器家用除甲醛pm2.5离子杀菌除烟尘-1411211340771.txt',
                                                   is_datetime=True))
    # open('../data/trainset/shenqi.json', 'w').write(json.dumps(json_comments, ensure_ascii=False))
    # for i in json_comments:
    #     print i
    # sm = cal_similarity_matrix(json_comments,
    #                            output_path='/Users/jayvee/github_project/shcolarship/OpinionRankProject/python/visualization/flask_app/'
    #                                        'static/trainset-taobao-shenqi-0.5-0.3-100-soft.json',
    #                            sim_rate=0.5,
    #                            alpha=0.3)
    sent_node_fea_list = []
    verb_list = []
    noun_list = []
    adj_list = []
    a = {}
    for comm in json_comments:
        comment = comm['comment']
        sent_node = SentenceNode(comment, None)
        sent_node_fea_list.append(sent_node.get_vec())
        verb_list.append(sent_node.verb_rate)
        noun_list.append(sent_node.noun_rate)
        adj_list.append(sent_node.adj_rate)

    # 动词的比例个数分布
    interval_rate = 0.001
    fea_key = 'verb_rate'
    partition = divide_fea_rates(interval_rate, sent_node_fea_list, fea_key)
    plt.bar(range(0, len(partition)), [len(a) for a in partition])
    plt.grid(True)
    plt.title('%s partition, with interval=%s, sent count=%s' % (fea_key, interval_rate, len(sent_node_fea_list)))
    plt.xlabel('divide index')
    plt.ylabel('sentence count')
    # plt.xticks(range(len(partition)),
    #            ['%s~%s' % (i * interval_rate, (i + 1) * interval_rate) for i in xrange(len(partition))])
    plt.show()

    # 名词的比例个数分布
    interval_rate = 0.001
    fea_key = 'noun_rate'
    partition = divide_fea_rates(interval_rate, sent_node_fea_list, fea_key)
    plt.bar(range(0, len(partition)), [len(a) for a in partition])
    plt.grid(True)
    plt.title('%s partition, with interval=%s, sent count=%s' % (fea_key, interval_rate, len(sent_node_fea_list)))
    plt.xlabel('divide index')
    plt.ylabel('sentence count')
    plt.show()

    # 形容词的比例个数分布
    interval_rate = 0.001
    fea_key = 'adj_rate'
    partition = divide_fea_rates(interval_rate, sent_node_fea_list, fea_key)
    plt.bar(range(0, len(partition)), [len(a) for a in partition])
    plt.grid(True)
    plt.title('%s partition, with interval=%s, sent count=%s' % (fea_key, interval_rate, len(sent_node_fea_list)))
    plt.xlabel('divide index')
    plt.ylabel('sentence count')
    plt.show()

    # matplotlib.
    verb_list.sort(cmp=(lambda x, y: -cmp(x, y)))
    # for x in xrange(len(sorted_list)):
    plt.plot(range(0, len(verb_list)), verb_list)
    plt.grid(True)
    plt.title('verb rates curve with sent count=%s' % len(verb_list))
    plt.xlabel('sentence index')
    plt.ylabel('verb rate')
    plt.show()

    noun_list.sort(cmp=(lambda x, y: -cmp(x, y)))
    # for x in xrange(len(sorted_list)):
    plt.plot(range(0, len(noun_list)), noun_list)
    plt.grid(True)
    plt.title('noun rates curve with sent count=%s' % len(noun_list))
    plt.xlabel('sentence index')
    plt.ylabel('noun rate')
    plt.show()

    adj_list.sort(cmp=(lambda x, y: -cmp(x, y)))
    # for x in xrange(len(sorted_list)):
    plt.plot(range(0, len(adj_list)), adj_list)
    plt.grid(True)
    plt.title('adj rates curve with sent count=%s' % len(adj_list))
    plt.xlabel('sentence index')
    plt.ylabel('adj rate')
    plt.show()

    print 'sentence number = %s' % len(adj_list)
