import os
from functools import wraps
from flask import Flask, redirect, url_for

from .projector import ProjectorSet


app = Flask(__name__)

_PROJECTOR_IP_ADDRS = os.environ.get('PROJECTOR_IP_ADDRS')
if _PROJECTOR_IP_ADDRS:
    app.config['PROJECTOR_IP_ADDRS'] = _PROJECTOR_IP_ADDRS.split(',')


@app.route('/')
def homepage():
    return '''
<doctype html>
<html>
  <head>
    <title>Gentry SDA Projectors</title>
  </head>
  <body>
    <form method="POST" action="/freeze"><input type="submit" value="Freeze"></form>
    <form method="POST" action="/unfreeze"><input type="submit" value="Unfreeze"></form>
    <form method="POST" action="/blank"><input type="submit" value="Blank"></form>
    <form method="POST" action="/unblank"><input type="submit" value="Unblank"></form>
  </body>
</html>
'''


def with_projectors(fn):
    """Pass the ProjectorSet as the first argument."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        args = (ProjectorSet(app.config['PROJECTOR_IP_ADDRS']),) + args
        return fn(*args, **kwargs)
    return wrapper


def redirect_home(fn):
    """Redirect after doing the work in the view."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        fn(*args, **kwargs)
        return redirect('/')
    return wrapper


@app.route('/freeze', methods=['POST'])
@redirect_home
@with_projectors
def freeze(projectors):
    projectors.freeze()


@app.route('/unfreeze', methods=['POST'])
@redirect_home
@with_projectors
def unfreeze(projectors):
    projectors.unfreeze()


@app.route('/blank', methods=['POST'])
@redirect_home
@with_projectors
def blank(projectors):
    projectors.blank()


@app.route('/unblank', methods=['POST'])
@redirect_home
@with_projectors
def unblank(projectors):
    projectors.unblank()
