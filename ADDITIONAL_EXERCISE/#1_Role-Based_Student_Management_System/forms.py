from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    # Allows role selection upon registration
    role = SelectField('Role', choices=[('viewer', 'Viewer'), ('admin', 'Admin')], validators=[DataRequired()])
    submit = SubmitField('Register')

class StudentForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Student Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Add Student')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')