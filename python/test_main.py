import codecs
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

    with open('%s/process/result/rank_errors/rank_errors', 'w') as fout:
        errors = []
        x = range(10)
        fout.write(codecs.BOM_UTF8)
        for i in x:
            try:
                error = amazon_main(0, i * 10, lda_model, rfclf)
                errors.append(error)
                fout.write('%s,%s\n' % (x[i], errors[i]))
                print '%s,%s\n' % (x[i], errors[i])
            except:
                continue
        # for j in x:
        #     fout.write('%s,%s\n' % (x[j], errors[j]))
        #     print '%s,%s\n' % (x[j], errors[j])
        print 'done'
