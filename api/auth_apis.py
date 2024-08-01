import json
import os
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import current_app as flask_app, Blueprint
from flask import jsonify, session, render_template, redirect, url_for, flash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_wtf.csrf import CSRFProtect

from forms import DataForm, EmailForm, OTPForm

api_blueprint = Blueprint('auth_blueprint', __name__)


@api_blueprint.route('/form', methods=['GET', 'POST'])
def form():
    form = DataForm()
    if form.validate_on_submit():
        data = {'name': form.name.data, 'language': form.language.data}
        with open("data_file.json", 'r') as r:
            content = r.read()
        if not content:
            with open("data_file.json", 'w') as w:
                w.write(json.dumps(data))
        else:
            existing_data = json.loads(content)
            existing_data.update(data)
            with open("data_file.json", 'w') as w:
                w.write(json.dumps(existing_data))
        flash('Data added successfully')
        return redirect(url_for('auth_blueprint.form'))
    return render_template('form.html', form=form)


# Email
def send_otp_email(recipient_email, otp):
    print("**** SENDING MAIL ****")
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    email_user = os.getenv('EMAIL_USER', 'defaultmail@gmail.com')
    email_password = os.getenv('EMAIL_PASSWORD', 'default_password')

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = recipient_email
    msg['Subject'] = 'Your OTP Code'

    body = f'Your OTP code is {otp}'
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_user, email_password)
        text = msg.as_string()
        server.sendmail(email_user, recipient_email, text)
        server.quit()
    except Exception as e:
        flask_app.logger.error(f"Error sending email: {e}")


def generate_and_store_otp(email):
    otp = random.randint(100000, 999999)
    with open('otp_data.json', 'r') as file:
        otp_data = json.load(file)
    otp_data[email] = otp
    with open('otp_data.json', 'w') as file:
        json.dump(otp_data, file)
    return otp


@api_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = EmailForm()
    if form.validate_on_submit():
        email = form.email.data
        otp = generate_and_store_otp(email)
        send_otp_email(email, otp)
        session['email'] = email
        flash('OTP sent to your email. Please check your email.')
        return redirect(url_for('auth_blueprint.verify_otp'))
    return render_template('register.html', form=form)


@api_blueprint.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    form = OTPForm()
    if form.validate_on_submit():
        email = session.get('email')
        entered_otp = form.otp.data
        with open('otp_data.json', 'r') as file:
            otp_data = json.load(file)
        if otp_data.get(email) == int(entered_otp):
            access_token = create_access_token(identity=email)
            message = 'Login successful!'
            return render_template('verify_result.html', message=message, access_token=access_token)
        else:
            message = 'Invalid OTP. Login unsuccessful.'
            return render_template('verify_result.html', message=message)
    return render_template('verify_otp.html', form=form)


@api_blueprint.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200