import codecs
import json
import random
import arrow
from process.amazon_process import amazon_main, train_models, amazon_preproc_by_asin
import pickle
from process.statistics_process import handle_amazon_result
from utils.CommonUtils import PROJECT_PATH

__author__ = 'jayvee'


def handle_result_main():
    for i in range(50):
        handle_amazon_result('%s/process/result/rank_errors/'
                             '2016-05-06T16:26:42.595089+00:00-amazon-rank_errors-%s' % (
                                 PROJECT_PATH, i))


def handle_amazon_main():
    # train_models(0, 100)
    mfile = open('%s/process/models/lda_model_100t.mod' % PROJECT_PATH, 'r')
    lda_model = pickle.load(mfile)
    mfile = open('%s/process/models/rf_model_100t.mod' % PROJECT_PATH, 'r')
    rfclf = pickle.load(mfile)
    ttt = arrow.utcnow()
    save_label = 'amazon'
    errors = []
    x = range(50)
    for i in x:
        try:
            fout = open('%s/process/result/rank_errors/%s-%s-rank_errors-%s' % (PROJECT_PATH, ttt, save_label, i),
                        'w')
            csvout = open(
                '%s/process/result/%s-%s-rawlist-%s.csv' % (PROJECT_PATH, ttt, save_label, i),
                'w')
            fout.write(codecs.BOM_UTF8)
            csvout.write(codecs.BOM_UTF8)
            # sum_oprank_errors, sum_textrank_errors, info_list, raw_list = amazon_main(0, 100, lda_model, rfclf)
            for info, raw_list in amazon_main(0, 100, lda_model, rfclf):
                fout.write('%s\n' % info)
                for raw in raw_list:
                    csvout.write(json.dumps(raw) + '\n')
            print 'loop %s done' % i
        except Exception, e:
            print e
            continue
    # for j in x:
    #     fout.write('%s,%s\n' % (x[j], errors[j]))
    #     print '%s,%s\n' % (x[j], errors[j])
    print 'done'


def handle_amazon_by_review_range(low, high, limit=None, category_name='AndroidAPP'):
    from utils.dao_utils.mongo_utils import get_db_inst
    print 'loading models'
    mfile = open('%s/process/models/lda_model_100t.mod' % PROJECT_PATH, 'r')
    lda_model = pickle.load(mfile)
    mfile = open('%s/process/models/rf_model.mod' % PROJECT_PATH, 'r')
    rfclf = pickle.load(mfile)
    mfile = open('%s/process/models/lexical_rf_model.mod' % PROJECT_PATH, 'r')
    lexical_rfclf = pickle.load(mfile)
    # ttt = arrow.utcnow()
    # save_label = 'amazon'
    print 'finding reviews records'
    meta_db_inst = get_db_inst('AmazonReviews', '%s_Meta' % category_name)
    db_result = get_db_inst('AmazonReviews', '%s_result_new' % category_name)
    meta_result = meta_db_inst.find({"vote_reviews_count": {"$gte": low, "$lte": high}}, {"asin": 1})
    count = 0
    ttt = arrow.utcnow()
    save_label = 'amazon'
    csvout = open(
        '%s/process/result/%s-%s-rawlist-%s.csv' % (PROJECT_PATH, ttt, save_label, 0),
        'w')
    csvout.write(codecs.BOM_UTF8)
    asin_list = []
    for res in meta_result:
        asin_list.append(res['asin'])
    print 'original result: %s' % len(asin_list)
    random.shuffle(asin_list)  # ensure random
    if limit:
        limit = min(limit, len(asin_list))  # maybe not necessary
        asin_list = asin_list[:limit]
    print 'start analyzing'
    for asin in asin_list:
        info, raw_list = amazon_preproc_by_asin(asin, rfclf=rfclf, lda_model=lda_model, lexical_rfclf=lexical_rfclf,category_name='VideoGames')
        if raw_list is None or info is None:
            continue
        for raw in raw_list:
            csvout.write(json.dumps(raw) + '\n')
        splits = info.split('\t')
        item_id = splits[0].replace('itemID: ', '')
        total_reviews = eval(splits[1].replace('total reviews: ', ''))
        oprank_errors = eval(splits[2].replace('oprank_errors: ', ''))
        lexical_errors = eval(splits[3].replace('lexical_errors: ', ''))
        textrank_errors = eval(splits[4].replace('textrank_errors: ', ''))
        sum_oprank_errors = eval(splits[5].replace('sum_oprank_errors: ', ''))
        sum_lexical_errors = eval(splits[6].replace('sum_lexical_errors: ', ''))
        sum_textrank_errors = eval(splits[7].replace('sum_textrank_errors: ', ''))
        item = {'item_id': item_id, 'total_reviews': total_reviews, 'oprank_errors': oprank_errors,
                'textrank_errors': textrank_errors, 'sum_oprank_errors': sum_oprank_errors,
                'sum_textrank_errors': sum_textrank_errors}
        db_result.insert({'itemID': item['item_id'], 'total_reviews': item['total_reviews'],
                          'oprank_errors': item['oprank_errors'],
                          'textrank_errors': item['textrank_errors'], 'lexical_errors': lexical_errors})
        count += 1
    print 'handle %s docs' % count


if __name__ == '__main__':
    handle_amazon_by_review_range(10,150, category_name='VideoGames', limit=50)
    # handle_result_main()
