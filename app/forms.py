from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
	#StringField - Обычное поле ввода
	# Первый параметр - название поля ввода
	# Второй параметр будет ссылаться на список валидаторов для проверки корректности введенных данных (в скобках текст ошибки)
	email = StringField("Email: ", validators=[Email("Неккоректный email")])
	#DataRequired() требует чтобы в этом поле ввода был хотя бы один символ
	psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=2, max=100, message="lalala")])
	remember = BooleanField("Запомнить", default = False)
	submit = SubmitField("Войти")

class RegisterForm(FlaskForm):
    name = StringField("Имя: ", validators=[Length(min=2, max=20, message="Имя должно быть от 2 до 20 символов")])
    email = StringField("Email: ", validators=[Email("Некорректный email")])
    psw = PasswordField("Пароль: ", validators=[DataRequired(), Length(min=2, max=100, message="lalala")])
    psw2 = PasswordField("Повтор пароля: ", validators=[DataRequired(), EqualTo('psw', message="Пароли не совпадают")])
    submit = SubmitField("Регистрация")

