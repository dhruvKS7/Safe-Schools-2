from flask import render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
from app import app
from app import database
from decimal import Decimal

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route('/')
def index():
    return render_template('index.html', dis='hide', msg='')

@app.route('/logout', methods=['POST'])
def logoutHandler():
    if request.method == 'POST':
        session['user'] = None
        return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def loginHandler():
    if request.method == 'POST':
        username = str(request.form.get("loginusername"))
        password = str(request.form.get("loginpassword"))
        output = database.login(username, password)
        if output == 'success':
            session['user'] = username
            return redirect(url_for('search'))
        else:
            return redirect(url_for('indexerr', msg=output))

@app.route('/register', methods=['POST'])
def registerHandler():
    if request.method == 'POST':
        username = str(request.form.get("registerusername"))
        password = str(request.form.get("registerpassword"))
        firstname = str(request.form.get("firstname"))
        lastname = str(request.form.get("lastname"))
        output = database.register(username, password, firstname, lastname)
        if output == 'success':
            return redirect(url_for('index'))
        else:        
            return redirect(url_for('indexerr', msg=output))

@app.route('/index')
def index2():
    return render_template('index.html', dis='hide', msg='')

@app.route('/indexerr/<msg>')
def indexerr(msg):
    return render_template('index.html', dis='show', msg=msg)

@app.route('/search')
def search():
    if session['user'] == None:
        return redirect(url_for('indexerr', msg="Invalid access"))
    else:
        schools = database.getSchools()
        return render_template('search.html', schools=schools)

@app.route('/favorites')
def favorites():
    if session['user'] == None:
        return redirect(url_for('indexerr', msg="Invalid access"))
    else:
        favorites = database.getFavorites(session['user'])
        return render_template('favorites.html', favorites=favorites)
    
@app.route('/ratings')
def ratings():
    if session['user'] == None:
        return redirect(url_for('indexerr', msg="Invalid access"))
    else:
        ratings = database.getRatings(session['user'])
        return render_template('ratings.html', ratings=ratings)

@app.route('/profile')
def profile():
    if session['user'] == None:
        return redirect(url_for('indexerr', msg="Invalid access"))
    else:
        first, last = database.getProfile(session['user'])
        return render_template('profile.html', first=first, last=last)

@app.route('/schoolClick', methods=['POST'])
def schoolClick():
    if request.method == 'POST':
        schoolID = int(request.form.get("schoolID"))
        sameid, name, schooltype, address, safety, rating, phone = database.schoolInfo(schoolID)
        return render_template('school.html', id=sameid, name=name, rating=rating, safety=safety, type=schooltype, phone=phone, address=address, dis='hide', msg='')
    
@app.route('/schoolerr/<msg>/<sid>')
def schoolerr(msg, sid):
    sid2 = int(sid)
    sameid, name, schooltype, address, safety, rating, phone = database.schoolInfo(sid2)
    return render_template('school.html', id=sameid, name=name, rating=rating, safety=safety, type=schooltype, phone=phone, address=address, dis='show', msg=msg)
    
@app.route('/addFavorite', methods=['POST'])
def addFav():
    if request.method == 'POST':
        schoolID = int(request.form.get("schoolID"))
        if database.favoriteExists(session['user'], schoolID):
            return redirect(url_for('schoolerr', msg='Already favorited school', sid=schoolID))
        else:
            favorites = database.addFavorite(session['user'], schoolID)
            return render_template('favorites.html', favorites=favorites)

@app.route('/addRating', methods=['POST'])
def addRating():
    if request.method == 'POST':
        schoolID = int(request.form.get("schoolID2"))
        rating = str(request.form.get("ratingschool"))
        if rating == None or len(rating) == 0:
            return redirect(url_for('schoolerr', msg='Empty rating', sid=schoolID))
        rating = Decimal(rating)
        if rating < 1 or rating > 10:
            return redirect(url_for('schoolerr', msg='Rating out of bounds', sid=schoolID))
        elif database.ratingExists(session['user'], schoolID):
            return redirect(url_for('schoolerr', msg='Already rated school', sid=schoolID))
        else:
            ratings = database.addRating(session['user'], schoolID, rating)
            return render_template('ratings.html', ratings=ratings)
    
@app.route('/searchString', methods=['POST'])
def searchString():
    if request.method == 'POST':
        query = str(request.form.get("searchQuery"))
        schools = database.searchByString(query)
        return render_template('search.html', schools=schools)
    
@app.route('/updateProfile', methods=['POST'])
def updateProfile():
    if request.method == 'POST':
        if session['user'] == None:
            return redirect(url_for('indexerr', msg="Invalid access"))
        else:
            newfirst = str(request.form.get("firstname"))
            newlast = str(request.form.get("lastname"))
            first, last = database.updateProfile(session['user'], newfirst, newlast)
            return render_template('profile.html', first=first, last=last)

@app.route('/removeRating', methods=['POST'])
def removeRating():
    if request.method == 'POST':
        if session['user'] == None:
            return redirect(url_for('indexerr', msg="Invalid access"))
        else:
            schoolID = int(request.form.get("schoolID"))
            ratings = database.removeRating(session['user'], schoolID)
            return render_template('ratings.html', ratings=ratings)
        
@app.route('/removeFavorite', methods=['POST'])
def removeFavorite():
    if request.method == 'POST':
        if session['user'] == None:
            return redirect(url_for('indexerr', msg="Invalid access"))
        else:
            schoolID = int(request.form.get("schoolID"))
            favorites = database.removeFavorite(session['user'], schoolID)
            return render_template('favorites.html', favorites=favorites)