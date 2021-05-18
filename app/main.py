# -*- coding: utf-8 -*-
"""

@author: M
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '1'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///DataBase.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

import routes

'''
from Models import Book, User

from main import db

#b = Book(title = 'ml',author = 'mohamed',publication='science',
#         ISBN = '1568',content = 'ml course',price = 1000, piece = 5,
#         image_file = 'C:\\Users\\M\\app\\static\\book_profile\\defalt.jpg')
b = User.query.filter_by(id= 1 ).first()
print(b)
db.session.delete(b)
db.session.commit()
'''

