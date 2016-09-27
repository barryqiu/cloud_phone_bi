# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, FileField, HiddenField, TextAreaField, SelectField
from wtforms.validators import Length, DataRequired


class AddGameForm(Form):
    gamename = StringField('游戏名称', validators=[DataRequired(), Length(1, 50)])
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
    gamedesc = TextAreaField('游戏描述')
    giftdesc = TextAreaField('礼包描述')
    id = HiddenField()
    submit = SubmitField('提交')
