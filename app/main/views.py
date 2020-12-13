from datetime import datetime
from flask import (
    current_app,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from . import main
from .forms import NameForm
from .. import db
from ..models import User
from flask_mail import Message
from threading import Thread
from .. import mail


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


@main.route('/user/<name>')
def user(name):
    return render_template('user.html', first_name=name)
    # return '<h2>Hello, you {}</h2>'.format(name)
