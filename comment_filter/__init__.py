import pickle
from flask import Flask, request, jsonify

from app import app

# 加载模型
with open('../svm_model.pickle', 'rb') as f:
    model = pickle.load(f)


# 创建一个API端点，接收用户的评论数据，利用加载的模型进行预测，并返回结果。
@app.route('/predict', methods=['POST'])
def predict():
    # 获取来自POST请求的数据，只接收json格式的数据
    data = request.get_json(force=True)
    user_review = data['review']

    # 使用模型进行预测
    prediction = model.predict([user_review])

    # 返回预测结果
    return jsonify({'prediction': prediction[0]})


if __name__ == '__main__':
    app.run(port=5000, debug=True)
app = Flask(__name__)
