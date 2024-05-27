# -*- coding: utf-8 -*-
import os
import pickle
import tempfile

from flask import Flask, request, redirect, render_template, url_for, session, jsonify, send_file, after_this_request
import pymysql
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:666666@localhost/comment'  # 使用Mysqlclient驱动进行连接
db = SQLAlchemy(app)


# 定义Comment模型
class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(80), nullable=False)


# # 使用应用程序上下文创建表
# with app.app_context():
#     db.create_all()

# 获取除违规评论以外的数据
@app.route('/comments')
def get_comments():
    comments_list = Comments.query.filter(Comments.content != "您发表了违规评论,请您文明用语!").all()  # 过滤违规评论
    comments = [{'username': c.uname, 'comment': c.content} for c in comments_list]
    return jsonify(comments)


# 获取用户所有评论
@app.route('/comment_all')
def get_comment_all():
    # 从查询参数中获取email
    email = request.args.get('email')
    if email:
        comment_all_list = Comments.query.filter(Comments.email == email).all()  # 获取用户所有评论
        comment_all = [{'ID': c.id, 'username': c.uname, 'comment': c.content} for c in comment_all_list]
        return jsonify(comment_all)
    else:
        return jsonify({"error": "Email is required"}), 400


# 获取管理员需要的数据
@app.route('/comment_admin')
def get_comment_admin():
    comment_admin_list = Comments.query.filter(Comments.content != "您发表了违规评论,请您文明用语!").all()  # 过滤违规评论
    comment_admin = [{'ID': c.id, 'username': c.uname, 'comment': c.content} for c in comment_admin_list]
    return jsonify(comment_admin)


# 用户删除历史评论接口，使用评论id来定位要删除的评论
@app.route('/delete/<int:comment_id>', methods=['DELETE'])
def delete(comment_id):
    comment_to_delete = Comments.query.get_or_404(comment_id)
    # 从数据库删除相应ID的评论
    db.session.delete(comment_to_delete)
    db.session.commit()
    return jsonify({'message': 'Comment deleted successfully'}), 200


# 管理员删除评论接口，使用评论id来定位要删除的评论
@app.route('/delete_comment/<int:comment_id>', methods=['PUT'])
def delete_comment(comment_id):
    comment_to_delete = Comments.query.get_or_404(comment_id)
    # 设置评论内容为“此评论已被管理员隐藏”
    comment_to_delete.content = "您发表了违规评论,请您文明用语!"
    db.session.commit()
    return jsonify({'message': 'Comment content updated successfully'}), 200


app.secret_key = '666666'  # 设置一个密钥用于加密 session 数据
model = None  # 定义一个全局变量用于存放加载的模型


# 在应用启动时加载模型
def load_models():
    global model, model_e
    # 加载model垃圾过滤模型
    try:
        with open('svm_spam_model.pickle', 'rb') as f:
            model = pickle.load(f)
        print("Model loaded successfully.")
    except FileNotFoundError:
        print("Model file not found!")
        model = None
    except Exception as e:
        print(f"An error occurred: {e}")
        model = None

    # 加载model_e，情感过滤模型
    try:
        with open('svm_model.pickle', 'rb') as f:
            model_e = pickle.load(f)
        print("Model E loaded successfully.")
    except FileNotFoundError:
        print("Model E file not found!")
        model_e = None
    except Exception as e:
        print(f"An error occurred while loading the second model: {e}")
        model_e = None


@app.route('/')
def first():
    return render_template('login.html')


# 用户注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")

    data = request.get_json()

    username = data["username"]
    password = data["password"]
    email = data["email"]
    print(username, password, email)

    # 连接数据库
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='666666', charset='utf8',
                           db='comment')
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

    try:
        # 查找邮箱，看是否已经注册
        sql_exam = "SELECT * FROM users WHERE email = %s"
        cursor.execute(sql_exam, [email])
        if cursor.fetchone():  # 如果查询到结果，说明邮箱已注册
            return jsonify({"isSuccess": False}), 409

        # 插入新用户
        sql = "INSERT INTO users(username, password, email) VALUES (%s, %s, %s)"
        cursor.execute(sql, [username, password, email])
        conn.commit()
        return jsonify({"isSuccess": True}), 200  # 注册成功

    except Exception as e:
        return jsonify({"isSuccess": False, "message": str(e)}), 500  # 返回错误信息
    finally:
        # 关闭连接
        cursor.close()
        conn.close()


# 用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    data = request.get_json()

    username = data["username"]
    password = data["password"]
    email = data["email"]

    conn = pymysql.connect(host='localhost', port=3306, user='root', password='666666', charset='utf8', db='comment')
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

    try:
        # 检查用户数据表中是否存在用户
        sql = "select * from users"
        cursor.execute(sql)
        user_list = cursor.fetchall()
        for user in user_list:
            if username == user.get('username') and password == user.get('password') and email == user.get(
                    'email'):  # 登录成功
                # 将用户信息存储在 session 中
                session["username"] = username
                session["email"] = email

                # 检查是否管理员账号
                if email == "15776876880@163.com":
                    # 是管理员则让is_admin为true
                    session["is_admin"] = True
                    return jsonify({"isSuccess": True, "redirect_url": "/index"}), 200
                # 不是管理员则设置is_admin为False
                session["is_admin"] = False
                return jsonify({"isSuccess": True, "redirect_url": "/index"}), 200

    except Exception as e:
        return jsonify({"isSuccess": False, "message": str(e)}), 500  # 返回错误信息
    finally:
        # 关闭连接
        cursor.close()
        conn.close()


# index主页
@app.route('/index')
def index():
    if 'username' in session:
        # 用户已登录，获取session中的信息
        username = session.get('username')
        email = session.get('email')
        is_admin = session.get('is_admin', False)  # 默认情况下，当键不存在时返回False
        # 在渲染的模板中包含用户信息和管理员标志
        return render_template('index.html', username=username, email=email, is_admin=is_admin)
    else:
        # 用户没有登录，重定向到登录页面
        return redirect(url_for('login'))


# 查看用户历史评论
@app.route('/user_comment')
def user_comment():
    if 'username' in session:
        # 用户已登录，获取session中的信息
        username = session.get('username')
        email = session.get('email')
        is_admin = session.get('is_admin', False)  # 默认情况下，当键不存在时返回False
        # 在渲染的模板中包含用户信息和管理员标志
        return render_template('user_comment.html', username=username, email=email, is_admin=is_admin)
    else:
        # 用户没有登录，重定向到登录页面
        return redirect(url_for('login'))


# 管理员评论管理
@app.route('/admin_comment')
def admin_comment():
    if 'is_admin' in session:
        # 管理员已登录，获取session中的信息
        username = session.get('username')
        email = session.get('email')
        is_admin = session.get('is_admin', False)  # 默认情况下，当键不存在时返回False
        # 在渲染的模板中包含用户信息和管理员标志
        return render_template('admin_comment.html', username=username, email=email, is_admin=is_admin)
    else:
        # 用户没有登录，重定向到登录页面
        return redirect(url_for('login'))


# 书籍主页
@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'GET':
        if 'username' in session:
            # 用户已登录，获取session中的信息
            username = session.get('username')
            email = session.get('email')
            is_admin = session.get('is_admin', False)  # 默认情况下，当键不存在时返回False
            # 在渲染的模板中包含用户信息和管理员标志
            return render_template("book.html", username=username, email=email, is_admin=is_admin)
        else:
            # 用户没有登录，重定向到登录页面
            return redirect(url_for('login'))

    # 获取用户名和评论内容
    comment = request.form.get('comment')
    username = session.get('username')
    email = session.get('email')
    is_admin = session.get('is_admin', False)

    # 连接数据库
    conn = pymysql.connect(host='localhost', port=3306, user='root', password='666666', charset='utf8', db='comment')
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

    # 调用训练好的模型进行预测
    content = [comment]
    predictions = model.predict(content)
    print(predictions)
    if predictions[0] == 0:  # 违规评论
        comment = "您发表了违规评论,请您文明用语!"
    # 将评论内容存入数据库
    sql = "insert into comments(uname, content,email) values('%s', '%s','%s')" % (username, comment, email)
    cursor.execute(sql)
    conn.commit()

    # 关闭连接
    cursor.close()
    conn.close()

    return render_template('book.html', username=username, email=email, is_admin=is_admin)


# 管理员文件上传预测接口
@app.route("/file_load")
def file_load():
    if request.method == 'GET':
        if 'username' in session:
            # 用户已登录，获取session中的信息
            username = session.get('username')
            email = session.get('email')
            is_admin = session.get('is_admin', False)  # 默认情况下，当键不存在时返回False
            # 在渲染的模板中包含用户信息和管理员标志
            return render_template("file_load.html", username=username, email=email, is_admin=is_admin)
        else:
            # 用户没有登录，重定向到登录页面
            return redirect(url_for('login'))


# 处理文件,将文件读取为文本列表并进行预测,将预测后的结果添加到列表元素中的开头,并将处理后的文本列表返回
def predict_model(file_path):
    lines = []
    predictions = []
    # 打开文件读取内容
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 并将每行作为独立的样本送入模型进行预测
    processed_lines = [line.strip() for line in lines]

    # 调用模型的predict()方法进行预测
    predictions = model_e.predict(processed_lines)

    # 将预测结果添加到每一行文本的开头
    labeled_lines = [f'{pred}\t{line}' for pred, line in zip(predictions, lines)]
    # 返回处理后的文本列表
    return labeled_lines


@app.route('/predict_file', methods=['POST'])
def predict_file():
    if 'file' not in request.files:
        return '没有文件部分', 400
    file = request.files['file']

    if file.filename == '':
        return '没有选择文件', 400
    if file:
        file_path = os.path.join(tempfile.gettempdir(), file.filename)
        file.save(file_path)

        # 确保之后删除传入文件
        @after_this_request
        def cleanup(response):
            try:
                os.unlink(file_path)
            except Exception as e:
                app.logger.error(f"Error removing input file: {e}")
            return response

        try:
            # 调用predict_model执行文件预测
            prediction_lines = predict_model(file_path)

            # 将带标签的文本列表保存到临时文件
            save_file_path = os.path.join(tempfile.gettempdir(), 'labeled_' + file.filename)
            with open(save_file_path, 'w', encoding='utf-8') as f:
                for line in prediction_lines:
                    f.write(line)

            # 传送文件给用户
            @after_this_request
            def cleanup_save_file(response):
                try:
                    os.unlink(save_file_path)
                except Exception as e:
                    app.logger.error(f"Error removing labeled file: {e}")
                return response

            return send_file(save_file_path, as_attachment=True, download_name='labeled_' + file.filename)

        except Exception as e:
            return str(e), 500

    return '文件上传异常', 500


# 将模型加载与应用启动绑定在一起
if __name__ == "__main__":
    load_models()
    if model and model_e is not None:
        app.run(debug=True)
    else:
        print("Failed to load the model. Application will not start.")
