from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
import base64
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:postgres@localhost:5432/sosmed'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class usermanage(db.Model):
    user_id = db.Column(db.Integer(), primary_key=True, index=True)
    Full_name = db.Column(db.String(100), nullable= False)
    user_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), default=False, unique=True)
    
    # rent_user = db.relationship('Transaksi', backref = 'rent', lazy = 'dynamic')

class timeline(db.Model):
    post_id = db.Column(db.Integer, primary_key= True, index=True)
    post_tweet = db.Column(db.String(30), nullable= False)
    search_tweet = db.Column(db.String(30), nullable= False)
    search_user = db.Column(db.String(30), nullable= False)
    list_tweet = db.Column(db.String(100), nullable= False)

class profil(db.Model):
    profil_id = db.Column(db.Integer, primary_key=True, index=True)
    pofil_name = db.Column(db.String(225), nullable= False)
    like_tweet = db.Column(db.Integer, nullable= False)
    followers = db.Column(db.Integer, nullable= False)
    following = db.Column(db.Integer, nullable= False)
    list_name = db.Column(db.String(225), nullable= False)

class reporting(db.Model):
    report_id = db.Column(db.Integer(), primary_key=True, index=True)
    mostpopular_user = db.Column(db.Integer, nullable= False)
    mostpopular_tweet = db.Column(db.Integer, nullable= False)
    inactiveusers = db.Column(db.Integer, nullable= False)
    
def get_userData(id):
    return usermanage.query.filter_by(user_id=id).first_or_404()

def auth():
    res = request.headers.get("Authorization")
    a = res.split()
    u = base64.b64decode(a[-1]).decode('utf-8')
    b = u.split(":")
    return b

def get_auth(user_name, password):
    return usermanage.query.filter_by(user_name=user_name, password=password).first()

def return_user(u):
    return {
        'user_id': u.user_id,
        'user_name': u.user_name,
        'Full_name': u.full_name,
        'email': u.email,
        'password': u.password
    }

def get_hash(password):
    return bcrypt.generate_password_hash(password).decode('utf-8')

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

@app.route('/users/')
def get_users():
    return jsonify([return_user(user) for user in usermanage.query.all ()])

@app.route('/users/<id>/')
def get_user(id):
    user = get_userData(id)
    return return_user(user)

@app.route('/users/', methods=['POST'])
def create_user():
    data = request.get_json()
    if (not 'user_name' in data) or (not 'email' in data) or (not 'password' in data) or (not 'Full_name' in data):
        return jsonify({
            'error': 'Bad Request',
            'message': 'Data yang anda masukkan tidak tepat'
        }), 400
    if (len(data['user_name']) < 4) or (len(data['email']) < 4) or (len(data['password']) < 4) or (len(data['Full_name']) < 4):
        return jsonify({
            'error' : 'Bad Request',
            'message' : 'Data yang anda masukkan salah'
        }), 400
    hash = get_hash(data['password'])
    u = usermanage(
        user_name= data['user_name'],
        email= data['email'],
        Full_name = data['Full_name'],
        password= hash
    )
    db.session.add(u)
    db.session.commit()
    return return_user(u), 201

@app.route('/users/<id>/', methods=['PUT'])
def update_user(id):
    data = request.get_json()
    user = get_userData(id)
    if 'Full_name' in data:
        user.Full_name=data['Full_name']
    if 'user_name' in data:
        user.user_name=data['user_name']
    if 'email' in data:
        user.email=data['email']
    if 'admin' in data:
        user.admin=data['admin']
    db.session.commit()
    # return jsonify({'Berhasil: Data pengguna telah di perbarui'}, return_user(user))
    return {
        'Full_name': user.Full_name,
        'user_id': user.user_id,
        'user_name': user.user_name,
        'email': user.email,
        'password': user.password
    }


if __name__ == '__main__':
    app.run(debug = True)