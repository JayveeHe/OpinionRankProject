from collections import defaultdict
import json
import math
import seaborn as sns
import matplotlib.pyplot as plt
from utils.CommonUtils import PROJECT_PATH
from utils.dao_utils.mongo_utils import get_db_inst

__author__ = 'jayvee'


def count_item_reviews_dist():
    meta_db_inst = get_db_inst('AmazonReviews', 'AndroidAPP_Meta')
    reviews_db_inst = get_db_inst('AmazonReviews', 'AndroidAPP')
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
    xx = []
    for i in range(1000):
        x_list.append((i * delta, (i + 1) * delta))
        pass
    for tu in x_list:
        try:
            # y_list.append(math.log(db_inst.find({"total_vote": {"$gt": tu[0], "$lt": tu[1]}}).count(), 10))
            y_list.append(db_inst.find({"total_vote": {"$gte": tu[0], "$lt": tu[1]}}).count())

            xx.append(tu[0])
            print y_list[-1]
        except:
            xx.append(tu[0])
            y_list.append(0)
    # y_list.append(math.log(db_inst.find({"total_vote": {"$gt": x_list[-1][1]}}).count(), 10))
    y_list.append(db_inst.find({"total_vote": {"$gt": x_list[-1][1]}}).count())
    xx.append(xx[-1] + 1)
    res = {"x": x_list, 'y': y_list}
    open('%s/data/amazon_data/%s' % (PROJECT_PATH, 'vote_counts.json'), 'w').write(json.dumps(res))
    # plt.plot(xx, y_list)
    # plt.grid()
    # plt.show()
    sns.distplot(y_list)
    plt.show()


def plot_errors_curves():
    import pymongo
    import numpy
    db_result = get_db_inst('AmazonReviews', 'AndroidAPP_result')
    find_result = db_result.find({"total_reviews": {"$gt": 0}}).sort('total_reviews', pymongo.ASCENDING)
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
    sb1 = plt.subplot(2, 1, 1)
    plt.xlabel('total_reviews')
    plt.ylabel('rank_errors')
    plt.title('Contrast of Rank Error between OpinionRank and TextRank')
    plt.plot(xlist, oprank_ylist, label='oprank_errors', color='blue', linestyle="-")
    plt.plot(xlist, textrank_ylist, label='textrank_errors', color='green', linestyle="-")
    plt.subplot(2, 1, 2, sharex=sb1)
    plt.xlabel('total_reviews')
    plt.ylabel('rank_error reduction(%)')
    plt.title('Contrast of Rank Error Reduction between OpinionRank and TextRank')
    plt.bar(xlist, contrast_ylist, label='textrank_errors', color='green')

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


if __name__ == '__main__':
    # count_vote_dist()
    plot_errors_curves()
    # count_item_reviews_dist()
