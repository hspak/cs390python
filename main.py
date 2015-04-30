from flask import Flask, render_template, request, session, escape, redirect, url_for
from parse_rest.user import User
from parse_rest.datatypes import Object
from parse_setup import setup

app = Flask(__name__, static_folder='static', static_url_path='')
app.secret_key = 'Super secret string'

class Post(Object):
  pass

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        username = escape(session['username'])
        if request.method == 'POST':
            user = User.Query.get(username=username);
            post = Post(text=request.form['post'])
            #post.image = request.form['file']
            post.groups = [{'UniqueID':'Family'}, {'UniqueID2':'Friends'}]
            post.user = user
            post.save()
            return render_template('home.html', username=username)
        else:
            return render_template('home.html', username=username)
    else:
        return render_template('signup.html')

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

@app.route('/circles')
def circles():
  if 'username' in session:
      friends = User.Query.all();
      return render_template('circles.html', friends=friends)
  else:
      return render_template('signup.html')

@app.route('/search')
def search():
    if 'username' in session:
        search = request.args.get('search')
        friends = User.Query.all();
        return render_template('search.html', friends=friends)
    else:
        return render_template('signup.html')

@app.route('/settings', methods=['GET', 'POST'])
def change():
    if 'username' in session:
        if request.method == 'POST':
            old_user = escape(session['username'])
            old_pass = escape(session['password'])
            user = User.login(old_user, old_pass)
            user.username = request.form['username']
            user.password = request.form['password']
            user.save()
            session.pop('username', None)
            return render_template('index.html')
        else:
            return render_template('settings.html')
    else:
        return render_template('signup.html')

@app.route('/addfriend')
def addfriend():
    if 'username' in session:
        # TODO: friends table?
        return request.args.get('email')
    else:
        return render_template('signup.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
