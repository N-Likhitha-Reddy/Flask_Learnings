from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash
import json
import logging
import random
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from forms import DataForm, EmailForm, OTPForm
from dotenv import load_dotenv

load_dotenv()

flask_app = Flask(__name__)
flask_app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')


class FileProcessingError(Exception):
    pass


# WTForms
@flask_app.route('/form', methods=['GET', 'POST'])
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
        return redirect(url_for('form'))
    return render_template('form.html', form=form)


# Email
def send_otp_email(recipient_email, otp):
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    email_user = os.getenv('EMAIL_USER')
    email_password = os.getenv('EMAIL_PASSWORD')

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
        flask_app.logger.info(f"OTP sent successfully to {recipient_email}")
    except smtplib.SMTPAuthenticationError as e:
        flask_app.logger.error(f"SMTP Authentication Error: {e}")
        flash("Error sending email. Please check your email credentials.")
    except smtplib.SMTPException as e:
        flask_app.logger.error(f"SMTP Error: {e}")
        flash("An error occurred while sending the email. Please try again later.")
    except Exception as e:
        flask_app.logger.error(f"Unexpected error: {e}")
        flash("An unexpected error occurred. Please try again later.")


def generate_and_store_otp(email):
    otp = random.randint(100000, 999999)
    try:
        with open('otp_data.json', 'r') as file:
            otp_data = json.load(file)
    except FileNotFoundError:
        otp_data = {}
    otp_data[email] = otp
    with open('otp_data.json', 'w') as file:
        json.dump(otp_data, file)
    return otp


@flask_app.route('/register', methods=['GET', 'POST'])
def register():
    form = EmailForm()
    if form.validate_on_submit():
        email = form.email.data
        otp = generate_and_store_otp(email)
        send_otp_email(email, otp)
        session['email'] = email
        flash('OTP sent to your email. Please check your email.')
        return redirect(url_for('verify_otp'))
    return render_template('register.html', form=form)


@flask_app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    form = OTPForm()
    if form.validate_on_submit():
        email = session.get('email')
        entered_otp = form.otp.data
        with open('otp_data.json', 'r') as file:
            otp_data = json.load(file)
        if otp_data.get(email) == int(entered_otp):
            message = 'Login successful!'
        else:
            message = 'Invalid OTP. Login unsuccessful.'
        return render_template('verify_result.html', message=message)
    return render_template('verify_otp.html', form=form)


# default page
@flask_app.route('/')
def index():
    flask_app.logger.info("Checking the count of webpage accessing")
    if 'count' in session:
        session['count'] += 1
    else:
        session['count'] = 1
    return f"Number of times page opened is: {session['count']}"


@flask_app.route('/post', methods=['POST'])
def post_data():
    try:
        logging.info("Trying to open a file")
        with open("data_file.json", 'r') as r:
            content = r.read()
    except FileNotFoundError as ex:
        logging.error("File not found error")
        return "Mentioned file doesn't exist"
    except Exception as ex:
        flask_app.logger.error(f"Unexpected error: {ex}")
        raise FileProcessingError("An error occurred while processing the file.")
    if not content:
        data = dict()
        data['Likhitha'] = 'Python'
        with open("data_file.json", 'w') as w:
            w.write(json.dumps(data))
            flask_app.logger.info("Data successfully written to data_file.json")
    else:
        with open("data_file.json", 'r') as r:
            data = json.loads(r.read())
            data['Likhitha'] = 'Python'
        with open("data_file.json", 'w') as w:
            w.write(json.dumps(data))
    return "data added successfully"


@flask_app.route('/get', methods=['GET'])
def get_data():
    try:
        with open("data_file.json", 'r') as r:
            content = r.read()
    except FileNotFoundError as ex:
        flask_app.logger.error("FileNotFoundError: data_file.json file not found")
        return "No data present in the file"
    if content:
        data = json.loads(content)
        flask_app.logger.info("Data successfully received")
        return data
    else:
        return "no data present in the file"


@flask_app.errorhandler(FileProcessingError)
def handle_file_processing_error(error):
    response = jsonify({"message": str(error)})
    response.status_code = 500
    return response


if __name__ == '__main__':
    try:
        with open('otp_data.json', 'r') as file:
            pass
    except FileNotFoundError:
        with open('otp_data.json', 'w') as file:
            json.dump({}, file)
    flask_app.run(debug=True)