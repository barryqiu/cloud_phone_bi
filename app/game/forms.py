5# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, FileField, HiddenField, TextAreaField, SelectField
from wtforms.validators import Length, DataRequired


class AddGameForm(Form):
    gamename = StringField('Game Name', validators=[DataRequired(), Length(1, 50)])
    packagename = StringField('Package Name', validators=[DataRequired(), Length(1, 50)])
    gameicon = FileField('Game Icon')
    gamebanner = FileField('Game Banner')
    music = FileField('Music File')
    datafilenames = TextAreaField('Data Files')
    id = HiddenField()
    submit = SubmitField('submit')


class AddGameTaskForm(Form):
    task_name = StringField('Task Name', validators=[DataRequired(), Length(1, 50)])
    task_des = TextAreaField('Task Description')
    submit = SubmitField('submit')


class AddGameServerForm(Form):
    server_name = SelectField('message_type', choices=[('android', 'android'), ('iphone', 'iphone')])
    packagename = StringField('Package Name', validators=[DataRequired(), Length(1, 50)])
    datafilenames = TextAreaField('Data Files')
    server_des = TextAreaField('Server Description')
    submit = SubmitField('submit')
