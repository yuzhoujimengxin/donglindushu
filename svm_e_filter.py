from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.svm import SVC
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import Pipeline
import numpy as np
import svmdata
import pickle
from text_transformer import ChineseTransformer
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

"""
划分训练集与预测集
"""
x_train, x_test, y_train, y_test, num_normal, num_spam = svmdata.data(6, 6, 0.3)

print("正常评论数为:", num_normal)
print("垃圾评论数为：", num_spam)

"""
停用词
"""
stop_words_file = open("stopwords.txt", 'r')
stop_words_content = stop_words_file.read()
stop_words_list = stop_words_content.splitlines()
stop_words_file.close()

"""
SVM
"""
print('*************************\nSVM\n*************************')

# 创建TF-IDF向量化和特征选择模型，实例化模型
tfidf_vect = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
chi2_feature = SelectKBest(chi2)

# 创建一个流水线，包括分词、停词、TF-IDF特征提取，特征选择，SVM训练
pipe = Pipeline([
    ('Trans', ChineseTransformer(stop_words=stop_words_list)),
    ('vect', TfidfVectorizer(token_pattern=r"(?u)\b\w+\b", max_df=0.5)),
    ('chi2', SelectKBest(chi2)),
    ('svm', SVC(kernel='linear', verbose=2))
])

# 定义搜索的参数空间
param_grid = {
    'chi2__k': [1000, 5000, 10000, 20000],  # 需要测试的不同特征数量
    'svm__C': [0.1, 1, 10],  # svm的参数C
}

# 在训练集上进行网格搜索
grid_search = GridSearchCV(pipe, param_grid, cv=5)  # 5折交叉
grid_search.fit(x_train, y_train)

# 打印出最好的参数以及在交叉验证中的得分
print("Best parameters: ", grid_search.best_params_)
print("Best cross-validation score: ", grid_search.best_score_)

# 使用最优参数进行模型的训练
best_model = grid_search.best_estimator_

# 使用训练好的模型进行预测
train_pre = best_model.predict(x_train)
print("Train accuracy: ", np.mean(train_pre == y_train))
print(classification_report(y_train, train_pre))

test_pre = best_model.predict(x_test)
print("Test accuracy: ", np.mean(test_pre == y_test))
print(classification_report(y_test, test_pre))

# 'x_test' 和 'y_test' 是测试集的特征和标签数据
test_pre = best_model.predict(x_test)

# 混淆矩阵
cm = confusion_matrix(y_test, test_pre)

# 绘制混淆矩阵热力图
plt.figure(figsize=(10, 7))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.title('Confusion Matrix')
plt.show()

"""
保存模型
"""
with open('svm_spam_model.pickle', 'wb') as fw:
    pickle.dump(best_model, fw)
