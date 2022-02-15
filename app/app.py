import sqlite3
import os
from flask import Flask, abort, redirect, render_template, request, g, flash, session, url_for, make_response
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from UserLogin import UserLogin
from forms import LoginForm, RegisterForm
from admin.admin import admin

#конфигурация
DATABASE = "/tmp/flsite.db"	
DEBUG = True	
SECRET_KEY = 'secretkey'
MAX_CONTENT_LENGTH = 1024*1024	#максимальный объем в байтах (1мб)

app = Flask(__name__)
app.config.from_object(__name__) #загружаем конфигурацию из приложения
#переопределим путь к бд
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

app.register_blueprint(admin, url_prefix='/admin')

login_manager = LoginManager(app)	#для авторизации
login_manager.login_view = 'login'	#этот обработчик будет вызываться, если неавторизованный пользоваттель посетил страницу
login_manager.login_message = "Авторизируйтесь для доступа к закрытым страницам"	#текст что будет показан
login_manager.login_message_category = "success"	#категория этого мгновенного сообщения

#декоратор
@login_manager.user_loader
def load_user(user_id):
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)

#общая функция для установаления соединения с базой данных
def connect_db():
	conn = sqlite3.connect(app.config['DATABASE'])
	conn.row_factory = sqlite3.Row
	return conn

#фунция, которая будет создавать бд без запуска веб сервера
def create_db():
	db = connect_db()
	with app.open_resource('sq_db.sql', mode='r') as f:
		db.cursor().executescript(f.read())
	db.commit()
	db.close()

#установление соединения
def get_db():
    #Соединение с БД, если оно еще не установлено
	if not hasattr(g, 'link_db'):
		g.link_db = connect_db()
	return g.link_db

#Перехват запросов (повторный код) декоратор
dbase = None
@app.before_request
def before_request():
	"""Установление соединения с БД перед выполнением запроса"""
	global dbase	#говорит, что будем обращаться к глобальной переменной (которая объявлена выше)
	db = get_db()	#установить соединение с бд
	dbase = FDataBase(db)	#FDataBase - класс, описанный в отдельном файле

#разрыв соединения
@app.teardown_appcontext
def close_db(error):
    #Закрываем соединение с БД, если оно было установлено
    if hasattr(g, 'link_db'):
        g.link_db.close()

@app.route("/")
def index():
	return render_template('index.html', menu=dbase.getMenu(), posts=dbase.getPostsAnonce())

#Обработчик добавления постов
@app.route("/add_post", methods=["POST", "GET"])
def addPost():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post']) > 10:
            res = dbase.addPost(request.form['name'], request.form['post'], request.form['url'])
            if not res:
                flash('Ошибка добавления статьи', category = 'error')
            else:
                flash('Статья добавлена успешно', category='success')
        else:
            flash('Ошибка добавления статьи', category='error')
 
    return render_template('add_post.html', menu = dbase.getMenu(), title="Добавление статьи")

#Обработчик отображения статьи
@app.route("/post/<alias>")
@login_required		#доступ к статьям только авторизированным польователям
def showPost(alias):
    title, post = dbase.getPost(alias)		#берем статью из бд
    if not title: 
        abort(404) 
    return render_template('post.html', menu=dbase.getMenu(), title=title, post=post)

#Обработчик авторизации польователя
@app.route("/login", methods=["POST", "GET"])
def login():
	if current_user.is_authenticated:	#если уже авторизован
		return redirect(url_for('profile'))

	form = LoginForm()
	if form.validate_on_submit():
		user = dbase.getUserByEmail(form.email.data)
		if user and check_password_hash(user['psw'], form.psw.data):
			userlogin = UserLogin().create(user)
			rm = form.remember.data
			login_user(userlogin, remember=rm)	#для запоминания авторизации после закрытия браузера
			return redirect(request.args.get("next") or url_for('profile'))

		flash("Неверная пара email/пароль", "error")

	return render_template("login.html", menu=dbase.getMenu(), title="Авторизация", form=form) 

	#как было без form wtf
	""" if request.method == "POST":
		user = dbase.getUserByEmail(request.form['email'])
		if user and check_password_hash(user['psw'], request.form['psw']):
			userlogin = UserLogin().create(user)
			rm = True if request.form.get('remainme') else False
			login_user(userlogin, remember=rm)	#для запоминания авторизации после закрытия браузера
			return redirect(request.args.get("next") or url_for('profile'))

		flash("Неверная пара логин/пароль", "error")

	return render_template("login.html", menu=dbase.getMenu(), title="Авторизация") 
	"""

#Обработчик регистрации
@app.route("/register", methods=["POST", "GET"])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		hash = generate_password_hash(form.psw.data)
		res = dbase.addUser(form.name.data, form.email.data, hash)
		if res:
			flash("Вы успешно зарегистрированы", "success")
			return redirect(url_for('login'))
		else:
			flash("Ошибка при добавлении в БД", "error")
	return render_template("register.html", menu=dbase.getMenu(), title="Регистрация", form=form)

	#как было до wtf form
	"""if request.method == "POST":
        session.pop('_flashes', None) 	#???????/
        if len(request.form['name']) > 1 and len(request.form['email']) > 1 \
            and len(request.form['psw']) > 1 and request.form['psw'] == request.form['psw2']:
            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash("Вы успешно зарегистрированы", "success")
                return redirect(url_for('login'))
            else:
                flash("Ошибка при добавлении в БД", "error")
        else:
            flash("Неверно заполнены поля", "error")
    return render_template("register.html", menu=dbase.getMenu(), title="Регистрация") 
    """

#обработчик выхода из аккаунта
@app.route('/logout')
@login_required
def logout():
    logout_user()	#специальная функция из flask_login
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('login'))

#обработчик страницы пользователя
@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html", menu=dbase.getMenu(), title="Профиль")

#отдельный обработчик для отображения аватара
@app.route('/userava')
@login_required
def userava():
    img = current_user.getAvatar(app)
    if not img:
        return ""
    h = make_response(img)	#создается объект запроса
    h.headers['Content-Type'] = 'image/png'
    return h	#возвращаем ответ сервера браузеру

#обработчик загрузки нового аватара
@app.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']	#берется поле file из объекта request, которое ассоциировано с загруженным на сервер файлом
        if file and current_user.verifyExt(file.filename):	#если файл успешно загружен и расширение png
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка обновления аватара", "error")
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")
 
    return redirect(url_for('profile'))

if __name__ == "__main__":
	app.run(debug=True)	






