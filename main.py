from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return "post"
    else:
        return render_template('login.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
