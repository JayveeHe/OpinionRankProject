# coding=utf-8
from collections import defaultdict
import json
import math
import os
# import seaborn as sns
import sys

projectpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print projectpath
sys.path.append(projectpath)
import matplotlib.pyplot as plt
from utils.dao_utils.mongo_utils import get_db_inst

__author__ = 'jayvee'


def count_item_reviews_dist(category_name='AndroidAPP'):
    meta_db_inst = get_db_inst('AmazonReviews', '%s_Meta' % category_name)
    reviews_db_inst = get_db_inst('AmazonReviews', category_name)
    meta_result = meta_db_inst.find({"vote_reviews_count": {"$exists": 0}})
    print 'total remain = %s' % meta_result.count()
    proc_count = 0
    for item in meta_result:
        asin = item['asin']
        rev_count = reviews_db_inst.find({'asin': asin}).count()
        vote_rev_count = reviews_db_inst.find({'asin': asin, 'total_vote': {'$gt': 0}}).count()
        item['reviews_count'] = rev_count
        item['vote_reviews_count'] = vote_rev_count
        meta_db_inst.update({'asin': asin}, item)
        proc_count += 1
        if proc_count % 1000 == 0:
            print '%s done' % proc_count
    print 'count_item_reviews_dist done'


def count_vote_dist():
    db_inst = get_db_inst('AmazonReviews', 'AndroidAPP')
    delta = 2
    x_list = []
    y_list = []
    log_y_list = []
    log_log_y_list = []
    xx = []
    for i in range(1000):
        x_list.append((i * delta, (i + 1) * delta))
        pass
    for tu in x_list:
        try:
            rev_count = db_inst.find({"total_vote": {"$gt": tu[0], "$lt": tu[1]}}).count()
            if rev_count > 0:
                y_list.append(rev_count)
                log_y_list.append(math.log(max(y_list[-1], 1), 10))
                log_log_y_list.append(math.log(max(log_y_list[-1], 1), 10))
                xx.append(tu[0])
                # print y_list[-1]
        except Exception, e:
            xx.append(tu[0])
            y_list.append(0)
            print 'error: %s' % e
    rest_count = db_inst.find({"total_vote": {"$gt": x_list[-1][1]}}).count()
    print 'rest %s' % rest_count
    y_list.append(rest_count)
    log_y_list.append(math.log(max(y_list[-1], 1), 10))
    log_log_y_list.append(math.log(max(log_y_list[-1], 1), 10))
    # y_list.append(db_inst.find({"total_vote": {"$gt": x_list[-1][1]}}).count())
    xx.append(xx[-1] + delta)
    # res = {"x": x_list, 'y': y_list}
    # open('%s/data/amazon_data/%s' % (PROJECT_PATH, 'vote_counts.json'), 'w').write(json.dumps(res))
    # plt.plot(xx, y_list)
    # plt.grid()
    # plt.show()
    # sbp = plt.subplot(1, 3, 1)
    fig1 = plt.figure('fig1')
    plt.xlabel('total_vote')
    plt.ylabel('nums of reviews')
    plt.plot(xx, y_list, label='nums of reviews')
    # plt.subplot(1, 3, 2)
    fig2 = plt.figure('fig2')
    plt.xlabel('total_vote')
    plt.ylabel('nums of reviews(log)')
    plt.plot(xx, log_y_list, label='nums of reviews(log)')
    plt.title('Reviews-Votes distribution')
    # plt.subplot(1, 3, 3)
    fig3 = plt.figure('fig3')
    plt.xlabel('total_vote')
    plt.ylabel('nums of reviews(log log)')
    plt.plot(xx, log_log_y_list, label='nums of reviews(log log)')
    # sns.distplot(y_list)
    plt.show()


def plot_errors_curves():
    """
    绘制errors的对比图
    :return:
    """
    import pymongo
    import numpy
    db_result = get_db_inst('AmazonReviews', 'AndroidAPP_result')
    find_result = db_result.find({"total_reviews": {"$gt": 0, '$lt': 2000}}).sort('total_reviews', pymongo.ASCENDING)
    xlist = []
    xdict = {}
    oprank_ylist = []
    textrank_ylist = []
    contrast_ylist = []
    log_oprank_ylist = []
    log_textrank_ylist = []
    count = 0
    for item in find_result:
        if xdict.get(item['total_reviews']):
            xdict[item['total_reviews']]['oprank_errors'].append(item['oprank_errors'])
            xdict[item['total_reviews']]['textrank_errors'].append(item['textrank_errors'])
        else:
            xdict[item['total_reviews']] = {'oprank_errors': [item['oprank_errors']],
                                            'textrank_errors': [item['textrank_errors']]}
        count += 1
        if item['total_reviews'] not in xlist:
            xlist.append(item['total_reviews'])
    for x in xlist:
        op_e = numpy.mean(xdict[x]['oprank_errors'])
        t_e = numpy.mean(xdict[x]['textrank_errors'])
        oprank_ylist.append(op_e)
        textrank_ylist.append(t_e)
        # log_oprank_ylist.append(math.log(max(op_e, 0.00000000001)))
        # log_textrank_ylist.append(math.log(max(t_e, 0.00000000001)))
        contrast_ylist.append(100 * (t_e - op_e) / max(t_e, 0.00000000001))

    print count
    print 'mean contrast: %s' % numpy.mean(contrast_ylist)
    # plt.subplot(3, 1, 1)
    # plt.plot(xlist, log_oprank_ylist, label='log_oprank_errors', color='blue', linestyle="-")
    # plt.plot(xlist, log_textrank_ylist, label='log_textrank_errors', color='green', linestyle="-")
    xmax, xmin = max(xlist), min(xlist)
    dx = (xmax - xmin) * 0.1
    fig = plt.figure('contrast fig')
    sb1 = plt.subplot(1, 1, 1)
    plt.xlim(0, xmax + dx)
    plt.xlabel('total_reviews')
    plt.ylabel('rank_errors')
    plt.title('Contrast of Rank Error between OpinionRank and TextRank')
    plt.plot(xlist, oprank_ylist, label='oprank_errors', color='blue', linestyle="-")
    plt.plot(xlist, textrank_ylist, label='textrank_errors', color='green', linestyle="-")
    plt.legend(loc='upper left')

    # plt.subplot(2, 1, 2, sharex=sb1)
    # plt.xlabel('total_reviews')
    # plt.ylabel('rank_error reduction(%)')
    # plt.title('Contrast of Rank Error Reduction between OpinionRank and TextRank')
    # plt.bar(xlist, contrast_ylist, label='textrank_errors', color='green')
    # plt.legend(loc='upper right')

    plt.show()


def plot_rank_error_cdf(category_name='AndroidAPP'):
    """
    绘制errorsCDF的对比图
    :return:
    """
    import pymongo
    import numpy
    db_result = get_db_inst('AmazonReviews', '%s_result_new' % category_name)
    find_result = db_result.find({"total_reviews": {"$gt": 0, '$lt': 2000}}).sort('total_reviews', pymongo.ASCENDING)
    xlist = []
    xdict = {}
    oprank_ylist = []
    textrank_ylist = []
    lexical_rank_ylist = []
    contrast_ylist = []
    contrast_lex_ylist = []
    log_oprank_ylist = []
    log_textrank_ylist = []
    count = 0
    for item in find_result:
        if xdict.get(item['total_reviews']):
            xdict[item['total_reviews']]['oprank_errors'].append(item['oprank_errors'])
            xdict[item['total_reviews']]['textrank_errors'].append(item['textrank_errors'])
            xdict[item['total_reviews']]['lexical_errors'].append(item.get('lexical_errors', 0))
        else:
            xdict[item['total_reviews']] = {'oprank_errors': [item['oprank_errors']],
                                            'textrank_errors': [item['textrank_errors']],
                                            'lexical_errors': [item.get('lexical_errors', 0)]
                                            }
        count += 1
        if item['total_reviews'] not in xlist:
            xlist.append(item['total_reviews'])

    sum_oprank_errors = 0.0
    sum_textrank_errors = 0.0
    sum_lexical_rank_errors = 0.0
    max_sum = 0.0
    print 'calc max sum'
    for x in xlist:
        op_e = numpy.mean(xdict[x]['oprank_errors'])
        t_e = numpy.mean(xdict[x]['textrank_errors'])
        lex_e = numpy.mean(xdict[x].get('lexical_errors', 0))
        max_sum += max(op_e, t_e, lex_e)
    for x in xlist:
        op_e = numpy.mean(xdict[x]['oprank_errors'])
        t_e = numpy.mean(xdict[x]['textrank_errors'])
        lex_e = numpy.mean(xdict[x].get('lexical_errors', 0))
        sum_oprank_errors += op_e
        sum_textrank_errors += t_e
        sum_lexical_rank_errors += lex_e
        # oprank_ylist.append(sum_oprank_errors)
        # textrank_ylist.append(sum_textrank_errors)
        oprank_ylist.append(sum_oprank_errors / max_sum)
        textrank_ylist.append(sum_textrank_errors / max_sum)
        lexical_rank_ylist.append(sum_lexical_rank_errors / max_sum)
        # log_oprank_ylist.append(math.log(max(op_e, 0.00000000001)))
        # log_textrank_ylist.append(math.log(max(t_e, 0.00000000001)))
        contrast_ylist.append(100 * (t_e - op_e) / max(t_e, 0.00000000001))
        contrast_lex_ylist.append(100 * (t_e - lex_e) / max(t_e, 0.00000000001))

    print count
    print 'mean contrast: %s' % numpy.mean(contrast_ylist)
    # plt.subplot(3, 1, 1)
    # plt.plot(xlist, log_oprank_ylist, label='log_oprank_errors', color='blue', linestyle="-")
    # plt.plot(xlist, log_textrank_ylist, label='log_textrank_errors', color='green', linestyle="-")
    xmax, xmin = max(xlist), min(xlist)
    dx = (xmax - xmin) * 0.1
    fig = plt.figure('contrast fig')
    sb1 = plt.subplot(1, 1, 1)
    plt.xlim(0, xmax + dx)
    plt.xlabel('total_reviews', fontsize=16)
    plt.ylabel('rank_errors(CDF)', fontsize=16)
    plt.title('CDF of Rank Error between OpinionRank and TextRank', fontsize=18)
    plt.plot(xlist, oprank_ylist, label='oprank_errors', color='blue', linestyle="-")
    plt.plot(xlist, textrank_ylist, label='textrank_errors', color='green', linestyle="-")
    plt.plot(xlist, lexical_rank_ylist, label='lexical_oprank_errors', color='red', linestyle="-")
    plt.legend(loc='upper left', prop={'size': 18})
    plt.show()
    # '''
    plt.subplot(1, 1, 1, sharex=sb1)
    plt.xlabel('total_reviews', fontsize=16)
    plt.ylabel('rank_error reduction(%)', fontsize=16)
    plt.title('Contrast of Rank Error Reduction between OpinionRank and TextRank', fontsize=18)
    plt.bar(xlist, contrast_ylist, label='reduction_rate', color='green')
    plt.legend(loc='upper right', prop={'size': 18})
    plt.show()
    # '''
    plt.subplot(1, 1, 1, sharex=sb1)
    plt.xlabel('total_reviews', fontsize=16)
    plt.ylabel('rank_error reduction(%)', fontsize=16)
    plt.title('Contrast of Rank Error Reduction between Lexical-OpinionRank and TextRank', fontsize=18)
    plt.bar(xlist, contrast_lex_ylist, label='reduction_rate', color='green')
    plt.legend(loc='upper right', prop={'size': 18})
    plt.show()


def plot_ndcg_cdf(category_name='AndroidAPP'):
    """
    绘制ndcgCDF的对比图
    :return:
    """
    import pymongo
    import numpy
    db_result = get_db_inst('AmazonReviews', '%s_result_ndcg' % category_name)
    find_result = db_result.find({"total_reviews": {"$gt": 0, '$lt': 2000}}).sort('total_reviews', pymongo.ASCENDING)
    xlist = []
    xdict = {}
    oprank_ylist = []
    textrank_ylist = []
    lexical_rank_ylist = []
    contrast_ylist = []
    contrast_lex_ylist = []
    log_oprank_ylist = []
    log_textrank_ylist = []
    count = 0
    for item in find_result:
        if xdict.get(item['total_reviews']):
            xdict[item['total_reviews']]['oprank_ndcg'].append(item['oprank_ndcg'])
            xdict[item['total_reviews']]['textrank_ndcg'].append(item['textrank_ndcg'])
            xdict[item['total_reviews']]['lexical_ndcg'].append(item.get('lexical_ndcg', 0))
        else:
            xdict[item['total_reviews']] = {'oprank_ndcg': [item['oprank_ndcg']],
                                            'textrank_ndcg': [item['textrank_ndcg']],
                                            'lexical_ndcg': [item.get('lexical_ndcg', 0)]
                                            }
        count += 1
        if item['total_reviews'] not in xlist:
            xlist.append(item['total_reviews'])

    sum_oprank_ndcg = 0.0
    sum_textrank_ndcg = 0.0
    sum_lexical_rank_ndcg = 0.0
    max_sum = 0.0
    print 'calc max sum'
    for x in xlist:
        op_e = numpy.mean(xdict[x]['oprank_ndcg'])
        t_e = numpy.mean(xdict[x]['textrank_ndcg'])
        lex_e = numpy.mean(xdict[x].get('lexical_ndcg', 0))
        max_sum += max(op_e, t_e, lex_e)
    for x in xlist:
        op_e = numpy.mean(xdict[x]['oprank_ndcg'])
        t_e = numpy.mean(xdict[x]['textrank_ndcg'])
        lex_e = numpy.mean(xdict[x].get('lexical_ndcg', 0))
        sum_oprank_ndcg += op_e
        sum_textrank_ndcg += t_e
        sum_lexical_rank_ndcg += lex_e
        # oprank_ylist.append(sum_oprank_ndcg)
        # textrank_ylist.append(sum_textrank_ndcg)
        oprank_ylist.append(sum_oprank_ndcg / max_sum)
        textrank_ylist.append(sum_textrank_ndcg / max_sum)
        lexical_rank_ylist.append(sum_lexical_rank_ndcg / max_sum)
        # log_oprank_ylist.append(math.log(max(op_e, 0.00000000001)))
        # log_textrank_ylist.append(math.log(max(t_e, 0.00000000001)))
        contrast_ylist.append(100 * (t_e - op_e) / max(t_e, 0.00000000001))
        contrast_lex_ylist.append(100 * (t_e - lex_e) / max(t_e, 0.00000000001))

    print count
    print 'mean contrast: %s' % numpy.mean(contrast_ylist)
    # plt.subplot(3, 1, 1)
    # plt.plot(xlist, log_oprank_ylist, label='log_oprank_ndcg', color='blue', linestyle="-")
    # plt.plot(xlist, log_textrank_ylist, label='log_textrank_ndcg', color='green', linestyle="-")
    xmax, xmin = max(xlist), min(xlist)
    dx = (xmax - xmin) * 0.1
    fig = plt.figure('contrast fig')
    sb1 = plt.subplot(1, 1, 1)
    plt.xlim(0, xmax + dx)
    fig.set_facecolor('white')
    plt.grid(True)
    plt.xlabel('total_reviews', fontsize=16)
    plt.ylabel('rank_ndcg(CDF)', fontsize=16)
    plt.title('CDF of nDCG between OpinionRank and TextRank', fontsize=18)
    plt.plot(xlist, oprank_ylist, label='oprank_ndcg', color='blue', linestyle="-")
    plt.plot(xlist, textrank_ylist, label='textrank_ndcg', color='green', linestyle="-")
    plt.plot(xlist, lexical_rank_ylist, label='lexical_oprank_ndcg', color='red', linestyle="-")
    plt.legend(loc='lower right', prop={'size': 18})
    plt.show()
    # '''
    plt.subplot(1, 1, 1, sharex=sb1)
    plt.xlabel('total_reviews', fontsize=16)
    plt.ylabel('rank_error reduction(%)', fontsize=16)
    plt.title('Contrast of Rank Error Reduction between OpinionRank and TextRank', fontsize=18)
    plt.bar(xlist, contrast_ylist, label='reduction_rate', color='green')
    plt.legend(loc='upper right', prop={'size': 18})
    plt.show()
    # '''
    plt.subplot(1, 1, 1, sharex=sb1)
    plt.xlabel('total_reviews', fontsize=16)
    plt.ylabel('rank_error reduction(%)', fontsize=16)
    plt.title('Contrast of Rank Error Reduction between Lexical-OpinionRank and TextRank', fontsize=18)
    plt.bar(xlist, contrast_lex_ylist, label='reduction_rate', color='green')
    plt.legend(loc='upper right', prop={'size': 18})
    plt.show()


def handle_amazon_result(fin_path):
    """
    puts amazon oprank and textrank error result into mongoDB
    :param fin_path:
    :return:
    """
    with open(fin_path, 'r') as fin:
        itemlist = []
        for line in fin:
            splits = line.split('\t')
            item_id = splits[0].replace('itemID: ', '')
            total_reviews = eval(splits[1].replace('total reviews: ', ''))
            oprank_errors = eval(splits[2].replace('oprank_errors: ', ''))
            textrank_errors = eval(splits[3].replace('textrank_errors: ', ''))
            sum_oprank_errors = eval(splits[4].replace('sum_oprank_errors: ', ''))
            sum_textrank_errors = eval(splits[5].replace('sum_textrank_errors: ', ''))
            itemlist.append({'item_id': item_id, 'total_reviews': total_reviews, 'oprank_errors': oprank_errors,
                             'textrank_errors': textrank_errors, 'sum_oprank_errors': sum_oprank_errors,
                             'sum_textrank_errors': sum_textrank_errors})
        # sortedlist = sorted(itemlist, cmp=lambda x, y: cmp(x['total_reviews'], y['total_reviews']))
        db_result = get_db_inst('AmazonReviews', 'AndroidAPP_result')
        for item in itemlist:
            db_result.insert({'itemID': item['item_id'], 'total_reviews': item['total_reviews'],
                              'oprank_errors': item['oprank_errors'],
                              'textrank_errors': item['textrank_errors']})
        print 'handled!'


def cal_better_rate(category_name='AndroidAPP', a='oprank_errors', b='textrank_errors'):
    """
    计算opinion rank比textrank好的情况占比
    :return:
    """
    db_result = get_db_inst('AmazonReviews', '%s_result_ndcg' % category_name)
    find_result = db_result.find({"total_reviews": {"$gt": 0, '$lt': 2000}})
    count = find_result.count()
    better_count = 0.0
    for item in find_result:
        if item[a] <= item[b]:
            better_count += 1.0
    print 'better rate: %s (%s/%s)' % ((better_count / count), int(better_count), count)
    return better_count / count


if __name__ == '__main__':
    # count_vote_dist()
    category = 'AndroidAPP'
    cal_better_rate(category_name=category, a='oprank_ndcg', b='lexical_ndcg')
    # count_vote_dist()
    # plot_rank_error_cdf(category_name=category)
    plot_ndcg_cdf(category_name=category)

    # plot_errors_curves()
    # count_item_reviews_dist('VideoGames')
