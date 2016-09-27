# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, DataRequired
from wtforms import ValidationError
from ..models import User, Admin


class LoginForm(Form):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 50)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


class ChangePasswordForm(Form):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='密码不一致')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('修改密码')


class RegistrationForm(Form):
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              '用户名仅支持字母，数字，.或者下划线')])
    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='密码不一致')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('注册')

    def validate_username(self, field):
        if Admin.query.filter_by(user_name=field.data).first():
            raise ValidationError('用户名已经存在')
