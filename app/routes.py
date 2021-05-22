
import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from main import app, db, bcrypt
from forms import RegistrationForm, LoginForm, UpdateAccountForm
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
    return render_template('about.html')
    
@app.route("/contact")
def contact():
    return render_template('contact.html')


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


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/user_profile', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account",methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.address = form.address.data
        current_user.state = form.state.data
        current_user.pincode = form.pincode.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.address.data=current_user.address
        form.state.data=current_user.state
        form.pincode.data=current_user.pincode
        if current_user.image_file[0] == 'C':
            image_file = url_for('static', filename='user_profile/' + 'defalt.png')
        else:
            image_file = url_for('static', filename='user_profile/' + current_user.image_file)
        
    return render_template('profile.html', title='Account',image_file=image_file, form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))




@app.route("/addcart/<int:book_id>")
def addcart(book_id):
    if current_user.is_authenticated:
        book = Book.query.get_or_404(book_id)
        if book.piece <= 0:
            return render_template('infobook.html', book=book )
        else:    
            cart=Cart(user_id=current_user.id,book_id=book_id)
            db.session.add(cart)
            db.session.commit()
            flash('Book has been Successfully Added in Cart', 'success')
            return redirect(url_for('cart'))
        #book.piece -= 1

    else:
        flash('Login to add Book in your Cart', 'danger')
        return redirect(url_for('login'))
    return render_template('infobook.html', book=book )


@app.route("/cart")
def cart():
    carts=Cart.query.filter_by(user_id=current_user.id).all()
    sum=0
    for cart in carts:
        sum=sum+cart.cartbook.price
    return render_template('cart.html', carts=carts,total=sum) 

@app.route("/add_order")
def add_order():
    if current_user.is_authenticated:
        carts=Cart.query.filter_by(user_id=current_user.id).all()
        sum=0
        for cart in carts:
            sum=sum+cart.cartbook.price
        order=Order(user_id=current_user.id,amount=sum)
        db.session.add(order)
        db.session.commit()
        oid=order.id
        for cart in carts:
            orderbook=OrderBook(user_id=current_user.id,book_id=cart.cartbook.id,order_id=oid)
            cart.cartbook.piece=cart.cartbook.piece-1
            if(cart.cartbook.piece <= 0):
                return  redirect(url_for('cart'))               
            db.session.add(orderbook)
            db.session.commit()
            
        flash('Book has been Ordered Successfully', 'success')
        Cart.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        return redirect(url_for('order'))
    return render_template('order.html', title="order")

@app.route('/admin_infom')
def admin_infom():
    if current_user.is_authenticated:
        users = User.query.order_by(User.username).all()
        books = Book.query.order_by(Book.title).all()
    else:
        return redirect(url_for('about'))
    return render_template('admin_section.html', users = users , books = books)

@app.route("/order")
def order():
    orders=Order.query.filter_by(user_id=current_user.id).all()
    return render_template('order.html', orders=orders) 


@app.route("/detail/<int:order_id>")
def detail(order_id):
    orders=Order.query.get_or_404(order_id)
    orderbooks=OrderBook.query.filter_by(order_id=order_id)
    return render_template('detail_order.html', orders=orders,orderbooks=orderbooks) 



@app.route("/book_info/<int:book_id>/delete_book", methods=['POST'])
@login_required
def delete_book(book_id):
    if current_user.is_authenticated:
        book = Book.query.get_or_404(book_id)
        db.session.delete(book)
        db.session.commit()
        return redirect(url_for('home'))
