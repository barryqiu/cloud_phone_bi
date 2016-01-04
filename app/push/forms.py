# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, HiddenField, TextAreaField, SelectField
from wtforms.validators import Length, DataRequired


class AddPushForm(Form):
    platform = StringField('platform', validators=[DataRequired(), Length(1, 50)])
    audience = TextAreaField('audience')
    message_type = SelectField('message_type', choices=[('1', 'reboot'),
                                                        ('2', 'install'),
                                                        ('3', 'uninstall'),
                                                        ('4', 'web key reboot'),
                                                        ('5', 'clear game data')
                                                        ])
    content = TextAreaField('content')

    id = HiddenField()
    submit = SubmitField('submit')
