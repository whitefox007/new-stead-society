from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from stead import db, app
from stead.models import User, Permission, Follow, Role
from stead.users.forms import RegistrationForm, LoginForm, EditNameForm, EditPasswordForm, PasswordResetRequestForm, \
    PasswordResetForm, FinancialForm, ChangeProfileForm
from flask_uploads import UploadSet, configure_uploads, DOCUMENTS
from werkzeug.security import generate_password_hash
from stead.users.picture_handler import save_picture, residue_profile_pics
from stead.decorator import admin_required, permission_required
from stead.email import send_email

users = Blueprint('users', __name__)

doc = UploadSet('photos', DOCUMENTS)
app.config['UPLOADED_PHOTOS_DEST'] = 'stead/static/financial_doc'
upload = configure_uploads(app, doc)


@users.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.blueprint != 'users' \
            and request.endpoint != 'static':
        return redirect(url_for('users.unconfirmed'))


@users.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('users.login'))
    return render_template('auth/unconfirmed.html')


@users.route('/account/<username>')
def account(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('faccount.html', title='Account Page', user=user)


@users.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        if form.picture.data:

            picture_file = save_picture(form.picture.data, 'profile_pics', (125, 125))
            # picture_file = photos.save(form.picture.data)
            user = User(first_name=form.firstName.data, middle_name=form.middleName.data, last_name=form.lastName.data,
                        username=form.username.data, email=form.email.data, birthday=form.dateOfBirth.data,
                        profile_image=picture_file, address=form.address.data,
                        phone_no=form.phoneNumber.data, gender=form.gender.data, password=form.password.data)

            db.session.add(user)
        else:
            user = User(first_name=form.firstName.data, middle_name=form.middleName.data, last_name=form.lastName.data,
                        username=form.username.data, email=form.email.data, birthday=form.dateOfBirth.data,
                        address=form.address.data,
                        phone_no=form.phoneNumber.data, gender=form.gender.data, password=form.password.data)

            db.session.add(user)
        db.session.commit()

        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')

        return redirect(url_for('core.home'))
    return render_template('auth/registration.html', form=form)


@users.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('core.home'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('core.home'))


@users.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('core.home'))


@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Grab the user from our User Models table
        user = User.query.filter_by(email=form.email.data).first()

        # Check that the user was supplied and the password is right
        # The verify_password method comes from the User object
        # https://stackoverflow.com/questions/2209755/python-operation-vs-is-not

        if user.check_password(form.password.data) and user is not None:
            # Log in the user

            login_user(user)
            flash('Logged in successfully.')

            # If a user was trying to visit a page that requires a login
            # flask saves that URL as 'next'.
            next = request.args.get('next')

            # So let's now check if that next exists, otherwise we'll go to
            # the welcome page.
            if next == None or not next[0] == '/':
                next = url_for('core.home')

            return redirect(next)
    return render_template('auth/login.html', form=form, title="Log In")


@users.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('core.home'))


@users.route("/account/edit_name", methods=['GET', 'POST'])
@login_required
def edit_name():
    form = EditNameForm()

    if form.validate_on_submit():

        current_user.first_name = form.firstName.data
        current_user.last_name = form.lastName.data
        db.session.commit()
        flash('User Account Updated')
        return redirect(url_for('core.account'))

    elif request.method == 'GET':
        form.firstName.data = current_user.first_name
        form.lastName.data = current_user.last_name

    return render_template('editUsername.html', form=form, title='Profile | Edit Name')


@users.route("/account/edit_password", methods=['GET', 'POST'])
@login_required
def edit_password():
    form = EditPasswordForm()

    if form.validate_on_submit():
        current_user.password_hash = generate_password_hash(form.new_password.data)

        db.session.commit()
        flash('User Account Updated')
        return redirect(url_for('core.account'))

    return render_template('changePassword.html', form=form, title='Profile | Edit Password')


@users.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('core.home'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('users.account', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are now following %s.' % username)
    return redirect(url_for('users.account', username=username))


@users.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('core.home'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=10,
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='users.followers', pagination=pagination,
                           follows=follows)


@users.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('users.account', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('users.account', username=username))


@users.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=20,
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='users.followed_by', pagination=pagination,
                           follows=follows)


@users.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('core.home'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token)
        flash('An email with instructions to reset your password has been '
              'sent to you.')
        return redirect(url_for('users.login'))
    return render_template('auth/reset_password1.html', form=form, title="Reset Your Password")


@users.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('core.home'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.new_password.data):
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('users.login'))
        else:
            return redirect(url_for('core.home'))
    return render_template('auth/reset_password.html', form=form, title="Password Update")

@users.route("/account/change_profile_pic", methods=['GET', 'POST'])
@login_required
def change_profile_pic():

    form = ChangeProfileForm()

    if form.validate_on_submit():
        change_profile_pic_file = save_picture(form.profile_pic.data, 'profile_pics', (125, 125))
        current_user.profile_image = change_profile_pic_file

        db.session.commit()
        residue_profile_pics()
        flash('Profile Pic has been updated')
        return redirect(url_for('core.account'))

    return render_template('change_Profile_pic.html', form=form, title='Profile | Change Profile Picture')


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


@users.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
