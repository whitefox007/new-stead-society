from flask import render_template, Blueprint

projects = Blueprint('projects', __name__)


@projects.route('/project')
def project():
    return render_template('project.html', title='Project Page')


@projects.route('/projects_link')
def projects_link():
    return render_template('projects_link.html', title='Project Page')