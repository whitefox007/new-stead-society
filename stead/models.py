from stead import db, login_manager, app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from stead.role.models import Role, Permission
from stead.news_posts.models import NewsPost
from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


# By inheriting the UserMixin we get access to a lot of built-in attributes
# which we will be able to call in our views!
# is_authenticated()
# is_active()
# is_anonymous()
# get_id()


# The user_loader decorator allows flask-login to load the current user
# and grab their id.

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model, UserMixin):
    # Create a table in the db
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, index=True, nullable=False)
    middle_name = db.Column(db.String, index=True, nullable=False)
    last_name = db.Column(db.String, index=True, nullable=False)
    email = db.Column(db.String(64), unique=True)
    username = db.Column(db.String(64), unique=True)
    profile_image = db.Column(db.String(20), nullable=False, default='avarta.png')
    password_hash = db.Column(db.String(128))
    birthday = db.Column(db.Date)
    address = db.Column(db.String)
    phone_no = db.Column(db.String)
    gender = db.Column(db.String)
    confirmed = db.Column(db.Boolean, default=True)
    posts = db.relationship('Post', backref='author', lazy=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    news_post = db.relationship('NewsPost', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    followed = db.relationship('Follow',
                                foreign_keys=[Follow.follower_id],
                                backref=db.backref('follower', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    def __repr__(self):
        return '<User %r>' % self.first_name, self.last_name, self.email, self.username, self.password_hash, \
                self.profile_image, self.gender, self.role_id, self.phone_no, self.birthday, self.address

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        self.follow(self)
        if self.role is None:
            if self.email == 'movie.alvina@gmail.com' or 'alimamyconteh099@gmail.com':
                self.role = Role.query.filter_by(name='Administrator').first()
        if self.role is None:
            self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # https://stackoverflow.com/questions/23432478/flask-generate-password-hash-not-constant-output
        return check_password_hash(self.password_hash, password)

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)

    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        if user.id is None:
            return False
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        if user.id is None:
            return False

        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    @staticmethod
    def authenticate(email, password):

        user = User.query.filter(User.email == email).first()
        if user and user.check_password(password):
            return user
        return False

    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.user_id) \
            .filter(Follow.follower_id == self.id)

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def __repr__(self):
        return '<Comment %r>' % self.body


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.TEXT, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    def __init__(self, content, user_id):
        self.content = content
        self.user_id = user_id


class ClassRegistration(db.Model):
    CATEGORY = (
        ('Python', 'Python'),
        ('Revit', 'Revit'),
        ('Electronic', 'Electronic'),
        ('Microsoft Suite', 'Microsoft Suite'),
    )

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, index=True, nullable=False)
    middle_name = db.Column(db.String, index=True, nullable=False)
    last_name = db.Column(db.String, index=True, nullable=False)
    email = db.Column(db.String(64), unique=True)
    address = db.Column(db.String)
    phone_no = db.Column(db.String)
    course1 = db.Column(db.String)
    course2 = db.Column(db.String)
    course3 = db.Column(db.String)
    course4 = db.Column(db.String)
