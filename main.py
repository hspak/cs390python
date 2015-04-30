from flask import Flask, render_template, request, session, escape, redirect, url_for
from parse_rest.user import User
from parse_rest.datatypes import Object
from parse_setup import setup
import json, httplib

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__, static_folder='static', static_url_path='')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
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
        password = escape(session['password'])
        if request.method == 'POST':
            user = User.login(username, password)
            post = Post(text=request.form['post'])
            pic = request.files['file']
            print "wtf"
            if pic:
                headers = {
                "X-Parse-Application-Id": "h2Co5EGV2YoBuPL2Cl7axkcLE0s9FNKpaPcpSbNm",
                "X-Parse-REST-API-Key": "o59euguskg7BBNZlFEuVxTNL0u93glStq7memfVH",
                "Content-Type": "image/jpeg"
                }
                connection = httplib.HTTPSConnection('api.parse.com', 443)
                connection.connect()
                connection.request('POST', '/1/files/pic.jpg', pic, headers)
                result = json.loads(connection.getresponse().read())
                print result

            post.circles = user.postingTo
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
    u.postingTo = ['all']
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
def settings():
    if 'username' in session:
        old_user = escape(session['username'])
        old_pass = escape(session['password'])
        user = User.login(old_user, old_pass)
        if request.method == 'POST':
            user.username = request.form['username']
            user.password = request.form['password']
            user.save()
            session.pop('username', None)
            
        circles = []
        for circle in user.circles:
            c = Circle.Query.get(objectId=circle.get('objectId'))
            circles.append(c.name)

        checked = list(set(circles) & set(user.postingTo))
        unchecked = list(set(circles) - set(checked))
        return render_template('settings.html', checked=checked, unchecked=unchecked)
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

@app.route('/updateCircles', methods=['POST'])
def updateCircles():
    if 'username' in session:
        old_user = escape(session['username'])
        old_pass = escape(session['password'])
        user = User.login(old_user, old_pass)
        if request.method == 'POST':
            cKeys = dict((key, request.form.getlist(key)) for key in request.form.keys())
            user.postingTo = list(cKeys.keys())
            user.save()
            return redirect(url_for('settings'))
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
