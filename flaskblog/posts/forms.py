from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, EqualTo, ValidationError

class PostForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired()])
    content = TextAreaField('Content',validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpeg','jpg', 'png'])])
    submit = SubmitField('Post')

class CommentForm(FlaskForm):
    content = TextAreaField('Content')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Post')
