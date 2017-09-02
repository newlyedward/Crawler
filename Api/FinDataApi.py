from flask import Flask, request, make_response, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
import pandas as pd

app = Flask(__name__, static_url_path='')


# class NameForm(FlaskForm):
#     name = StringField('What is your name?', validators=[Required()])
#     submit = SubmitField('Submit')
#
#
# @app.route('/user/<name>')
# def show_user_profile(name):
#     # show the user profile for that user
#     return render_template('user.html', name=name)


# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'), 404
#
#
# @app.errorhandler(500)
# def internal_server_error(e):
#     return render_template('500.html'), 500
# @app.route('/sum/<int:a>/<int:b>/')
# def sum(a, b):
#     return '%d + %d = %d' % (a, b, a + b)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/data/', methods=['POST'])
def data():
    file_string = r'J:\h5\future\dlce\day\JL8.h5'
    df = pd.read_hdf(file_string, 'table')
    dfj = df.to_json(orient='split', date_format='epoch', date_unit='ms')
    return dfj


if __name__ == '__main__':
    app.run(debug=True)  # default host='0.0.0.0', port=5000
