# -*- coding: utf-8 -*-
from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, ChangePasswordForm, RegistrationForm


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(mobile_num=form.mobile_num.data,
                    password=form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        admin = User.query.filter_by(mobile_num=form.mobile_num.data).first()
        if admin is not None and admin.verify_password(form.password.data):
            if admin.role < 3:
                flash('您不是管理员')
                return render_template('auth/login.html', form=form)
            login_user(admin, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('用户名或者密码错误')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已经登出')
    return redirect(url_for('main.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('密码已经被修改')
            return redirect(url_for('auth.logout'))
        else:
            flash('密码错误')
    return render_template("auth/change_password.html", form=form)
