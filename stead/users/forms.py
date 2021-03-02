# Form Based Imports
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms import ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired

from flask_login import current_user
# User Based Imports
from flask_login import current_user
from stead.models import User


class RegistrationForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    middleName = StringField('Middle Name')
    lastName = StringField('Late Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=4,
                                                                          max=50)])  # check the username and also check for validation
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    phoneNumber = StringField('Phone Number', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired(), Length(min=4, max=100)])
    dateOfBirth = DateField('Date Of Birth', validators=[DataRequired()], format='%Y-%m-%d')
    gender = RadioField('Select Your Sex', choices=[('male', 'Male'), ('female', 'Female')],
                        validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Sign Up')

    @staticmethod
    def check_email(field):
        # Check if not None for that user email!
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Your email has been registered already!')

    @staticmethod
    def check_username(self, field):
        # Check if not None for that username!
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Sorry, that username is taken')

    def validate(self):
        if not super(RegistrationForm, self).validate():
            return False

        if User.query.filter_by(username=self.username.data).first():
            self.username.errors.append("Sorry, that username is taken")
            return False
        elif User.query.filter_by(email=self.email.data).first():
            self.email.errors.append("Your email has been registered already!")
            return False
        return True


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')

    def validate(self):
        if not super(LoginForm, self).validate():
            return False

        self.user = User.authenticate(self.email.data, self.password.data)
        if not self.user:
            self.password.errors.append("Invalid password.")
            return False
        return True


class EditNameForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    submit = SubmitField('Save')


class EditPasswordForm(FlaskForm):
    current_password = PasswordField('Current password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired(), Length(min=8, max=50)])
    confirm_new_password = PasswordField('Reenter password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Save')

    def validate(self):
        if not super(EditPasswordForm, self).validate():
            return False

        self.user = User.authenticate(current_user.email, self.current_password.data)
        if not self.user:
            self.current_password.errors.append("Invalid password.")
            return False
        return True


class ChangeProfileForm(FlaskForm):
    profile_pic = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png']), FileRequired()])
    submit = SubmitField('Save')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    submit = SubmitField('Reset Password')


class PasswordResetForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[
        DataRequired(), EqualTo('confirm_new_password', message='Passwords must match')])
    confirm_new_password = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Reset Password')


class FinancialForm(FlaskForm):
    financial_recorded = FileField('Update Profile Picture', validators=[FileAllowed(['xcel'])])
    submit = SubmitField('Submit Record')


class ClassRegistrationForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    middleName = StringField('Middle Name')
    lastName = StringField('Late Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phoneNumber = StringField('Phone Number', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired(), Length(min=4, max=100)])
    course1 = SelectField('Select Course',
                          choices=[('None', ''), ('Python', 'Python'), ('Revit', 'Revit'), ('Electronic', 'Electronic'),
                                   ('Microsoft Suite', 'Microsoft Suite')], )
    course2 = SelectField('Select Course',
                          choices=[('None', ''), ('Python', 'Python'), ('Revit', 'Revit'), ('Electronic', 'Electronic'),
                                   ('Microsoft Suite', 'Microsoft Suite')], )
    course3 = SelectField('Select Course',
                          choices=[('None', ''), ('Python', 'Python'), ('Revit', 'Revit'), ('Electronic', 'Electronic'),
                                   ('Microsoft Suite', 'Microsoft Suite')], )
    course4 = SelectField('Select Course',
                          choices=[('None', ''), ('Python', 'Python'), ('Revit', 'Revit'), ('Electronic', 'Electronic'),
                                   ('Microsoft Suite', 'Microsoft Suite')], )
    submit = SubmitField('Sign Up')

    @staticmethod
    def check_email(field):
        # Check if not None for that user email!
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Your email has been registered already!')

    def validate(self):
        if not super(ClassRegistrationForm, self).validate():
            return False

        if User.query.filter_by(email=self.email.data).first():
            self.email.errors.append("Your email has been registered already!")
            return False
        return True
