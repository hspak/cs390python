from flask import Flask, render_template, request, session, escape, redirect, url_for
from parse_rest.user import User
from parse_rest.datatypes import Object
from parse_setup import setup
import urllib2

app = Flask(__name__, static_folder='static', static_url_path='')
app.secret_key = 'Super secret string'

class Post(Object):
  pass

class Circle(Object):
  pass

class Request(Object):
  pass

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        username = escape(session['username'])
        if request.method == 'POST':
            user = User.Query.get(username=username);
            post = Post(text=request.form['post'])
            if request.form['file'] != '':
                headers = {'X-Parse-Application-Id':  "h2Co5EGV2YoBuPL2Cl7axkcLE0s9FNKpaPcpSbNm",
                           'X-Parse-REST-API-Key':   "o59euguskg7BBNZlFEuVxTNL0u93glStq7memfVH",
                           'Content-Type': 'image/jpeg'} 
                print request.form['file']
                url = "https://api.parse.com/1/files/" + request.form['file']
                print url
                req = urllib2.Request(url, None, headers)
                urllib2.urlopen(req)

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
    circle = Circle(name="all", owner=u, users=[u])
    circle.save()
    u.circles = [circle]
    u.save()

    session['username'] = username
    session['password'] = password
    u = User.login(username, password)
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

@app.route('/circles', methods=['GET', 'POST'])
def circles():
    if 'username' in session:
        username = escape(session['username'])
        password = escape(session['password'])
        user = User.login(username, password)
        friends = User.Query.all();
        if request.method == 'POST':
            circle = Circle(name=request.form['name'])
            circle.users = [user]
            circle.owner = user
            user.circles.append(circle)
            circle.save()
            user.save()
        req = Request.Query.filter(toUser=username)
        return render_template('circles.html', friends=friends, user=username, req=req)
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

@app.route('/search')
def search():
    if 'username' in session:
        search = request.args.get('search')
        friends = User.Query.all();
        return render_template('search.html', friends=friends)
    else:
        return render_template('signup.html')

@app.route('/addfriend')
def addfriend():
    if 'username' in session:
        email = request.args.get('email')
        friend = User.Query.get(email=escape(email))
        req = Request(fromUser=session['username'], toUser=friend.username)
        req.save()
        return redirect(url_for('index'))
    else:
        return render_template('signup.html')

@app.route('/rmfriend')
def rmfriend():
    if 'username' in session:
        rmUsername = request.args.get('rmUser')
        username = escape(session['username'])
        user = User.Query.get(username=username)
        rmUser = User.Query.get(username=rmUsername)
        circles = Circle.Query.filter(owner=user)
        for circle in circles:
            for u in circle.users:
                if u == rmUser:
                    circle.users.remove(u)
                    circle.save()
                    break
        return redirect(url_for('index'))
    else:
        return render_template('signup.html')


@app.route('/accept')
def accept():
    if 'username' in session:
        toUser = request.args.get('toUser')
        fromUser = request.args.get('fromUser')
        username = escape(session['username'])
        toUserObj = User.Query.get(username=username)
        fromUserObj = User.Query.get(username=fromUser)

        req = Request.Query.get(toUser=toUser, fromUser=fromUser)
        req.delete()

        fromCircle = Circle.Query.get(owner=toUserObj, name="all")
        fromCircle.users.append(fromUserObj)
        toCircle = Circle.Query.get(owner=fromUserObj, name="all")
        toCircle.users.append(toUserObj)
        fromCircle.save()
        toCircle.save()
        return redirect(url_for('index'))
    else:
        return render_template('signup.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
