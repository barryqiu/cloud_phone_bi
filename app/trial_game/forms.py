5# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, FileField, HiddenField, TextAreaField, SelectField
from wtforms.validators import Length, DataRequired


class AddGameForm(Form):
    gamename = StringField('Game Name', validators=[DataRequired(), Length(1, 50)])
    packagename = StringField('Package Name', validators=[DataRequired(), Length(1, 50)])
    gameicon = FileField('Game Icon')
    gamebanner = FileField('Game Banner')
    datafilenames = TextAreaField('Data Files')
    gamedesc = TextAreaField('Game Desc')
    giftdesc = TextAreaField('Gift Desc')
    id = HiddenField()
    submit = SubmitField('submit')
