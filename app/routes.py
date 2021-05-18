
import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from main import app, db, bcrypt
from forms import RegistrationForm, LoginForm
from Models import User,Admin,Book,Cart,Order,OrderBook
from flask_login import login_user, current_user, logout_user, login_required



'''
def test():
    return render_template('books.html', title = 'Mohamed')
'''    
@app.route("/")
@app.route("/home")
def home():
    books=Book.query.all()
    
    return render_template('books.html', books=books)


@app.route("/about")
def about():
    return render_template('about.html', title='About')
    
@app.route("/contact")
def contact():
    return render_template('contact.html', title='Contact Page')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('signin.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)



@app.route("/book_info/<int:book_id>")
def book_info(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('infobook.html', book=book)



@app.route("/account")
@login_required
def account():
    return render_template('profile.html')
    
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))




@app.route("/addcart/<int:book_id>")
def addcart(book_id):
    if current_user.is_authenticated:
        book = Book.query.get_or_404(book_id)
        cart=Cart(user_id=current_user.id,book_id=book_id)
        db.session.add(cart)
        db.session.commit()
        flash('Book has been Successfully Added in Cart', 'success')
        return redirect(url_for('cart'))
    else:
        flash('Login to add Book in your Cart', 'danger')
        return redirect(url_for('login'))
    return render_template('infobook.html', book=book)


@app.route("/cart")
def cart():
    carts=Cart.query.filter_by(user_id=current_user.id).all()
    sum=0
    for cart in carts:
        sum=sum+cart.cartbook.price
    return render_template('cart.html', carts=carts,total=sum) 