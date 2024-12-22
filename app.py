from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from argon2 import PasswordHasher

# 1.创建Flask应用实例------------------------------------
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 设置密钥，用于加密 session

# 2.SQLite----------------------------------------------
# 连接 SQLite
def conn_db():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row  # 允许以字典的方式访问查询结果
    print("数据库连接成功！")
    return conn

# 3.创建用户表（如果表不存在）
def create_table():
    conn = conn_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    close_db(conn, cursor)


# 断开 SQLite
def close_db(conn, cursor):
    cursor.close()
    conn.close()

# 初始主页-------------------------------------------
@app.route('/')
def home():
    return render_template('index.html')

# 注册-----------------------------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    # 直接进入注册页面，否则会执行下面的逻辑验证
    if request.method == 'GET':
        return render_template('register.html')
    
    # 从前端获取用户输入
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirmPassword')

    # 初始化注册错误信息
    register_error = None

    try:  # 使用 try...except...finally 进行异常处理

        # 连接 SQLite 和 创建游标
        conn = conn_db()
        cursor = conn.cursor()
        
        # 从数据库获取用户名
        sql = "SELECT * FROM users WHERE username = ?"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()

        # 检查用户名是否存在
        if user:
            register_error = "用户名已存在！"
        
        # 检查密码是否匹配
        elif password != confirm_password:
            register_error = "两次密码不匹配！"
        
        # 存储数据
        elif not register_error:
            # 对密码加密
            ph = PasswordHasher()
            hashed_password = ph.hash(password)

            # 创建新用户
            sql = "INSERT INTO users (username, password) VALUES (?, ?)"
            cursor.execute(sql, (username, hashed_password))
            conn.commit()

        # 如果有错误，渲染 register.html 并传递注册错误信息
        if register_error:
            return render_template('register.html', register_error=register_error)
        
        # 注册成功，在当前页面渲染 login.html
        return render_template('login.html', register_success="注册成功，请登录！")
        
    except sqlite3.Error as e:
        return f"注册出现数据库错误: {str(e)}"
    finally:
        close_db(conn, cursor)

# 登录-------------------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    # 直接进入登录页面，否则会执行下面的逻辑验证
    if request.method == 'GET':
        return render_template('login.html')

    # 从前端获取用户输入
    username = request.form.get('username')
    password = request.form.get('password')

    # 初始化登录错误信息
    login_error = None

    try:  # 使用 try...except...finally 进行异常处理
        
        # 连接 SQLite 和 创建游标
        conn = conn_db()
        cursor = conn.cursor()
        
        # 从数据库获取用户名
        sql = "SELECT * FROM users WHERE username = ?"
        cursor.execute(sql, (username,))
        user = cursor.fetchone()

        # 检查用户名是否存在
        if not user:
            login_error = "用户名不存在！"
        
        # 验证密码是否正确
        else:
            try:
                ph = PasswordHasher()
                ph.verify(user['password'], password)  # 使用 argon2 验证密码
            except:
                login_error = "密码错误！"

        # 如果有错误，渲染 login.html 并传递登录错误信息
        if login_error:
            return render_template('login.html', login_error=login_error)

        # 登录成功，保存用户名到 session
        session['username'] = username
        # 登录成功，重定向到首页
        return redirect(url_for('home'))

    except sqlite3.Error as e:
        return f"数据库错误: {str(e)}", 500
    finally:
        close_db(conn, cursor)

# 判断登录
@app.route('/user-profile')
def user_profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('user-profile.html', username=session['username'])

# 退出登录
@app.route('/logout')
def logout():
    session.clear()  # 清除会话数据
    return redirect(url_for('home'))

# 主程序---------------------------------------------------
if __name__ == '__main__':
    create_table()
    app.run(debug=True)
