
import os
from sklearn.model_selection import train_test_split


# ��ȡ�������ݺ���
def singleData(num, name, data):
    # ��ȡ�ļ������ļ��б�
    files = os.listdir(name)
    # �����ȡ���ļ�������0�����ȡָ���������ļ�
    if num > 0:
        files = files[:num]
        # �����ļ�
    for file in files:
        # ʹ�� with open ���ļ�����֤��ȡ�������Զ��ر��ļ�
        with open(os.path.join(name, file), 'r', encoding='utf-8') as fi:
            # ʹ�� ' '.join �� split ���ļ����ݰ��ո�ָ������һ���б�
            lines = ' '.join(fi.readlines()).split()
            # �����ļ���������ӵ������б���
            data.extend(lines)


# ��ȡ�������ݺ���
def allData(num1, num2):
    # �����յ������б�
    data = []
    # ��ȡ���������ļ�������
    singleData(num1, 'emotion_n', data)
    # �����������ݵ�����
    num_normal = len(data)
    # ��ȡ���������ļ�������
    singleData(num2, 'emotion_s', data)
    # �����������ݵ�����
    num_spam = len(data) - num_normal
    # �����������ݼ����ݶ�Ӧ������
    return data, num_normal, num_spam


# ���ݻ��ֺ���
def data(normaldoc, spamdoc, ratio):
    # ��ȡ�������ݼ����ݵ�����
    x, num_normal, num_spam = allData(normaldoc, spamdoc)
    # ������ǩ�б��������ݱ��Ϊ1���������ݱ��Ϊ0
    y = [1] * num_normal + [0] * num_spam
    # ����ѵ�����Ͳ��Լ�
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=ratio)

    # ����ѵ���������Լ��͸�������ݵ�����
    return x_train, x_test, y_train, y_test, num_normal, num_spam
