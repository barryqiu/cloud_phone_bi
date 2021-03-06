from flask import render_template, redirect, url_for, flash

from .. import db
from . import game
from flask.ext.login import login_required
from werkzeug.utils import secure_filename
from ..utils import TimeUtil, upload_to_cdn
from ..models import GameTask, GameServer, Server, Game
from .forms import AddGameForm, AddGameTaskForm, AddGameServerForm
from flask import current_app as app


@game.route('/add', methods=['GET', 'POST'])
@login_required
def game_add():
    form = AddGameForm()
    if form.validate_on_submit():
        try:
            game = Game(game_name=form.gamename.data, package_name=form.packagename.data,
                        data_file_names=form.datafilenames.data, allow_allot=form.allowallot.data)

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

            musicfilename = TimeUtil.get_time_stamp() + secure_filename(form.music.data.filename)
            form.music.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + musicfilename)
            game.music_url = upload_to_cdn("/uploads/" + musicfilename,
                                            app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + musicfilename)
            if not game.music_url:
                game.music_url = "/uploads/" + musicfilename

            if form.giftimg.data.filename:
                giftimgfilename = TimeUtil.get_time_stamp() + secure_filename(form.giftimg.data.filename)
                form.giftimg.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + giftimgfilename)
                game.gift_url = upload_to_cdn("/uploads/" + giftimgfilename,
                                               app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + giftimgfilename)
                if not game.gift_url:
                    game.gift_url = "/uploads/" + giftimgfilename

            if form.apk.data.filename:
                apkfilename = TimeUtil.get_time_stamp() + secure_filename(form.apk.data.filename)
                form.apk.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + apkfilename)
                game.apk_url = upload_to_cdn("/uploads/" + apkfilename,
                                             app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + apkfilename)
                if not game.apk_url:
                    game.apk_url = "/uploads/" + apkfilename

            if form.qr.data.filename:
                qrfilename = TimeUtil.get_time_stamp() + secure_filename(form.qr.data.filename)
                form.qr.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + qrfilename)
                game.qr_url = upload_to_cdn("/uploads/" + qrfilename,
                                            app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + qrfilename)
                if not game.qr_url:
                    game.qr_url = "/uploads/" + qrfilename

            if form.bannerside.data.filename:
                bannersidefilename = TimeUtil.get_time_stamp() + secure_filename(form.bannerside.data.filename)
                form.bannerside.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + bannersidefilename)
                game.banner_side = upload_to_cdn("/uploads/" + bannersidefilename,
                                             app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + bannersidefilename)
                if not game.banner_side:
                    game.banner_side = "/uploads/" + bannersidefilename

            if form.squareimg.data.filename:
                squareimgfilename = TimeUtil.get_time_stamp() + secure_filename(form.squareimg.data.filename)
                form.squareimg.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + squareimgfilename)
                game.square_img = upload_to_cdn("/uploads/" + squareimgfilename,
                                            app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + squareimgfilename)
                if not game.square_img:
                    game.square_img = "/uploads/" + squareimgfilename

            db.session.add(game)
            db.session.commit()
            flash('add game success')
        except Exception, e:
            db.session.rollback()
            flash('add game fail' + e.message, 'error')
        return redirect(url_for('game.game_list'))
    return render_template('game/add.html', form=form)


@game.route('/edit/<page>/<game_id>', methods=['GET', 'POST'])
@login_required
def game_edit(page, game_id):
    form = AddGameForm()
    game = Game.query.get(game_id)
    if form.validate_on_submit():
        try:
            game.game_name = form.gamename.data
            game.package_name = form.packagename.data
            game.data_file_names = form.datafilenames.data
            game.allow_allot = form.allowallot.data
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

            if form.music.data.filename:
                musicfilename = TimeUtil.get_time_stamp() + secure_filename(form.music.data.filename)
                form.music.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + musicfilename)
                game.music_url = upload_to_cdn("/uploads/" + musicfilename,
                                               app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + musicfilename)
                if not game.music_url:
                    game.music_url = "/uploads/" + musicfilename

            if form.giftimg.data.filename:
                giftimgfilename = TimeUtil.get_time_stamp() + secure_filename(form.giftimg.data.filename)
                form.giftimg.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + giftimgfilename)
                game.gift_url = upload_to_cdn("/uploads/" + giftimgfilename,
                                              app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + giftimgfilename)
                if not game.gift_url:
                    game.gift_url = "/uploads/" + giftimgfilename

            if form.apk.data.filename:
                apkfilename = TimeUtil.get_time_stamp() + secure_filename(form.apk.data.filename)
                form.apk.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + apkfilename)
                game.apk_url = upload_to_cdn("/uploads/" + apkfilename,
                                              app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + apkfilename)
                if not game.apk_url:
                    game.apk_url = "/uploads/" + apkfilename

            if form.qr.data.filename:
                qrfilename = TimeUtil.get_time_stamp() + secure_filename(form.qr.data.filename)
                form.qr.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + qrfilename)
                game.qr_url = upload_to_cdn("/uploads/" + qrfilename,
                                             app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + qrfilename)
                if not game.qr_url:
                    game.qr_url = "/uploads/" + qrfilename

            if form.bannerside.data.filename:
                bannersidefilename = TimeUtil.get_time_stamp() + secure_filename(form.bannerside.data.filename)
                form.bannerside.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + bannersidefilename)
                game.banner_side = upload_to_cdn("/uploads/" + bannersidefilename,
                                                 app.root_path + '/' + app.config[
                                                     'UPLOAD_FOLDER'] + '/' + bannersidefilename)
                if not game.banner_side:
                    game.banner_side = "/uploads/" + bannersidefilename

            if form.squareimg.data.filename:
                squareimgfilename = TimeUtil.get_time_stamp() + secure_filename(form.squareimg.data.filename)
                form.squareimg.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + squareimgfilename)
                game.square_img = upload_to_cdn("/uploads/" + squareimgfilename,
                                                app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + squareimgfilename)
                if not game.square_img:
                    game.square_img = "/uploads/" + squareimgfilename

            db.session.add(game)
            db.session.commit()
            flash('update success!')
        except Exception, e:
            db.session.rollback()
            # print "xxxxxxxxxxxxxx" + str(e)
            flash('update fail!' + e.message)
        return redirect(url_for('game.game_list', page=page))
    form.gamename.data = game.game_name
    form.packagename.data = game.package_name
    form.id.data = game.id
    form.datafilenames.data = game.data_file_names
    print game.allow_allot
    form.allowallot.data = '%s' % game.allow_allot
    print form.allowallot.data
    return render_template('game/edit.html', form=form)


@game.route('/list', defaults={'page': 1})
@game.route('/list/<int:page>')
@login_required
def game_list(page):
    pagination = Game.query.filter_by(state=1).order_by(Game.add_time.desc()).paginate(
        page, per_page=app.config['GAME_NUM_PER_PAGE'], error_out=False)
    games = pagination.items
    return render_template('game/list.html', games=games, pagination=pagination)


@game.route('/del/<page>/<game_id>')
@login_required
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
@login_required
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
            flash('add game task success')
        except Exception:
            flash('add game task fail', 'error')
        return redirect(url_for('game.game_task_list', game_id=game_id))
    return render_template('game/task_add.html', form=form)


@game.route('/task/<game_id>/list', defaults={'page': 1})
@game.route('/task/<game_id>/list/<int:page>')
@login_required
def game_task_list(game_id, page):
    game = Game.query.get(game_id)
    pagination = GameTask.query.filter_by(game_id=game_id).order_by(GameTask.add_time.desc()).paginate(
        page, per_page=app.config['GAME_NUM_PER_PAGE'], error_out=False)
    game_tasks = pagination.items
    return render_template('game/task_list.html', gametasks=game_tasks, pagination=pagination, game_id=game_id,
                           game=game)


@game.route('/task/<game_id>/<page>/edit/<task_id>', methods=['GET', 'POST'])
@login_required
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
        except Exception, e:
            flash('edit game task fail', 'error')
        return redirect(url_for('game.game_task_list', game_id=game_id, page=page))
    form.task_name.data = task.task_name
    form.task_des.data = task.task_des
    return render_template('game/task_edit.html', form=form)


@game.route('/task/<game_id>/<page>/del/<task_id>')
@login_required
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


@game.route('/server/<game_id>/add', methods=['GET', 'POST'])
@login_required
def game_server_add(game_id):
    form = AddGameServerForm()
    servers = Server.query.filter_by().all()
    server_names = []
    for server in servers:
        server_names.append((server.server_name,server.server_name))
    form.server_name.choices = server_names
    if form.validate_on_submit():
        try:
            game_server = GameServer()
            game_server.game_id = game_id
            game_server.server_name = form.server_name.data
            game_server.server_des = form.server_des.data
            game_server.package_name = form.packagename.data
            game_server.data_file_names = form.datafilenames.data
            db.session.add(game_server)
            db.session.commit()
            flash('add game server success')
        except Exception:
            flash('add game server fail', 'error')
        return redirect(url_for('game.game_server_list', game_id=game_id))
    return render_template('game/server_add.html', form=form)


@game.route('/server/<game_id>/list', defaults={'page': 1})
@game.route('/server/<game_id>/list/<int:page>')
@login_required
def game_server_list(game_id, page):
    game = Game.query.get(game_id)
    pagination = GameServer.query.filter_by(game_id=game_id).order_by(GameServer.add_time.desc()).paginate(
        page, per_page=app.config['GAME_NUM_PER_PAGE'], error_out=False)
    game_servers = pagination.items
    return render_template('game/server_list.html', gameservers=game_servers, pagination=pagination, game_id=game_id,
                           game=game)


@game.route('/server/<game_id>/<page>/edit/<server_id>', methods=['GET', 'POST'])
@login_required
def game_server_edit(game_id, page, server_id):
    form = AddGameServerForm()
    servers = Server.query.filter_by().all()
    server_names = []
    for server in servers:
        server_names.append((server.server_name,server.server_name))
    form.server_name.choices = server_names
    server = GameServer.query.get(server_id)
    if form.validate_on_submit():
        try:
            server.package_name = form.packagename.data
            server.data_file_names = form.datafilenames.data
            server.server_name = form.server_name.data
            server.server_des = form.server_des.data
            db.session.add(server)
            db.session.commit()
            flash('update success!')
        except Exception, e:
            flash('edit game server fail', 'error')
        return redirect(url_for('game.game_server_list', game_id=game_id, page=page))
    form.server_name.data = server.server_name
    form.server_des.data = server.server_des
    form.packagename.data = server.package_name
    form.datafilenames.data = server.data_file_names
    return render_template('game/server_edit.html', form=form)


@game.route('/server/<game_id>/<page>/del/<server_id>')
@login_required
def game_server_del(page, game_id, server_id):
    try:
        server_ids = server_id.split(",")
        GameServer.query.filter(GameServer.id.in_(server_ids)).delete(synchronize_session='fetch')
        db.session.commit()
        flash('del success.')
    except Exception, e:
        db.session.rollback()
        flash('del fail.', 'error')
    return redirect(url_for('game.game_server_list', game_id=game_id, page=page))


