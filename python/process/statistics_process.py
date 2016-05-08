import json
import math
import seaborn as sns
import matplotlib.pyplot as plt
from utils.CommonUtils import PROJECT_PATH
from utils.dao_utils.mongo_utils import get_db_inst

__author__ = 'jayvee'


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


def handle_amazon_result(fin_path):
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
    count_vote_dist()
