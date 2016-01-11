from json import dump
from flask import render_template, redirect, url_for, flash
from .. import db
from . import game
from werkzeug.utils import secure_filename
from ..utils import TimeUtil
from ..models import Game, GameTask
from .forms import AddGameForm, AddGameTaskForm
from flask import current_app as app


@game.route('/add', methods=['GET', 'POST'])
def game_add():
    form = AddGameForm()
    if form.validate_on_submit():
        try:
            game = Game(game_name=form.gamename.data, package_name=form.packagename.data)
            filename = TimeUtil.get_time_stamp() + secure_filename(form.gameicon.data.filename)
            form.gameicon.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + filename)
            game.icon_url = "/uploads/" + filename
            db.session.add(game)
            db.session.commit()
            flash('add game success')
        except Exception:
            db.session.rollback()
            flash('add game fail', 'error')
        return redirect(url_for('game.game_list'))
    return render_template('game/add.html', form=form)


@game.route('/edit/<page>/<game_id>', methods=['GET', 'POST'])
def game_edit(page, game_id):
    form = AddGameForm()
    game = Game.query.get(game_id)
    if form.validate_on_submit():
        try:
            game.game_name = form.gamename.data
            game.package_name = form.packagename.data
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
        return redirect(url_for('game.game_list', page=page))
    form.gamename.data = game.game_name
    form.packagename.data = game.package_name
    form.id.data = game.id
    return render_template('game/edit.html', form=form)


@game.route('/list', defaults={'page': 1})
@game.route('/list/<int:page>')
def game_list(page):
    pagination = Game.query.filter_by(state=1).order_by(Game.add_time.desc()).paginate(
        page, per_page=app.config['GAME_NUM_PER_PAGE'], error_out=False)
    games = pagination.items
    return render_template('game/list.html', games=games, pagination=pagination)


@game.route('/del/<page>/<game_id>')
def game_del(page, game_id):
    try:
        gameids = game_id.split(",")
        games = Game.query.filter(Game.id.in_(gameids)).all()
        for game in games:
            game.state = 0
        db.session.bulk_save_objects(games)
        db.session.commit()
        flash('del success.')
    except Exception:
        db.session.rollback()
        flash('del fail.', 'error')
    return redirect(url_for('game.game_list', page=page))


@game.route('/task/<game_id>/add', methods=['GET', 'POST'])
def game_task_add(game_id):
    form = AddGameTaskForm()
    if form.validate_on_submit():
        try:
            game_task = GameTask()
            game_task.game_id = game_id
            game_task.task_name = form.task_name.data
            game_task.task_des = form.task_des.data
            db.session.add(game_task)
            db.session.commit()
            flash('add game success')
        except Exception:
            flash('add gametask fail', 'error')
        return redirect(url_for('game.game_task_list', game_id=game_id))
    return render_template('game/task_add.html', form=form)


@game.route('/task/<game_id>/list', defaults={'page': 1})
@game.route('/task/<game_id>/list/<int:page>')
def game_task_list(game_id, page):
    pagination = GameTask.query.filter_by(game_id=game_id).order_by(GameTask.add_time.desc()).paginate(
        page, per_page=app.config['GAME_NUM_PER_PAGE'], error_out=False)
    game_tasks = pagination.items
    return render_template('game/task_list.html', gametasks=game_tasks, pagination=pagination, game_id=game_id)


@game.route('/task/<game_id>/<page>/edit/<task_id>', methods=['GET', 'POST'])
def game_task_edit(game_id, page, task_id):
    form = AddGameTaskForm()
    task = GameTask.query.get(task_id)
    if form.validate_on_submit():
        try:
            task.task_name = form.task_name.data
            task.task_des = form.task_des.data
            db.session.add(task)
            db.session.commit()
            flash('update success!')
        except Exception , e:
            flash('edit gametask fail', 'error')
        return redirect(url_for('game.game_task_list', game_id=game_id, page=page))
    form.task_name.data = task.task_name
    form.task_des.data = task.task_des
    return render_template('game/task_edit.html', form=form)


@game.route('/task/<game_id>/<page>/del/<task_id>')
def game_task_del(page, game_id, task_id):
    try:
        task_ids = task_id.split(",")
        GameTask.query.filter(GameTask.id.in_(task_ids)).delete(synchronize_session='fetch')
        db.session.commit()
        flash('del success.')
    except Exception, e:
        db.session.rollback()
        flash('del fail.', 'error')
    return redirect(url_for('game.game_task_list', game_id=game_id, page=page))
