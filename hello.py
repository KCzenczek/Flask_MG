from flask import (
    Flask,
    request,
    make_response,
    redirect,
    abort,
    render_template,
)


app = Flask(__name__)


@app.route('/')
def index():
    # response = make_response('<h1>Hello world!</h1>')
    # response.set_cookie('reply', '42')
    # return response
    return render_template('index.html')


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

# if __name__ == '__main__':
#     app.run()
