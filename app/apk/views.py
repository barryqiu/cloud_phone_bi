from flask import render_template, redirect, url_for, flash

from .. import db
from . import apk
from flask.ext.login import login_required
from werkzeug.utils import secure_filename
from ..utils import TimeUtil, upload_to_cdn
from ..models import Apk, Category, CategoryApk
from .forms import AddApkForm, CategoryForm, CategoryApkForm
from flask import current_app as app


@apk.route('/add', methods=['GET', 'POST'])
@login_required
def apk_add():
    form = AddApkForm()
    if form.validate_on_submit():
        try:
            apk = Apk(apk_name=form.apkname.data, package_name=form.packagename.data,
                      data_file_names=form.datafilenames.data, allow_allot=form.allowallot.data)

            if form.apkicon.data.filename:
                filename = TimeUtil.get_time_stamp() + secure_filename(form.apkicon.data.filename)
                form.apkicon.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + filename)
                apk.icon_url = upload_to_cdn("/uploads/" + filename,
                                             app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + filename)
                if not apk.icon_url:
                    apk.icon_url = "/uploads/" + filename

            if form.apkbanner.data.filename:
                bannerfilename = TimeUtil.get_time_stamp() + secure_filename(form.apkbanner.data.filename)
                form.apkbanner.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + bannerfilename)
                apk.banner_url = upload_to_cdn("/uploads/" + bannerfilename,
                                               app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + bannerfilename)
                if not apk.banner_url:
                    apk.banner_url = "/uploads/" + bannerfilename

            if form.music.data.filename:
                musicfilename = TimeUtil.get_time_stamp() + secure_filename(form.music.data.filename)
                form.music.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + musicfilename)
                apk.music_url = upload_to_cdn("/uploads/" + musicfilename,
                                              app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + musicfilename)
                if not apk.music_url:
                    apk.music_url = "/uploads/" + musicfilename

            if form.apk.data.filename:
                apkfilename = TimeUtil.get_time_stamp() + secure_filename(form.apk.data.filename)
                form.apk.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + apkfilename)
                apk.apk_url = upload_to_cdn("/uploads/" + apkfilename,
                                            app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + apkfilename)
                if not apk.apk_url:
                    apk.apk_url = "/uploads/" + apkfilename

            if form.qr.data.filename:
                qrfilename = TimeUtil.get_time_stamp() + secure_filename(form.qr.data.filename)
                form.qr.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + qrfilename)
                apk.qr_url = upload_to_cdn("/uploads/" + qrfilename,
                                           app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + qrfilename)
                if not apk.qr_url:
                    apk.qr_url = "/uploads/" + qrfilename

            if form.bannerside.data.filename:
                bannersidefilename = TimeUtil.get_time_stamp() + secure_filename(form.bannerside.data.filename)
                form.bannerside.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + bannersidefilename)
                apk.banner_side = upload_to_cdn("/uploads/" + bannersidefilename,
                                                app.root_path + '/' + app.config[
                                                    'UPLOAD_FOLDER'] + '/' + bannersidefilename)
                if not apk.banner_side:
                    apk.banner_side = "/uploads/" + bannersidefilename

            if form.squareimg.data.filename:
                squareimgfilename = TimeUtil.get_time_stamp() + secure_filename(form.squareimg.data.filename)
                form.squareimg.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + squareimgfilename)
                apk.square_img = upload_to_cdn("/uploads/" + squareimgfilename,
                                               app.root_path + '/' + app.config[
                                                   'UPLOAD_FOLDER'] + '/' + squareimgfilename)
                if not apk.square_img:
                    apk.square_img = "/uploads/" + squareimgfilename

            db.session.add(apk)
            db.session.commit()
            flash('add apk success')
        except Exception, e:
            db.session.rollback()
            flash('add apk fail' + e.message, 'error')
        return redirect(url_for('apk.apk_list'))
    return render_template('apk/add.html', form=form)


@apk.route('/edit/<page>/<apk_id>', methods=['GET', 'POST'])
@login_required
def apk_edit(page, apk_id):
    form = AddApkForm()
    apk = Apk.query.get(apk_id)
    if form.validate_on_submit():
        try:
            apk.apk_name = form.apkname.data
            apk.package_name = form.packagename.data
            apk.data_file_names = form.datafilenames.data
            apk.allow_allot = form.allowallot.data
            if form.apkicon.data.filename:
                filename = TimeUtil.get_time_stamp() + secure_filename(form.apkicon.data.filename)
                form.apkicon.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + filename)
                apk.icon_url = upload_to_cdn("/uploads/" + filename,
                                             app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + filename)
                if not apk.icon_url:
                    apk.icon_url = "/uploads/" + filename
            if form.apkbanner.data.filename:
                bannerfilename = TimeUtil.get_time_stamp() + secure_filename(form.apkbanner.data.filename)
                form.apkbanner.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + bannerfilename)
                apk.banner_url = upload_to_cdn("/uploads/" + bannerfilename,
                                               app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + bannerfilename)
                if not apk.banner_url:
                    apk.banner_url = "/uploads/" + bannerfilename

            if form.music.data.filename:
                musicfilename = TimeUtil.get_time_stamp() + secure_filename(form.music.data.filename)
                form.music.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + musicfilename)
                apk.music_url = upload_to_cdn("/uploads/" + musicfilename,
                                              app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + musicfilename)
                if not apk.music_url:
                    apk.music_url = "/uploads/" + musicfilename

            if form.apk.data.filename:
                apkfilename = TimeUtil.get_time_stamp() + secure_filename(form.apk.data.filename)
                form.apk.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + apkfilename)
                apk.apk_url = upload_to_cdn("/uploads/" + apkfilename,
                                            app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + apkfilename)
                if not apk.apk_url:
                    apk.apk_url = "/uploads/" + apkfilename

            if form.qr.data.filename:
                qrfilename = TimeUtil.get_time_stamp() + secure_filename(form.qr.data.filename)
                form.qr.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + qrfilename)
                apk.qr_url = upload_to_cdn("/uploads/" + qrfilename,
                                           app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + qrfilename)
                if not apk.qr_url:
                    apk.qr_url = "/uploads/" + qrfilename

            if form.bannerside.data.filename:
                bannersidefilename = TimeUtil.get_time_stamp() + secure_filename(form.bannerside.data.filename)
                form.bannerside.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + bannersidefilename)
                apk.banner_side = upload_to_cdn("/uploads/" + bannersidefilename,
                                                app.root_path + '/' + app.config[
                                                    'UPLOAD_FOLDER'] + '/' + bannersidefilename)
                if not apk.banner_side:
                    apk.banner_side = "/uploads/" + bannersidefilename

            if form.squareimg.data.filename:
                squareimgfilename = TimeUtil.get_time_stamp() + secure_filename(form.squareimg.data.filename)
                form.squareimg.data.save(app.root_path + '/' + app.config['UPLOAD_FOLDER'] + '/' + squareimgfilename)
                apk.square_img = upload_to_cdn("/uploads/" + squareimgfilename,
                                               app.root_path + '/' + app.config[
                                                   'UPLOAD_FOLDER'] + '/' + squareimgfilename)
                if not apk.square_img:
                    apk.square_img = "/uploads/" + squareimgfilename

            db.session.add(apk)
            db.session.commit()
            flash('update success!')
        except Exception, e:
            db.session.rollback()
            # print "xxxxxxxxxxxxxx" + str(e)
            flash('update fail!' + e.message)
        return redirect(url_for('apk.apk_list', page=page))
    form.apkname.data = apk.apk_name
    form.packagename.data = apk.package_name
    form.id.data = apk.id
    form.datafilenames.data = apk.data_file_names
    print apk.allow_allot
    form.allowallot.data = '%s' % apk.allow_allot
    print form.allowallot.data
    return render_template('apk/edit.html', form=form)


@apk.route('/list', defaults={'page': 1})
@apk.route('/list/<int:page>')
@login_required
def apk_list(page):
    pagination = Apk.query.filter_by(state=1).order_by(Apk.id.asc()).paginate(
        page, per_page=app.config['GAME_NUM_PER_PAGE'], error_out=False)
    apks = pagination.items
    return render_template('apk/list.html', apks=apks, pagination=pagination)


@apk.route('/del/<page>/<apk_id>')
@login_required
def apk_del(page, apk_id):
    try:
        apkids = apk_id.split(",")
        apks = Apk.query.filter(Apk.id.in_(apkids)).all()
        for apk in apks:
            apk.state = 0
        db.session.bulk_save_objects(apks)
        db.session.commit()
        flash('del success.')
    except Exception:
        db.session.rollback()
        flash('del fail.', 'error')
    return redirect(url_for('apk.apk_list', page=page))


@apk.route('/category/add', methods=['GET', 'POST'])
@login_required
def category_add():
    form = CategoryForm()
    if form.validate_on_submit():
        try:
            category = Category(category_name=form.category_name.data, state=1)
            db.session.add(category)
            db.session.commit()
            flash('add category success')
        except Exception:
            flash('add category task fail', 'error')
        return redirect(url_for('apk.category_list'))
    return render_template('apk/category_add.html', form=form)


@apk.route('/category/list', defaults={'page': 1})
@apk.route('/category/list/<int:page>')
@login_required
def category_list(page):
    pagination = Category.query.filter_by(state=1).order_by(Category.add_time.desc()).paginate(
        page, per_page=app.config['GAME_NUM_PER_PAGE'], error_out=False)
    categories = pagination.items
    return render_template('apk/category_list.html', categories=categories, pagination=pagination)


@apk.route('/category/<page>/edit/<category_id>', methods=['GET', 'POST'])
@login_required
def category_edit(page, category_id):
    form = CategoryForm()
    category = Category.query.get(category_id)
    if form.validate_on_submit():
        try:
            category.category_name = form.category_name.data
            db.session.add(category)
            db.session.commit()
            flash('update success!')
        except Exception, e:
            flash('edit category fail', 'error')
        return redirect(url_for('apk.category_list', page=page))
    form.category_name.data = category.category_name
    return render_template('apk/category_edit.html', form=form)


@apk.route('/category/<page>/del/<category_id>')
@login_required
def category_del(page, category_id):
    try:
        category_ids = category_id.split(",")
        Category.query.filter(Category.id.in_(category_ids)).update({Category.state: 0}, synchronize_session=False)
        db.session.commit()
        flash('del success.')
    except Exception, e:
        db.session.rollback()
        flash('del fail.', 'error')
    return redirect(url_for('apk.category_list', page=page))


@apk.route('/category/<int:category_id>/apk/add', methods=['GET', 'POST'])
@login_required
def category_apk_add(category_id):
    form = CategoryApkForm()
    category = Category.query.get(category_id)
    if form.validate_on_submit():
        try:
            apk_id = form.apk_id.data
            curr_apk = Apk.query.get(apk_id)
            if not curr_apk:
                flash('wrong apk id ')
                return render_template('apk/category_apk_add.html', form=form, category=category)
            category_apk = CategoryApk(apk=curr_apk, category=category)
            db.session.add(category_apk)
            db.session.commit()
            flash('add category apk success')
        except Exception:
            flash('add category task fail', 'error')
        return redirect(url_for('apk.category_apk_list', category_id=category_id))
    return render_template('apk/category_apk_add.html', form=form, category=category)


@apk.route('/category/<int:category_id>/apk/list', defaults={'page': 1})
@apk.route('/category/<int:category_id>/apk/list/<int:page>')
@login_required
def category_apk_list(category_id, page):
    category = Category.query.get(category_id)
    pagination = CategoryApk.query.filter_by(category_id=category_id).paginate(
        page, per_page=app.config['GAME_NUM_PER_PAGE'], error_out=False)
    category_apks = pagination.items
    return render_template('apk/category_apk_list.html', category_apks=category_apks, category=category,
                           pagination=pagination)


@apk.route('/category/<category_id>/apk/<page>/del/<apk_id>')
@login_required
def category_apk_del(page, category_id, apk_id):
    try:
        apk_ids = apk_id.split(",")
        CategoryApk.query.filter(CategoryApk.apk_id.in_(apk_ids),
                                 CategoryApk.category_id == category_id).delete(
                                synchronize_session='fetch')
        db.session.commit()
        flash('del success.')
    except Exception, e:
        db.session.rollback()
        flash('del fail.', 'error')
    return redirect(url_for('apk.category_apk_list', category_id=category_id, page=page))
