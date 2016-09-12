from json import dump
from flask import render_template, redirect, url_for, flash
from .. import db
from . import trial_game
from flask.ext.login import login_required
from werkzeug.utils import secure_filename
from ..utils import TimeUtil, upload_to_cdn
from ..models import Game, GameTask, GameServer, Server
from .forms import AddGameForm
from flask import current_app as app

TRIAL_GAME_STATE = 2


@trial_game.route('/add', methods=['GET', 'POST'])
@login_required
def game_add():
    form = AddGameForm()
    if form.validate_on_submit():
        try:
            game = Game(game_name=form.gamename.data, package_name=form.packagename.data,
                        data_file_names=form.datafilenames.data, game_desc=form.gamedesc.data,
                        gift_desc = form.giftdesc.data)

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
                                                 app.root_path + '/' + app.config[
                                                     'UPLOAD_FOLDER'] + '/' + bannersidefilename)
                if not game.banner_side:
                    game.banner_side = "/uploads/" + bannersidefilename

            if form.squareimg.data.filename:
                squareimgfilename = TimeUtil.get_time_stamp() + secure_filename(form.squareimg.data.filename)
                form.squareimg.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + squareimgfilename)
                game.square_img = upload_to_cdn("/uploads/" + squareimgfilename,
                                                app.root_path + '/' + app.config[
                                                    'UPLOAD_FOLDER'] + '/' + squareimgfilename)
                if not game.square_img:
                    game.square_img = "/uploads/" + squareimgfilename

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
@login_required
def game_edit(page, game_id):
    form = AddGameForm()
    game = Game.query.get(game_id)
    if form.validate_on_submit():
        try:
            game.game_name = form.gamename.data
            game.package_name = form.packagename.data
            game.data_file_names = form.datafilenames.data
            game.game_desc = form.gamedesc.data
            game.gift_desc = form.giftdesc.data
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
                                                app.root_path + '/' + app.config[
                                                    'UPLOAD_FOLDER'] + '/' + squareimgfilename)
                if not game.square_img:
                    game.square_img = "/uploads/" + squareimgfilename

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
    form.gamedesc.data = game.game_desc
    form.giftdesc.data = game.gift_desc
    return render_template('game/edit.html', form=form)


@trial_game.route('/list', defaults={'page': 1})
@trial_game.route('/list/<int:page>')
@login_required
def game_list(page):
    pagination = Game.query.filter_by(state=app.config['TRIAL_GAME_STATE']).order_by(Game.add_time.desc()).paginate(
        page, per_page=app.config['GAME_NUM_PER_PAGE'], error_out=False)
    games = pagination.items
    return render_template('game/trial_list.html', games=games, pagination=pagination)


@trial_game.route('/del/<page>/<game_id>')
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
    return redirect(url_for('trial_game.game_list', page=page))
