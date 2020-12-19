from datetime import datetime
from flask import (
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
    flash,
)
from . import main
from .forms import NameForm, EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import User, Role
from flask_mail import Message
from threading import Thread
from .. import mail
from ..decorators import admin_required
from flask_login import login_required, current_user


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_name=form.name.data).first()
        if user is None:
            user = User(user_name=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            if current_app.config['FLASKY_ADMIN']:
                send_email(
                    current_app.config['FLASKY_ADMIN'],
                    'ny gut {}'.format(form.name.data),
                    'mail/new_user',
                    user=user
                )
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('.index'))
    return render_template(
        'index.html',
        form=form, name=session.get('name'),
        current_time=datetime.utcnow(), known=session.get('known', False)
    )


def send_email(to, subject, template, **kwargs):
    msg = Message(
        subject,
        sender=current_app.config['FLASKY_MAIL_SENDER'],
        recipients=[to]
    )
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    # here we end sending not async mails
    mail.send(msg)
    # solution instead of app => current...
    # thr = Thread(target=send_async_email, args=[current_app._get_current_object(), msg])
    # thr.start()
    # return thr
#
# def send_async_email(app, msg):
#     with app.app_context():
#          mail.send(msg)


@main.route('/user/<user_name>')
def user(user_name):
    user = User.query.filter_by(user_name=user_name).first_or_404()
    # page = request.args.get('page', 1, type=int)
    # pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
    #     page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
    #     error_out=False)
    # posts = pagination.items
    return render_template('user.html', user=user,
                           current_time=datetime.utcnow(),
                           # posts=posts,
                           # pagination=pagination
                           )


@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('.user', user_name=current_user.user_name))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form, current_time=datetime.utcnow())


@main.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.user_name = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('.user', user_name=user.user_name))
    form.email.data = user.email
    form.username.data = user.user_name
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, current_time=datetime.utcnow(), user=user)


@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "tylko dla admisiów :)"


@main.route('/user_agent')
def user_agent():
    user_agent = request.headers.get('User-Agent', 'no u-a')
    ala = request.headers.get('ala', 'no ala here')
    return (
        '<h1>Hello world!</h1>'
        '{0}<br/>{1}'.format(user_agent, ala)
    )


@main.route('/sth')
def add_url():
    return '<h1>Hello sth</h1>'


main.add_url_rule('/', 'sth', add_url)


# @main.route('/user/<name>')
# def user(name):
#     return render_template('user.html', first_name=name)
#     # return '<h2>Hello, you {}</h2>'.format(name)
