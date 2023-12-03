from flask import Blueprint, render_template, abort, request, flash
from flask_login import login_required, current_user

import app
from app.models import Roles
from app import dispatcher
from sim_runner.src.api.core import Command, Opcodes

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@login_required
@main.route('/profile')
def profile():
    return render_template('profile.html', current_user=current_user)


@login_required
@main.route('/admin')
def admin():
    if current_user.role != Roles.admin:
        abort(404)

    return render_template('admin.html', current_user=current_user)


@login_required
@main.route('/upload')
def upload():
    return render_template('upload.html', current_user=current_user)


@main.route('/upload', methods=['POST'])
def signup_post():

    if request.files.get('fw') or request.files.get('config') or request.form.get('params'):
        res = dispatcher.balancer.route_message(Command(
            opcode=Opcodes.configure_autopilot,
            kwargs={
                'firmware': request.files['fw'].read().decode('utf-8')
                if request.files['fw'] else None,

                'config': request.files['config'].read().decode('utf-8')
                if request.files['config'] else [] +
                [request.form['params']] if request.form['params'] else []
            }
        ))
        if res == -1:
            flash('No available workers')
            return render_template('upload.html', current_user=current_user)
    if request.files.get('mission'):
        dispatcher.balancer.route_message(Command(
            opcode=Opcodes.upload_mission,
            kwargs={
                'mission': request.files['mission'].read().decode('utf-8')
            }
        ))
    res = dispatcher.balancer.route_message(Command(
        opcode=Opcodes.start_mission,
    ))

    if res == -1:
        flash('No available workers')
    return render_template('upload.html', current_user=current_user)