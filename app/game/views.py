from flask import render_template, redirect, url_for, flash
from .. import db
from . import game
from werkzeug.utils import secure_filename
from ..utils import TimeUtil
from ..models import Game
from .forms import AddGameForm
from flask import current_app as app


@game.route('/add', methods=['GET', 'POST'])
def game_add():
    form = AddGameForm()
    if form.validate_on_submit():
        try:
            game = Game(game_name=form.gamename.data)
            filename = TimeUtil.get_time_stamp() + secure_filename(form.gameicon.data.filename)
            form.gameicon.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + filename)
            game.icon_url = "/uploads/" + filename
            db.session.add(game)
            db.session.commit()
            flash('add game success')
        except Exception:
            flash('add game fail', 'error')
        return redirect(url_for('game.game_list'))
    return render_template('game/add.html', form=form)


@game.route('/edit/<game_id>', methods=['GET', 'POST'])
def game_edit(game_id):
    form = AddGameForm()
    if form.validate_on_submit():
        try:
            game = Game.query.get(form.id.data)
            game.game_name = form.gamename.data
            if form.gameicon.data.filename:
                filename = TimeUtil.get_time_stamp() + secure_filename(form.gameicon.data.filename)
                form.gameicon.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + filename)
                game.icon_url = "/uploads/" + filename
            db.session.add(game)
            db.session.commit()
            flash('update success!')
        except Exception:
            db.session.rollback()
            # print "xxxxxxxxxxxxxx" + str(e)
            flash('update fail!')
        return redirect(url_for('game.game_list'))
    game = Game.query.get(game_id)
    form.gamename.data = game.game_name
    form.id.data = game.id
    return render_template('game/edit.html', form=form)


@game.route('/list', defaults={'page': 1})
@game.route('/list/<int:page>')
def game_list(page):
    pagination = Game.query.filter_by(state=1).order_by(Game.add_time.desc()).paginate(
        page, per_page=app.config['GAME_NUM_PER_PAGE'], error_out=False)
    games = pagination.items
    return render_template('game/list.html', games=games, pagination=pagination)


@game.route('/del/<game_id>')
def game_del(game_id):
    try:
        gameids = game_id.split(",")
        games = Game.query.filter(Game.id.in_(gameids)).all()
        # game = Game.query.get(game_id)
        for game in games:
            game.state = 0
        db.session.bulk_save_objects(games)
        db.session.commit()
        flash('del success.')
    except Exception:
        db.session.rollback()
        flash('del fail.', 'error')
    return redirect(url_for('game.game_list'))
