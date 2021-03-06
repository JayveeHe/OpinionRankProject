import codecs
import json
import arrow
from process.amazon_process import amazon_main, train_models
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
    # with open('%s/process/result/%s-%s-rf_lda_feature_as_words_lda.csv' % (PROJECT_PATH, ttt, save_label), 'w')
    # with open('%s/process/result/rank_errors/%s-%s-rank_errors' % (PROJECT_PATH, ttt, save_label), 'w') as fout, \
    #         open('%s/process/result/%s-%s-rf_lda_feature_as_words_lda.csv' % (PROJECT_PATH, ttt, save_label),
    #              'w') as csvout:
    #     errors = []
    #     x = range(10)
    #     fout.write(codecs.BOM_UTF8)
    #     csvout.write(codecs.BOM_UTF8)
    #     for i in x:
    #         try:
    #             sum_oprank_errors, sum_textrank_errors, info_list, raw_list = amazon_main(0, i * 10, lda_model, rfclf)
    #             # errors.append(error)
    #             for info in info_list:
    #                 fout.write('%s\tsum_oprank_errors: %s\tsum_textrank_errors: %s\n' % (
    #                     info, sum_oprank_errors, sum_textrank_errors))
    #             for raw in raw_list:
    #                 csvout.write(json.dumps(raw) + '\n')
    #                 # print '%s,%s\n' % (x[i], errors[i])
    #         except Exception, e:
    #             print e
    #             continue
    #     # for j in x:
    #     #     fout.write('%s,%s\n' % (x[j], errors[j]))
    #     #     print '%s,%s\n' % (x[j], errors[j])
    #     print 'done'
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
                    # errors.append(error)
                    # for info in info_list:
                    #     fout.write('%s\n' % info)
                    # for raw in raw_list:
                    #     csvout.write(json.dumps(raw) + '\n')
                    # print '%s,%s\n' % (x[i], errors[i])
            print 'loop %s done' % i
        except Exception, e:
            print e
            continue
    # for j in x:
    #     fout.write('%s,%s\n' % (x[j], errors[j]))
    #     print '%s,%s\n' % (x[j], errors[j])
    print 'done'


if __name__ == '__main__':
    handle_result_main()
