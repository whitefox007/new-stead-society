from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_pagedown.fields import PageDownField


class PostForm(FlaskForm):
    content = TextAreaField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Post')


class CommentForm(FlaskForm):
    body = TextAreaField('What is your comment about my post?', validators=[DataRequired()])
    submit = SubmitField('Post')

