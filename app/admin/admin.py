from flask import Blueprint, render_template, redirect, flash, request, url_for, session, g
import sqlite3
import os

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

menu = [{'url': '.index', 'title': 'Панель'},
		{'url': '.listusers', 'title': 'Список пользователей'},
        {'url': '.listpubs', 'title': 'Список статей'},
        {'url': '.logout', 'title': 'Выйти'},]

def login_admin():
    session['admin_logged'] = 1

db = None	#будет ссылаться на бд
@admin.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    global db
    db = g.get('link_db')	#в свойтстве link_db храниться соединение с бд
 
@admin.teardown_request
def teardown_request(request):
    global db
    db = None
    return request

@admin.route('/')
def index():
	if not isLogged():
		return redirect(url_for('.login'))
	return render_template('admin/index.html', menu=menu, title='Админ-панель')

def isLogged():
    return True if session.get('admin_logged') else False
 
def logout_admin():	#выход из админ панели
    session.pop('admin_logged', None)

@admin.route('/login', methods=["POST", "GET"])
def login():
    if isLogged():
        return redirect(url_for('.index'))

    if request.method == "POST":
        if request.form['user'] == "admin" and request.form['psw'] == "12345":
            login_admin()
            return redirect(url_for('.index'))	#index из текущего bluerint
        else:
            flash("Неверная пара логин/пароль", "error")
 
    return render_template('admin/login.html', title='Админ-панель')

@admin.route('/logout', methods=["POST", "GET"])
def logout():
    if not isLogged():
        return redirect(url_for('.login'))
    logout_admin()
    return redirect(url_for('.login'))

@admin.route('/list-pubs')
def listpubs():
    if not isLogged():
        return redirect(url_for('.login'))
    list = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT title, text, url FROM posts")
            list = cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка получения статей из БД " + str(e))
 
    return render_template('admin/listpubs.html', title='Список статей', menu=menu, list=list)
 
@admin.route('/list-users')
def listusers():
    if not isLogged():
        return redirect(url_for('.login'))
    list = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT name, email FROM users ORDER BY time DESC")
            list = cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка получения статей из БД " + str(e))
 
    return render_template('admin/listusers.html', title='Список пользователей', menu=menu, list=list)











