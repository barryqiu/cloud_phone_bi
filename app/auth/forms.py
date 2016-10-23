# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, DataRequired
from wtforms import ValidationError
from ..models import User, Admin


class LoginForm(Form):
    mobile_num = StringField('手机号', validators=[DataRequired(), Length(11, 11)])
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
    mobile_num = StringField('手机号', validators=[
        DataRequired(), Length(11, 11), Regexp('^1[0-9]*$', 0,
                                               '请输入正确的手机号')])
    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='密码不一致')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('注册')

    def validate_mobile_num(self, field):
        if User.query.filter_by(mobile_num=field.data).first():
            raise ValidationError('手机号已经被注册')
