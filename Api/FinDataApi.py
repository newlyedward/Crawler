from flask import Flask, request, Response, jsonify, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
import pandas as pd
import json
import datetime as dt

from Quant.future import Future
from Quant.instrument import Instrument
from utils import LogHandler

log = LogHandler('FinDataApi')

app = Flask(__name__, static_url_path='')
Bootstrap(app)


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
def home():
    return render_template('home.html')


# @app.route('/service')
# def service():
#     return 'service'
#
#
# @app.route('/about')
# def about():
#     return 'about'


@app.route('/segment/', methods=['POST'])
def segment():
    response = jsonify({'result': 'none'})
    if request.method == 'POST' and request.form:
        params = request.form.to_dict()
        try:
            if params['asset'] == '期货':
                future = Future()
                if params['segment'] == '主力合约' or params['segment'] == '商品指数':
                    response = Response(future.variety().to_json(orient='split', force_ascii=False),
                                        mimetype='application/json')
                elif params['segment'] == '大商所':
                    response = Response(future.contract('DCE', update=dt.datetime.now())
                                        .to_json(orient='split', force_ascii=False), mimetype='application/json')
                elif params['segment'] == '期权':
                    response = Response(future.option(update=dt.datetime.now())
                                        .to_json(orient='split', force_ascii=False), mimetype='application/json')
        except KeyError:
            text = json.dumps(params, ensure_ascii=False)
            log.info('/segment/params is error: %s', text)
            response = jsonify({'result': 'KeyError'})

    return response


@app.route('/hq/<asset>/<segment>/<code>')
def hq(asset, segment, code):
    return render_template("hq.html", asset=asset, segment=segment, title=code)


@app.route('/hq/data/', methods=['POST'])
def data():
    response = jsonify({'result': 'none'})

    if request.method != 'POST' or not request.form:
        return response

    params = request.form.to_dict()

    try:
        asset = params['asset']
        segment = params['segment']
        code = params['code']
        period = params['period']
    except KeyError:
        response = jsonify({'result': 'KeyError'})

    instrument = Instrument(market=segment, period=period)
    if segment == 'maincontract':
        code = code + 'l8'
    elif segment == 'cindex':
        code = code + 'l9'

    df = instrument.bar(code, asset, ktype=period)
    dfj = df.to_json(orient='split', date_format='epoch', date_unit='ms')
    response = Response(dfj, mimetype='application/json')
    return response


def run():
    app.run(debug=True)


if __name__ == '__main__':
    app.run(debug=True)  # default host='0.0.0.0', port=5000
