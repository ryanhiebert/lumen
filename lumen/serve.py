import os
from functools import wraps
from flask import Flask, redirect, url_for, render_template

from .projector import ProjectorSet


app = Flask(__name__)

_PROJECTOR_IP_ADDRS = os.environ.get('PROJECTOR_IP_ADDRS')
if _PROJECTOR_IP_ADDRS:
    app.config['PROJECTOR_IP_ADDRS'] = _PROJECTOR_IP_ADDRS.split(',')
else:
    app.config['PROJECTOR_IP_ADDRS'] = []


@app.route('/')
def homepage():
    return render_template('index.html')


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


@app.route('/poweron', methods=['POST'])
@redirect_home
@with_projectors
def poweron(projectors):
    projectors.poweron()


@app.route('/poweroff', methods=['POST'])
@redirect_home
@with_projectors
def poweroff(projectors):
    projectors.poweroff()


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
