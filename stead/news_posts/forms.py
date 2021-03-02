from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from flask_pagedown.fields import PageDownField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired


class NewPostForm(FlaskForm):
    # no empty titles or text possible
    # we'll grab the date automatically from the Model later
    title = StringField('Title', validators=[DataRequired()])
    text = PageDownField('Text', validators=[DataRequired()])
    picture = FileField('Blog Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('BlogPost')
