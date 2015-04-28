from flask import Flask, render_template, request, session, escape, redirect, url_for
from parse_rest.user import User
from parse_setup import setup

app = Flask(__name__)
app.secret_key = 'Super secret string'

@app.route('/')
def index():
    if 'username' in session:
        user = escape(session['username'])
        return render_template('index.html', user=user)
    else:
        return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    u = User.signup(username, password, email=email)
    u.save()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        session['username'] = username
        session['password'] = password
        u = User.login(username, password)
        u.save()
        return redirect(url_for('index'))
    else:
        if 'username' in session:
            return redirect(url_for('index'))
        else:
            return render_template('login.html', new=True)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.debug = True
    app.run()
