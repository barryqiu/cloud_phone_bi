from flask import render_template, redirect, request, url_for, flash
from .. import db
from . import game
from ..models import Admin
from .forms import AddGameForm


@game.route('/add', methods=['GET', 'POST'])
def game_add():
    form = AddGameForm
    if form.validate_on_submit():
        game = Admin(game_name=form.gamename.data)
        db.session.add(game)
        db.session.commit()
        flash('Invalid username or password.')
        return redirect(url_for('game.game_list'))
    return render_template('game/list.html', form=form)


@game.route('/list', methods=['GET', 'POST'])
def game_list():
    games = []
    return render_template('game/list.html', gamelist=games)
