import re
import jieba
from sklearn.base import BaseEstimator, TransformerMixin


class ChineseTransformer(BaseEstimator, TransformerMixin):
    # ... 省略其他方法 ...
    def __init__(self, stop_words=None):
        self.stop_words = stop_words if stop_words is not None else []

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        processed_texts = []
        for text in X:
            # 过滤数字、非字母数字字符和下划线
            text = re.sub(r"(?!\n)(\d|\W|_)", " ", text)
            # 进行分词
            words = jieba.cut(text)
            # 进行停词
            if self.stop_words:
                words = [word for word in words if word not in self.stop_words]
            processed_texts.append(' '.join(words))
        return processed_texts

    # 读取文件内容并对文件内文本进行数据预处理，将处理后的数据用空格连接为字符串，保存在文本列表里，文件中每一行作为列表的一个元素
    def transform_file(self, old_file, y=None):
        processed_texts = []
        try:
            with open(old_file, 'r', encoding='utf-8') as fi:
                r_texts = fi.readlines()  # 读取所有行
        except IOError as e:  # IOError用于文件相关的错误捕获
            print("IOError:", e)
            return []  # 发生错误时返回空列表

        for text in r_texts:
            # 过滤数字、非字母数字字符和下划线
            text = re.sub(r"(?!\n)(\d|\W|_)", " ", text)
            # 进行分词
            words = jieba.cut(text)
            # 进行停词
            if self.stop_words:
                words = [word for word in words if word not in self.stop_words]
            processed_texts.append(' '.join(words))
        return processed_texts


# 测试代码
if __name__ == '__main__':
    # 创建一个实例
    transformer = ChineseTransformer(stop_words=['的', '了', '和'])

    # 验证transform方法
    sample_texts = ['这是第一个测试文本。', '这是第二个测试文本！']
    transformed = transformer.transform(sample_texts)
    print(transformed)

    # 验证transform_file方法
    transformed_file = transformer.transform_file('spam/2.txt')  # 将'path_to_your_file.txt'替换为您的文件路径
    with open('comment_filter/_spam/spam1.txt', 'w', encoding='utf-8') as fi:
        for line in transformed_file:
            # 在文件中每行文本后加入换行符
            fi.write(f"{line}\n")
        print("成功了！")
