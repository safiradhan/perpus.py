from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from sqlalchemy import text
import base64
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:postgres@localhost/latihan_baru'
app.config['SECRET_KEY']='secret'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


class User(db.Model):
    id_user = db.Column(db.Integer, primary_key=True, index=True)
    full_name = db.Column(db.String(40), nullable=False)
    user_name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(45), nullable=False, unique=True)
    password = db.Column(db.String(30), default=False, unique=True)
    admin = db.Column(db.Boolean, default=False)
    rent_user = db.relationship('Administration', backref = 'renter', lazy = 'dynamic')
    def __repr__(self):
        return f'User <{self.email}>'

class Book(db.Model):
    book_id = db.Column(db.Integer, primary_key=True, index= True)
    book_name = db.Column(db.String(40), nullable=False)
    book_author = db.Column(db.String(40), nullable=False, unique=True)
    book_year = db.Column(db.Integer, nullable=False)
    book_count = db.Column(db.Integer, nullable=False)
    rent_book = db.relationship('Transaksi', backref = 'pegunjung', lazy = 'dynamic')
    def __repr__(self):
        return f'Book <{self.book_name}>'

class Transaksi(db.Model):
    booking_id = db.Column(db.Integer, primary_key = True, index = True)
    rent_date = db.Column(db.String(25), nullable = False)
    rent_due = db.Column(db.String(25), nullable = False)
    is_returned = db.Column(db.Boolean, default = False)
    return_date = db.Column(db.String(25))
    fine = db.Column(db.Integer, nullable = False, default = 0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable = False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.book_id'), nullable = False)

    def __repr__(self):
        return f'Transaksi <{self.booking_id}>'
################################################################user###################################################
def get_userData(id):
    return User.query.filter_by(user_id=id).first_or_404()

def get_bookData(id):
    return Book.query.filter_by(book_id=id).first_or_404()

def get_rentData(id):
    return Transaksi.query.filter_by(booking_id=id).first_or_404()

def authz():
    token = request.headers.get('Authorization')
    token2 = token.replace("Basic ","")
    plain = base64.b64decode(token2).decode('utf-8')
    plain3 = plain.split(":")
    user = User.query.filter_by(user_name=plain3[0]).first()
    a = False
    if user is None :
        return a
    else: 
        hashcheck = bcrypt.check_password_hash(user.password, plain3[1])
        return hashcheck

def get_auth(user_name, password):
    return User.query.filter_by(user_name=user_name, password=password).first()

def return_user(u):
    return {'user id' : u.user_id,'username':u.user_name,'full name':u.full_name, 'email' : u.email, 'admin': u.admin}

def return_book(b):
    return {'book id' : b.book_id,'book name':b.book_name, 'author': b.book_author,
        'release year' : b.release_year, 'stock' : b.book_count}

def return_rent(rent):
    return {"1 Booking Information":{
                'Booking id': rent.booking_id, 
                'Rent date':rent.rent_date, 
                'Rent due': rent.rent_due, 
                'Is returned': rent.is_returned, 
                'Return date':rent.return_date, 
                'Fine': rent.fine
            },
            '2 Renter Information':{  
                'Name':rent.renter.full_name, 
                'Email': rent.renter.email, 
                'User id': rent.renter.user_id
                }, 
            '3 Book Information':{ 
                'Book id': rent.bookr.book_id, 
                'Book name': rent.bookr.book_name, 
                'Release year': rent.bookr.release_year, 
                'Book Author': rent.bookr.book_author, 
                'Book Publisher': rent.bookr.publisher
            }
        }

def get_hash(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')
@app.route('/user/')
def get_users():
    return jsonify([
        {
            'id' : user.public_id, 'name': user.name, 'email' : user.email,
            'password': user.password
            } for user in user.query.all()
    ])

def libraryFine(returned, deadLine):
    dmy1 = returned.split('/')
    d1 = int(dmy1[0])
    m1 = int(dmy1[1])
    y1 = int(dmy1[2])
    
    dmy2 = deadLine.split('/')
    d2 = int(dmy2[0]) 
    m2 = int(dmy2[1])
    y2 = int(dmy2[2])
    
    if d2 < d1 and m2 == m1 and y2 == y1:
        res = (d1 - d2) * 15
    elif m2 < m1 and y2 == y1:
        res = (m1 - m2) * 500
    elif y2 < y1:
        res = 10000
    else:
        res = 0
    
    return res
def count_stock(book_id):
    query =  Transaksi.query.filter_by(is_returned=False, book_id=book_id).count()
    return query


@app.route('/testAuth/', methods=['GET'])
def testAuth():
    resp = request.headers['Authorization']
    resp = resp.replace('Basic ', '')
    decode = base64.b64decode(resp).decode('utf-8')
    decode = decode.split(':')
    
    if (decode[0] == 'safira') and (decode[1] == 'firafira23'):
        return {
            'message' : decode
        }
    else:
        return 'Invalid User', 401


#############################################book#############################################################
@app.route('/users/')
def get_users():
    return jsonify([return_user(user) for user in User.query.all ()])

@app.route('/book/')
def get_book():
    return jsonify([
        {
            'book_id' : book.book_id, 'book_name': book.book_name, 'book_year' : book.book_year,
            'book_count': book.book_count
            } for book in Book.query.all()
    ])
@app.route('/users/<id>/')
def get_user(id):
    user = get_userData(id)
    return return_user(user)

@app.route('/book/<book_id>/')
def get_bookData(book_id):
    print(book_id)
    book = book.query.filter_by(book_id=id).first_or_404()
    return {
        'book_id' : book.book_id,
        'book_name' : book.book_name,
        'book_title': book.book_title, 
        'book_year': book.book_year,
        'book_count' : book.book_count
        }
######################################################TRANSAKSI######################################################
# @app.route('/rent/')
# def get_transaksi():
#     token = request.headers.get('Authorization')
#     token2 = token.replace("Basic ","")
#     plain = base64.b64decode(token2).decode('utf-8')
#     plain3 = plain.split(":")
#     book = book.query.filter_by(user_name=plain3[0], password=plain3[1]).fist()
#     if plain3[0] in user.user_name and plain[1] in user.password:
#         return jsonify([
#         {
#             'booking_id' : Administration.booking_id, 'tanggal pinjam': Administration.tanggalpinjam, 'tanggalkembali' : Administration.tanggalkembali,
#             'telah kembali': Administration.tanggalkembali
#             } for Administration in Administration.query.all()
#     ])

#################################################################USER_CRUD#########################################################################      

@app.route('/users/', methods=['POST'])
def create_user():
    data = request.get_json()
    if (not 'user_name' in data) or (not 'email' in data) or (not 'full_name'in data):
        return jsonify({
            'error': 'Bad Request',
            'message': 'Full Name, Username or email not given'
        }), 400
    if (len(data['user_name']) < 4) or len(data['email']) < 6:
        return jsonify({
            'error' : 'Bad Request',
            'message' : 'Userame and email must be contain minimum of 4 letters'
        }), 400
    hash = get_hash(data['password'])
    u = User(
        user_name= data['user_name'],
        full_name= data['full_name'],
            email= data['email'],
            admin= data.get('admin', False),
            password= hash
        )
    db.session.add(u)
    db.session.commit()
    return  return_user(u), 201

@app.route('/book/', methods=['POST'])
def create_book():
    data = request.get_json()
    if not 'book_id' in data or not 'book_name' in data or not 'book_title' in data or not 'book_year' in data or not 'book_count':
        return jsonify({
            'error': 'Bad Request',
            'message': 'Maaf, Data yang anda masukan tidak tepat'
        }), 400
    if (len(data['book_id']) < 2) or (len(data['book_name']) < 3) or (len(data['book_title']) < 4) (len(data['book_year']) < 2):
        return jsonify({
            'error' : 'Bad Request',
            'message' : 'Maaf, Data yang anda masukan tidak tepat'
        }), 400

    b = Book(
        book_id=data['book_id'],
        book_name=data['book_name'],
        book_title=data['book_title'],
        book_year=data['book_year'],
        book_count=data['book_count'],
    )
    db.session.add(b)
    db.session.commit()
    return {
        'book_id': b.book_id, 'book_name': b.book_name,
        'book_year': b.book_year, 'book_title': b.book_title,
        'book_count': b.book_count
    },201

@app.route('/users/<id>/', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    user = get_userData(id)
    if 'user_name' in data:
        user.user_name=data['user_name']
    if 'full_name' in data:
        user.full_name=data['full_name']
    if 'email' in data:
        user.email=data['email']
    if 'admin' in data:
        user.admin=data['admin']
    db.session.commit()
    return jsonify({'Berhasil: Data pengguna telah di perbarui'}, return_user(user))

@app.route('/bookss/<id>/', methods=['PUT'])
def update_book(id):
    data = request.get_json()
    user = get_bookData(id)
    if 'book_name' in data:
        book.book_name=data['book_name']
    if 'book_author' in data:
        book.book_author=data['book_author']
    if 'book_year' in data:
        book.book_year=data['book_year']
    if 'stock' in data:
        book.book_count=data['stock']
    db.session.commit()
    return jsonify({'Berhasil': 'Data buku telah di pebarui'}, return_book(buku))

# Endpoint get data user from database filter by user code, with path parameters
@app.route('/users/<id>/', methods=['DELETE'])
def delete_user(id):
    user = User.query.filter_by(public_id=id).first_or_404()
    db.session.delete(user)
    db.session.commit()
    return {
        'success': 'Data deleted successfully'
    }

@app.route('/book/<id>/', methods=['DELETE'])
def delete_book(id):
    book = Book.query.filter_by(book_id=id).first_or_404()
    db.session.delete(book)
    db.session.commit()
    return {
        'success': 'Data deleted successfully'
    }

###################################################Transaksi############################################################
@app.route('/rents/', methods=['GET'])
def get_rents():
    login = authz()
    if login:
        return jsonify([return_rent(rent) for rent in Transaksi.query.all()])
    else: return {"Error":"Wrong Username or Password"}

@app.route('/rents/<id>/', methods=['GET'])
def get_rent(id):
    login = authz()
    if login:
        rent = get_rentData(id)
        user = get_userData(id)
        return jsonify([return_rent(rent)])
    else: return {"Error":"Wrong Username or Password"}

@app.route('/rents/users/<id>', methods=['GET'])
def get_rent_users(id):
    login = authz()
    if login:
        rent = Transaksi.query.filter_by(user_id=id)
        return jsonify([
            {
                "Book Name" : pembaca.pengunjung.book_name,
                "Renter Name" : pembaca.PEMINJAM.full_name,
                "Rent Date" : pembaca.rent_date,
                "Rent Due" : pembaca.rent_due

            }for pembaca in rent
        ])

@app.route('/rents/books/<id>', methods=['GET'])
def get_rent_books(id):
    login = authz()
    if login:
        rent = Transaksi.query.filter_by(book_id=id)
        return jsonify([
            {
                "Book Name" : userx.pengunjung.book_name,
                "User Name" : userx.PEMINJAM.full_name,
                "Rent Date" : userx.rent_date,
                "Rent Due" : userx.rent_due,
                "Is returned" : userx.is_returned

            }for userx in rent
        ])

@app.route('/rents/',methods=['POST']) # PEMINJAMAN
def create_rent():
    data=request.get_json()
    login = authz()
    if login:
        book = Book.query.filter_by(book_id=data['book_id']).first()
        book_count = count_stock(book.book_id)
        if book_count == book.book_count:
            return {"Error":"Sorry, this book has been rented out, please wait"}
        else :
            is_returned = data.get('is returned', False)
            # book = Book
            rent = Transaksi(
                rent_date = data['rent date'], rent_due = data['rent due'], user_id=data['user_id'], 
                book_id=data['book_id'], is_returned=is_returned
            )
            db.session.add(rent)
            db.session.commit()    
            return jsonify([{"Success": "Rent data has been saved"}, return_rent(rent)]), 201 
    else: return {"Error":"Wrong Username or Password"}

@app.route('/rents/<id>/',methods={'PUT'}) # PENGEMBALIAN
def update_rent(id):
    data = request.get_json()
    login = authz()
    if login:
        rent = get_rentData(id)
        if 'rent date' in data:
            rent.rent_date = data.get('rent date', rent.rent_date)
        if 'rent due' in data:
            rent.rent_due = data.get('rent due', rent.rent_due)
        if 'is returned' in data:
            rent.is_returned=data['is returned']
            if rent.is_returned:
                rent.return_date = data['return date']
                count_fine = get_fine(rent.rent_due,rent.return_date)
                rent.fine = count_fine
        db.session.commit() 
        return jsonify([{"Success": "Rent data has been updated"}, return_rent(rent)]), 201 
    else: return {"Error":"Wrong Username or Password"}

@app.route('/rents/<id>/', methods=['DELETE'])
def delete_rent(id):
    login = authz()
    if login:
        rent = Transaksi.query.filter_by(booking_id=id).first_or_404()
        db.session.delete(rent)
        db.session.commit()
        return {
            'success': 'Rent data deleted successfully'
        }  
    else: return {"Error":"Wrong Username or Password"}

if __name__ == '__main__':
    app.run(debug = True)


