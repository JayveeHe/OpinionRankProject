# coding=utf-8
import jieba
import jieba.analyse
import jieba.posseg as pseg

__author__ = 'jayvee'


def seg_sentence(sent):
    """
    分词
    :param sent:
    :return:
    """
    seg_generator = jieba.cut(sent)
    seg_result = []
    for i in seg_generator:
        seg_result.append(i)
    return seg_result


def get_pos(sent):
    """
    获取句子的词性
    :param sent:
    :return:
    """
    result = []
    for word, flag in pseg.cut(sent):
        result.append((word, flag))
    return result


def get_keywords(sent, topk=None):
    """
    获取句子的关键词及相应的评分
    :param sent:
    :param topk:
    :return:
    """
    seg_count = len(jieba.analyse.extract_tags(sent, withWeight=True, topK=len(sent)))
    if topk:
        tags = jieba.analyse.extract_tags(sent, withWeight=True, topK=topk)
    else:
        tags = jieba.analyse.extract_tags(sent, withWeight=True, topK=len(sent))
    result = []
    for w, freq in tags:
        result.append((w, freq * seg_count))
    return result


def remove_illegal_characters(raw_text):
    # 去除非法字符
    refined_content = ''
    for s in raw_text:
        try:
            s.decode('utf8').encode('gbk')
            refined_content += s
        except UnicodeEncodeError:
            # print '%s encode error, illegal utf8 ch' % s
            pass
        except UnicodeDecodeError:
            # print '%s decode error, illegal utf8 ch' % s
            pass
    return refined_content


if __name__ == '__main__':
    for i in jieba.cut('北京电影学院体育场'):
        print i
        # print seg_sentence(u'好用，非常实惠的商品')
        # for key in get_keywords(u'好用，非常实惠的商品'):
        #     print key[0], key[1]
        # print get_pos(u'好用，非常实惠的商品')
