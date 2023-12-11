import base64
import random
import string
from datetime import datetime


import psycopg2
from flask import Flask, jsonify, render_template, redirect, url_for, request, flash, session
from werkzeug.utils import secure_filename
import secrets, os
import predictor
import numpy as np
import cv2
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

con = psycopg2.connect(database="xx", user="xx", password="xx",
                       host="xx", port="5432")
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

#create flask project
app = Flask(__name__)
#A secret key that will be used for securely signing the session cookie
app.secret_key = '###!!#%$%#'
#serve a page to the client and establishes a connection
socketio = SocketIO(app)
#store files located outside the actual application package
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), "uploads")



#We then use the route() to tell Flask what URL should trigger our function.
@app.route('/upload_file')
def upload_file():
    if 'loggedin' in session:
        return render_template('index2.html')



#We then use the route() decorator to tell Flask what URL should trigger our function.
@app.route('/')
def index():
    if 'loggedin' in session:
        return render_template("index.html")
    else:
        return render_template('login.html')


    

#We then use the route() decorator to tell Flask what URL should trigger our function.
@app.route('/discarded')
def discarded():
    if 'loggedin' in session:
        cursor = con.cursor()
        cursor.execute("SELECT class, tstamp ,image, id FROM results;")
        results = cursor.fetchall()
        context = []
        for result in results:
            obj = {}
            obj['cls'] = result[0]
            obj['time'] = result[1]
            id = result[3]
            img = base64.b64encode(result[2]).decode('utf-8')
            obj['img'] = img
            obj['id'] = id
            context.append(obj)
        return render_template("index.html", context=context)
    else:
        return render_template('login.html')

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

#We then use the route() decorator to tell Flask what URL should trigger our function.
@app.route('/classify', methods=['GET', 'POST'])
def classify():
    if request.method == 'POST' and 'loggedin' in session:
        startDate = request.form.get('startDate')
        endDate = request.form.get('endDate')
        startDate = datetime.strptime(startDate, "%d/%m/%Y")
        endDate = datetime.strptime(endDate, "%d/%m/%Y")

        cursor = con.cursor()
        classes = []


        cursor.execute("""SELECT * FROM results WHERE tstamp BETWEEN %s and %s;""", (startDate, endDate))
        results = cursor.fetchall()
        for res in results:
            id = res[0]
            img = res[5]
            ext = res[6]

            filename = id_generator() + ext
            pth = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f = open(pth, 'wb')
            f.write(img)
            f.close()

            #Predict
            prediction = predictor.predict(pth)
            os.remove(pth)
            #Save into database
            update_cursor = con.cursor()
            cls = 0
            if prediction == "Plain Road":
                cls = 1
            update_cursor.execute(f"UPDATE results set class = {cls} where id = {id}")
            con.commit()



            classes.append({"id": id, "class": prediction, "date": str(datetime.today().strftime("%a, %d %b %Y"))})
        return jsonify({"predictions": classes})
    else:
        return render_template('login.html')





#We then use the route() decorator to tell Flask what URL should trigger our function.
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        # Create variables for easy access
        email = request.form['email']
        user_password = request.form['password']
        # Check if account exists using MySQL
        cursor = con.cursor()
        cursor.execute('SELECT * FROM potholeusers WHERE username = %s AND password = %s', (email, user_password,))
        # Fetch one record and return result
        users = cursor.fetchone()
        # If account exists in accounts table in out database
        if users:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['user_id'] = users[0]
            session['user_name'] = users[1]
            # Redirect to home page
            return redirect(url_for('index'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    return render_template('login.html', msg=msg)

#We then use the route() decorator to tell Flask what URL should trigger our function.
@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if 'loggedin' in session:
        if request.method == 'GET':
            return render_template("index2.html")

        files = request.files.getlist('file')
        resp = []
        no_of_files = len(files)

        i = 0
        for file in files:
            filename = secrets.token_hex(8)
            _, f_ext = os.path.splitext(file.filename)
            filename = filename + f_ext
            pth = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(pth)
            res = predictor.predict(pth)
            # Save into Database
            f = open(pth, 'rb')
            file_data = f.read()
            cursor = con.cursor()
            res_int = 0
            if res == "Plain Road":
                res_int = 1
            else:
                res_int = 0
            cursor.execute("INSERT INTO results(image, class, ext, tstamp) VALUES (%s,%s,%s, %s) RETURNING id",
                           (file_data, res_int, f_ext, datetime.now()))
            f.close()
            con.commit()
            resp.append({"no": i, "result": res, "img": base64.b64encode(file_data).decode("utf-8")})

        flash("Results Fetched")
        return render_template("index2.html", context=resp)
    else:
        msg = 'Please Login'
    return render_template('login.html', msg=msg)

#We then use the route() decorator to tell Flask what URL should trigger our function.
@app.route('/all_results')
def all_results():
    if 'loggedin' in session:
        cursor = con.cursor()
        cursor.execute("SELECT class, tstamp ,image, ext FROM results;")
        results = cursor.fetchall()
        context = []
        for result in results:
            obj = {}
            obj['cls'] = result[0]
            obj['time'] = result[1]
            ext = result[3]
            img = base64.b64encode(result[2]).decode('utf-8')
            obj['img'] = img
            obj['ext'] = ext
            context.append(obj)

        return render_template("results.html", context=context)
    else:
        return render_template('login.html')

#We then use the route() decorator to tell Flask what URL should trigger our function.
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    return redirect(url_for('login'))


@socketio.on('disconnect')
def disconnect_user():
    session.pop('loggedin', None)


if __name__ == '__main__':
    app.run()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
