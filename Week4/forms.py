from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, regexp


class DataForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    language = StringField('Language', validators=[DataRequired()])
    submit = SubmitField('Submit')


class EmailForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(),
        regexp(r'^[a-zA-Z0-9._%+-]+@gmail\.com$', message="Email must be in the format '[a-zA-Z0-9._%+-]@gmail.com'")
    ])
    submit = SubmitField('Send OTP')


class OTPForm(FlaskForm):
    otp = StringField('OTP', validators=[DataRequired()])
    submit = SubmitField('Verify OTP')
