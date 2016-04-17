from json import dump
from flask import render_template, redirect, url_for, flash
from .. import db
from . import trial_game
from werkzeug.utils import secure_filename
from ..utils import TimeUtil, upload_to_cdn
from ..models import Game, GameTask, GameServer, Server
from .forms import AddGameForm
from flask import current_app as app

TRIAL_GAME_STATE = 2


@trial_game.route('/add', methods=['GET', 'POST'])
def game_add():
    form = AddGameForm()
    if form.validate_on_submit():
        try:
            game = Game(game_name=form.gamename.data, package_name=form.packagename.data,
                        data_file_names=form.datafilenames.data)

            filename = TimeUtil.get_time_stamp() + secure_filename(form.gameicon.data.filename)
            form.gameicon.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + filename)
            game.icon_url = upload_to_cdn("/uploads/" + filename,
                                          app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + filename)
            if not game.icon_url:
                game.icon_url = "/uploads/" + filename

            bannerfilename = TimeUtil.get_time_stamp() + secure_filename(form.gamebanner.data.filename)
            form.gamebanner.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + bannerfilename)
            game.banner_url = upload_to_cdn("/uploads/" + bannerfilename,
                                            app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + bannerfilename)
            if not game.banner_url:
                game.banner_url = "/uploads/" + bannerfilename

            game.state = app.config['TRIAL_GAME_STATE']

            db.session.add(game)
            db.session.commit()
            flash('add game success')
        except Exception, e:
            db.session.rollback()
            flash('add game fail' + e.message, 'error')
        return redirect(url_for('trial_game.game_list'))
    return render_template('game/add.html', form=form)


@trial_game.route('/edit/<page>/<game_id>', methods=['GET', 'POST'])
def game_edit(page, game_id):
    form = AddGameForm()
    game = Game.query.get(game_id)
    if form.validate_on_submit():
        try:
            game.game_name = form.gamename.data
            game.package_name = form.packagename.data
            game.data_file_names = form.datafilenames.data
            if form.gameicon.data.filename:
                filename = TimeUtil.get_time_stamp() + secure_filename(form.gameicon.data.filename)
                form.gameicon.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + filename)
                game.icon_url = upload_to_cdn("/uploads/" + filename,
                                          app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + filename)
                if not game.icon_url:
                    game.icon_url = "/uploads/" + filename
            if form.gamebanner.data.filename:
                bannerfilename = TimeUtil.get_time_stamp() + secure_filename(form.gamebanner.data.filename)
                form.gamebanner.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + bannerfilename)
                game.banner_url = upload_to_cdn("/uploads/" + bannerfilename,
                                                app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + bannerfilename)
                if not game.banner_url:
                    game.banner_url = "/uploads/" + bannerfilename
            db.session.add(game)
            db.session.commit()
            flash('update success!')
        except Exception, e:
            db.session.rollback()
            # print "xxxxxxxxxxxxxx" + str(e)
            flash('update fail!' + e.message)
        return redirect(url_for('trial_game.game_list', page=page))
    form.gamename.data = game.game_name
    form.packagename.data = game.package_name
    form.id.data = game.id
    form.datafilenames.data = game.data_file_names
    return render_template('game/edit.html', form=form)


@trial_game.route('/list', defaults={'page': 1})
@trial_game.route('/list/<int:page>')
def game_list(page):
    pagination = Game.query.filter_by(state=app.config['TRIAL_GAME_STATE']).order_by(Game.add_time.desc()).paginate(
        page, per_page=app.config['GAME_NUM_PER_PAGE'], error_out=False)
    games = pagination.items
    return render_template('game/trial_list.html', games=games, pagination=pagination)


@trial_game.route('/del/<page>/<game_id>')
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
    return redirect(url_for('trial_game.game_list', page=page))