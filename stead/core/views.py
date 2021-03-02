from flask import render_template, Blueprint, make_response, redirect, url_for
from stead.models import db, User, ClassRegistration
from stead.news_posts.models import NewsPost
from flask_login import login_required
from stead.users.forms import ClassRegistrationForm

core = Blueprint('core', __name__)


@core.route('/')
def home():
    members = len(User.query.all())
    male = User.query.filter_by(gender='male').count()
    female = User.query.filter_by(gender='female').count()
    news_post = NewsPost.query.order_by(NewsPost.date.desc()).all()
    return render_template('home.html', members=members, male=male, female=female, news_post=news_post)


@core.route('/account')
def account():
    return render_template('account.html', title='User Profile')


@core.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('forum.chat')))
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)  # 30 days
    return resp


@core.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('forum.chat')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)  # 30 days
    return resp


@core.route('/about')
def about():
    return render_template('about.html', title='About Page')


@core.route('/events')
def events():
    return render_template('events.html', title='Events')


@core.route('/events/space-competition-sierra-leone')
def competition():
    return render_template('space_competition_sierra_leone.html',
                           title='SPACE SCIENCE AND ASTRONOMY COMPETITION IN SIERRA LEONE')


@core.route('/events/capacity_building', methods=['GET', 'POST'])
def capacity_building():
    form = ClassRegistrationForm()
    if form.validate_on_submit():
        user = ClassRegistration(first_name=form.firstName.data, middle_name=form.middleName.data,
                                 last_name=form.lastName.data,
                                 email=form.email.data,
                                 address=form.address.data,
                                 phone_no=form.phoneNumber.data, course1=form.course1.data,
                                 course2=form.course2.data, course3=form.course3.data, course4=form.course4.data, )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('core.home'))
    return render_template('capacity_building.html', title='Capacity Building', form=form)


@core.route('/events/student_list')
@login_required
def student_list():
    students = ClassRegistration.query.all()
    return render_template('student_list.html', title='Student List', students=students)
