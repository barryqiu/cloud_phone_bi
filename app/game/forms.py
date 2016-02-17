5# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, FileField, HiddenField, TextAreaField
from wtforms.validators import Length, DataRequired


class AddGameForm(Form):
    gamename = StringField('Game Name', validators=[DataRequired(), Length(1, 50)])
    packagename = StringField('Package Name', validators=[DataRequired(), Length(1, 50)])
    gameicon = FileField('Game Icon')
    gamebanner = FileField('Game Banner')
    datafilenames = TextAreaField('Data Files')
    id = HiddenField()
    submit = SubmitField('submit')


class AddGameTaskForm(Form):
    task_name = StringField('Task Name', validators=[DataRequired(), Length(1, 50)])
    task_des = TextAreaField('Task Description')
    submit = SubmitField('submit')


class AddGameServerForm(Form):
    server_name = StringField('Server Name', validators=[DataRequired(), Length(1, 50)])
    server_des = TextAreaField('Server Description')
    submit = SubmitField('submit')
