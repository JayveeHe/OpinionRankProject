import codecs
import arrow
from process.amazon_process import amazon_main, train_models
import pickle
from utils.CommonUtils import PROJECT_PATH

__author__ = 'jayvee'

if __name__ == '__main__':
    # train_models(0, 100)
    mfile = open('%s/process/models/lda_model_100t.mod' % PROJECT_PATH, 'r')
    lda_model = pickle.load(mfile)
    # mfile = open('nb_model.mod', 'r')
    # nbclf = pickle.load(mfile)
    mfile = open('%s/process/models/rf_model_100t.mod' % PROJECT_PATH, 'r')
    rfclf = pickle.load(mfile)
    ttt = arrow.utcnow().timestamp
    save_label = 'amazon'
    # with open('%s/process/result/%s-%s-rf_lda_feature_as_words_lda.csv' % (PROJECT_PATH, ttt, save_label), 'w')
    with open('%s/process/result/rank_errors/rank_errors' % PROJECT_PATH, 'w') as fout, \
            open('%s/process/result/%s-%s-rf_lda_feature_as_words_lda.csv' % (PROJECT_PATH, ttt, save_label),
                 'w') as csvout:
        errors = []
        x = range(10)
        fout.write(codecs.BOM_UTF8)
        csvout.write(codecs.BOM_UTF8)
        for i in x:
            try:
                sum_oprank_errors, sum_textrank_errors, info_list, raw_list = amazon_main(0, i * 10, lda_model, rfclf)
                # errors.append(error)
                for info in info_list:
                    fout.write(info + '\n')
                for raw in raw_list:
                    csvout.write(raw + '\n')
                    # print '%s,%s\n' % (x[i], errors[i])
            except:
                continue
        # for j in x:
        #     fout.write('%s,%s\n' % (x[j], errors[j]))
        #     print '%s,%s\n' % (x[j], errors[j])
        print 'done'
