# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, FileField, HiddenField, TextAreaField, SelectField
from wtforms.validators import Length, DataRequired


class AddGameForm(Form):
    gamename = StringField('游戏名称', validators=[DataRequired(), Length(1, 50)])
    allowallot = SelectField('上架', choices=[('0', '否'), ('1', '是')])
    packagename = StringField('包名', validators=[DataRequired(), Length(1, 50)])
    gameicon = FileField('图标')
    gamebanner = FileField('主 Banner 图')
    giftimg = FileField('礼包图')
    music = FileField('音乐文件')
    apk = FileField('Apk 文件')
    qr = FileField('二维码图')
    bannerside = FileField('子 Banner 图')
    squareimg = FileField('小图')
    datafilenames = TextAreaField('数据文件')
    id = HiddenField()
    submit = SubmitField('提交')


class AddGameTaskForm(Form):
    task_name = StringField('任务名称', validators=[DataRequired(), Length(1, 50)])
    task_des = TextAreaField('任务描述')
    submit = SubmitField('提交')


class AddGameServerForm(Form):
    server_name = SelectField('服务器名称', choices=[('android', 'android'), ('iphone', 'iphone')])
    packagename = StringField('包名', validators=[DataRequired(), Length(1, 50)])
    datafilenames = TextAreaField('数据文件')
    server_des = TextAreaField('服务器描述')
    submit = SubmitField('提交')
