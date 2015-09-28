from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo, DataRequired
from wtforms import ValidationError
from ..models import User, Admin


class AddGameForm(Form):
    gamename = StringField('Game Name', validators=[DataRequired(), Length(1, 50)])
    gameicon = FileField('ICON', validators=[DataRequired()])
    submit = SubmitField('Log In')
