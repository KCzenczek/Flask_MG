import os
from flask import (
    Flask,
    request,
    make_response,
    redirect,
    abort,
    render_template,
    session,
    url_for,
    flash,
)
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_mail import Message
from threading import Thread


basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY_FLASK_MG')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['FLASKY_MAIL_SENDER'] = 'Flasky admincio'
app.config['FLASKY_ADMIN'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
mail = Mail(app)


class Role(db.Model):
    #  one role many have many users
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    #  each user can have only one role
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.user_name


class NameForm(FlaskForm):
    name = StringField(
        'what is your name?',
        validators=[DataRequired()],
    )
    submit = SubmitField('send')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_name=form.name.data).first()
        if user is None:
            user = User(user_name=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                send_email(
                    app.config['FLASKY_ADMIN'],
                    'ny gut {}'.format(form.name.data),
                    'mail/new_user',
                    user=user
                )
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template(
        'index.html',
        form=form, name=session.get('name'),
        current_time=datetime.utcnow(), known=session.get('known', False)
    )


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    msg = Message(
        subject,
        sender=app.config['FLASKY_MAIL_SENDER'],
        recipients=[to]
    )
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@app.route('/user_agent')
def user_agent():
    user_agent = request.headers.get('User-Agent', 'no u-a')
    ala = request.headers.get('ala', 'no ala here')
    return (
            '<h1>Hello world!</h1>'
            '{0}<br/>{1}'.format(user_agent, ala)
    )


@app.route('/sth')
def add_url():
    return '<h1>Hello sth</h1>'


app.add_url_rule('/', 'sth', add_url)


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', first_name=name)
    # return '<h2>Hello, you {}</h2>'.format(name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# @app.route('/redirect')
# def redirection():
#     return redirect('/user_agent')
#
# @app.route('/users/<id>')
# def get_user(id):
#     user = None
#     if not user:
#         abort(404)
#     return 'yo man'


if __name__ == '__main__':
    app.run()
