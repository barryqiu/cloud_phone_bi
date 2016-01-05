# -*- coding: utf-8 -*-
from flask.ext.wtf import Form
from wtforms import  SubmitField, HiddenField, TextAreaField, SelectField


class AddPushForm(Form):
    platform = SelectField('message_type', choices=[('android', 'android'), ('iphone', 'iphone')])
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
