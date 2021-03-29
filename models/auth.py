# auth.py
import os
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import User, db
from email_validator import validate_email, EmailNotValidError

auth = Blueprint('auth', __name__)

base_inp_dir = "filesystem_for_data/Audio_input_files/"
base_out_dir = "filesystem_for_data/Audio_output_files/"
base_gmail_cred_dir = "filesystem_for_data/gmail_cred/"

@auth.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    uname = request.form.get('uname')
    password = request.form.get('psw')
    remember = True if request.form.get('remember') else False

    if ("@" in uname and "." in uname):
        user = db.query(User).filter_by(email=uname).first()
    else:
        user = db.query(User).filter_by(uname=uname).first()

    # check if user actually exists
    # take the user supplied password, hash it, and compare it to the hashed password in database
    if not user:
        flash('Username is incorrect')
        return redirect(url_for('auth.login'))

    elif not check_password_hash(user.password, password):
        flash('Password is incorrect')
        return redirect(url_for('auth.login'))

    else:
        # if the above check passes, then we know the user has the right credentials
        login_user(user, remember=remember)
        # flash('Logged in successfully!')
        return redirect(url_for('home'))


@auth.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    email = request.form.get('email')
    uname = request.form.get('uname')
    gender = request.form.get('gender')
    password = request.form.get('psw')
    con_password = request.form.get('confirmpsw')

    try:
        # Validate.
        valid = validate_email(email)

        # Update with the normalized form.
        email = valid.email
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        flash("Invalid email address: "+ str(e))
        return redirect(url_for('auth.signup'))


    if password != con_password:
        flash("Password doesn't match")
        return redirect(url_for('auth.signup'))

    user = db.query(User).filter_by(id=uname).first()  # if this returns a user, then the email already exists in database

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        flash('Username already exists')
        return redirect(url_for('auth.signup'))
        
    user = db.query(User).filter_by(email=email).first()  # if this returns a user, then the email already exists in database

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))

    user = db.query(User).filter_by(uname=uname).first()  # if this returns a user, then the email already exists in database

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        flash('Username already exists')
        return redirect(url_for('auth.signup'))
  
    # create new user with the form data. Hash the password so plaintext version isn't saved.
    new_user = User(fname = fname, lname = lname, email=email, uname=uname, gender=gender, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.add(new_user)
    db.commit()

    #adding user directories for user specific data
    if not os.path.exists(base_inp_dir+uname):
        os.mkdir(base_inp_dir+uname)
    if not os.path.exists(base_out_dir+uname):
        os.mkdir(base_out_dir+uname)
    if not os.path.exists(base_gmail_cred_dir+uname):
        os.mkdir(base_gmail_cred_dir+uname)


    flash('Your account has been registered successfully!')
    return redirect(url_for("auth.login"))

    # code to validate and add user to database goes here
    # return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))