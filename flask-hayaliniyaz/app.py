from email.policy import default
from flask import Flask , render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os

DB_NAME='dreamlist.db'

app=Flask(__name__)
app.config['SECRET_KEY']="bcvbcvbvb"
app.config['SQLALCHEMY_DATABASE_URI']=f"sqlite:///{DB_NAME}"
db=SQLAlchemy(app)

class Users(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100), nullable=False)
    surname=db.Column(db.String(100), nullable=False)
    email=db.Column(db.String(100), nullable=False)
    password=db.Column(db.String(200), nullable=False)
    dreams=db.relationship('Dreams', backref='dreamer')

    def __repr__(self):
        return self.name+" "+self.surname

class Dreams(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    dream=db.Column(db.String(300), nullable=False)
    detail=db.Column(db.Text)
    quote=db.Column(db.String(300), nullable=False)
    date_added=db.Column(db.DateTime)
    dreamer_id=db.Column(db.Integer, db.ForeignKey('users.id'))

@app.route("/")
def home():
    if 'email' in session:
        email=session['email']
        me=Users.query.filter_by(email=email).first()
        dreams=Dreams.query.all()
        return render_template('home.html', me=me, dreams=dreams)
    return  redirect(url_for('login'))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method=="POST":
        name=request.form.get('name')
        surname=request.form.get('surname')
        email=request.form.get('email')
        password=request.form.get('password')

        search=Users.query.filter_by(email=email).first()
        if search !=None:
            flash('Bu email ile bir hesap zaten var!!')
            return render_template('register.html')
        new_user=Users(name=name, surname=surname,
                    email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if 'email' in session:
        return redirect(url_for('home'))
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")

        search=Users.query.filter_by(email=email).first()
        if search is None:
            flash('Düzgün gir şunları!!')
            return render_template('login.html')
            
        if password==search.password:
            session['email']=email
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.pop("email", None)
    return redirect(url_for('login'))

@app.route("/create", methods=["GET", "POST"])
def create():
    if 'email' in session:
        email=session['email']
        me=Users.query.filter_by(email=email).first()
        if request.method=="POST":
            dream=request.form.get("dream")
            detail=request.form.get("detail")
            quote=request.form.get("quote")
            new_dream=Dreams(dream=dream, detail=detail,
                           quote=quote, dreamer_id=me.id )
            db.session.add(new_dream)
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('create.html')

@app.errorhandler(404)
def error(e):
    return render_template('404.html')

if __name__=="__main__":
    if not os.path.exists(DB_NAME):
        db.create_all(app=app)
        print("Database Oluşturuldu!")

    app.debug=True
    app.run()