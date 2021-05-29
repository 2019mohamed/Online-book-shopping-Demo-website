
import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from main import app, db, bcrypt
from forms import RegistrationForm, LoginForm, UpdateAccountForm, AddBookForm,UpdateBookForm
from Models import User,Book,Cart,Order,OrderBook
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
    return render_template('login.html', title='Login', form=form)



@app.route("/book_info/<int:book_id>")
def book_info(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('infobook.html', book=book)


def save_picture(form_picture , user = True):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    if user :
        picture_path = os.path.join(app.root_path, 'static/user_profile', picture_fn)
        output_size = (150, 150)
    else:
        picture_path = os.path.join(app.root_path, 'static/book_profile', picture_fn)
        output_size = (300, 300)
        
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn



@app.route("/add_book",methods=['GET', 'POST'])
def add_book():
    form = AddBookForm()
    if form.validate_on_submit():
        picture_file = save_picture(form.picture.data, user = False)
        book = Book(title=form.title.data, author=form.author.data, publication=form.publication.data,ISBN=form.ISBN.data,content=form.content.data,price=form.price.data,piece=form.piece.data,image_file=picture_file)
        db.session.add(book)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add_book.html', form=form) 
    


@app.route("/edit_book/<int:book_id>",methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    form = UpdateBookForm()
    book = Book.query.get_or_404(book_id)
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data , user = False)
            book.image_file=picture_file
        book.title=form.title.data
        book.author=form.author.data
        book.publication=form.publication.data
        book.ISBN=form.ISBN.data
        book.content=form.content.data
        book.price=form.price.data
        book.piece=form.piece.data
        db.session.commit()
        return redirect(url_for('home'))
    elif request.method == 'GET':
        form.title.data = book.title
        form.author.data = book.author
        form.publication.data=book.publication
        form.ISBN.data=book.ISBN
        form.content.data=book.content
        form.price.data=book.price
        form.piece.data=book.piece
    return render_template('add_book.html', form=form,book=book)


@app.route("/account",methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data , user= True)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.address = form.address.data
        current_user.state = form.state.data
        current_user.pincode = form.pincode.data
        db.session.commit()
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
        #if book.piece <= 0:
         #   return render_template('infobook.html', book=book )
        #else:    
        cart=Cart(user_id=current_user.id,book_id=book_id)
        db.session.add(cart)
        db.session.commit()
        return redirect(url_for('cart'))
        #book.piece -= 1

    else:
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
