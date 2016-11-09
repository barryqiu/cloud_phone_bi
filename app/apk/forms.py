# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, FileField, HiddenField, TextAreaField, SelectField, RadioField
from wtforms.validators import Length, DataRequired


class AddApkForm(Form):
    apkname = StringField('apk名称', validators=[DataRequired(), Length(1, 50)])
    allowallot = SelectField('上架', choices=[('0', '否'), ('1', '是')])
    packagename = StringField('包名', validators=[DataRequired(), Length(1, 50)])
    apkicon = FileField('图标')
    apkbanner = FileField('主 Banner 图')
    music = FileField('音乐文件')
    apk = FileField('Apk 文件')
    qr = FileField('二维码图')
    bannerside = FileField('子 Banner 图')
    squareimg = FileField('小图')
    datafilenames = TextAreaField('数据文件')
    id = HiddenField()
    submit = SubmitField('提交')
