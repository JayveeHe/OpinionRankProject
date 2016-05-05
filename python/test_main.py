import codecs
from process.amazon_process import amazon_main, train_models

__author__ = 'jayvee'

if __name__ == '__main__':
    # train_models(0, 100)
    errors = []
    x = range(100)
    for i in x:
        error = amazon_main(0, i * 10)
        errors.append(error)
    with open('%s/process/result/rank_errors/rank_errors', 'w') as fout:
        fout.write(codecs.BOM_UTF8)
        for j in x:
            fout.write('%s,%s\n' % (x[j], errors[j]))
            print '%s,%s\n' % (x[j], errors[j])
        print 'done'
