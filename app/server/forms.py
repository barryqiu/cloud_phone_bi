5# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, FileField, HiddenField, TextAreaField
from wtforms.validators import Length, DataRequired


class AddServerForm(Form):
    servername = StringField('Server Name', validators=[DataRequired(), Length(1, 50)])
    servericon = FileField('Server Icon')
    submit = SubmitField('submit')
