# 导入所需库
import os
from sklearn.model_selection import train_test_split


# 读取单类数据函数
def singleData(num, name, data):
    # 获取文件夹下文件列表
    files = os.listdir(name)
    # 如果读取的文件数大于0，则读取指定数量的文件
    if num > 0:
        files = files[:num]
        # 遍历文件
    for file in files:
        # 使用 with open 打开文件，保证读取结束后自动关闭文件
        with open(os.path.join(name, file), 'r', encoding='utf-8') as fi:
            # 使用 ' '.join 和 split 将文件内容按空格分隔并组成一个列表
            lines = ' '.join(fi.readlines()).split()
            # 将该文件的内容添加到数据列表中
            data.extend(lines)


# 读取所有数据函数
def allData(num1, num2):
    # 创建空的数据列表
    data = []
    # 读取正常数据文件的内容
    singleData(num1, 'normal', data)
    # 计算正常数据的数量
    num_normal = len(data)
    # 读取垃圾数据文件的内容
    singleData(num2, 'spam', data)
    # 计算垃圾数据的数量
    num_spam = len(data) - num_normal
    # 返回所有数据及数据对应的数量
    return data, num_normal, num_spam


# 数据划分函数
def data(normaldoc, spamdoc, ratio):
    # 获取所有数据及数据的数量
    x, num_normal, num_spam = allData(normaldoc, spamdoc)
    # 创建标签列表，正常数据标记为1，垃圾数据标记为0
    y = [1] * num_normal + [0] * num_spam
    # 划分训练集和测试集
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=ratio)

    # 返回训练集、测试集和各类别数据的数量
    return x_train, x_test, y_train, y_test, num_normal, num_spam
