# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, FileField, HiddenField
from wtforms.validators import Length, DataRequired


class AddGameForm(Form):
    gamename = StringField('Game Name', validators=[DataRequired(), Length(1, 50)])
    gameicon = FileField('Game Icon')
    id = HiddenField()
    submit = SubmitField('submit')
