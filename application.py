import random
import string
import json
import requests
import httplib2

from flask import session as login_session
from flask import (Flask, render_template, request,
                   redirect, jsonify, url_for,
                   flash, make_response)
from flask_httpauth import HTTPBasicAuth
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from models import Base, Category, CategoryItem, User


auth = HTTPBasicAuth()

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Login Session
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        return responseWith("Invalid state parameter.", 401)

    # Obtain authorization code
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        return responseWith("Failed to upgrade the authorization code.", 401)

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        return responseWith(result.get('error'), 500)

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        return responseWith(
            "Token's user ID doesn't match given user ID.", 401)

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        return responseWith("Token's client ID does not match app's.", 401)

    # # Check if the user is already logged in
    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        return responseWith('Current user is already connected.', 200)

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    response = requests.get(userinfo_url, params=params)
    data = response.json()
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    flash("you are now logged in as %s" % login_session['username'])
    return responseWith('User successfully connected.', 200)


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/logout')
def gdisconnect():
    return logout()


def logout():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        return responseWith('Current user not connected.', 401)
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['gplus_id']
        del login_session['credentials']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']

        flash("You have successfully been logged out")
        return redirect(url_for('showCatalogCategories'))
    else:
        return responseWith('Failed to revoke token for given user.', 400)


# User helper functions
def responseWith(message, response_code):
    response = make_response(json.dumps(message), response_code)
    response.headers['Content-Type'] = 'application/json'
    return response


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def startSession():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state


# JSON APIs
# List of categories
@app.route('/catalog/categories/JSON/')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Category=[r.serialize for r in categories])


# List items in a category
@app.route('/catalog/<string:category>/JSON')
def categoryItemsJSON(category):
    category = session.query(Category).filter_by(name=category).one()
    items = session.query(CategoryItem).filter_by(
        category_id=category.id).all()
    return jsonify(CategoryItem=[i.serialize for i in items])


# A Single Item
@app.route('/catalog/<string:category>/<string:item>/JSON')
def singleMenuItemJSON(category, item):
    item = session.query(CategoryItem).filter_by(name=item).one()
    return jsonify(CategoryItem=item.serialize)


# Catalog CRUD
@app.route('/catalog')
@app.route('/')
def showCatalogCategories():
    render = "publicitem_list.html"
    startSession()
    categories = session.query(Category).all()
    # get recently added items
    latest_items = session.query(CategoryItem).order_by(
        desc(CategoryItem.created_date)).limit(10).all()
    return render_template('home.html', categories=categories,
                           items=latest_items,
                           STATE=login_session.get('state'),
                           render_html=render)


@app.route('/catalog/<string:category>/items')
@app.route('/catalog/<string:category>')
def showItems(category):
    if 'username' not in login_session:
        render = "publicitem_list.html"
    else:
        render = "item_list.html"
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category).one()
    items = session.query(CategoryItem).filter_by(
        category_id=category.id).all()
    return render_template('home.html', category=category,
                           items=items, categories=categories,
                           render_html=render,
                           STATE=login_session.get('state'))


@app.route('/catalog/<string:category>/<string:item>')
def showItemDesc(category, item):
    item = session.query(CategoryItem).filter_by(name=item).one()
    category = session.query(Category).filter_by(id=item.category_id).one()
    if (('username' not in login_session) or
            (item.user_id != login_session['user_id'])):
        return render_template('publicdescription.html', category=category,
                               item=item, STATE=login_session.get('state'))
    else:
        return render_template('description.html', category=category,
                               item=item, STATE=login_session.get('state'))


@app.route('/catalog/<string:category>/add', methods=['GET', 'POST'])
def newItem(category):
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(name=category).one()
    if request.method == 'POST':
        form_category = int(request.form['category'])
        if category.id != form_category:
            category = session.query(Category).filter_by(
                id=form_category).one()
        newItem = CategoryItem(name=request.form['name'],
                               description=request.form['description'],
                               category_id=category.id,
                               user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash("new menu item created!")
        return redirect(url_for('showItems', category=category.name))
    else:
        return render_template('item_form.html',
                               category=category, categories=categories)


@app.route('/catalog/<string:item>/edit', methods=['GET', 'POST'])
def editItem(item):
    categories = session.query(Category).all()
    item = session.query(CategoryItem).filter_by(name=item).one()
    category = session.query(Category).filter_by(id=item.category_id).one()
    if (('username' not in login_session) or
            (item.user_id != login_session['user_id'])):
        flash("You do not own this item")
        return redirect(url_for('showItems', category=category.name))
    if request.method == 'POST':
        form_category = int(request.form['category'])
        if category.id != form_category:
            category = session.query(Category).filter_by(
                id=form_category).one()
        if request.form['name']:
            item.name = request.form['name']
            item.description = request.form['description']
            item.category = category
        session.add(item)
        session.commit()
        flash("the item has updated!")
        return redirect(url_for('showItems', category=category.name))
    else:
        return render_template('item_form.html', category=category,
                               categories=categories, item=item)


@app.route('/catalog/<string:item>/delete', methods=['GET', 'POST'])
def deleteItem(item):
    item = session.query(CategoryItem).filter_by(name=item).one()
    category = session.query(Category).filter_by(id=item.category_id).one()
    if (('username' not in login_session) or
            (item.user_id != login_session['user_id'])):
        flash("You do not own this item")
        return redirect(url_for('showItems', category=category.name))
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("the item is now gone!")
        return redirect(url_for('showItems', category=category.name))
    else:
        return render_template('deleteitem.html', item=item, category=category)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
