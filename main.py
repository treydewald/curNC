from flask import Flask
from flask import Markup
from flask import render_template
from flask import session, redirect, url_for, escape, request, render_template_string
from flask_wtf import Form
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from wtforms.validators import Required
from flask_restful import Resource
import os
import csv
from flask import Flask, flash, request, redirect, url_for
from flask import send_from_directory
from werkzeug.utils import secure_filename
import pandas as pd
import pymysql
import getpass
import HTMLParser
import html
import xml
import urllib
#from six.moves import html_parser
#from html.parser import HTMLParser

UPLOAD_FOLDER = 'C:/Users/Trey/Downloads'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['SECRET_KEY'] = "c'est ne pas une string"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

h = HTMLParser.HTMLParser()



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload/<string:currency>', methods=['GET', 'POST'])
def upload_file(currency):
        if 'username' in session:
                username_session = escape(session['username'])
                if username_session == 'Admin':
                        adminActive = 1
                        if request.method == 'POST':
        # check if the post request has the file part
                                if 'file' not in request.files:
                                        flash('No file part')
                                        return redirect(request.url)
                                file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
                                if file.filename == '':
                                        flash('No selected file')
                                        return redirect(request.url)
                                if file and allowed_file(file.filename):
                                    ## CURRENTLY GIVES FILE PATH THAT IS INVALID, NEED FILE PATH OF FILE SELECTED ##
                                        print(os.path.abspath(file.filename))
                                        with open(os.path.abspath(file.filename).replace('\\','/'), 'r') as csv_file:
                                            csv_reader = csv.reader(csv_file)
                                            next(csv_reader)
                                            db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                                            c = db.cursor()
                                            c.execute('USE bitcoin;')
                                            c.execute('DELETE FROM '+currency+';')
                                            c.execute('DELETE FROM '+currency+'2;')
                                            linenumber = 0
                                            for line in csv_reader:
                                                command = 'INSERT INTO '+currency+" values('"+line[0]+"', '"+line[1]+"', '"+line[2]+"', '"+line[3]+"', '"+line[4]+"', '"+line[5]+"', '"+line[6]+"');"
                                                c.execute(command)
                                                command = 'INSERT INTO '+currency+"2 values('"+line[0]+"', '"+line[1]+"', '"+line[2]+"', '"+line[3]+"', '"+line[4]+"', '"+line[5]+"', '"+line[6]+"');"
                                                c.execute(command)
                                                linenumber += 1
                                            print(linenumber)
                                            db.commit()
                                            db.close()
                                        filename = secure_filename(file.filename)
                                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                                        return redirect(url_for(currency, filename=filename))
                        return render_template('upload.html', session_user_name=username_session, adminActive = adminActive, currency = currency.capitalize())
                else:
                        return redirect(url_for('homePage'))
        else:
                return redirect(url_for('homePage'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)



def cleanDBString(DBString):
        DBString = DBString.replace("(", "")
        DBString = DBString.replace("'", "")
        DBString = DBString.replace(",", "")
        DBString = DBString.replace(")", "")
        return DBString

def cleanDBStringInt(DBString):
        DBString = DBString.replace("(", "")
        DBString = DBString.replace("'", "")
        DBString = DBString.replace(",", "")
        DBString = DBString.replace(")", "")
        DBString = int(DBString)
        return DBString

def netOutput(netInt):
        if netInt >= 0:
                outputString = "+"+str(netInt)
        else:
                outputString = str(netInt)
        return outputString

def upvote(currency):
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        c.execute('USE bitcoin;')
        c.execute("UPDATE userfeedback SET upvotes=upvotes+1 WHERE currency = '"+currency+"';")
        db.commit()
        db.close()

def downvote(currency):
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        c.execute('USE bitcoin;')
        c.execute("UPDATE userfeedback SET downvotes=downvotes+1 WHERE currency = '"+currency+"';")
        db.commit()
        db.close()

@app.route('/downvote/<string:currency>')
def downvoteCur(currency):
        downvote(currency)
        return redirect(url_for(currency))
        
@app.route('/upvote/<string:currency>')
def upvoteCur(currency):
        upvote(currency)
        return redirect(url_for(currency))

@app.route('/remove-comment/<string:username>/<string:comment>/<string:currency>/')
def removeComment(username, comment, currency):
        h = HTMLParser.HTMLParser()
        removeString = "DELETE FROM comments WHERE username = '"+username+"' AND comment = '"+comment+"' AND currency = '"+currency+"';"
        removeString = removeString.replace("&#39;", "")
        removeString = h.unescape(removeString)
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        c.execute('USE bitcoin;')
        c.execute(removeString)
        db.commit()
        db.close()
        return redirect(url_for('manage'))

@app.route('/remove-comment-admin/<string:username>/<string:comment>/<string:currency>/')
def removeCommentAdmin(username, comment, currency):
        h = HTMLParser.HTMLParser()
        removeString = "DELETE FROM comments WHERE username = '%s' AND comment = '%s' AND currency = '%s';" % (unicode(username), unicode(comment), unicode(currency))
        removeString = removeString.replace("&#39;", "")
        removeString = h.unescape(removeString)
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        c.execute('USE bitcoin;')
        c.execute(removeString)
        db.commit()
        db.close()
        return redirect(url_for('adminManage'))


def generateFavoritesList(username):
        h = HTMLParser.HTMLParser()
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        username = str(username)
        c.execute('USE bitcoin;')
        newTable = str('CREATE TABLE IF NOT EXISTS '+username+'(name VARCHAR(40));')
        newTable = newTable.replace("&#39;", "")
        print(newTable)
        newTable = h.unescape(newTable)
        c.execute(newTable)
        db.commit()
        checkUser = 'SELECT * FROM '+username+""
        checkUser = checkUser.replace("&#39;", "")
        checkUser = h.unescape(checkUser)
        print(checkUser)
        c.execute(checkUser)
        db.commit()
        db.close()

def favoritesTable(favoritesString):
        h = HTMLParser.HTMLParser()
        favoritesList = favoritesString.split()
        favoritesList = list(set(favoritesList))
        return favoritesList
        
@app.route('/favorite/<string:currency>')
def favorite(currency):
        h = HTMLParser.HTMLParser()
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        username_session = escape(session['username'])
        username = username_session.replace("&#39;", "")
        username = h.unescape(username)
        generateFavoritesList(username_session)
        c.execute('USE bitcoin;')
        addCurrency = "INSERT INTO "+username+" values('"+currency+"');"
        addCurrency2 = "INSERT INTO %s values('%s');" % (unicode(username), unicode(currency))
        addCurrency = addCurrency.replace("&#39;", "")
        addCurrency = h.unescape(addCurrency)
        c.execute(addCurrency2)
        db.commit()
        db.close()
        return redirect(url_for('homePage'))
        
@app.route('/remove/<string:currency>')
def remove(currency):
        h = HTMLParser.HTMLParser()
        currencyUncap = currency.lower()
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        username_session = escape(session['username'])
        username = username_session.replace("&#39;", "")
        username = h.unescape(username)
        generateFavoritesList(username_session)
        c.execute('USE bitcoin;')
        removeCurrency = "DELETE FROM "+username+" WHERE name='"+currencyUncap+"';"
        removeCurrency = removeCurrency.replace("&#39;", "")
        removeCurrency = h.unescape(removeCurrency)
        removeCurrency2 = "DELETE FROM %s WHERE name='%s';" % (unicode(username), unicode(currency))
        c.execute(removeCurrency2)
        db.commit()
        db.close()
        return redirect(url_for('homePage'))

@app.route('/remove-manage/<string:currency>')
def removeManage(currency):
        h = HTMLParser.HTMLParser()
        currencyUncap = currency.lower()
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        username_session = escape(session['username'])
        username = username_session.replace("&#39;", "")
        username = h.unescape(username)
        generateFavoritesList(username_session)
        c.execute('USE bitcoin;')
        removeCurrency = "DELETE FROM %s WHERE name='%s';" % (unicode(username), unicode(currencyUncap))
        removeCurrency = removeCurrency.replace("&#39;", "")
        removeCurrency = h.unescape(removeCurrency)
        c.execute(removeCurrency)
        db.commit()
        db.close()
        return redirect(url_for('manage'))  

@app.route('/', methods=['GET', 'POST', 'POST2'])
def homePage():
        h = HTMLParser.HTMLParser()
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        c.execute('SELECT Price FROM bitcoin LIMIT 2, 1;')
        l = c.fetchall()
        l2 = str(l)
        priceBitcoin = l2
        priceBitcoin = cleanDBString(priceBitcoin)
        c.execute('SELECT Price FROM ethereum LIMIT 2, 1;')
        l = c.fetchall()
        l2 = str(l)
        priceEthereum = l2
        priceEthereum = cleanDBString(priceEthereum)
        c.execute('SELECT Price FROM xrp LIMIT 2, 1;')
        l = c.fetchall()
        l2 = str(l)
        priceXRP = l2
        priceXRP = cleanDBString(priceXRP)
        c.execute('SELECT Price FROM litecoin LIMIT 2, 1;')
        l = c.fetchall()
        l2 = str(l)
        priceLitecoin = l2
        priceLitecoin = cleanDBString(priceLitecoin)
        c.execute('SELECT Price FROM eos LIMIT 2, 1;')
        l = c.fetchall()
        l2 = str(l)
        priceEOS = l2
        priceEOS = cleanDBString(priceEOS)
        c.execute('SELECT Price FROM bitcoinCash LIMIT 2, 1;')
        l = c.fetchall()
        l2 = str(l)
        pricebitcoinCash = l2
        pricebitcoinCash = cleanDBString(pricebitcoinCash)
        c.execute('SELECT Price FROM binanceCoin LIMIT 2, 1;')
        l = c.fetchall()
        l2 = str(l)
        pricebinanceCoin = l2
        pricebinanceCoin = cleanDBString(pricebinanceCoin)
        c.execute('SELECT Price FROM tether LIMIT 2, 1;')
        l = c.fetchall()
        l2 = str(l)
        pricetether = l2
        pricetether = cleanDBString(pricetether)
        c.execute('SELECT Price FROM stellar LIMIT 2, 1;')
        l = c.fetchall()
        l2 = str(l)
        pricestellar = l2
        pricestellar = cleanDBString(pricestellar)
        c.execute('SELECT Price FROM cardano LIMIT 2, 1;')
        l = c.fetchall()
        l2 = str(l)
        pricecardano = l2
        pricecardano = cleanDBString(pricecardano)
        c.execute('SELECT Price FROM tron LIMIT 2, 1;')
        l = c.fetchall()
        l2 = str(l)
        pricetron = l2
        pricetron = cleanDBString(pricetron)
        c.execute('SELECT Price FROM monero LIMIT 2, 1;')
        l = c.fetchall()
        l2 = str(l)
        pricemonero = l2
        pricemonero = cleanDBString(pricemonero)
        c.execute('SELECT Price FROM bitcoinSV LIMIT 2, 1;')
        l = c.fetchall()
        l2 = str(l)
        pricebitcoinSV = l2
        pricebitcoinSV = cleanDBString(pricebitcoinSV)
        c.execute('SELECT Price FROM dash LIMIT 2, 1;')
        l = c.fetchall()
        l2 = str(l)
        pricedash = l2
        pricedash = cleanDBString(pricedash)
        c.execute('SELECT Price FROM iota LIMIT 2, 1;')
        l = c.fetchall()
        l2 = str(l)
        priceiota = l2
        priceiota = cleanDBString(priceiota)
        c.execute('SELECT Price FROM tezos LIMIT 2, 1;')
        l = c.fetchall()
        l2 = str(l)
        pricetezos = l2
        pricetezos = cleanDBString(pricetezos)
        c.execute('SELECT Price FROM ethereumClassic LIMIT 2, 1;')
        l = c.fetchall()
        l2 = str(l)
        priceethereumClassic = l2
        priceethereumClassic = cleanDBString(priceethereumClassic)
        c.execute('SELECT Price FROM neo LIMIT 2, 1;')
        l = c.fetchall()
        l2 = str(l)
        priceneo = l2
        priceneo = cleanDBString(priceneo)
        c.execute('SELECT Price FROM ontology LIMIT 2, 1;')
        l = c.fetchall()
        l2 = str(l)
        priceontology = l2
        priceontology = cleanDBString(priceontology)
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='bitcoin'")
        l = c.fetchall()
        l2 = str(l)
        bitcoinUp = l2
        bitcoinUp = cleanDBStringInt(bitcoinUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='bitcoin'")
        l = c.fetchall()
        l2 = str(l)
        bitcoinDown = l2
        bitcoinDown = cleanDBStringInt(bitcoinDown)
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='ethereum'")
        l = c.fetchall()
        l2 = str(l)
        ethereumUp = l2
        ethereumUp = cleanDBStringInt(ethereumUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='ethereum'")
        l = c.fetchall()
        l2 = str(l)
        ethereumDown = l2
        ethereumDown = cleanDBStringInt(ethereumDown)
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='xrp'")
        l = c.fetchall()
        l2 = str(l)
        xrpUp = l2
        xrpUp = cleanDBStringInt(xrpUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='xrp'")
        l = c.fetchall()
        l2 = str(l)
        xrpDown = l2
        xrpDown = cleanDBStringInt(xrpDown)
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='litecoin'")
        l = c.fetchall()
        l2 = str(l)
        litecoinUp = l2
        litecoinUp = cleanDBStringInt(litecoinUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='litecoin'")
        l = c.fetchall()
        l2 = str(l)
        litecoinDown = l2
        litecoinDown = cleanDBStringInt(litecoinDown)
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='eos'")
        l = c.fetchall()
        l2 = str(l)
        eosUp = l2
        eosUp = cleanDBStringInt(eosUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='eos'")
        l = c.fetchall()
        l2 = str(l)
        eosDown = l2
        eosDown = cleanDBStringInt(eosDown)
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='bitcoinCash'")
        l = c.fetchall()
        l2 = str(l)
        bitcoinCashUp = l2
        bitcoinCashUp = cleanDBStringInt(bitcoinCashUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='bitcoinCash'")
        l = c.fetchall()
        l2 = str(l)
        bitcoinCashDown = l2
        bitcoinCashDown = cleanDBStringInt(bitcoinCashDown)
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='binanceCoin'")
        l = c.fetchall()
        l2 = str(l)
        binanceCoinUp = l2
        binanceCoinUp = cleanDBStringInt(binanceCoinUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='binanceCoin'")
        l = c.fetchall()
        l2 = str(l)
        binanceCoinDown = l2
        binanceCoinDown = cleanDBStringInt(binanceCoinDown)
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='tether'")
        l = c.fetchall()
        l2 = str(l)
        tetherUp = l2
        tetherUp = cleanDBStringInt(tetherUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='tether'")
        l = c.fetchall()
        l2 = str(l)
        tetherDown = l2
        tetherDown = cleanDBStringInt(tetherDown)
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='stellar'")
        l = c.fetchall()
        l2 = str(l)
        stellarUp = l2
        stellarUp = cleanDBStringInt(stellarUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='stellar'")
        l = c.fetchall()
        l2 = str(l)
        stellarDown = l2
        stellarDown = cleanDBStringInt(stellarDown)
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='cardano'")
        l = c.fetchall()
        l2 = str(l)
        cardanoUp = l2
        cardanoUp = cleanDBStringInt(cardanoUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='cardano'")
        l = c.fetchall()
        l2 = str(l)
        cardanoDown = l2
        cardanoDown = cleanDBStringInt(cardanoDown)
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='tron'")
        l = c.fetchall()
        l2 = str(l)
        tronUp = l2
        tronUp = cleanDBStringInt(tronUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='tron'")
        l = c.fetchall()
        l2 = str(l)
        tronDown = l2
        tronDown = cleanDBStringInt(tronDown)
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='monero'")
        l = c.fetchall()
        l2 = str(l)
        moneroUp = l2
        moneroUp = cleanDBStringInt(moneroUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='monero'")
        l = c.fetchall()
        l2 = str(l)
        moneroDown = l2
        moneroDown = cleanDBStringInt(moneroDown)
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='bitcoinSV'")
        l = c.fetchall()
        l2 = str(l)
        bitcoinSVUp = l2
        bitcoinSVUp = cleanDBStringInt(bitcoinSVUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='bitcoinSV'")
        l = c.fetchall()
        l2 = str(l)
        bitcoinSVDown = l2
        bitcoinSVDown = cleanDBStringInt(bitcoinSVDown)
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='dash'")
        l = c.fetchall()
        l2 = str(l)
        dashUp = l2
        dashUp = cleanDBStringInt(dashUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='dash'")
        l = c.fetchall()
        l2 = str(l)
        dashDown = l2
        dashDown = cleanDBStringInt(dashDown)
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='iota'")
        l = c.fetchall()
        l2 = str(l)
        iotaUp = l2
        iotaUp = cleanDBStringInt(iotaUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='iota'")
        l = c.fetchall()
        l2 = str(l)
        iotaDown = l2
        iotaDown = cleanDBStringInt(iotaDown)
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='tezos'")
        l = c.fetchall()
        l2 = str(l)
        tezosUp = l2
        tezosUp = cleanDBStringInt(tezosUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='tezos'")
        l = c.fetchall()
        l2 = str(l)
        tezosDown = l2
        tezosDown = cleanDBStringInt(tezosDown)
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='ethereumClassic'")
        l = c.fetchall()
        l2 = str(l)
        ethereumClassicUp = l2
        ethereumClassicUp = cleanDBStringInt(ethereumClassicUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='ethereumClassic'")
        l = c.fetchall()
        l2 = str(l)
        ethereumClassicDown = l2
        ethereumClassicDown = cleanDBStringInt(ethereumClassicDown)
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='neo'")
        l = c.fetchall()
        l2 = str(l)
        neoUp = l2
        neoUp = cleanDBStringInt(neoUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='neo'")
        l = c.fetchall()
        l2 = str(l)
        neoDown = l2
        neoDown = cleanDBStringInt(neoDown)
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='ontology'")
        l = c.fetchall()
        l2 = str(l)
        ontologyUp = l2
        ontologyUp = cleanDBStringInt(ontologyUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='ontology'")
        l = c.fetchall()
        l2 = str(l)
        ontologyDown = l2
        ontologyDown = cleanDBStringInt(ontologyDown)
        db.close()
        if 'username' in session:
                db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                c = db.cursor()
                h = HTMLParser.HTMLParser()
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                generateFavoritesList(username_session)
                username_session = escape(session['username'])
                c.execute('USE bitcoin;')
                username = username_session.replace("&#39;", "")
                username = h.unescape(username)
                getFavorites = 'SELECT * FROM '+username+';'
                getFavorites = getFavorites.replace("&#39;", "")
                getFavorites = h.unescape(getFavorites)
                c.execute(getFavorites)
                l = c.fetchall()
                l2 = str(l)
                #print("Got this far")
                favoritesString = l2
                favoritesString = cleanDBString(favoritesString)
                favoritesList = favoritesTable(favoritesString)
                favoritesList.sort()
                priceList = []
                for x in range(0, len(favoritesList)):
                        getPrice = 'SELECT Price FROM '+favoritesList[x]+' LIMIT 2, 1;'
                        getPrice = getPrice.replace("&#39;", "")
                        getPrice = h.unescape(getPrice)
                        c.execute(getPrice)
                        l = c.fetchall()
                        l2 = str(l)
                        priceX = l2
                        priceX = cleanDBString(priceX)
                        priceList.append(priceX)
                upvoteList = []
                for x in range(0, len(favoritesList)):
                        getUpvotes = "SELECT upvotes FROM userfeedback WHERE currency='"+favoritesList[x]+"';"
                        getUpvotes = getUpvotes.replace("&#39;", "")
                        getUpvotes = h.unescape(getUpvotes)
                        c.execute(getUpvotes)
                        l = c.fetchall()
                        l2 = str(l)
                        upvotesX = l2
                        upvotesX = cleanDBString(upvotesX)
                        upvoteList.append(upvotesX)
                downvoteList = []
                for x in range(0, len(favoritesList)):
                        getDownvotes = "SELECT downvotes FROM userfeedback WHERE currency='"+favoritesList[x]+"';"
                        getDownvotes = getDownvotes.replace("&#39;", "")
                        getDownvotes = h.unescape(getDownvotes)
                        c.execute(getDownvotes)
                        l = c.fetchall()
                        l2 = str(l)
                        downvotesX = l2
                        downvotesX = cleanDBString(downvotesX)
                        downvoteList.append(downvotesX)
                for x in range(0, len(favoritesList)):
                        if favoritesList[x] == 'eos':
                                favoritesList[x] = 'EOS'
                        elif favoritesList[x] == 'xrp':
                                favoritesList[x] = 'XRP'
                        else:
                                favoritesList[x] = favoritesList[x].capitalize()
                favoriteUrl = []
                for x in range(0, len(favoritesList)):
                        favoriteUrl.append(favoritesList[x].lower())
                db.close()
                #print("Got this far")
                favoritesLen = len(favoritesList)
                favoritesActive = None
                favoritesActive1 = None
                favoritesActive2 = None
                favoritesActive3 = None
                favoritesActive4 = None
                favoritesActive5 = None
                favoritesActive6 = None
                favoritesActive7 = None
                favoritesActive8 = None
                favoritesActive9 = None
                favoritesActive10 = None
                if favoritesLen == 0:
                        favoritesActive = None
                if favoritesLen == 1:
                        favoritesActive1 = 1
                        favoritesActive = 1
                if favoritesLen == 2:
                        favoritesActive1 = 1
                        favoritesActive2 = 1
                        favoritesActive = 1
                if favoritesLen == 3:
                        favoritesActive1 = 1
                        favoritesActive2 = 1
                        favoritesActive3 = 1
                        favoritesActive = 1
                if favoritesLen == 4:
                        favoritesActive1 = 1
                        favoritesActive2 = 1
                        favoritesActive3 = 1
                        favoritesActive4 = 1
                        favoritesActive = 1
                if favoritesLen == 5:
                        favoritesActive1 = 1
                        favoritesActive2 = 1
                        favoritesActive3 = 1
                        favoritesActive4 = 1
                        favoritesActive5 = 1
                        favoritesActive = 1
                if favoritesLen == 6:
                        favoritesActive1 = 1
                        favoritesActive2 = 1
                        favoritesActive3 = 1
                        favoritesActive4 = 1
                        favoritesActive5 = 1
                        favoritesActive6 = 1
                        favoritesActive = 1
                if favoritesLen == 7:
                        favoritesActive1 = 1
                        favoritesActive2 = 1
                        favoritesActive3 = 1
                        favoritesActive4 = 1
                        favoritesActive5 = 1
                        favoritesActive6 = 1
                        favoritesActive7 = 1
                        favoritesActive = 1
                if favoritesLen == 8:
                        favoritesActive1 = 1
                        favoritesActive2 = 1
                        favoritesActive3 = 1
                        favoritesActive4 = 1
                        favoritesActive5 = 1
                        favoritesActive6 = 1
                        favoritesActive7 = 1
                        favoritesActive8 = 1
                        favoritesActive = 1
                if favoritesLen == 9:
                        favoritesActive1 = 1
                        favoritesActive2 = 1
                        favoritesActive3 = 1
                        favoritesActive4 = 1
                        favoritesActive5 = 1
                        favoritesActive6 = 1
                        favoritesActive7 = 1
                        favoritesActive8 = 1
                        favoritesActive9 = 1
                        favoritesActive = 1
                if favoritesLen == 10:
                        favoritesActive1 = 1
                        favoritesActive2 = 1
                        favoritesActive3 = 1
                        favoritesActive4 = 1
                        favoritesActive5 = 1
                        favoritesActive6 = 1
                        favoritesActive7 = 1
                        favoritesActive8 = 1
                        favoritesActive9 = 1
                        favoritesActive10 = 1
                        favoritesActive = 1
                activeList = [favoritesActive, favoritesActive1, favoritesActive2, favoritesActive3, favoritesActive4, favoritesActive5, favoritesActive6, favoritesActive7, favoritesActive8, favoritesActive9, favoritesActive10]
                return render_template('index.html', binanceCoinUp=binanceCoinUp, binanceCoinDown = binanceCoinDown, tetherUp=tetherUp, tetherDown = tetherDown, stellarUp=stellarUp, stellarDown = stellarDown, cardanoUp=cardanoUp, cardanoDown = cardanoDown, tronUp=tronUp, tronDown = tronDown,  moneroUp=moneroUp, moneroDown = moneroDown, bitcoinSVUp=bitcoinSVUp, bitcoinSVDown = bitcoinSVDown, dashUp=dashUp, dashDown = dashDown, iotaUp=iotaUp, iotaDown = iotaDown, tezosUp=tezosUp, tezosDown = tezosDown, ethereumClassicUp=ethereumClassicUp, ethereumClassicDown = ethereumClassicDown, neoUp=neoUp, neoDown = neoDown, ontologyUp=ontologyUp, ontologyDown = ontologyDown, pricebitcoinCash = pricebitcoinCash, bitcoinCashUp=bitcoinCashUp, bitcoinCashDown = bitcoinCashDown, pricebinanceCoin = pricebinanceCoin, pricetether = pricetether, pricestellar = pricestellar, pricecardano = pricecardano, pricetron = pricetron, pricemonero = pricemonero, pricebitcoinSV = pricebitcoinSV, pricedash = pricedash, priceiota = priceiota, pricetezos = pricetezos, priceethereumClassic = priceethereumClassic, priceneo = priceneo, priceontology = priceontology, adminActive = adminActive, favoriteUrl= favoriteUrl, activeList = activeList, favoritesActive = favoritesActive, favoritesActive1 = favoritesActive1, favoritesActive2 = favoritesActive2, favoritesActive3 = favoritesActive3, favoritesActive4 = favoritesActive4, favoritesActive5 = favoritesActive5, favoritesActive6 = favoritesActive6, favoritesActive7 = favoritesActive7, favoritesActive8 = favoritesActive8, favoritesActive9 = favoritesActive9, favoritesActive10 = favoritesActive10, favoritesList = favoritesList, priceList = priceList, upvoteList = upvoteList, downvoteList= downvoteList, session_user_name=username_session, priceBitcoin=priceBitcoin, priceEthereum=priceEthereum, priceXRP=priceXRP, priceLitecoin=priceLitecoin, priceEOS=priceEOS, bitcoinUp=bitcoinUp, bitcoinDown=bitcoinDown, ethereumUp=ethereumUp, ethereumDown=ethereumDown, xrpUp=xrpUp, xrpDown=xrpDown, litecoinUp=litecoinUp, litecoinDown=litecoinDown, eosUp=eosUp, eosDown=eosDown)
        return render_template('index.html', binanceCoinUp=binanceCoinUp, binanceCoinDown = binanceCoinDown, tetherUp=tetherUp, tetherDown = tetherDown, stellarUp=stellarUp, stellarDown = stellarDown, cardanoUp=cardanoUp, cardanoDown = cardanoDown, tronUp=tronUp, tronDown = tronDown,  moneroUp=moneroUp, moneroDown = moneroDown, bitcoinSVUp=bitcoinSVUp, bitcoinSVDown = bitcoinSVDown, dashUp=dashUp, dashDown = dashDown, iotaUp=iotaUp, iotaDown = iotaDown, tezosUp=tezosUp, tezosDown = tezosDown, ethereumClassicUp=ethereumClassicUp, ethereumClassicDown = ethereumClassicDown, neoUp=neoUp, neoDown = neoDown, ontologyUp=ontologyUp, ontologyDown = ontologyDown, pricebinanceCoin = pricebinanceCoin, pricetether = pricetether, pricestellar = pricestellar, pricecardano = pricecardano, pricetron = pricetron, pricemonero = pricemonero, pricebitcoinSV = pricebitcoinSV, pricedash = pricedash, priceiota = priceiota, pricetezos = pricetezos, priceethereumClassic = priceethereumClassic, priceneo = priceneo, priceontology = priceontology, pricebitcoinCash = pricebitcoinCash, bitcoinCashUp=bitcoinCashUp, bitcoinCashDown = bitcoinCashDown,  priceBitcoin=priceBitcoin, priceEthereum=priceEthereum, priceXRP=priceXRP, priceLitecoin=priceLitecoin, priceEOS=priceEOS, bitcoinUp=bitcoinUp, bitcoinDown=bitcoinDown, ethereumUp=ethereumUp, ethereumDown=ethereumDown, xrpUp=xrpUp, xrpDown=xrpDown, litecoinUp=litecoinUp, litecoinDown=litecoinDown, eosUp=eosUp, eosDown=eosDown)

@app.route('/create-account', methods=['GET', 'POST'])
def createAccount():
        h = HTMLParser.HTMLParser()
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        cur=db.cursor()
        error = None
        if request.method == 'POST':
                username_form  = request.form['username']
                password_form  = request.form['password']
                password_form2  = request.form['password2']
                if "curNC" in username_form:
                        error = "Names containing 'curNC' are reserved for admins"
                if " " in username_form:
                        error = "Names cannot contain a space"
                elif password_form != password_form2 and password_form2 != "":
                        error = "Passwords don't match"
                elif username_form == "":
                        error = "No username entered"
                elif password_form == "":
                        error = "Please enter a password for your account"
                elif password_form2 == "":
                        error = "Please repeat the password"
                else:
                        cur.execute("USE bitcoin;")
                        cur.execute("SELECT COUNT(1) FROM usersworking WHERE name = %s;", [username_form]) # CHECKS IF USERNAME EXSIST
                        if cur.fetchone()[0]:
                                error = "Account already exists"
                        else:
                                addUserString = "INSERT INTO usersworking values('"+username_form+"', '"+password_form+"');"
                                addUserString = h.unescape(addUserString)
                                print(addUserString)
                                cur.execute(addUserString)
                                db.commit()
                                session['username'] = request.form['username']
                                db.close()
                                return redirect(url_for('homePage'))
                return render_template('create.html', error = error)
        return render_template('create.html', error = error)

@app.route('/login', methods=['GET', 'POST'])
def logIn():
        h = HTMLParser.HTMLParser()
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        cur=db.cursor()
        error = None
        if 'username' in session:
                return redirect(url_for('homePage'))
        if request.method == 'POST':
                username_form  = request.form['username']
                username_form = username_form.capitalize()
                password_form  = request.form['password']
                cur.execute("SELECT COUNT(1) FROM usersworking WHERE name = %s;", [username_form]) # CHECKS IF USERNAME EXSIST
                if cur.fetchone()[0]:
                        cur.execute("SELECT pass FROM usersworking WHERE name = %s;", [username_form]) # FETCH THE HASHED PASSWORD
                        for row in cur.fetchall():
                                if password_form == row[0]:
                                        session['username'] = (request.form['username']).capitalize()
                                        return redirect(url_for('homePage'))
                                else:
                                        error = "Invalid Credential"
                else:
                        error = "Invalid Credential"
        return render_template('login.html', error=error)

@app.route('/logout')
def logOut():
    session.pop('username', None)
    return redirect(url_for('homePage'))

@app.route('/introduction')
def introduction():
        if 'username' in session:
                h = HTMLParser.HTMLParser()
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                return render_template('introduction.html', adminActive = adminActive, session_user_name=username_session)
        return render_template('introduction.html')

def cleanComment(comment):
        h = HTMLParser.HTMLParser()
        returnComment = None
        returnUsername = None
        comment = comment.replace("(", "")
        comment = comment.replace(")", "")
        for x in range(len(comment)-1):
                if comment[x] == "'":
                        if comment[x+1] == ",":
                                if returnComment == None:
                                        returnComment = comment[:x]
                                else:
                                        if returnUsername == None:
                                                returnUsername = comment[:x]
                                                returnUsername = returnUsername.replace(returnComment, "")
        returnComment = returnComment.replace("'", "")
        returnComment = returnComment.replace(",", "")
        returnUsername = returnUsername.replace("'", "")
        returnUsername = returnUsername.replace(",", "")
        returnUsername = returnUsername[1:]
        returnList = [returnComment, returnUsername]
        return returnList

def cleanManage(x):
        x = x.replace('"', "")
        x = x.replace('(', "")
        x = x.replace(')', "")
        x = x.replace("'", "")
        x = x.replace(',', "")
        x = x.replace("]", "")
        x = x.replace("[", "")
        return x

def curCommentProcess(raw):
        newList = raw.split(", ")
        try:
                commentCur1 = [cleanManage(newList[0]), cleanManage(newList[2]).capitalize()]
        except IndexError:
                commentCur1 = None
        try:
                commentCur2 = [cleanManage(newList[3]), cleanManage(newList[5]).capitalize()]
        except IndexError:
                commentCur2 = None
        try:
                commentCur3 = [cleanManage(newList[6]), cleanManage(newList[8]).capitalize()]
        except IndexError:
                commentCur3 = None
        try:
                commentCur4 = [cleanManage(newList[9]), cleanManage(newList[11]).capitalize()]
        except IndexError:
                commentCur4 = None
        try:
                commentCur5 = [cleanManage(newList[12]), cleanManage(newList[14]).capitalize()]
        except:
                commentCur5 = None
        try:
                commentCur6 = [cleanManage(newList[15]), cleanManage(newList[17]).capitalize()]
        except IndexError:
                commentCur6 = None
        try:
                commentCur7 = [cleanManage(newList[18]), cleanManage(newList[20]).capitalize()]
        except IndexError:
                commentCur7 = None
        try:
                commentCur8 = [cleanManage(newList[21]), cleanManage(newList[23]).capitalize()]
        except IndexError:
                commentCur8 = None
        try:
                commentCur9 = [cleanManage(newList[24]), cleanManage(newList[26]).capitalize()]
        except IndexError:
                commentCur9 = None
        try:
                commentCur10 = [cleanManage(newList[27]), cleanManage(newList[29]).capitalize()]
        except:
                commentCur10 = None
        toReturn = [commentCur1, commentCur2, commentCur3, commentCur4, commentCur5, commentCur6, commentCur7, commentCur8, commentCur9, commentCur10]
        return toReturn

def curCommentProcessAdmin(raw):
        newList = raw.split(", ")
        try:
                commentCur1 = [cleanManage(newList[0]), cleanManage(newList[1]), cleanManage(newList[2]).capitalize()]
        except IndexError:
                commentCur1 = None
        try:
                commentCur2 = [cleanManage(newList[3]), cleanManage(newList[4]), cleanManage(newList[5]).capitalize()]
        except IndexError:
                commentCur2 = None
        try:
                commentCur3 = [cleanManage(newList[6]), cleanManage(newList[7]), cleanManage(newList[8]).capitalize()]
        except IndexError:
                commentCur3 = None
        try:
                commentCur4 = [cleanManage(newList[9]), cleanManage(newList[10]), cleanManage(newList[11]).capitalize()]
        except IndexError:
                commentCur4 = None
        try:
                commentCur5 = [cleanManage(newList[12]), cleanManage(newList[13]), cleanManage(newList[14]).capitalize()]
        except:
                commentCur5 = None
        try:
                commentCur6 = [cleanManage(newList[15]), cleanManage(newList[16]), cleanManage(newList[17]).capitalize()]
        except IndexError:
                commentCur6 = None
        try:
                commentCur7 = [cleanManage(newList[18]), cleanManage(newList[19]), cleanManage(newList[20]).capitalize()]
        except IndexError:
                commentCur7 = None
        try:
                commentCur8 = [cleanManage(newList[21]), cleanManage(newList[22]), cleanManage(newList[23]).capitalize()]
        except IndexError:
                commentCur8 = None
        try:
                commentCur9 = [cleanManage(newList[24]), cleanManage(newList[25]), cleanManage(newList[26]).capitalize()]
        except IndexError:
                commentCur9 = None
        try:
                commentCur10 = [cleanManage(newList[27]), cleanManage(newList[28]), cleanManage(newList[29]).capitalize()]
        except:
                commentCur10 = None
        try:
                commentCur11 = [cleanManage(newList[30]), cleanManage(newList[31]), cleanManage(newList[32]).capitalize()]
        except IndexError:
                commentCur11 = None
        try:
                commentCur12 = [cleanManage(newList[33]), cleanManage(newList[34]), cleanManage(newList[35]).capitalize()]
        except IndexError:
                commentCur12 = None
        try:
                commentCur13 = [cleanManage(newList[36]), cleanManage(newList[37]), cleanManage(newList[38]).capitalize()]
        except IndexError:
                commentCur13 = None
        try:
                commentCur14 = [cleanManage(newList[39]), cleanManage(newList[40]), cleanManage(newList[41]).capitalize()]
        except IndexError:
                commentCur14 = None
        try:
                commentCur15 = [cleanManage(newList[42]), cleanManage(newList[43]), cleanManage(newList[44]).capitalize()]
        except IndexError:
                commentCur15 = None
        try:
                commentCur16 = [cleanManage(newList[45]), cleanManage(newList[46]), cleanManage(newList[47]).capitalize()]
        except IndexError:
                commentCur16 = None
        try:
                commentCur17 = [cleanManage(newList[48]), cleanManage(newList[49]), cleanManage(newList[50]).capitalize()]
        except IndexError:
                commentCur17 = None
        try:
                commentCur18 = [cleanManage(newList[51]), cleanManage(newList[52]), cleanManage(newList[53]).capitalize()]
        except IndexError:
                commentCur18 = None
        try:
                commentCur19 = [cleanManage(newList[54]), cleanManage(newList[55]), cleanManage(newList[56]).capitalize()]
        except IndexError:
                commentCur19 = None
        try:
                commentCur20 = [cleanManage(newList[57]), cleanManage(newList[58]), cleanManage(newList[59]).capitalize()]
        except IndexError:
                commentCur20 = None
        try:
                commentCur21 = [cleanManage(newList[60]), cleanManage(newList[61]), cleanManage(newList[62]).capitalize()]
        except IndexError:
                commentCur21 = None
        try:
                commentCur22 = [cleanManage(newList[63]), cleanManage(newList[64]), cleanManage(newList[65]).capitalize()]
        except IndexError:
                commentCur22 = None
        try:
                commentCur23 = [cleanManage(newList[66]), cleanManage(newList[67]), cleanManage(newList[68]).capitalize()]
        except IndexError:
                commentCur23 = None
        try:
                commentCur24 = [cleanManage(newList[69]), cleanManage(newList[70]), cleanManage(newList[71]).capitalize()]
        except IndexError:
                commentCur24 = None
        try:
                commentCur25 = [cleanManage(newList[72]), cleanManage(newList[73]), cleanManage(newList[74]).capitalize()]
        except IndexError:
                commentCur25 = None
        try:
                commentCur26 = [cleanManage(newList[75]), cleanManage(newList[76]), cleanManage(newList[77]).capitalize()]
        except IndexError:
                commentCur26 = None
        try:
                commentCur27 = [cleanManage(newList[78]), cleanManage(newList[79]), cleanManage(newList[80]).capitalize()]
        except IndexError:
                commentCur27 = None
        try:
                commentCur28 = [cleanManage(newList[81]), cleanManage(newList[82]), cleanManage(newList[83]).capitalize()]
        except IndexError:
                commentCur28 = None
        try:
                commentCur29 = [cleanManage(newList[84]), cleanManage(newList[85]), cleanManage(newList[86]).capitalize()]
        except IndexError:
                commentCur29 = None
        try:
                commentCur30 = [cleanManage(newList[87]), cleanManage(newList[88]), cleanManage(newList[89]).capitalize()]
        except IndexError:
                commentCur30 = None
        toReturn = [commentCur1, commentCur2, commentCur3, commentCur4, commentCur5, commentCur6, commentCur7, commentCur8, commentCur9, commentCur10, commentCur11, commentCur12, commentCur13, commentCur14, commentCur15, commentCur16, commentCur17, commentCur18, commentCur19, commentCur20, commentCur21, commentCur22, commentCur23, commentCur24, commentCur25, commentCur26, commentCur27, commentCur28, commentCur29, commentCur30]
        return toReturn

@app.route('/manage')
def manage():
        if 'username' in session:
                h = HTMLParser.HTMLParser()
                db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                c = db.cursor()
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                generateFavoritesList(username_session)
                c.execute('USE bitcoin;')
                username = username_session.replace("&#39;", "")
                username = h.unescape(username)
                getFavorites = 'SELECT * FROM %s;' % (unicode(username))
                getFavorites = getFavorites.replace("&#39;", "")
                getFavorites = h.unescape(getFavorites)
                c.execute(getFavorites)
                l = c.fetchall()
                l2 = str(l)
                favoritesString = l2
                favoritesString = cleanDBString(favoritesString)
                favoritesList = favoritesTable(favoritesString)
                favoritesList.sort()
                priceList = []
                for x in range(0, len(favoritesList)):
                        getPrice = 'SELECT Price FROM %s LIMIT 2, 1;' % (unicode(favoritesList[x]))
                        getPrice = getPrice.replace("&#39;", "")
                        getPrice = h.unescape(getPrice)
                        c.execute(getPrice)
                        l = c.fetchall()
                        l2 = str(l)
                        priceX = l2
                        priceX = cleanDBString(priceX)
                        priceList.append(priceX)
                upvoteList = []
                for x in range(0, len(favoritesList)):
                        getUpvotes = "SELECT upvotes FROM userfeedback WHERE currency='%s';" % (unicode(favoritesList[x]))
                        getUpvotes = getUpvotes.replace("&#39;", "")
                        getUpvotes = h.unescape(getUpvotes)
                        c.execute(getUpvotes)
                        l = c.fetchall()
                        l2 = str(l)
                        upvotesX = l2
                        upvotesX = cleanDBString(upvotesX)
                        upvoteList.append(upvotesX)
                downvoteList = []
                for x in range(0, len(favoritesList)):
                        getDownvotes = "SELECT downvotes FROM userfeedback WHERE currency='%s';" % (unicode(favoritesList[x]))
                        getDownvotes = getDownvotes.replace("&#39;", "")
                        getDownvotes = h.unescape(getDownvotes)
                        c.execute(getDownvotes)
                        l = c.fetchall()
                        l2 = str(l)
                        downvotesX = l2
                        downvotesX = cleanDBString(downvotesX)
                        downvoteList.append(downvotesX)
                for x in range(0, len(favoritesList)):
                        if favoritesList[x] == 'eos':
                                favoritesList[x] = 'EOS'
                        elif favoritesList[x] == 'xrp':
                                favoritesList[x] = 'XRP'
                        else:
                                favoritesList[x] = favoritesList[x].capitalize()
                allComments = "SELECT * FROM comments WHERE username='%s';" % (unicode(username))
                allComments = allComments.replace("&#39;", "")
                allComments = h.unescape(allComments)
                c.execute(allComments)
                l = c.fetchall()
                l2 = str(l)
                commentsRaw = l2
                commentsRawClone = commentsRaw
                commentsRaw = curCommentProcess(commentsRaw)
                favoriteUrl = []
                for x in range(0, len(favoritesList)):
                        favoriteUrl.append(favoritesList[x].lower())
                db.close()
                favoritesLen = len(favoritesList)
                favoritesActive = None
                favoritesActive1 = None
                favoritesActive2 = None
                favoritesActive3 = None
                favoritesActive4 = None
                favoritesActive5 = None
                favoritesActive6 = None
                favoritesActive7 = None
                favoritesActive8 = None
                favoritesActive9 = None
                favoritesActive10 = None
                if favoritesLen == 0:
                        favoritesActive = None
                if favoritesLen == 1:
                        favoritesActive1 = 1
                        favoritesActive = 1
                if favoritesLen == 2:
                        favoritesActive1 = 1
                        favoritesActive2 = 1
                        favoritesActive = 1
                if favoritesLen == 3:
                        favoritesActive1 = 1
                        favoritesActive2 = 1
                        favoritesActive3 = 1
                        favoritesActive = 1
                if favoritesLen == 4:
                        favoritesActive1 = 1
                        favoritesActive2 = 1
                        favoritesActive3 = 1
                        favoritesActive4 = 1
                        favoritesActive = 1
                if favoritesLen == 5:
                        favoritesActive1 = 1
                        favoritesActive2 = 1
                        favoritesActive3 = 1
                        favoritesActive4 = 1
                        favoritesActive5 = 1
                        favoritesActive = 1
                if favoritesLen == 6:
                        favoritesActive1 = 1
                        favoritesActive2 = 1
                        favoritesActive3 = 1
                        favoritesActive4 = 1
                        favoritesActive5 = 1
                        favoritesActive6 = 1
                        favoritesActive = 1
                if favoritesLen == 7:
                        favoritesActive1 = 1
                        favoritesActive2 = 1
                        favoritesActive3 = 1
                        favoritesActive4 = 1
                        favoritesActive5 = 1
                        favoritesActive6 = 1
                        favoritesActive7 = 1
                        favoritesActive = 1
                if favoritesLen == 8:
                        favoritesActive1 = 1
                        favoritesActive2 = 1
                        favoritesActive3 = 1
                        favoritesActive4 = 1
                        favoritesActive5 = 1
                        favoritesActive6 = 1
                        favoritesActive7 = 1
                        favoritesActive8 = 1
                        favoritesActive = 1
                if favoritesLen == 9:
                        favoritesActive1 = 1
                        favoritesActive2 = 1
                        favoritesActive3 = 1
                        favoritesActive4 = 1
                        favoritesActive5 = 1
                        favoritesActive6 = 1
                        favoritesActive7 = 1
                        favoritesActive8 = 1
                        favoritesActive9 = 1
                        favoritesActive = 1
                if favoritesLen == 10:
                        favoritesActive1 = 1
                        favoritesActive2 = 1
                        favoritesActive3 = 1
                        favoritesActive4 = 1
                        favoritesActive5 = 1
                        favoritesActive6 = 1
                        favoritesActive7 = 1
                        favoritesActive8 = 1
                        favoritesActive9 = 1
                        favoritesActive10 = 1
                        favoritesActive = 1
                return render_template('manage.html', adminActive = adminActive, favoriteUrl = favoriteUrl, commentsRawClone = commentsRawClone, favoritesActive1 = favoritesActive1, favoritesActive2 = favoritesActive2, favoritesActive3 = favoritesActive3, favoritesActive4 = favoritesActive4, favoritesActive5 = favoritesActive5, favoritesActive6 = favoritesActive6, favoritesActive7 = favoritesActive7, favoritesActive8 = favoritesActive8, favoritesActive9 = favoritesActive9, favoritesActive10 = favoritesActive10,  commentsRaw = commentsRaw, favoritesActive = favoritesActive, favoritesList = favoritesList, priceList = priceList, upvoteList = upvoteList, downvoteList= downvoteList, session_user_name=username_session)
        return render_template('index.html')

@app.route('/admin-manage')
def adminManage():
        if 'username' in session:
                h = HTMLParser.HTMLParser()
                db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                c = db.cursor()
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                allComments = "SELECT * FROM comments;"
                allComments = allComments.replace("&#39;", "")
                allComments = h.unescape(allComments)
                c.execute(allComments)
                l = c.fetchall()
                l2 = str(l)
                commentsRaw = l2
                commentsRawClone = commentsRaw
                commentsRaw = curCommentProcessAdmin(commentsRaw)
                if adminActive == 1:
                        return render_template('admin-manage.html', adminActive = adminActive, commentsRawClone = commentsRawClone, commentsRaw = commentsRaw, session_user_name=username_session)
                else:
                        return redirect(url_for('homePage'))
        return redirect(url_for('homePage'))

@app.route('/bitcoin', methods=['GET', 'POST'])
def bitcoin():
        h = HTMLParser.HTMLParser()
        labels = []
        values = []
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        for x in range (1, 31):
                c.execute('SELECT Date FROM bitcoin2 LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message2 = l2
                message2 = cleanDBString(message2)
                labels.append(message2)
        for x in range (1, 31):
                c.execute('SELECT Price FROM bitcoin LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message = l2
                message = cleanDBString(message)
                values.append(message)
        c.execute("SELECT COUNT(*) FROM comments WHERE currency='bitcoin'")
        l = c.fetchall()
        l2 = str(l)
        numberComments = l2
        c.execute("SELECT * FROM comments WHERE currency='bitcoin';")
        l = c.fetchall()
        #l2 = str(l)
        commentsRaw = l
        try:
                comment1 = cleanComment(str(commentsRaw[0]))
                username1 = comment1[1]
                comment1 = comment1[0]
        except IndexError:
                username1 = None
                comment1 = None
        try:
                comment2 = cleanComment(str(commentsRaw[1]))
                username2 = comment2[1]
                comment2 = comment2[0]
        except IndexError:
                username2 = None
                comment2 = None
        try:
                comment3 = cleanComment(str(commentsRaw[2]))
                username3 = comment3[1]
                comment3 = comment3[0]
        except IndexError:
                username3 = None
                comment3 = None
        try:
                comment4 = cleanComment(str(commentsRaw[3]))
                username4 = comment4[1]
                comment4 = comment4[0]
        except IndexError:
                username4 = None
                comment4 = None
        try:
                comment5 = cleanComment(str(commentsRaw[4]))
                username5 = comment5[1]
                comment5 = comment5[0]
        except IndexError:
                username5 = None
                comment5 = None
        try:
                comment6 = cleanComment(str(commentsRaw[5]))
                username6 = comment6[1]
                comment6 = comment6[0]
        except IndexError:
                username6 = None
                comment6 = None
        try:
                comment7 = cleanComment(str(commentsRaw[6]))
                username7 = comment7[1]
                comment7 = comment7[0]
        except IndexError:
                username7 = None
                comment7 = None
        try:
                comment8 = cleanComment(str(commentsRaw[7]))
                username8 = comment8[1]
                comment8 = comment8[0]
        except IndexError:
                username8 = None
                comment8 = None
        try:
                comment9 = cleanComment(str(commentsRaw[8]))
                username9 = comment9[1]
                comment9 = comment9[0]
        except IndexError:
                username9 = None
                comment9 = None
        try:
                comment10 = cleanComment(str(commentsRaw[9]))
                username10 = comment10[1]
                comment10 = comment10[0]
        except IndexError:
                username10 = None
                comment10 = None
        ## NEED TO PROCESS COMMENTSRAW USING SPACING
        ##TO GENERATE A LIST OF USERNAMES, COMMENTS, THEN PASS TO HTML PAGE
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='bitcoin'")
        l = c.fetchall()
        l2 = str(l)
        bitcoinUp = l2
        bitcoinUp = cleanDBStringInt(bitcoinUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='bitcoin'")
        l = c.fetchall()
        l2 = str(l)
        bitcoinDown = l2
        bitcoinDown = cleanDBStringInt(bitcoinDown)
        db.close()
        labels.reverse()
        values.reverse()
        colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
        line_labels=labels
        line_values=values        
        if 'username' in session:
                h = HTMLParser.HTMLParser()
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                if request.method == 'POST':
                        comment_form  = request.form['comment']
                        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                        c = db.cursor()
                        c.execute("USE bitcoin;")
                        addCommentString = "INSERT INTO comments values('%s', '%s', 'bitcoin');" % (unicode(comment_form), unicode(username_session))
                        addCommentString = addCommentString.replace("&#39;", "'")
                        addCommentString = h.unescape(addCommentString)
                        c.execute(addCommentString)
                        db.commit()
                        c.execute("SELECT * FROM comments WHERE currency='bitcoin';")
                        l = c.fetchall()
                        #l2 = str(l)
                        commentsRaw = l
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment6 = cleanComment(str(commentsRaw[5]))
                                username6 = comment6[1]
                                comment6 = comment6[0]
                        except IndexError:
                                username6 = None
                                comment6 = None
                        try:
                                comment7 = cleanComment(str(commentsRaw[6]))
                                username7 = comment7[1]
                                comment7 = comment7[0]
                        except IndexError:
                                username7 = None
                                comment7 = None
                        try:
                                comment8 = cleanComment(str(commentsRaw[7]))
                                username8 = comment8[1]
                                comment8 = comment8[0]
                        except IndexError:
                                username8 = None
                                comment8 = None
                        try:
                                comment9 = cleanComment(str(commentsRaw[8]))
                                username9 = comment9[1]
                                comment9 = comment9[0]
                        except IndexError:
                                username9 = None
                                comment9 = None
                        try:
                                comment10 = cleanComment(str(commentsRaw[9]))
                                username10 = comment10[1]
                                comment10 = comment10[0]
                        except IndexError:
                                username10 = None
                                comment10 = None
                        c.execute("SELECT upvotes FROM userfeedback WHERE currency='bitcoin'")
                        l = c.fetchall()
                        l2 = str(l)
                        bitcoinUp = l2
                        bitcoinUp = cleanDBStringInt(bitcoinUp)
                        c.execute("SELECT downvotes FROM userfeedback WHERE currency='bitcoin'")
                        l = c.fetchall()
                        l2 = str(l)
                        bitcoinDown = l2
                        bitcoinDown = cleanDBStringInt(bitcoinDown)
                        db.close()
                        return render_template('bitcoin.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10,  comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, bitcoinUp = bitcoinUp, bitcoinDown= bitcoinDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Bitcoin Price in USD', max = max(line_values), labels= line_labels, values=line_values)
                return render_template('bitcoin.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10,  comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10,adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5,  bitcoinUp = bitcoinUp, bitcoinDown= bitcoinDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Bitcoin Price in USD', max = max(line_values), labels= line_labels, values=line_values)
        return render_template('bitcoin.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10,  comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10,username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, bitcoinUp = bitcoinUp, bitcoinDown= bitcoinDown, commentsRaw=commentsRaw, title='Bitcoin Price in USD', max = max(line_values), labels= line_labels, values=line_values)

@app.route('/ethereum', methods=['GET', 'POST'])
def ethereum():
        h = HTMLParser.HTMLParser()
        labels = []
        values = []
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        for x in range (1, 31):
                c.execute('SELECT Date FROM ethereum2 LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message2 = l2
                message2 = cleanDBString(message2)
                labels.append(message2)
        for x in range (1, 31):
                c.execute('SELECT Price FROM ethereum LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message = l2
                message = cleanDBString(message)
                values.append(message)
        c.execute("SELECT COUNT(*) FROM comments WHERE currency='ethereum'")
        l = c.fetchall()
        l2 = str(l)
        numberComments = l2
        c.execute("SELECT * FROM comments WHERE currency='ethereum';")
        l = c.fetchall()
        #l2 = str(l)
        commentsRaw = l
        try:
                comment1 = cleanComment(str(commentsRaw[0]))
                username1 = comment1[1]
                comment1 = comment1[0]
        except IndexError:
                username1 = None
                comment1 = None
        try:
                comment2 = cleanComment(str(commentsRaw[1]))
                username2 = comment2[1]
                comment2 = comment2[0]
        except IndexError:
                username2 = None
                comment2 = None
        try:
                comment3 = cleanComment(str(commentsRaw[2]))
                username3 = comment3[1]
                comment3 = comment3[0]
        except IndexError:
                username3 = None
                comment3 = None
        try:
                comment4 = cleanComment(str(commentsRaw[3]))
                username4 = comment4[1]
                comment4 = comment4[0]
        except IndexError:
                username4 = None
                comment4 = None
        try:
                comment5 = cleanComment(str(commentsRaw[4]))
                username5 = comment5[1]
                comment5 = comment5[0]
        except IndexError:
                username5 = None
                comment5 = None
        try:
                comment6 = cleanComment(str(commentsRaw[5]))
                username6 = comment6[1]
                comment6 = comment6[0]
        except IndexError:
                username6 = None
                comment6 = None
        try:
                comment7 = cleanComment(str(commentsRaw[6]))
                username7 = comment7[1]
                comment7 = comment7[0]
        except IndexError:
                username7 = None
                comment7 = None
        try:
                comment8 = cleanComment(str(commentsRaw[7]))
                username8 = comment8[1]
                comment8 = comment8[0]
        except IndexError:
                username8 = None
                comment8 = None
        try:
                comment9 = cleanComment(str(commentsRaw[8]))
                username9 = comment9[1]
                comment9 = comment9[0]
        except IndexError:
                username9 = None
                comment9 = None
        try:
                comment10 = cleanComment(str(commentsRaw[9]))
                username10 = comment10[1]
                comment10 = comment10[0]
        except IndexError:
                username10 = None
                comment10 = None
        ## NEED TO PROCESS COMMENTSRAW USING SPACING
        ##TO GENERATE A LIST OF USERNAMES, COMMENTS, THEN PASS TO HTML PAGE
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='ethereum'")
        l = c.fetchall()
        l2 = str(l)
        ethereumUp = l2
        ethereumUp = cleanDBStringInt(ethereumUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='ethereum'")
        l = c.fetchall()
        l2 = str(l)
        ethereumDown = l2
        ethereumDown = cleanDBStringInt(ethereumDown)
        db.close()
        labels.reverse()
        values.reverse()
        colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
        line_labels=labels
        line_values=values        
        if 'username' in session:
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                if request.method == 'POST':
                        comment_form  = request.form['comment']
                        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                        c = db.cursor()
                        c.execute("USE bitcoin;")
                        addCommentString = "INSERT INTO comments values('%s', '%s', 'ethereum');" % (unicode(comment_form), unicode(username_session))
                        addCommentString = addCommentString.replace("&#39;", "'")
                        addCommentString = h.unescape(addCommentString)
                        c.execute(addCommentString)
                        db.commit()
                        c.execute("SELECT * FROM comments WHERE currency='ethereum';")
                        l = c.fetchall()
                        #l2 = str(l)
                        commentsRaw = l
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment6 = cleanComment(str(commentsRaw[5]))
                                username6 = comment6[1]
                                comment6 = comment6[0]
                        except IndexError:
                                username6 = None
                                comment6 = None
                        try:
                                comment7 = cleanComment(str(commentsRaw[6]))
                                username7 = comment7[1]
                                comment7 = comment7[0]
                        except IndexError:
                                username7 = None
                                comment7 = None
                        try:
                                comment8 = cleanComment(str(commentsRaw[7]))
                                username8 = comment8[1]
                                comment8 = comment8[0]
                        except IndexError:
                                username8 = None
                                comment8 = None
                        try:
                                comment9 = cleanComment(str(commentsRaw[8]))
                                username9 = comment9[1]
                                comment9 = comment9[0]
                        except IndexError:
                                username9 = None
                                comment9 = None
                        try:
                                comment10 = cleanComment(str(commentsRaw[9]))
                                username10 = comment10[1]
                                comment10 = comment10[0]
                        except IndexError:
                                username10 = None
                                comment10 = None
                        c.execute("SELECT upvotes FROM userfeedback WHERE currency='ethereum'")
                        l = c.fetchall()
                        l2 = str(l)
                        ethereumUp = l2
                        ethereumUp = cleanDBStringInt(ethereumUp)
                        c.execute("SELECT downvotes FROM userfeedback WHERE currency='ethereum'")
                        l = c.fetchall()
                        l2 = str(l)
                        ethereumDown = l2
                        ethereumDown = cleanDBStringInt(ethereumDown)
                        db.close()
                        return render_template('ethereum.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, ethereumUp = ethereumUp, ethereumDown= ethereumDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Ethereum Price in USD', max = max(line_values), labels= line_labels, values=line_values)
                return render_template('ethereum.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5,  ethereumUp = ethereumUp, ethereumDown= ethereumDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Ethereum Price in USD', max = max(line_values), labels= line_labels, values=line_values)
        return render_template('ethereum.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10,  username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, ethereumUp = ethereumUp, ethereumDown= ethereumDown, commentsRaw=commentsRaw, title='Ethereum Price in USD', max = max(line_values), labels= line_labels, values=line_values)

@app.route('/xrp', methods=['GET', 'POST'])
def xrp():
        labels = []
        values = []
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        for x in range (1, 31):
                c.execute('SELECT Date FROM xrp2 LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message2 = l2
                message2 = cleanDBString(message2)
                labels.append(message2)
        for x in range (1, 31):
                c.execute('SELECT Price FROM xrp LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message = l2
                message = cleanDBString(message)
                values.append(message)
        c.execute("SELECT COUNT(*) FROM comments WHERE currency='xrp'")
        l = c.fetchall()
        l2 = str(l)
        numberComments = l2
        c.execute("SELECT * FROM comments WHERE currency='xrp';")
        l = c.fetchall()
        #l2 = str(l)
        commentsRaw = l
        try:
                comment1 = cleanComment(str(commentsRaw[0]))
                username1 = comment1[1]
                comment1 = comment1[0]
        except IndexError:
                username1 = None
                comment1 = None
        try:
                comment2 = cleanComment(str(commentsRaw[1]))
                username2 = comment2[1]
                comment2 = comment2[0]
        except IndexError:
                username2 = None
                comment2 = None
        try:
                comment3 = cleanComment(str(commentsRaw[2]))
                username3 = comment3[1]
                comment3 = comment3[0]
        except IndexError:
                username3 = None
                comment3 = None
        try:
                comment4 = cleanComment(str(commentsRaw[3]))
                username4 = comment4[1]
                comment4 = comment4[0]
        except IndexError:
                username4 = None
                comment4 = None
        try:
                comment5 = cleanComment(str(commentsRaw[4]))
                username5 = comment5[1]
                comment5 = comment5[0]
        except IndexError:
                username5 = None
                comment5 = None
        try:
                comment6 = cleanComment(str(commentsRaw[5]))
                username6 = comment6[1]
                comment6 = comment6[0]
        except IndexError:
                username6 = None
                comment6 = None
        try:
                comment7 = cleanComment(str(commentsRaw[6]))
                username7 = comment7[1]
                comment7 = comment7[0]
        except IndexError:
                username7 = None
                comment7 = None
        try:
                comment8 = cleanComment(str(commentsRaw[7]))
                username8 = comment8[1]
                comment8 = comment8[0]
        except IndexError:
                username8 = None
                comment8 = None
        try:
                comment9 = cleanComment(str(commentsRaw[8]))
                username9 = comment9[1]
                comment9 = comment9[0]
        except IndexError:
                username9 = None
                comment9 = None
        try:
                comment10 = cleanComment(str(commentsRaw[9]))
                username10 = comment10[1]
                comment10 = comment10[0]
        except IndexError:
                username10 = None
                comment10 = None
        ## NEED TO PROCESS COMMENTSRAW USING SPACING
        ##TO GENERATE A LIST OF USERNAMES, COMMENTS, THEN PASS TO HTML PAGE
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='xrp'")
        l = c.fetchall()
        l2 = str(l)
        xrpUp = l2
        xrpUp = cleanDBStringInt(xrpUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='xrp'")
        l = c.fetchall()
        l2 = str(l)
        xrpDown = l2
        xrpDown = cleanDBStringInt(xrpDown)
        db.close()
        labels.reverse()
        values.reverse()
        colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
        line_labels=labels
        line_values=values        
        if 'username' in session:
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                if request.method == 'POST':
                        comment_form  = request.form['comment']
                        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                        c = db.cursor()
                        c.execute("USE bitcoin;")
                        comment_form = comment_form.replace("'", "")
                        addCommentString = "INSERT INTO comments values('%s', '%s', 'xrp');" % (unicode(comment_form), unicode(username_session))
                        addCommentString = addCommentString.replace("&#39;", "'")
                        addCommentString = h.unescape(addCommentString)
                        c.execute(addCommentString)
                        db.commit()
                        c.execute("SELECT * FROM comments WHERE currency='xrp';")
                        l = c.fetchall()
                        #l2 = str(l)
                        commentsRaw = l
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment6 = cleanComment(str(commentsRaw[5]))
                                username6 = comment6[1]
                                comment6 = comment6[0]
                        except IndexError:
                                username6 = None
                                comment6 = None
                        try:
                                comment7 = cleanComment(str(commentsRaw[6]))
                                username7 = comment7[1]
                                comment7 = comment7[0]
                        except IndexError:
                                username7 = None
                                comment7 = None
                        try:
                                comment8 = cleanComment(str(commentsRaw[7]))
                                username8 = comment8[1]
                                comment8 = comment8[0]
                        except IndexError:
                                username8 = None
                                comment8 = None
                        try:
                                comment9 = cleanComment(str(commentsRaw[8]))
                                username9 = comment9[1]
                                comment9 = comment9[0]
                        except IndexError:
                                username9 = None
                                comment9 = None
                        try:
                                comment10 = cleanComment(str(commentsRaw[9]))
                                username10 = comment10[1]
                                comment10 = comment10[0]
                        except IndexError:
                                username10 = None
                                comment10 = None
                        c.execute("SELECT upvotes FROM userfeedback WHERE currency='xrp'")
                        l = c.fetchall()
                        l2 = str(l)
                        xrpUp = l2
                        xrpUp = cleanDBStringInt(xrpUp)
                        c.execute("SELECT downvotes FROM userfeedback WHERE currency='xrp'")
                        l = c.fetchall()
                        l2 = str(l)
                        xrpDown = l2
                        xrpDown = cleanDBStringInt(xrpDown)
                        db.close()
                        return render_template('xrp.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, xrpUp = xrpUp, xrpDown= xrpDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='XRP Price in USD', max = max(line_values), labels= line_labels, values=line_values)
                return render_template('xrp.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5,  xrpUp = xrpUp, xrpDown= xrpDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='XRP Price in USD', max = max(line_values), labels= line_labels, values=line_values)
        return render_template('xrp.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10,  username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, xrpUp = xrpUp, xrpDown= xrpDown, commentsRaw=commentsRaw, title='XRP Price in USD', max = max(line_values), labels= line_labels, values=line_values)

@app.route('/litecoin', methods=['GET', 'POST'])
def litecoin():
        labels = []
        values = []
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        for x in range (1, 31):
                c.execute('SELECT Date FROM litecoin2 LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message2 = l2
                message2 = cleanDBString(message2)
                labels.append(message2)
        for x in range (1, 31):
                c.execute('SELECT Price FROM litecoin LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message = l2
                message = cleanDBString(message)
                values.append(message)
        c.execute("SELECT COUNT(*) FROM comments WHERE currency='litecoin'")
        l = c.fetchall()
        l2 = str(l)
        numberComments = l2
        c.execute("SELECT * FROM comments WHERE currency='litecoin';")
        l = c.fetchall()
        #l2 = str(l)
        commentsRaw = l
        try:
                comment1 = cleanComment(str(commentsRaw[0]))
                username1 = comment1[1]
                comment1 = comment1[0]
        except IndexError:
                username1 = None
                comment1 = None
        try:
                comment2 = cleanComment(str(commentsRaw[1]))
                username2 = comment2[1]
                comment2 = comment2[0]
        except IndexError:
                username2 = None
                comment2 = None
        try:
                comment3 = cleanComment(str(commentsRaw[2]))
                username3 = comment3[1]
                comment3 = comment3[0]
        except IndexError:
                username3 = None
                comment3 = None
        try:
                comment4 = cleanComment(str(commentsRaw[3]))
                username4 = comment4[1]
                comment4 = comment4[0]
        except IndexError:
                username4 = None
                comment4 = None
        try:
                comment5 = cleanComment(str(commentsRaw[4]))
                username5 = comment5[1]
                comment5 = comment5[0]
        except IndexError:
                username5 = None
                comment5 = None
        try:
                comment6 = cleanComment(str(commentsRaw[5]))
                username6 = comment6[1]
                comment6 = comment6[0]
        except IndexError:
                username6 = None
                comment6 = None
        try:
                comment7 = cleanComment(str(commentsRaw[6]))
                username7 = comment7[1]
                comment7 = comment7[0]
        except IndexError:
                username7 = None
                comment7 = None
        try:
                comment8 = cleanComment(str(commentsRaw[7]))
                username8 = comment8[1]
                comment8 = comment8[0]
        except IndexError:
                username8 = None
                comment8 = None
        try:
                comment9 = cleanComment(str(commentsRaw[8]))
                username9 = comment9[1]
                comment9 = comment9[0]
        except IndexError:
                username9 = None
                comment9 = None
        try:
                comment10 = cleanComment(str(commentsRaw[9]))
                username10 = comment10[1]
                comment10 = comment10[0]
        except IndexError:
                username10 = None
                comment10 = None
        ## NEED TO PROCESS COMMENTSRAW USING SPACING
        ##TO GENERATE A LIST OF USERNAMES, COMMENTS, THEN PASS TO HTML PAGE
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='litecoin'")
        l = c.fetchall()
        l2 = str(l)
        litecoinUp = l2
        litecoinUp = cleanDBStringInt(litecoinUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='litecoin'")
        l = c.fetchall()
        l2 = str(l)
        litecoinDown = l2
        litecoinDown = cleanDBStringInt(litecoinDown)
        db.close()
        labels.reverse()
        values.reverse()
        colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
        line_labels=labels
        line_values=values        
        if 'username' in session:
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                if request.method == 'POST':
                        comment_form  = request.form['comment']
                        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                        c = db.cursor()
                        c.execute("USE bitcoin;")
                        comment_form = comment_form.replace("'", "")
                        addCommentString = "INSERT INTO comments values('%s', '%s', 'litecoin');" % (unicode(comment_form), unicode(username_session))
                        addCommentString = addCommentString.replace("&#39;", "'")
                        addCommentString = h.unescape(addCommentString)
                        c.execute(addCommentString)
                        db.commit()
                        c.execute("SELECT * FROM comments WHERE currency='litecoin';")
                        l = c.fetchall()
                        #l2 = str(l)
                        commentsRaw = l
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment6 = cleanComment(str(commentsRaw[5]))
                                username6 = comment6[1]
                                comment6 = comment6[0]
                        except IndexError:
                                username6 = None
                                comment6 = None
                        try:
                                comment7 = cleanComment(str(commentsRaw[6]))
                                username7 = comment7[1]
                                comment7 = comment7[0]
                        except IndexError:
                                username7 = None
                                comment7 = None
                        try:
                                comment8 = cleanComment(str(commentsRaw[7]))
                                username8 = comment8[1]
                                comment8 = comment8[0]
                        except IndexError:
                                username8 = None
                                comment8 = None
                        try:
                                comment9 = cleanComment(str(commentsRaw[8]))
                                username9 = comment9[1]
                                comment9 = comment9[0]
                        except IndexError:
                                username9 = None
                                comment9 = None
                        try:
                                comment10 = cleanComment(str(commentsRaw[9]))
                                username10 = comment10[1]
                                comment10 = comment10[0]
                        except IndexError:
                                username10 = None
                                comment10 = None
                        c.execute("SELECT upvotes FROM userfeedback WHERE currency='litecoin'")
                        l = c.fetchall()
                        l2 = str(l)
                        litecoinUp = l2
                        litecoinUp = cleanDBStringInt(litecoinUp)
                        c.execute("SELECT downvotes FROM userfeedback WHERE currency='litecoin'")
                        l = c.fetchall()
                        l2 = str(l)
                        litecoinDown = l2
                        litecoinDown = cleanDBStringInt(litecoinDown)
                        db.close()
                        return render_template('litecoin.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, litecoinUp = litecoinUp, litecoinDown= litecoinDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Litecoin Price in USD', max = max(line_values), labels= line_labels, values=line_values)
                return render_template('litecoin.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5,  litecoinUp = litecoinUp, litecoinDown= litecoinDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Litecoin Price in USD', max = max(line_values), labels= line_labels, values=line_values)
        return render_template('litecoin.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10,  username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, litecoinUp = litecoinUp, litecoinDown= litecoinDown, commentsRaw=commentsRaw, title='Litecoin Price in USD', max = max(line_values), labels= line_labels, values=line_values)

@app.route('/eos', methods=['GET', 'POST'])
def eos():
        labels = []
        values = []
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        for x in range (1, 31):
                c.execute('SELECT Date FROM eos2 LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message2 = l2
                message2 = cleanDBString(message2)
                labels.append(message2)
        for x in range (1, 31):
                c.execute('SELECT Price FROM eos LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message = l2
                message = cleanDBString(message)
                values.append(message)
        c.execute("SELECT COUNT(*) FROM comments WHERE currency='eos'")
        l = c.fetchall()
        l2 = str(l)
        numberComments = l2
        c.execute("SELECT * FROM comments WHERE currency='eos';")
        l = c.fetchall()
        #l2 = str(l)
        commentsRaw = l
        try:
                comment1 = cleanComment(str(commentsRaw[0]))
                username1 = comment1[1]
                comment1 = comment1[0]
        except IndexError:
                username1 = None
                comment1 = None
        try:
                comment2 = cleanComment(str(commentsRaw[1]))
                username2 = comment2[1]
                comment2 = comment2[0]
        except IndexError:
                username2 = None
                comment2 = None
        try:
                comment3 = cleanComment(str(commentsRaw[2]))
                username3 = comment3[1]
                comment3 = comment3[0]
        except IndexError:
                username3 = None
                comment3 = None
        try:
                comment4 = cleanComment(str(commentsRaw[3]))
                username4 = comment4[1]
                comment4 = comment4[0]
        except IndexError:
                username4 = None
                comment4 = None
        try:
                comment5 = cleanComment(str(commentsRaw[4]))
                username5 = comment5[1]
                comment5 = comment5[0]
        except IndexError:
                username5 = None
                comment5 = None
        try:
                comment6 = cleanComment(str(commentsRaw[5]))
                username6 = comment6[1]
                comment6 = comment6[0]
        except IndexError:
                username6 = None
                comment6 = None
        try:
                comment7 = cleanComment(str(commentsRaw[6]))
                username7 = comment7[1]
                comment7 = comment7[0]
        except IndexError:
                username7 = None
                comment7 = None
        try:
                comment8 = cleanComment(str(commentsRaw[7]))
                username8 = comment8[1]
                comment8 = comment8[0]
        except IndexError:
                username8 = None
                comment8 = None
        try:
                comment9 = cleanComment(str(commentsRaw[8]))
                username9 = comment9[1]
                comment9 = comment9[0]
        except IndexError:
                username9 = None
                comment9 = None
        try:
                comment10 = cleanComment(str(commentsRaw[9]))
                username10 = comment10[1]
                comment10 = comment10[0]
        except IndexError:
                username10 = None
                comment10 = None
        ## NEED TO PROCESS COMMENTSRAW USING SPACING
        ##TO GENERATE A LIST OF USERNAMES, COMMENTS, THEN PASS TO HTML PAGE
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='eos'")
        l = c.fetchall()
        l2 = str(l)
        eosUp = l2
        eosUp = cleanDBStringInt(eosUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='eos'")
        l = c.fetchall()
        l2 = str(l)
        eosDown = l2
        eosDown = cleanDBStringInt(eosDown)
        db.close()
        labels.reverse()
        values.reverse()
        colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
        line_labels=labels
        line_values=values        
        if 'username' in session:
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                if request.method == 'POST':
                        comment_form  = request.form['comment']
                        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                        c = db.cursor()
                        c.execute("USE bitcoin;")
                        comment_form = comment_form.replace("'", "")
                        addCommentString = "INSERT INTO comments values('%s', '%s', 'eos');" % (unicode(comment_form), unicode(username_session))
                        addCommentString = addCommentString.replace("&#39;", "'")
                        addCommentString = h.unescape(addCommentString)
                        c.execute(addCommentString)
                        db.commit()
                        c.execute("SELECT * FROM comments WHERE currency='eos';")
                        l = c.fetchall()
                        #l2 = str(l)
                        commentsRaw = l
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment6 = cleanComment(str(commentsRaw[5]))
                                username6 = comment6[1]
                                comment6 = comment6[0]
                        except IndexError:
                                username6 = None
                                comment6 = None
                        try:
                                comment7 = cleanComment(str(commentsRaw[6]))
                                username7 = comment7[1]
                                comment7 = comment7[0]
                        except IndexError:
                                username7 = None
                                comment7 = None
                        try:
                                comment8 = cleanComment(str(commentsRaw[7]))
                                username8 = comment8[1]
                                comment8 = comment8[0]
                        except IndexError:
                                username8 = None
                                comment8 = None
                        try:
                                comment9 = cleanComment(str(commentsRaw[8]))
                                username9 = comment9[1]
                                comment9 = comment9[0]
                        except IndexError:
                                username9 = None
                                comment9 = None
                        try:
                                comment10 = cleanComment(str(commentsRaw[9]))
                                username10 = comment10[1]
                                comment10 = comment10[0]
                        except IndexError:
                                username10 = None
                                comment10 = None
                        c.execute("SELECT upvotes FROM userfeedback WHERE currency='eos'")
                        l = c.fetchall()
                        l2 = str(l)
                        eosUp = l2
                        eosUp = cleanDBStringInt(eosUp)
                        c.execute("SELECT downvotes FROM userfeedback WHERE currency='eos'")
                        l = c.fetchall()
                        l2 = str(l)
                        eosDown = l2
                        eosDown = cleanDBStringInt(eosDown)
                        db.close()
                        return render_template('eos.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, eosUp = eosUp, eosDown= eosDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='EOS Price in USD', max = max(line_values), labels= line_labels, values=line_values)
                return render_template('eos.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5,  eosUp = eosUp, eosDown= eosDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='EOS Price in USD', max = max(line_values), labels= line_labels, values=line_values)
        return render_template('eos.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10,  username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, eosUp = eosUp, eosDown= eosDown, commentsRaw=commentsRaw, title='EOS Price in USD', max = max(line_values), labels= line_labels, values=line_values)

@app.route('/bitcoinCash', methods=['GET', 'POST'])
def bitcoinCash():
        labels = []
        values = []
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        for x in range (1, 31):
                c.execute('SELECT Date FROM bitcoinCash2 LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message2 = l2
                message2 = cleanDBString(message2)
                labels.append(message2)
        for x in range (1, 31):
                c.execute('SELECT Price FROM bitcoinCash LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message = l2
                message = cleanDBString(message)
                values.append(message)
        c.execute("SELECT COUNT(*) FROM comments WHERE currency='bitcoinCash'")
        l = c.fetchall()
        l2 = str(l)
        numberComments = l2
        c.execute("SELECT * FROM comments WHERE currency='bitcoinCash';")
        l = c.fetchall()
        #l2 = str(l)
        commentsRaw = l
        try:
                comment1 = cleanComment(str(commentsRaw[0]))
                username1 = comment1[1]
                comment1 = comment1[0]
        except IndexError:
                username1 = None
                comment1 = None
        try:
                comment2 = cleanComment(str(commentsRaw[1]))
                username2 = comment2[1]
                comment2 = comment2[0]
        except IndexError:
                username2 = None
                comment2 = None
        try:
                comment3 = cleanComment(str(commentsRaw[2]))
                username3 = comment3[1]
                comment3 = comment3[0]
        except IndexError:
                username3 = None
                comment3 = None
        try:
                comment4 = cleanComment(str(commentsRaw[3]))
                username4 = comment4[1]
                comment4 = comment4[0]
        except IndexError:
                username4 = None
                comment4 = None
        try:
                comment5 = cleanComment(str(commentsRaw[4]))
                username5 = comment5[1]
                comment5 = comment5[0]
        except IndexError:
                username5 = None
                comment5 = None
        try:
                comment6 = cleanComment(str(commentsRaw[5]))
                username6 = comment6[1]
                comment6 = comment6[0]
        except IndexError:
                username6 = None
                comment6 = None
        try:
                comment7 = cleanComment(str(commentsRaw[6]))
                username7 = comment7[1]
                comment7 = comment7[0]
        except IndexError:
                username7 = None
                comment7 = None
        try:
                comment8 = cleanComment(str(commentsRaw[7]))
                username8 = comment8[1]
                comment8 = comment8[0]
        except IndexError:
                username8 = None
                comment8 = None
        try:
                comment9 = cleanComment(str(commentsRaw[8]))
                username9 = comment9[1]
                comment9 = comment9[0]
        except IndexError:
                username9 = None
                comment9 = None
        try:
                comment10 = cleanComment(str(commentsRaw[9]))
                username10 = comment10[1]
                comment10 = comment10[0]
        except IndexError:
                username10 = None
                comment10 = None
        ## NEED TO PROCESS COMMENTSRAW USING SPACING
        ##TO GENERATE A LIST OF USERNAMES, COMMENTS, THEN PASS TO HTML PAGE
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='bitcoinCash'")
        l = c.fetchall()
        l2 = str(l)
        bitcoinCashUp = l2
        bitcoinCashUp = cleanDBStringInt(bitcoinCashUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='bitcoinCash'")
        l = c.fetchall()
        l2 = str(l)
        bitcoinCashDown = l2
        bitcoinCashDown = cleanDBStringInt(bitcoinCashDown)
        db.close()
        labels.reverse()
        values.reverse()
        colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
        line_labels=labels
        line_values=values        
        if 'username' in session:
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                if request.method == 'POST':
                        comment_form  = request.form['comment']
                        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                        c = db.cursor()
                        c.execute("USE bitcoin;")
                        comment_form = comment_form.replace("'", "")
                        addCommentString = "INSERT INTO comments values('%s', '%s', 'bitcoinCash');" % (unicode(comment_form), unicode(username_session))
                        addCommentString = addCommentString.replace("&#39;", "'")
                        addCommentString = h.unescape(addCommentString)
                        c.execute(addCommentString)
                        db.commit()
                        c.execute("SELECT * FROM comments WHERE currency='bitcoinCash';")
                        l = c.fetchall()
                        #l2 = str(l)
                        commentsRaw = l
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment6 = cleanComment(str(commentsRaw[5]))
                                username6 = comment6[1]
                                comment6 = comment6[0]
                        except IndexError:
                                username6 = None
                                comment6 = None
                        try:
                                comment7 = cleanComment(str(commentsRaw[6]))
                                username7 = comment7[1]
                                comment7 = comment7[0]
                        except IndexError:
                                username7 = None
                                comment7 = None
                        try:
                                comment8 = cleanComment(str(commentsRaw[7]))
                                username8 = comment8[1]
                                comment8 = comment8[0]
                        except IndexError:
                                username8 = None
                                comment8 = None
                        try:
                                comment9 = cleanComment(str(commentsRaw[8]))
                                username9 = comment9[1]
                                comment9 = comment9[0]
                        except IndexError:
                                username9 = None
                                comment9 = None
                        try:
                                comment10 = cleanComment(str(commentsRaw[9]))
                                username10 = comment10[1]
                                comment10 = comment10[0]
                        except IndexError:
                                username10 = None
                                comment10 = None
                        c.execute("SELECT upvotes FROM userfeedback WHERE currency='bitcoinCash'")
                        l = c.fetchall()
                        l2 = str(l)
                        bitcoinCashUp = l2
                        bitcoinCashUp = cleanDBStringInt(bitcoinCashUp)
                        c.execute("SELECT downvotes FROM userfeedback WHERE currency='bitcoinCash'")
                        l = c.fetchall()
                        l2 = str(l)
                        bitcoinCashDown = l2
                        bitcoinCashDown = cleanDBStringInt(bitcoinCashDown)
                        db.close()
                        return render_template('bitcoinCash.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, bitcoinCashUp = bitcoinCashUp, bitcoinCashDown= bitcoinCashDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='bitcoinCash Price in USD', max = max(line_values), labels= line_labels, values=line_values)
                return render_template('bitcoinCash.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5,  bitcoinCashUp = bitcoinCashUp, bitcoinCashDown= bitcoinCashDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='bitcoinCash Price in USD', max = max(line_values), labels= line_labels, values=line_values)
        return render_template('bitcoinCash.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10,  username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, bitcoinCashUp = bitcoinCashUp, bitcoinCashDown= bitcoinCashDown, commentsRaw=commentsRaw, title='bitcoinCash Price in USD', max = max(line_values), labels= line_labels, values=line_values)

@app.route('/binanceCoin', methods=['GET', 'POST'])
def binanceCoin():
        labels = []
        values = []
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        for x in range (1, 31):
                c.execute('SELECT Date FROM binanceCoin2 LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message2 = l2
                message2 = cleanDBString(message2)
                labels.append(message2)
        for x in range (1, 31):
                c.execute('SELECT Price FROM binanceCoin LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message = l2
                message = cleanDBString(message)
                values.append(message)
        c.execute("SELECT COUNT(*) FROM comments WHERE currency='binanceCoin'")
        l = c.fetchall()
        l2 = str(l)
        numberComments = l2
        c.execute("SELECT * FROM comments WHERE currency='binanceCoin';")
        l = c.fetchall()
        #l2 = str(l)
        commentsRaw = l
        try:
                comment1 = cleanComment(str(commentsRaw[0]))
                username1 = comment1[1]
                comment1 = comment1[0]
        except IndexError:
                username1 = None
                comment1 = None
        try:
                comment2 = cleanComment(str(commentsRaw[1]))
                username2 = comment2[1]
                comment2 = comment2[0]
        except IndexError:
                username2 = None
                comment2 = None
        try:
                comment3 = cleanComment(str(commentsRaw[2]))
                username3 = comment3[1]
                comment3 = comment3[0]
        except IndexError:
                username3 = None
                comment3 = None
        try:
                comment4 = cleanComment(str(commentsRaw[3]))
                username4 = comment4[1]
                comment4 = comment4[0]
        except IndexError:
                username4 = None
                comment4 = None
        try:
                comment5 = cleanComment(str(commentsRaw[4]))
                username5 = comment5[1]
                comment5 = comment5[0]
        except IndexError:
                username5 = None
                comment5 = None
        try:
                comment6 = cleanComment(str(commentsRaw[5]))
                username6 = comment6[1]
                comment6 = comment6[0]
        except IndexError:
                username6 = None
                comment6 = None
        try:
                comment7 = cleanComment(str(commentsRaw[6]))
                username7 = comment7[1]
                comment7 = comment7[0]
        except IndexError:
                username7 = None
                comment7 = None
        try:
                comment8 = cleanComment(str(commentsRaw[7]))
                username8 = comment8[1]
                comment8 = comment8[0]
        except IndexError:
                username8 = None
                comment8 = None
        try:
                comment9 = cleanComment(str(commentsRaw[8]))
                username9 = comment9[1]
                comment9 = comment9[0]
        except IndexError:
                username9 = None
                comment9 = None
        try:
                comment10 = cleanComment(str(commentsRaw[9]))
                username10 = comment10[1]
                comment10 = comment10[0]
        except IndexError:
                username10 = None
                comment10 = None
        ## NEED TO PROCESS COMMENTSRAW USING SPACING
        ##TO GENERATE A LIST OF USERNAMES, COMMENTS, THEN PASS TO HTML PAGE
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='binanceCoin'")
        l = c.fetchall()
        l2 = str(l)
        binanceCoinUp = l2
        binanceCoinUp = cleanDBStringInt(binanceCoinUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='binanceCoin'")
        l = c.fetchall()
        l2 = str(l)
        binanceCoinDown = l2
        binanceCoinDown = cleanDBStringInt(binanceCoinDown)
        db.close()
        labels.reverse()
        values.reverse()
        colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
        line_labels=labels
        line_values=values        
        if 'username' in session:
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                if request.method == 'POST':
                        comment_form  = request.form['comment']
                        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                        c = db.cursor()
                        c.execute("USE bitcoin;")
                        comment_form = comment_form.replace("'", "")
                        addCommentString = "INSERT INTO comments values('%s', '%s', 'binanceCoin');" % (unicode(comment_form), unicode(username_session))
                        addCommentString = addCommentString.replace("&#39;", "'")
                        addCommentString = h.unescape(addCommentString)
                        c.execute(addCommentString)
                        db.commit()
                        c.execute("SELECT * FROM comments WHERE currency='binanceCoin';")
                        l = c.fetchall()
                        #l2 = str(l)
                        commentsRaw = l
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment6 = cleanComment(str(commentsRaw[5]))
                                username6 = comment6[1]
                                comment6 = comment6[0]
                        except IndexError:
                                username6 = None
                                comment6 = None
                        try:
                                comment7 = cleanComment(str(commentsRaw[6]))
                                username7 = comment7[1]
                                comment7 = comment7[0]
                        except IndexError:
                                username7 = None
                                comment7 = None
                        try:
                                comment8 = cleanComment(str(commentsRaw[7]))
                                username8 = comment8[1]
                                comment8 = comment8[0]
                        except IndexError:
                                username8 = None
                                comment8 = None
                        try:
                                comment9 = cleanComment(str(commentsRaw[8]))
                                username9 = comment9[1]
                                comment9 = comment9[0]
                        except IndexError:
                                username9 = None
                                comment9 = None
                        try:
                                comment10 = cleanComment(str(commentsRaw[9]))
                                username10 = comment10[1]
                                comment10 = comment10[0]
                        except IndexError:
                                username10 = None
                                comment10 = None
                        c.execute("SELECT upvotes FROM userfeedback WHERE currency='binanceCoin'")
                        l = c.fetchall()
                        l2 = str(l)
                        binanceCoinUp = l2
                        binanceCoinUp = cleanDBStringInt(binanceCoinUp)
                        c.execute("SELECT downvotes FROM userfeedback WHERE currency='binanceCoin'")
                        l = c.fetchall()
                        l2 = str(l)
                        binanceCoinDown = l2
                        binanceCoinDown = cleanDBStringInt(binanceCoinDown)
                        db.close()
                        return render_template('binanceCoin.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, binanceCoinUp = binanceCoinUp, binanceCoinDown= binanceCoinDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Binance Coin Price in USD', max = max(line_values), labels= line_labels, values=line_values)
                return render_template('binanceCoin.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5,  binanceCoinUp = binanceCoinUp, binanceCoinDown= binanceCoinDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Binance Coin Price in USD', max = max(line_values), labels= line_labels, values=line_values)
        return render_template('binanceCoin.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10,  username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, binanceCoinUp = binanceCoinUp, binanceCoinDown= binanceCoinDown, commentsRaw=commentsRaw, title='Binance Coin Price in USD', max = max(line_values), labels= line_labels, values=line_values)

@app.route('/tether', methods=['GET', 'POST'])
def tether():
        labels = []
        values = []
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        for x in range (1, 31):
                c.execute('SELECT Date FROM tether2 LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message2 = l2
                message2 = cleanDBString(message2)
                labels.append(message2)
        for x in range (1, 31):
                c.execute('SELECT Price FROM tether LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message = l2
                message = cleanDBString(message)
                values.append(message)
        c.execute("SELECT COUNT(*) FROM comments WHERE currency='tether'")
        l = c.fetchall()
        l2 = str(l)
        numberComments = l2
        c.execute("SELECT * FROM comments WHERE currency='tether';")
        l = c.fetchall()
        #l2 = str(l)
        commentsRaw = l
        try:
                comment1 = cleanComment(str(commentsRaw[0]))
                username1 = comment1[1]
                comment1 = comment1[0]
        except IndexError:
                username1 = None
                comment1 = None
        try:
                comment2 = cleanComment(str(commentsRaw[1]))
                username2 = comment2[1]
                comment2 = comment2[0]
        except IndexError:
                username2 = None
                comment2 = None
        try:
                comment3 = cleanComment(str(commentsRaw[2]))
                username3 = comment3[1]
                comment3 = comment3[0]
        except IndexError:
                username3 = None
                comment3 = None
        try:
                comment4 = cleanComment(str(commentsRaw[3]))
                username4 = comment4[1]
                comment4 = comment4[0]
        except IndexError:
                username4 = None
                comment4 = None
        try:
                comment5 = cleanComment(str(commentsRaw[4]))
                username5 = comment5[1]
                comment5 = comment5[0]
        except IndexError:
                username5 = None
                comment5 = None
        try:
                comment6 = cleanComment(str(commentsRaw[5]))
                username6 = comment6[1]
                comment6 = comment6[0]
        except IndexError:
                username6 = None
                comment6 = None
        try:
                comment7 = cleanComment(str(commentsRaw[6]))
                username7 = comment7[1]
                comment7 = comment7[0]
        except IndexError:
                username7 = None
                comment7 = None
        try:
                comment8 = cleanComment(str(commentsRaw[7]))
                username8 = comment8[1]
                comment8 = comment8[0]
        except IndexError:
                username8 = None
                comment8 = None
        try:
                comment9 = cleanComment(str(commentsRaw[8]))
                username9 = comment9[1]
                comment9 = comment9[0]
        except IndexError:
                username9 = None
                comment9 = None
        try:
                comment10 = cleanComment(str(commentsRaw[9]))
                username10 = comment10[1]
                comment10 = comment10[0]
        except IndexError:
                username10 = None
                comment10 = None
        ## NEED TO PROCESS COMMENTSRAW USING SPACING
        ##TO GENERATE A LIST OF USERNAMES, COMMENTS, THEN PASS TO HTML PAGE
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='tether'")
        l = c.fetchall()
        l2 = str(l)
        tetherUp = l2
        tetherUp = cleanDBStringInt(tetherUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='tether'")
        l = c.fetchall()
        l2 = str(l)
        tetherDown = l2
        tetherDown = cleanDBStringInt(tetherDown)
        db.close()
        labels.reverse()
        values.reverse()
        colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
        line_labels=labels
        line_values=values        
        if 'username' in session:
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                if request.method == 'POST':
                        comment_form  = request.form['comment']
                        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                        c = db.cursor()
                        c.execute("USE bitcoin;")
                        comment_form = comment_form.replace("'", "")
                        addCommentString = "INSERT INTO comments values('%s', '%s', 'tether');" % (unicode(comment_form), unicode(username_session))
                        addCommentString = addCommentString.replace("&#39;", "'")
                        addCommentString = h.unescape(addCommentString)
                        c.execute(addCommentString)
                        db.commit()
                        c.execute("SELECT * FROM comments WHERE currency='tether';")
                        l = c.fetchall()
                        #l2 = str(l)
                        commentsRaw = l
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment6 = cleanComment(str(commentsRaw[5]))
                                username6 = comment6[1]
                                comment6 = comment6[0]
                        except IndexError:
                                username6 = None
                                comment6 = None
                        try:
                                comment7 = cleanComment(str(commentsRaw[6]))
                                username7 = comment7[1]
                                comment7 = comment7[0]
                        except IndexError:
                                username7 = None
                                comment7 = None
                        try:
                                comment8 = cleanComment(str(commentsRaw[7]))
                                username8 = comment8[1]
                                comment8 = comment8[0]
                        except IndexError:
                                username8 = None
                                comment8 = None
                        try:
                                comment9 = cleanComment(str(commentsRaw[8]))
                                username9 = comment9[1]
                                comment9 = comment9[0]
                        except IndexError:
                                username9 = None
                                comment9 = None
                        try:
                                comment10 = cleanComment(str(commentsRaw[9]))
                                username10 = comment10[1]
                                comment10 = comment10[0]
                        except IndexError:
                                username10 = None
                                comment10 = None
                        c.execute("SELECT upvotes FROM userfeedback WHERE currency='tether'")
                        l = c.fetchall()
                        l2 = str(l)
                        tetherUp = l2
                        tetherUp = cleanDBStringInt(tetherUp)
                        c.execute("SELECT downvotes FROM userfeedback WHERE currency='tether'")
                        l = c.fetchall()
                        l2 = str(l)
                        tetherDown = l2
                        tetherDown = cleanDBStringInt(tetherDown)
                        db.close()
                        return render_template('tether.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, tetherUp = tetherUp, tetherDown= tetherDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Tether Price in USD', max = max(line_values), labels= line_labels, values=line_values)
                return render_template('tether.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5,  tetherUp = tetherUp, tetherDown= tetherDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Tether Price in USD', max = max(line_values), labels= line_labels, values=line_values)
        return render_template('tether.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10,  username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, tetherUp = tetherUp, tetherDown= tetherDown, commentsRaw=commentsRaw, title='Tether Price in USD', max = max(line_values), labels= line_labels, values=line_values)

@app.route('/stellar', methods=['GET', 'POST'])
def stellar():
        labels = []
        values = []
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        for x in range (1, 31):
                c.execute('SELECT Date FROM stellar2 LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message2 = l2
                message2 = cleanDBString(message2)
                labels.append(message2)
        for x in range (1, 31):
                c.execute('SELECT Price FROM stellar LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message = l2
                message = cleanDBString(message)
                values.append(message)
        c.execute("SELECT COUNT(*) FROM comments WHERE currency='stellar'")
        l = c.fetchall()
        l2 = str(l)
        numberComments = l2
        c.execute("SELECT * FROM comments WHERE currency='stellar';")
        l = c.fetchall()
        #l2 = str(l)
        commentsRaw = l
        try:
                comment1 = cleanComment(str(commentsRaw[0]))
                username1 = comment1[1]
                comment1 = comment1[0]
        except IndexError:
                username1 = None
                comment1 = None
        try:
                comment2 = cleanComment(str(commentsRaw[1]))
                username2 = comment2[1]
                comment2 = comment2[0]
        except IndexError:
                username2 = None
                comment2 = None
        try:
                comment3 = cleanComment(str(commentsRaw[2]))
                username3 = comment3[1]
                comment3 = comment3[0]
        except IndexError:
                username3 = None
                comment3 = None
        try:
                comment4 = cleanComment(str(commentsRaw[3]))
                username4 = comment4[1]
                comment4 = comment4[0]
        except IndexError:
                username4 = None
                comment4 = None
        try:
                comment5 = cleanComment(str(commentsRaw[4]))
                username5 = comment5[1]
                comment5 = comment5[0]
        except IndexError:
                username5 = None
                comment5 = None
        try:
                comment6 = cleanComment(str(commentsRaw[5]))
                username6 = comment6[1]
                comment6 = comment6[0]
        except IndexError:
                username6 = None
                comment6 = None
        try:
                comment7 = cleanComment(str(commentsRaw[6]))
                username7 = comment7[1]
                comment7 = comment7[0]
        except IndexError:
                username7 = None
                comment7 = None
        try:
                comment8 = cleanComment(str(commentsRaw[7]))
                username8 = comment8[1]
                comment8 = comment8[0]
        except IndexError:
                username8 = None
                comment8 = None
        try:
                comment9 = cleanComment(str(commentsRaw[8]))
                username9 = comment9[1]
                comment9 = comment9[0]
        except IndexError:
                username9 = None
                comment9 = None
        try:
                comment10 = cleanComment(str(commentsRaw[9]))
                username10 = comment10[1]
                comment10 = comment10[0]
        except IndexError:
                username10 = None
                comment10 = None
        ## NEED TO PROCESS COMMENTSRAW USING SPACING
        ##TO GENERATE A LIST OF USERNAMES, COMMENTS, THEN PASS TO HTML PAGE
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='stellar'")
        l = c.fetchall()
        l2 = str(l)
        stellarUp = l2
        stellarUp = cleanDBStringInt(stellarUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='stellar'")
        l = c.fetchall()
        l2 = str(l)
        stellarDown = l2
        stellarDown = cleanDBStringInt(stellarDown)
        db.close()
        labels.reverse()
        values.reverse()
        colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
        line_labels=labels
        line_values=values        
        if 'username' in session:
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                if request.method == 'POST':
                        comment_form  = request.form['comment']
                        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                        c = db.cursor()
                        c.execute("USE bitcoin;")
                        comment_form = comment_form.replace("'", "")
                        addCommentString = "INSERT INTO comments values('%s', '%s', 'stellar');" % (unicode(comment_form), unicode(username_session))
                        addCommentString = addCommentString.replace("&#39;", "'")
                        addCommentString = h.unescape(addCommentString)
                        c.execute(addCommentString)
                        db.commit()
                        c.execute("SELECT * FROM comments WHERE currency='stellar';")
                        l = c.fetchall()
                        #l2 = str(l)
                        commentsRaw = l
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment6 = cleanComment(str(commentsRaw[5]))
                                username6 = comment6[1]
                                comment6 = comment6[0]
                        except IndexError:
                                username6 = None
                                comment6 = None
                        try:
                                comment7 = cleanComment(str(commentsRaw[6]))
                                username7 = comment7[1]
                                comment7 = comment7[0]
                        except IndexError:
                                username7 = None
                                comment7 = None
                        try:
                                comment8 = cleanComment(str(commentsRaw[7]))
                                username8 = comment8[1]
                                comment8 = comment8[0]
                        except IndexError:
                                username8 = None
                                comment8 = None
                        try:
                                comment9 = cleanComment(str(commentsRaw[8]))
                                username9 = comment9[1]
                                comment9 = comment9[0]
                        except IndexError:
                                username9 = None
                                comment9 = None
                        try:
                                comment10 = cleanComment(str(commentsRaw[9]))
                                username10 = comment10[1]
                                comment10 = comment10[0]
                        except IndexError:
                                username10 = None
                                comment10 = None
                        c.execute("SELECT upvotes FROM userfeedback WHERE currency='stellar'")
                        l = c.fetchall()
                        l2 = str(l)
                        stellarUp = l2
                        stellarUp = cleanDBStringInt(stellarUp)
                        c.execute("SELECT downvotes FROM userfeedback WHERE currency='stellar'")
                        l = c.fetchall()
                        l2 = str(l)
                        stellarDown = l2
                        stellarDown = cleanDBStringInt(stellarDown)
                        db.close()
                        return render_template('stellar.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, stellarUp = stellarUp, stellarDown= stellarDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Stellar Price in USD', max = max(line_values), labels= line_labels, values=line_values)
                return render_template('stellar.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5,  stellarUp = stellarUp, stellarDown= stellarDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Stellar Price in USD', max = max(line_values), labels= line_labels, values=line_values)
        return render_template('stellar.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10,  username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, stellarUp = stellarUp, stellarDown= stellarDown, commentsRaw=commentsRaw, title='Stellar Price in USD', max = max(line_values), labels= line_labels, values=line_values)

@app.route('/cardano', methods=['GET', 'POST'])
def cardano():
        labels = []
        values = []
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        for x in range (1, 31):
                c.execute('SELECT Date FROM cardano2 LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message2 = l2
                message2 = cleanDBString(message2)
                labels.append(message2)
        for x in range (1, 31):
                c.execute('SELECT Price FROM cardano LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message = l2
                message = cleanDBString(message)
                values.append(message)
        c.execute("SELECT COUNT(*) FROM comments WHERE currency='cardano'")
        l = c.fetchall()
        l2 = str(l)
        numberComments = l2
        c.execute("SELECT * FROM comments WHERE currency='cardano';")
        l = c.fetchall()
        #l2 = str(l)
        commentsRaw = l
        try:
                comment1 = cleanComment(str(commentsRaw[0]))
                username1 = comment1[1]
                comment1 = comment1[0]
        except IndexError:
                username1 = None
                comment1 = None
        try:
                comment2 = cleanComment(str(commentsRaw[1]))
                username2 = comment2[1]
                comment2 = comment2[0]
        except IndexError:
                username2 = None
                comment2 = None
        try:
                comment3 = cleanComment(str(commentsRaw[2]))
                username3 = comment3[1]
                comment3 = comment3[0]
        except IndexError:
                username3 = None
                comment3 = None
        try:
                comment4 = cleanComment(str(commentsRaw[3]))
                username4 = comment4[1]
                comment4 = comment4[0]
        except IndexError:
                username4 = None
                comment4 = None
        try:
                comment5 = cleanComment(str(commentsRaw[4]))
                username5 = comment5[1]
                comment5 = comment5[0]
        except IndexError:
                username5 = None
                comment5 = None
        try:
                comment6 = cleanComment(str(commentsRaw[5]))
                username6 = comment6[1]
                comment6 = comment6[0]
        except IndexError:
                username6 = None
                comment6 = None
        try:
                comment7 = cleanComment(str(commentsRaw[6]))
                username7 = comment7[1]
                comment7 = comment7[0]
        except IndexError:
                username7 = None
                comment7 = None
        try:
                comment8 = cleanComment(str(commentsRaw[7]))
                username8 = comment8[1]
                comment8 = comment8[0]
        except IndexError:
                username8 = None
                comment8 = None
        try:
                comment9 = cleanComment(str(commentsRaw[8]))
                username9 = comment9[1]
                comment9 = comment9[0]
        except IndexError:
                username9 = None
                comment9 = None
        try:
                comment10 = cleanComment(str(commentsRaw[9]))
                username10 = comment10[1]
                comment10 = comment10[0]
        except IndexError:
                username10 = None
                comment10 = None
        ## NEED TO PROCESS COMMENTSRAW USING SPACING
        ##TO GENERATE A LIST OF USERNAMES, COMMENTS, THEN PASS TO HTML PAGE
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='cardano'")
        l = c.fetchall()
        l2 = str(l)
        cardanoUp = l2
        cardanoUp = cleanDBStringInt(cardanoUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='cardano'")
        l = c.fetchall()
        l2 = str(l)
        cardanoDown = l2
        cardanoDown = cleanDBStringInt(cardanoDown)
        db.close()
        labels.reverse()
        values.reverse()
        colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
        line_labels=labels
        line_values=values        
        if 'username' in session:
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                if request.method == 'POST':
                        comment_form  = request.form['comment']
                        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                        c = db.cursor()
                        c.execute("USE bitcoin;")
                        comment_form = comment_form.replace("'", "")
                        addCommentString = "INSERT INTO comments values('%s', '%s', 'cardano');" % (unicode(comment_form), unicode(username_session))
                        addCommentString = addCommentString.replace("&#39;", "'")
                        addCommentString = h.unescape(addCommentString)
                        c.execute(addCommentString)
                        db.commit()
                        c.execute("SELECT * FROM comments WHERE currency='cardano';")
                        l = c.fetchall()
                        #l2 = str(l)
                        commentsRaw = l
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment6 = cleanComment(str(commentsRaw[5]))
                                username6 = comment6[1]
                                comment6 = comment6[0]
                        except IndexError:
                                username6 = None
                                comment6 = None
                        try:
                                comment7 = cleanComment(str(commentsRaw[6]))
                                username7 = comment7[1]
                                comment7 = comment7[0]
                        except IndexError:
                                username7 = None
                                comment7 = None
                        try:
                                comment8 = cleanComment(str(commentsRaw[7]))
                                username8 = comment8[1]
                                comment8 = comment8[0]
                        except IndexError:
                                username8 = None
                                comment8 = None
                        try:
                                comment9 = cleanComment(str(commentsRaw[8]))
                                username9 = comment9[1]
                                comment9 = comment9[0]
                        except IndexError:
                                username9 = None
                                comment9 = None
                        try:
                                comment10 = cleanComment(str(commentsRaw[9]))
                                username10 = comment10[1]
                                comment10 = comment10[0]
                        except IndexError:
                                username10 = None
                                comment10 = None
                        c.execute("SELECT upvotes FROM userfeedback WHERE currency='cardano'")
                        l = c.fetchall()
                        l2 = str(l)
                        cardanoUp = l2
                        cardanoUp = cleanDBStringInt(cardanoUp)
                        c.execute("SELECT downvotes FROM userfeedback WHERE currency='cardano'")
                        l = c.fetchall()
                        l2 = str(l)
                        cardanoDown = l2
                        cardanoDown = cleanDBStringInt(cardanoDown)
                        db.close()
                        return render_template('cardano.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, cardanoUp = cardanoUp, cardanoDown= cardanoDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Cardano Price in USD', max = max(line_values), labels= line_labels, values=line_values)
                return render_template('cardano.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5,  cardanoUp = cardanoUp, cardanoDown= cardanoDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Cardano Price in USD', max = max(line_values), labels= line_labels, values=line_values)
        return render_template('cardano.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10,  username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, cardanoUp = cardanoUp, cardanoDown= cardanoDown, commentsRaw=commentsRaw, title='Cardano Price in USD', max = max(line_values), labels= line_labels, values=line_values)

@app.route('/tron', methods=['GET', 'POST'])
def tron():
        labels = []
        values = []
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        for x in range (1, 31):
                c.execute('SELECT Date FROM tron2 LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message2 = l2
                message2 = cleanDBString(message2)
                labels.append(message2)
        for x in range (1, 31):
                c.execute('SELECT Price FROM tron LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message = l2
                message = cleanDBString(message)
                values.append(message)
        c.execute("SELECT COUNT(*) FROM comments WHERE currency='tron'")
        l = c.fetchall()
        l2 = str(l)
        numberComments = l2
        c.execute("SELECT * FROM comments WHERE currency='tron';")
        l = c.fetchall()
        #l2 = str(l)
        commentsRaw = l
        try:
                comment1 = cleanComment(str(commentsRaw[0]))
                username1 = comment1[1]
                comment1 = comment1[0]
        except IndexError:
                username1 = None
                comment1 = None
        try:
                comment2 = cleanComment(str(commentsRaw[1]))
                username2 = comment2[1]
                comment2 = comment2[0]
        except IndexError:
                username2 = None
                comment2 = None
        try:
                comment3 = cleanComment(str(commentsRaw[2]))
                username3 = comment3[1]
                comment3 = comment3[0]
        except IndexError:
                username3 = None
                comment3 = None
        try:
                comment4 = cleanComment(str(commentsRaw[3]))
                username4 = comment4[1]
                comment4 = comment4[0]
        except IndexError:
                username4 = None
                comment4 = None
        try:
                comment5 = cleanComment(str(commentsRaw[4]))
                username5 = comment5[1]
                comment5 = comment5[0]
        except IndexError:
                username5 = None
                comment5 = None
        try:
                comment6 = cleanComment(str(commentsRaw[5]))
                username6 = comment6[1]
                comment6 = comment6[0]
        except IndexError:
                username6 = None
                comment6 = None
        try:
                comment7 = cleanComment(str(commentsRaw[6]))
                username7 = comment7[1]
                comment7 = comment7[0]
        except IndexError:
                username7 = None
                comment7 = None
        try:
                comment8 = cleanComment(str(commentsRaw[7]))
                username8 = comment8[1]
                comment8 = comment8[0]
        except IndexError:
                username8 = None
                comment8 = None
        try:
                comment9 = cleanComment(str(commentsRaw[8]))
                username9 = comment9[1]
                comment9 = comment9[0]
        except IndexError:
                username9 = None
                comment9 = None
        try:
                comment10 = cleanComment(str(commentsRaw[9]))
                username10 = comment10[1]
                comment10 = comment10[0]
        except IndexError:
                username10 = None
                comment10 = None
        ## NEED TO PROCESS COMMENTSRAW USING SPACING
        ##TO GENERATE A LIST OF USERNAMES, COMMENTS, THEN PASS TO HTML PAGE
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='tron'")
        l = c.fetchall()
        l2 = str(l)
        tronUp = l2
        tronUp = cleanDBStringInt(tronUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='tron'")
        l = c.fetchall()
        l2 = str(l)
        tronDown = l2
        tronDown = cleanDBStringInt(tronDown)
        db.close()
        labels.reverse()
        values.reverse()
        colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
        line_labels=labels
        line_values=values        
        if 'username' in session:
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                if request.method == 'POST':
                        comment_form  = request.form['comment']
                        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                        c = db.cursor()
                        c.execute("USE bitcoin;")
                        comment_form = comment_form.replace("'", "")
                        addCommentString = "INSERT INTO comments values('%s', '%s', 'tron');" % (unicode(comment_form), unicode(username_session))
                        addCommentString = addCommentString.replace("&#39;", "'")
                        addCommentString = h.unescape(addCommentString)
                        c.execute(addCommentString)
                        db.commit()
                        c.execute("SELECT * FROM comments WHERE currency='tron';")
                        l = c.fetchall()
                        #l2 = str(l)
                        commentsRaw = l
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment6 = cleanComment(str(commentsRaw[5]))
                                username6 = comment6[1]
                                comment6 = comment6[0]
                        except IndexError:
                                username6 = None
                                comment6 = None
                        try:
                                comment7 = cleanComment(str(commentsRaw[6]))
                                username7 = comment7[1]
                                comment7 = comment7[0]
                        except IndexError:
                                username7 = None
                                comment7 = None
                        try:
                                comment8 = cleanComment(str(commentsRaw[7]))
                                username8 = comment8[1]
                                comment8 = comment8[0]
                        except IndexError:
                                username8 = None
                                comment8 = None
                        try:
                                comment9 = cleanComment(str(commentsRaw[8]))
                                username9 = comment9[1]
                                comment9 = comment9[0]
                        except IndexError:
                                username9 = None
                                comment9 = None
                        try:
                                comment10 = cleanComment(str(commentsRaw[9]))
                                username10 = comment10[1]
                                comment10 = comment10[0]
                        except IndexError:
                                username10 = None
                                comment10 = None
                        c.execute("SELECT upvotes FROM userfeedback WHERE currency='tron'")
                        l = c.fetchall()
                        l2 = str(l)
                        tronUp = l2
                        tronUp = cleanDBStringInt(tronUp)
                        c.execute("SELECT downvotes FROM userfeedback WHERE currency='tron'")
                        l = c.fetchall()
                        l2 = str(l)
                        tronDown = l2
                        tronDown = cleanDBStringInt(tronDown)
                        db.close()
                        return render_template('tron.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, tronUp = tronUp, tronDown= tronDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Tron Price in USD', max = max(line_values), labels= line_labels, values=line_values)
                return render_template('tron.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5,  tronUp = tronUp, tronDown= tronDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Tron Price in USD', max = max(line_values), labels= line_labels, values=line_values)
        return render_template('tron.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10,  username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, tronUp = tronUp, tronDown= tronDown, commentsRaw=commentsRaw, title='Tron Price in USD', max = max(line_values), labels= line_labels, values=line_values)

@app.route('/monero', methods=['GET', 'POST'])
def monero():
        labels = []
        values = []
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        for x in range (1, 31):
                c.execute('SELECT Date FROM monero2 LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message2 = l2
                message2 = cleanDBString(message2)
                labels.append(message2)
        for x in range (1, 31):
                c.execute('SELECT Price FROM monero LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message = l2
                message = cleanDBString(message)
                values.append(message)
        c.execute("SELECT COUNT(*) FROM comments WHERE currency='monero'")
        l = c.fetchall()
        l2 = str(l)
        numberComments = l2
        c.execute("SELECT * FROM comments WHERE currency='monero';")
        l = c.fetchall()
        #l2 = str(l)
        commentsRaw = l
        try:
                comment1 = cleanComment(str(commentsRaw[0]))
                username1 = comment1[1]
                comment1 = comment1[0]
        except IndexError:
                username1 = None
                comment1 = None
        try:
                comment2 = cleanComment(str(commentsRaw[1]))
                username2 = comment2[1]
                comment2 = comment2[0]
        except IndexError:
                username2 = None
                comment2 = None
        try:
                comment3 = cleanComment(str(commentsRaw[2]))
                username3 = comment3[1]
                comment3 = comment3[0]
        except IndexError:
                username3 = None
                comment3 = None
        try:
                comment4 = cleanComment(str(commentsRaw[3]))
                username4 = comment4[1]
                comment4 = comment4[0]
        except IndexError:
                username4 = None
                comment4 = None
        try:
                comment5 = cleanComment(str(commentsRaw[4]))
                username5 = comment5[1]
                comment5 = comment5[0]
        except IndexError:
                username5 = None
                comment5 = None
        try:
                comment6 = cleanComment(str(commentsRaw[5]))
                username6 = comment6[1]
                comment6 = comment6[0]
        except IndexError:
                username6 = None
                comment6 = None
        try:
                comment7 = cleanComment(str(commentsRaw[6]))
                username7 = comment7[1]
                comment7 = comment7[0]
        except IndexError:
                username7 = None
                comment7 = None
        try:
                comment8 = cleanComment(str(commentsRaw[7]))
                username8 = comment8[1]
                comment8 = comment8[0]
        except IndexError:
                username8 = None
                comment8 = None
        try:
                comment9 = cleanComment(str(commentsRaw[8]))
                username9 = comment9[1]
                comment9 = comment9[0]
        except IndexError:
                username9 = None
                comment9 = None
        try:
                comment10 = cleanComment(str(commentsRaw[9]))
                username10 = comment10[1]
                comment10 = comment10[0]
        except IndexError:
                username10 = None
                comment10 = None
        ## NEED TO PROCESS COMMENTSRAW USING SPACING
        ##TO GENERATE A LIST OF USERNAMES, COMMENTS, THEN PASS TO HTML PAGE
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='monero'")
        l = c.fetchall()
        l2 = str(l)
        moneroUp = l2
        moneroUp = cleanDBStringInt(moneroUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='monero'")
        l = c.fetchall()
        l2 = str(l)
        moneroDown = l2
        moneroDown = cleanDBStringInt(moneroDown)
        db.close()
        labels.reverse()
        values.reverse()
        colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
        line_labels=labels
        line_values=values        
        if 'username' in session:
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                if request.method == 'POST':
                        comment_form  = request.form['comment']
                        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                        c = db.cursor()
                        c.execute("USE bitcoin;")
                        comment_form = comment_form.replace("'", "")
                        addCommentString = "INSERT INTO comments values('%s', '%s', 'monero');" % (unicode(comment_form), unicode(username_session))
                        addCommentString = addCommentString.replace("&#39;", "'")
                        addCommentString = h.unescape(addCommentString)
                        c.execute(addCommentString)
                        db.commit()
                        c.execute("SELECT * FROM comments WHERE currency='monero';")
                        l = c.fetchall()
                        #l2 = str(l)
                        commentsRaw = l
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment6 = cleanComment(str(commentsRaw[5]))
                                username6 = comment6[1]
                                comment6 = comment6[0]
                        except IndexError:
                                username6 = None
                                comment6 = None
                        try:
                                comment7 = cleanComment(str(commentsRaw[6]))
                                username7 = comment7[1]
                                comment7 = comment7[0]
                        except IndexError:
                                username7 = None
                                comment7 = None
                        try:
                                comment8 = cleanComment(str(commentsRaw[7]))
                                username8 = comment8[1]
                                comment8 = comment8[0]
                        except IndexError:
                                username8 = None
                                comment8 = None
                        try:
                                comment9 = cleanComment(str(commentsRaw[8]))
                                username9 = comment9[1]
                                comment9 = comment9[0]
                        except IndexError:
                                username9 = None
                                comment9 = None
                        try:
                                comment10 = cleanComment(str(commentsRaw[9]))
                                username10 = comment10[1]
                                comment10 = comment10[0]
                        except IndexError:
                                username10 = None
                                comment10 = None
                        c.execute("SELECT upvotes FROM userfeedback WHERE currency='monero'")
                        l = c.fetchall()
                        l2 = str(l)
                        moneroUp = l2
                        moneroUp = cleanDBStringInt(moneroUp)
                        c.execute("SELECT downvotes FROM userfeedback WHERE currency='monero'")
                        l = c.fetchall()
                        l2 = str(l)
                        moneroDown = l2
                        moneroDown = cleanDBStringInt(moneroDown)
                        db.close()
                        return render_template('monero.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, moneroUp = moneroUp, moneroDown= moneroDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Monero Price in USD', max = max(line_values), labels= line_labels, values=line_values)
                return render_template('monero.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5,  moneroUp = moneroUp, moneroDown= moneroDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Monero Price in USD', max = max(line_values), labels= line_labels, values=line_values)
        return render_template('monero.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10,  username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, moneroUp = moneroUp, moneroDown= moneroDown, commentsRaw=commentsRaw, title='Monero Price in USD', max = max(line_values), labels= line_labels, values=line_values)

@app.route('/bitcoinSV', methods=['GET', 'POST'])
def bitcoinSV():
        labels = []
        values = []
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        for x in range (1, 31):
                c.execute('SELECT Date FROM bitcoinSV2 LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message2 = l2
                message2 = cleanDBString(message2)
                labels.append(message2)
        for x in range (1, 31):
                c.execute('SELECT Price FROM bitcoinSV LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message = l2
                message = cleanDBString(message)
                values.append(message)
        c.execute("SELECT COUNT(*) FROM comments WHERE currency='bitcoinSV'")
        l = c.fetchall()
        l2 = str(l)
        numberComments = l2
        c.execute("SELECT * FROM comments WHERE currency='bitcoinSV';")
        l = c.fetchall()
        #l2 = str(l)
        commentsRaw = l
        try:
                comment1 = cleanComment(str(commentsRaw[0]))
                username1 = comment1[1]
                comment1 = comment1[0]
        except IndexError:
                username1 = None
                comment1 = None
        try:
                comment2 = cleanComment(str(commentsRaw[1]))
                username2 = comment2[1]
                comment2 = comment2[0]
        except IndexError:
                username2 = None
                comment2 = None
        try:
                comment3 = cleanComment(str(commentsRaw[2]))
                username3 = comment3[1]
                comment3 = comment3[0]
        except IndexError:
                username3 = None
                comment3 = None
        try:
                comment4 = cleanComment(str(commentsRaw[3]))
                username4 = comment4[1]
                comment4 = comment4[0]
        except IndexError:
                username4 = None
                comment4 = None
        try:
                comment5 = cleanComment(str(commentsRaw[4]))
                username5 = comment5[1]
                comment5 = comment5[0]
        except IndexError:
                username5 = None
                comment5 = None
        try:
                comment6 = cleanComment(str(commentsRaw[5]))
                username6 = comment6[1]
                comment6 = comment6[0]
        except IndexError:
                username6 = None
                comment6 = None
        try:
                comment7 = cleanComment(str(commentsRaw[6]))
                username7 = comment7[1]
                comment7 = comment7[0]
        except IndexError:
                username7 = None
                comment7 = None
        try:
                comment8 = cleanComment(str(commentsRaw[7]))
                username8 = comment8[1]
                comment8 = comment8[0]
        except IndexError:
                username8 = None
                comment8 = None
        try:
                comment9 = cleanComment(str(commentsRaw[8]))
                username9 = comment9[1]
                comment9 = comment9[0]
        except IndexError:
                username9 = None
                comment9 = None
        try:
                comment10 = cleanComment(str(commentsRaw[9]))
                username10 = comment10[1]
                comment10 = comment10[0]
        except IndexError:
                username10 = None
                comment10 = None
        ## NEED TO PROCESS COMMENTSRAW USING SPACING
        ##TO GENERATE A LIST OF USERNAMES, COMMENTS, THEN PASS TO HTML PAGE
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='bitcoinSV'")
        l = c.fetchall()
        l2 = str(l)
        bitcoinSVUp = l2
        bitcoinSVUp = cleanDBStringInt(bitcoinSVUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='bitcoinSV'")
        l = c.fetchall()
        l2 = str(l)
        bitcoinSVDown = l2
        bitcoinSVDown = cleanDBStringInt(bitcoinSVDown)
        db.close()
        labels.reverse()
        values.reverse()
        colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
        line_labels=labels
        line_values=values        
        if 'username' in session:
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                if request.method == 'POST':
                        comment_form  = request.form['comment']
                        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                        c = db.cursor()
                        c.execute("USE bitcoin;")
                        comment_form = comment_form.replace("'", "")
                        addCommentString = "INSERT INTO comments values('%s', '%s', 'bitcoinSV');" % (unicode(comment_form), unicode(username_session))
                        addCommentString = addCommentString.replace("&#39;", "'")
                        addCommentString = h.unescape(addCommentString)
                        c.execute(addCommentString)
                        db.commit()
                        c.execute("SELECT * FROM comments WHERE currency='bitcoinSV';")
                        l = c.fetchall()
                        #l2 = str(l)
                        commentsRaw = l
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment6 = cleanComment(str(commentsRaw[5]))
                                username6 = comment6[1]
                                comment6 = comment6[0]
                        except IndexError:
                                username6 = None
                                comment6 = None
                        try:
                                comment7 = cleanComment(str(commentsRaw[6]))
                                username7 = comment7[1]
                                comment7 = comment7[0]
                        except IndexError:
                                username7 = None
                                comment7 = None
                        try:
                                comment8 = cleanComment(str(commentsRaw[7]))
                                username8 = comment8[1]
                                comment8 = comment8[0]
                        except IndexError:
                                username8 = None
                                comment8 = None
                        try:
                                comment9 = cleanComment(str(commentsRaw[8]))
                                username9 = comment9[1]
                                comment9 = comment9[0]
                        except IndexError:
                                username9 = None
                                comment9 = None
                        try:
                                comment10 = cleanComment(str(commentsRaw[9]))
                                username10 = comment10[1]
                                comment10 = comment10[0]
                        except IndexError:
                                username10 = None
                                comment10 = None
                        c.execute("SELECT upvotes FROM userfeedback WHERE currency='bitcoinSV'")
                        l = c.fetchall()
                        l2 = str(l)
                        bitcoinSVUp = l2
                        bitcoinSVUp = cleanDBStringInt(bitcoinSVUp)
                        c.execute("SELECT downvotes FROM userfeedback WHERE currency='bitcoinSV'")
                        l = c.fetchall()
                        l2 = str(l)
                        bitcoinSVDown = l2
                        bitcoinSVDown = cleanDBStringInt(bitcoinSVDown)
                        db.close()
                        return render_template('bitcoinSV.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, bitcoinSVUp = bitcoinSVUp, bitcoinSVDown= bitcoinSVDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Bitcoin SV Price in USD', max = max(line_values), labels= line_labels, values=line_values)
                return render_template('bitcoinSV.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5,  bitcoinSVUp = bitcoinSVUp, bitcoinSVDown= bitcoinSVDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Bitcoin SV Price in USD', max = max(line_values), labels= line_labels, values=line_values)
        return render_template('bitcoinSV.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10,  username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, bitcoinSVUp = bitcoinSVUp, bitcoinSVDown= bitcoinSVDown, commentsRaw=commentsRaw, title='Bitcoin SV Price in USD', max = max(line_values), labels= line_labels, values=line_values)

@app.route('/dash', methods=['GET', 'POST'])
def dash():
        labels = []
        values = []
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        for x in range (1, 31):
                c.execute('SELECT Date FROM dash2 LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message2 = l2
                message2 = cleanDBString(message2)
                labels.append(message2)
        for x in range (1, 31):
                c.execute('SELECT Price FROM dash LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message = l2
                message = cleanDBString(message)
                values.append(message)
        c.execute("SELECT COUNT(*) FROM comments WHERE currency='dash'")
        l = c.fetchall()
        l2 = str(l)
        numberComments = l2
        c.execute("SELECT * FROM comments WHERE currency='dash';")
        l = c.fetchall()
        #l2 = str(l)
        commentsRaw = l
        try:
                comment1 = cleanComment(str(commentsRaw[0]))
                username1 = comment1[1]
                comment1 = comment1[0]
        except IndexError:
                username1 = None
                comment1 = None
        try:
                comment2 = cleanComment(str(commentsRaw[1]))
                username2 = comment2[1]
                comment2 = comment2[0]
        except IndexError:
                username2 = None
                comment2 = None
        try:
                comment3 = cleanComment(str(commentsRaw[2]))
                username3 = comment3[1]
                comment3 = comment3[0]
        except IndexError:
                username3 = None
                comment3 = None
        try:
                comment4 = cleanComment(str(commentsRaw[3]))
                username4 = comment4[1]
                comment4 = comment4[0]
        except IndexError:
                username4 = None
                comment4 = None
        try:
                comment5 = cleanComment(str(commentsRaw[4]))
                username5 = comment5[1]
                comment5 = comment5[0]
        except IndexError:
                username5 = None
                comment5 = None
        try:
                comment6 = cleanComment(str(commentsRaw[5]))
                username6 = comment6[1]
                comment6 = comment6[0]
        except IndexError:
                username6 = None
                comment6 = None
        try:
                comment7 = cleanComment(str(commentsRaw[6]))
                username7 = comment7[1]
                comment7 = comment7[0]
        except IndexError:
                username7 = None
                comment7 = None
        try:
                comment8 = cleanComment(str(commentsRaw[7]))
                username8 = comment8[1]
                comment8 = comment8[0]
        except IndexError:
                username8 = None
                comment8 = None
        try:
                comment9 = cleanComment(str(commentsRaw[8]))
                username9 = comment9[1]
                comment9 = comment9[0]
        except IndexError:
                username9 = None
                comment9 = None
        try:
                comment10 = cleanComment(str(commentsRaw[9]))
                username10 = comment10[1]
                comment10 = comment10[0]
        except IndexError:
                username10 = None
                comment10 = None
        ## NEED TO PROCESS COMMENTSRAW USING SPACING
        ##TO GENERATE A LIST OF USERNAMES, COMMENTS, THEN PASS TO HTML PAGE
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='dash'")
        l = c.fetchall()
        l2 = str(l)
        dashUp = l2
        dashUp = cleanDBStringInt(dashUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='dash'")
        l = c.fetchall()
        l2 = str(l)
        dashDown = l2
        dashDown = cleanDBStringInt(dashDown)
        db.close()
        labels.reverse()
        values.reverse()
        colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
        line_labels=labels
        line_values=values        
        if 'username' in session:
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                if request.method == 'POST':
                        comment_form  = request.form['comment']
                        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                        c = db.cursor()
                        c.execute("USE bitcoin;")
                        comment_form = comment_form.replace("'", "")
                        addCommentString = "INSERT INTO comments values('%s', '%s', 'dash');" % (unicode(comment_form), unicode(username_session))
                        addCommentString = addCommentString.replace("&#39;", "'")
                        addCommentString = h.unescape(addCommentString)
                        c.execute(addCommentString)
                        db.commit()
                        c.execute("SELECT * FROM comments WHERE currency='dash';")
                        l = c.fetchall()
                        #l2 = str(l)
                        commentsRaw = l
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment6 = cleanComment(str(commentsRaw[5]))
                                username6 = comment6[1]
                                comment6 = comment6[0]
                        except IndexError:
                                username6 = None
                                comment6 = None
                        try:
                                comment7 = cleanComment(str(commentsRaw[6]))
                                username7 = comment7[1]
                                comment7 = comment7[0]
                        except IndexError:
                                username7 = None
                                comment7 = None
                        try:
                                comment8 = cleanComment(str(commentsRaw[7]))
                                username8 = comment8[1]
                                comment8 = comment8[0]
                        except IndexError:
                                username8 = None
                                comment8 = None
                        try:
                                comment9 = cleanComment(str(commentsRaw[8]))
                                username9 = comment9[1]
                                comment9 = comment9[0]
                        except IndexError:
                                username9 = None
                                comment9 = None
                        try:
                                comment10 = cleanComment(str(commentsRaw[9]))
                                username10 = comment10[1]
                                comment10 = comment10[0]
                        except IndexError:
                                username10 = None
                                comment10 = None
                        c.execute("SELECT upvotes FROM userfeedback WHERE currency='dash'")
                        l = c.fetchall()
                        l2 = str(l)
                        dashUp = l2
                        dashUp = cleanDBStringInt(dashUp)
                        c.execute("SELECT downvotes FROM userfeedback WHERE currency='dash'")
                        l = c.fetchall()
                        l2 = str(l)
                        dashDown = l2
                        dashDown = cleanDBStringInt(dashDown)
                        db.close()
                        return render_template('dash.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, dashUp = dashUp, dashDown= dashDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Dash Price in USD', max = max(line_values), labels= line_labels, values=line_values)
                return render_template('dash.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5,  dashUp = dashUp, dashDown= dashDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Dash Price in USD', max = max(line_values), labels= line_labels, values=line_values)
        return render_template('dash.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10,  username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, dashUp = dashUp, dashDown= dashDown, commentsRaw=commentsRaw, title='Dash Price in USD', max = max(line_values), labels= line_labels, values=line_values)

@app.route('/iota', methods=['GET', 'POST'])
def iota():
        labels = []
        values = []
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        for x in range (1, 31):
                c.execute('SELECT Date FROM iota2 LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message2 = l2
                message2 = cleanDBString(message2)
                labels.append(message2)
        for x in range (1, 31):
                c.execute('SELECT Price FROM iota LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message = l2
                message = cleanDBString(message)
                values.append(message)
        c.execute("SELECT COUNT(*) FROM comments WHERE currency='iota'")
        l = c.fetchall()
        l2 = str(l)
        numberComments = l2
        c.execute("SELECT * FROM comments WHERE currency='iota';")
        l = c.fetchall()
        #l2 = str(l)
        commentsRaw = l
        try:
                comment1 = cleanComment(str(commentsRaw[0]))
                username1 = comment1[1]
                comment1 = comment1[0]
        except IndexError:
                username1 = None
                comment1 = None
        try:
                comment2 = cleanComment(str(commentsRaw[1]))
                username2 = comment2[1]
                comment2 = comment2[0]
        except IndexError:
                username2 = None
                comment2 = None
        try:
                comment3 = cleanComment(str(commentsRaw[2]))
                username3 = comment3[1]
                comment3 = comment3[0]
        except IndexError:
                username3 = None
                comment3 = None
        try:
                comment4 = cleanComment(str(commentsRaw[3]))
                username4 = comment4[1]
                comment4 = comment4[0]
        except IndexError:
                username4 = None
                comment4 = None
        try:
                comment5 = cleanComment(str(commentsRaw[4]))
                username5 = comment5[1]
                comment5 = comment5[0]
        except IndexError:
                username5 = None
                comment5 = None
        try:
                comment6 = cleanComment(str(commentsRaw[5]))
                username6 = comment6[1]
                comment6 = comment6[0]
        except IndexError:
                username6 = None
                comment6 = None
        try:
                comment7 = cleanComment(str(commentsRaw[6]))
                username7 = comment7[1]
                comment7 = comment7[0]
        except IndexError:
                username7 = None
                comment7 = None
        try:
                comment8 = cleanComment(str(commentsRaw[7]))
                username8 = comment8[1]
                comment8 = comment8[0]
        except IndexError:
                username8 = None
                comment8 = None
        try:
                comment9 = cleanComment(str(commentsRaw[8]))
                username9 = comment9[1]
                comment9 = comment9[0]
        except IndexError:
                username9 = None
                comment9 = None
        try:
                comment10 = cleanComment(str(commentsRaw[9]))
                username10 = comment10[1]
                comment10 = comment10[0]
        except IndexError:
                username10 = None
                comment10 = None
        ## NEED TO PROCESS COMMENTSRAW USING SPACING
        ##TO GENERATE A LIST OF USERNAMES, COMMENTS, THEN PASS TO HTML PAGE
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='iota'")
        l = c.fetchall()
        l2 = str(l)
        iotaUp = l2
        iotaUp = cleanDBStringInt(iotaUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='iota'")
        l = c.fetchall()
        l2 = str(l)
        iotaDown = l2
        iotaDown = cleanDBStringInt(iotaDown)
        db.close()
        labels.reverse()
        values.reverse()
        colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
        line_labels=labels
        line_values=values        
        if 'username' in session:
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                if request.method == 'POST':
                        comment_form  = request.form['comment']
                        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                        c = db.cursor()
                        c.execute("USE bitcoin;")
                        comment_form = comment_form.replace("'", "")
                        addCommentString = "INSERT INTO comments values('%s', '%s', 'iota');" % (unicode(comment_form), unicode(username_session))
                        addCommentString = addCommentString.replace("&#39;", "'")
                        addCommentString = h.unescape(addCommentString)
                        c.execute(addCommentString)
                        db.commit()
                        c.execute("SELECT * FROM comments WHERE currency='iota';")
                        l = c.fetchall()
                        #l2 = str(l)
                        commentsRaw = l
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment6 = cleanComment(str(commentsRaw[5]))
                                username6 = comment6[1]
                                comment6 = comment6[0]
                        except IndexError:
                                username6 = None
                                comment6 = None
                        try:
                                comment7 = cleanComment(str(commentsRaw[6]))
                                username7 = comment7[1]
                                comment7 = comment7[0]
                        except IndexError:
                                username7 = None
                                comment7 = None
                        try:
                                comment8 = cleanComment(str(commentsRaw[7]))
                                username8 = comment8[1]
                                comment8 = comment8[0]
                        except IndexError:
                                username8 = None
                                comment8 = None
                        try:
                                comment9 = cleanComment(str(commentsRaw[8]))
                                username9 = comment9[1]
                                comment9 = comment9[0]
                        except IndexError:
                                username9 = None
                                comment9 = None
                        try:
                                comment10 = cleanComment(str(commentsRaw[9]))
                                username10 = comment10[1]
                                comment10 = comment10[0]
                        except IndexError:
                                username10 = None
                                comment10 = None
                        c.execute("SELECT upvotes FROM userfeedback WHERE currency='iota'")
                        l = c.fetchall()
                        l2 = str(l)
                        iotaUp = l2
                        iotaUp = cleanDBStringInt(iotaUp)
                        c.execute("SELECT downvotes FROM userfeedback WHERE currency='iota'")
                        l = c.fetchall()
                        l2 = str(l)
                        iotaDown = l2
                        iotaDown = cleanDBStringInt(iotaDown)
                        db.close()
                        return render_template('iota.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, iotaUp = iotaUp, iotaDown= iotaDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='IOTA Price in USD', max = max(line_values), labels= line_labels, values=line_values)
                return render_template('iota.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5,  iotaUp = iotaUp, iotaDown= iotaDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='IOTA Price in USD', max = max(line_values), labels= line_labels, values=line_values)
        return render_template('iota.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10,  username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, iotaUp = iotaUp, iotaDown= iotaDown, commentsRaw=commentsRaw, title='IOTA Price in USD', max = max(line_values), labels= line_labels, values=line_values)

@app.route('/tezos', methods=['GET', 'POST'])
def tezos():
        labels = []
        values = []
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        for x in range (1, 31):
                c.execute('SELECT Date FROM tezos2 LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message2 = l2
                message2 = cleanDBString(message2)
                labels.append(message2)
        for x in range (1, 31):
                c.execute('SELECT Price FROM tezos LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message = l2
                message = cleanDBString(message)
                values.append(message)
        c.execute("SELECT COUNT(*) FROM comments WHERE currency='tezos'")
        l = c.fetchall()
        l2 = str(l)
        numberComments = l2
        c.execute("SELECT * FROM comments WHERE currency='tezos';")
        l = c.fetchall()
        #l2 = str(l)
        commentsRaw = l
        try:
                comment1 = cleanComment(str(commentsRaw[0]))
                username1 = comment1[1]
                comment1 = comment1[0]
        except IndexError:
                username1 = None
                comment1 = None
        try:
                comment2 = cleanComment(str(commentsRaw[1]))
                username2 = comment2[1]
                comment2 = comment2[0]
        except IndexError:
                username2 = None
                comment2 = None
        try:
                comment3 = cleanComment(str(commentsRaw[2]))
                username3 = comment3[1]
                comment3 = comment3[0]
        except IndexError:
                username3 = None
                comment3 = None
        try:
                comment4 = cleanComment(str(commentsRaw[3]))
                username4 = comment4[1]
                comment4 = comment4[0]
        except IndexError:
                username4 = None
                comment4 = None
        try:
                comment5 = cleanComment(str(commentsRaw[4]))
                username5 = comment5[1]
                comment5 = comment5[0]
        except IndexError:
                username5 = None
                comment5 = None
        try:
                comment6 = cleanComment(str(commentsRaw[5]))
                username6 = comment6[1]
                comment6 = comment6[0]
        except IndexError:
                username6 = None
                comment6 = None
        try:
                comment7 = cleanComment(str(commentsRaw[6]))
                username7 = comment7[1]
                comment7 = comment7[0]
        except IndexError:
                username7 = None
                comment7 = None
        try:
                comment8 = cleanComment(str(commentsRaw[7]))
                username8 = comment8[1]
                comment8 = comment8[0]
        except IndexError:
                username8 = None
                comment8 = None
        try:
                comment9 = cleanComment(str(commentsRaw[8]))
                username9 = comment9[1]
                comment9 = comment9[0]
        except IndexError:
                username9 = None
                comment9 = None
        try:
                comment10 = cleanComment(str(commentsRaw[9]))
                username10 = comment10[1]
                comment10 = comment10[0]
        except IndexError:
                username10 = None
                comment10 = None
        ## NEED TO PROCESS COMMENTSRAW USING SPACING
        ##TO GENERATE A LIST OF USERNAMES, COMMENTS, THEN PASS TO HTML PAGE
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='tezos'")
        l = c.fetchall()
        l2 = str(l)
        tezosUp = l2
        tezosUp = cleanDBStringInt(tezosUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='tezos'")
        l = c.fetchall()
        l2 = str(l)
        tezosDown = l2
        tezosDown = cleanDBStringInt(tezosDown)
        db.close()
        labels.reverse()
        values.reverse()
        colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
        line_labels=labels
        line_values=values        
        if 'username' in session:
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                if request.method == 'POST':
                        comment_form  = request.form['comment']
                        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                        c = db.cursor()
                        c.execute("USE bitcoin;")
                        comment_form = comment_form.replace("'", "")
                        addCommentString = "INSERT INTO comments values('%s', '%s', 'tezos');" % (unicode(comment_form), unicode(username_session))
                        addCommentString = addCommentString.replace("&#39;", "'")
                        addCommentString = h.unescape(addCommentString)
                        c.execute(addCommentString)
                        db.commit()
                        c.execute("SELECT * FROM comments WHERE currency='tezos';")
                        l = c.fetchall()
                        #l2 = str(l)
                        commentsRaw = l
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment6 = cleanComment(str(commentsRaw[5]))
                                username6 = comment6[1]
                                comment6 = comment6[0]
                        except IndexError:
                                username6 = None
                                comment6 = None
                        try:
                                comment7 = cleanComment(str(commentsRaw[6]))
                                username7 = comment7[1]
                                comment7 = comment7[0]
                        except IndexError:
                                username7 = None
                                comment7 = None
                        try:
                                comment8 = cleanComment(str(commentsRaw[7]))
                                username8 = comment8[1]
                                comment8 = comment8[0]
                        except IndexError:
                                username8 = None
                                comment8 = None
                        try:
                                comment9 = cleanComment(str(commentsRaw[8]))
                                username9 = comment9[1]
                                comment9 = comment9[0]
                        except IndexError:
                                username9 = None
                                comment9 = None
                        try:
                                comment10 = cleanComment(str(commentsRaw[9]))
                                username10 = comment10[1]
                                comment10 = comment10[0]
                        except IndexError:
                                username10 = None
                                comment10 = None
                        c.execute("SELECT upvotes FROM userfeedback WHERE currency='tezos'")
                        l = c.fetchall()
                        l2 = str(l)
                        tezosUp = l2
                        tezosUp = cleanDBStringInt(tezosUp)
                        c.execute("SELECT downvotes FROM userfeedback WHERE currency='tezos'")
                        l = c.fetchall()
                        l2 = str(l)
                        tezosDown = l2
                        tezosDown = cleanDBStringInt(tezosDown)
                        db.close()
                        return render_template('tezos.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, tezosUp = tezosUp, tezosDown= tezosDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Tezos Price in USD', max = max(line_values), labels= line_labels, values=line_values)
                return render_template('tezos.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5,  tezosUp = tezosUp, tezosDown= tezosDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Tezos Price in USD', max = max(line_values), labels= line_labels, values=line_values)
        return render_template('tezos.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10,  username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, tezosUp = tezosUp, tezosDown= tezosDown, commentsRaw=commentsRaw, title='Tezos Price in USD', max = max(line_values), labels= line_labels, values=line_values)

@app.route('/cosmos', methods=['GET', 'POST'])
def cosmos():
        labels = []
        values = []
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        for x in range (1, 31):
                c.execute('SELECT Date FROM cosmos2 LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message2 = l2
                message2 = cleanDBString(message2)
                labels.append(message2)
        for x in range (1, 31):
                c.execute('SELECT Price FROM cosmos LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message = l2
                message = cleanDBString(message)
                values.append(message)
        c.execute("SELECT COUNT(*) FROM comments WHERE currency='cosmos'")
        l = c.fetchall()
        l2 = str(l)
        numberComments = l2
        c.execute("SELECT * FROM comments WHERE currency='cosmos';")
        l = c.fetchall()
        #l2 = str(l)
        commentsRaw = l
        try:
                comment1 = cleanComment(str(commentsRaw[0]))
                username1 = comment1[1]
                comment1 = comment1[0]
        except IndexError:
                username1 = None
                comment1 = None
        try:
                comment2 = cleanComment(str(commentsRaw[1]))
                username2 = comment2[1]
                comment2 = comment2[0]
        except IndexError:
                username2 = None
                comment2 = None
        try:
                comment3 = cleanComment(str(commentsRaw[2]))
                username3 = comment3[1]
                comment3 = comment3[0]
        except IndexError:
                username3 = None
                comment3 = None
        try:
                comment4 = cleanComment(str(commentsRaw[3]))
                username4 = comment4[1]
                comment4 = comment4[0]
        except IndexError:
                username4 = None
                comment4 = None
        try:
                comment5 = cleanComment(str(commentsRaw[4]))
                username5 = comment5[1]
                comment5 = comment5[0]
        except IndexError:
                username5 = None
                comment5 = None
        try:
                comment6 = cleanComment(str(commentsRaw[5]))
                username6 = comment6[1]
                comment6 = comment6[0]
        except IndexError:
                username6 = None
                comment6 = None
        try:
                comment7 = cleanComment(str(commentsRaw[6]))
                username7 = comment7[1]
                comment7 = comment7[0]
        except IndexError:
                username7 = None
                comment7 = None
        try:
                comment8 = cleanComment(str(commentsRaw[7]))
                username8 = comment8[1]
                comment8 = comment8[0]
        except IndexError:
                username8 = None
                comment8 = None
        try:
                comment9 = cleanComment(str(commentsRaw[8]))
                username9 = comment9[1]
                comment9 = comment9[0]
        except IndexError:
                username9 = None
                comment9 = None
        try:
                comment10 = cleanComment(str(commentsRaw[9]))
                username10 = comment10[1]
                comment10 = comment10[0]
        except IndexError:
                username10 = None
                comment10 = None
        ## NEED TO PROCESS COMMENTSRAW USING SPACING
        ##TO GENERATE A LIST OF USERNAMES, COMMENTS, THEN PASS TO HTML PAGE
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='cosmos'")
        l = c.fetchall()
        l2 = str(l)
        cosmosUp = l2
        cosmosUp = cleanDBStringInt(cosmosUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='cosmos'")
        l = c.fetchall()
        l2 = str(l)
        cosmosDown = l2
        cosmosDown = cleanDBStringInt(cosmosDown)
        db.close()
        labels.reverse()
        values.reverse()
        colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
        line_labels=labels
        line_values=values        
        if 'username' in session:
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                if request.method == 'POST':
                        comment_form  = request.form['comment']
                        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                        c = db.cursor()
                        c.execute("USE bitcoin;")
                        comment_form = comment_form.replace("'", "")
                        addCommentString = "INSERT INTO comments values('%s', '%s', 'cosmos');" % (unicode(comment_form), unicode(username_session))
                        addCommentString = addCommentString.replace("&#39;", "'")
                        addCommentString = h.unescape(addCommentString)
                        c.execute(addCommentString)
                        db.commit()
                        c.execute("SELECT * FROM comments WHERE currency='cosmos';")
                        l = c.fetchall()
                        #l2 = str(l)
                        commentsRaw = l
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment6 = cleanComment(str(commentsRaw[5]))
                                username6 = comment6[1]
                                comment6 = comment6[0]
                        except IndexError:
                                username6 = None
                                comment6 = None
                        try:
                                comment7 = cleanComment(str(commentsRaw[6]))
                                username7 = comment7[1]
                                comment7 = comment7[0]
                        except IndexError:
                                username7 = None
                                comment7 = None
                        try:
                                comment8 = cleanComment(str(commentsRaw[7]))
                                username8 = comment8[1]
                                comment8 = comment8[0]
                        except IndexError:
                                username8 = None
                                comment8 = None
                        try:
                                comment9 = cleanComment(str(commentsRaw[8]))
                                username9 = comment9[1]
                                comment9 = comment9[0]
                        except IndexError:
                                username9 = None
                                comment9 = None
                        try:
                                comment10 = cleanComment(str(commentsRaw[9]))
                                username10 = comment10[1]
                                comment10 = comment10[0]
                        except IndexError:
                                username10 = None
                                comment10 = None
                        c.execute("SELECT upvotes FROM userfeedback WHERE currency='cosmos'")
                        l = c.fetchall()
                        l2 = str(l)
                        cosmosUp = l2
                        cosmosUp = cleanDBStringInt(cosmosUp)
                        c.execute("SELECT downvotes FROM userfeedback WHERE currency='cosmos'")
                        l = c.fetchall()
                        l2 = str(l)
                        cosmosDown = l2
                        cosmosDown = cleanDBStringInt(cosmosDown)
                        db.close()
                        return render_template('cosmos.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, cosmosUp = cosmosUp, cosmosDown= cosmosDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Cosmos Price in USD', max = max(line_values), labels= line_labels, values=line_values)
                return render_template('cosmos.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5,  cosmosUp = cosmosUp, cosmosDown= cosmosDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Cosmos Price in USD', max = max(line_values), labels= line_labels, values=line_values)
        return render_template('cosmos.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10,  username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, cosmosUp = cosmosUp, cosmosDown= cosmosDown, commentsRaw=commentsRaw, title='Cosmos Price in USD', max = max(line_values), labels= line_labels, values=line_values)

@app.route('/ethereumClassic', methods=['GET', 'POST'])
def ethereumClassic():
        labels = []
        values = []
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        for x in range (1, 31):
                c.execute('SELECT Date FROM ethereumClassic2 LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message2 = l2
                message2 = cleanDBString(message2)
                labels.append(message2)
        for x in range (1, 31):
                c.execute('SELECT Price FROM ethereumClassic LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message = l2
                message = cleanDBString(message)
                values.append(message)
        c.execute("SELECT COUNT(*) FROM comments WHERE currency='ethereumClassic'")
        l = c.fetchall()
        l2 = str(l)
        numberComments = l2
        c.execute("SELECT * FROM comments WHERE currency='ethereumClassic';")
        l = c.fetchall()
        #l2 = str(l)
        commentsRaw = l
        try:
                comment1 = cleanComment(str(commentsRaw[0]))
                username1 = comment1[1]
                comment1 = comment1[0]
        except IndexError:
                username1 = None
                comment1 = None
        try:
                comment2 = cleanComment(str(commentsRaw[1]))
                username2 = comment2[1]
                comment2 = comment2[0]
        except IndexError:
                username2 = None
                comment2 = None
        try:
                comment3 = cleanComment(str(commentsRaw[2]))
                username3 = comment3[1]
                comment3 = comment3[0]
        except IndexError:
                username3 = None
                comment3 = None
        try:
                comment4 = cleanComment(str(commentsRaw[3]))
                username4 = comment4[1]
                comment4 = comment4[0]
        except IndexError:
                username4 = None
                comment4 = None
        try:
                comment5 = cleanComment(str(commentsRaw[4]))
                username5 = comment5[1]
                comment5 = comment5[0]
        except IndexError:
                username5 = None
                comment5 = None
        try:
                comment6 = cleanComment(str(commentsRaw[5]))
                username6 = comment6[1]
                comment6 = comment6[0]
        except IndexError:
                username6 = None
                comment6 = None
        try:
                comment7 = cleanComment(str(commentsRaw[6]))
                username7 = comment7[1]
                comment7 = comment7[0]
        except IndexError:
                username7 = None
                comment7 = None
        try:
                comment8 = cleanComment(str(commentsRaw[7]))
                username8 = comment8[1]
                comment8 = comment8[0]
        except IndexError:
                username8 = None
                comment8 = None
        try:
                comment9 = cleanComment(str(commentsRaw[8]))
                username9 = comment9[1]
                comment9 = comment9[0]
        except IndexError:
                username9 = None
                comment9 = None
        try:
                comment10 = cleanComment(str(commentsRaw[9]))
                username10 = comment10[1]
                comment10 = comment10[0]
        except IndexError:
                username10 = None
                comment10 = None
        ## NEED TO PROCESS COMMENTSRAW USING SPACING
        ##TO GENERATE A LIST OF USERNAMES, COMMENTS, THEN PASS TO HTML PAGE
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='ethereumClassic'")
        l = c.fetchall()
        l2 = str(l)
        ethereumClassicUp = l2
        ethereumClassicUp = cleanDBStringInt(ethereumClassicUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='ethereumClassic'")
        l = c.fetchall()
        l2 = str(l)
        ethereumClassicDown = l2
        ethereumClassicDown = cleanDBStringInt(ethereumClassicDown)
        db.close()
        labels.reverse()
        values.reverse()
        colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
        line_labels=labels
        line_values=values        
        if 'username' in session:
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                if request.method == 'POST':
                        comment_form  = request.form['comment']
                        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                        c = db.cursor()
                        c.execute("USE bitcoin;")
                        comment_form = comment_form.replace("'", "")
                        addCommentString = "INSERT INTO comments values('%s', '%s', 'ethereumClassic');" % (unicode(comment_form), unicode(username_session))
                        addCommentString = addCommentString.replace("&#39;", "'")
                        addCommentString = h.unescape(addCommentString)
                        c.execute(addCommentString)
                        db.commit()
                        c.execute("SELECT * FROM comments WHERE currency='ethereumClassic';")
                        l = c.fetchall()
                        #l2 = str(l)
                        commentsRaw = l
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment6 = cleanComment(str(commentsRaw[5]))
                                username6 = comment6[1]
                                comment6 = comment6[0]
                        except IndexError:
                                username6 = None
                                comment6 = None
                        try:
                                comment7 = cleanComment(str(commentsRaw[6]))
                                username7 = comment7[1]
                                comment7 = comment7[0]
                        except IndexError:
                                username7 = None
                                comment7 = None
                        try:
                                comment8 = cleanComment(str(commentsRaw[7]))
                                username8 = comment8[1]
                                comment8 = comment8[0]
                        except IndexError:
                                username8 = None
                                comment8 = None
                        try:
                                comment9 = cleanComment(str(commentsRaw[8]))
                                username9 = comment9[1]
                                comment9 = comment9[0]
                        except IndexError:
                                username9 = None
                                comment9 = None
                        try:
                                comment10 = cleanComment(str(commentsRaw[9]))
                                username10 = comment10[1]
                                comment10 = comment10[0]
                        except IndexError:
                                username10 = None
                                comment10 = None
                        c.execute("SELECT upvotes FROM userfeedback WHERE currency='ethereumClassic'")
                        l = c.fetchall()
                        l2 = str(l)
                        ethereumClassicUp = l2
                        ethereumClassicUp = cleanDBStringInt(ethereumClassicUp)
                        c.execute("SELECT downvotes FROM userfeedback WHERE currency='ethereumClassic'")
                        l = c.fetchall()
                        l2 = str(l)
                        ethereumClassicDown = l2
                        ethereumClassicDown = cleanDBStringInt(ethereumClassicDown)
                        db.close()
                        return render_template('ethereumClassic.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, ethereumClassicUp = ethereumClassicUp, ethereumClassicDown= ethereumClassicDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Ethereum Classic Price in USD', max = max(line_values), labels= line_labels, values=line_values)
                return render_template('ethereumClassic.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5,  ethereumClassicUp = ethereumClassicUp, ethereumClassicDown= ethereumClassicDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Ethereum Classic Price in USD', max = max(line_values), labels= line_labels, values=line_values)
        return render_template('ethereumClassic.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10,  username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, ethereumClassicUp = ethereumClassicUp, ethereumClassicDown= ethereumClassicDown, commentsRaw=commentsRaw, title='Ethereum Classic Price in USD', max = max(line_values), labels= line_labels, values=line_values)

@app.route('/neo', methods=['GET', 'POST'])
def neo():
        labels = []
        values = []
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        for x in range (1, 31):
                c.execute('SELECT Date FROM neo2 LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message2 = l2
                message2 = cleanDBString(message2)
                labels.append(message2)
        for x in range (1, 31):
                c.execute('SELECT Price FROM neo LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message = l2
                message = cleanDBString(message)
                values.append(message)
        c.execute("SELECT COUNT(*) FROM comments WHERE currency='neo'")
        l = c.fetchall()
        l2 = str(l)
        numberComments = l2
        c.execute("SELECT * FROM comments WHERE currency='neo';")
        l = c.fetchall()
        #l2 = str(l)
        commentsRaw = l
        try:
                comment1 = cleanComment(str(commentsRaw[0]))
                username1 = comment1[1]
                comment1 = comment1[0]
        except IndexError:
                username1 = None
                comment1 = None
        try:
                comment2 = cleanComment(str(commentsRaw[1]))
                username2 = comment2[1]
                comment2 = comment2[0]
        except IndexError:
                username2 = None
                comment2 = None
        try:
                comment3 = cleanComment(str(commentsRaw[2]))
                username3 = comment3[1]
                comment3 = comment3[0]
        except IndexError:
                username3 = None
                comment3 = None
        try:
                comment4 = cleanComment(str(commentsRaw[3]))
                username4 = comment4[1]
                comment4 = comment4[0]
        except IndexError:
                username4 = None
                comment4 = None
        try:
                comment5 = cleanComment(str(commentsRaw[4]))
                username5 = comment5[1]
                comment5 = comment5[0]
        except IndexError:
                username5 = None
                comment5 = None
        try:
                comment6 = cleanComment(str(commentsRaw[5]))
                username6 = comment6[1]
                comment6 = comment6[0]
        except IndexError:
                username6 = None
                comment6 = None
        try:
                comment7 = cleanComment(str(commentsRaw[6]))
                username7 = comment7[1]
                comment7 = comment7[0]
        except IndexError:
                username7 = None
                comment7 = None
        try:
                comment8 = cleanComment(str(commentsRaw[7]))
                username8 = comment8[1]
                comment8 = comment8[0]
        except IndexError:
                username8 = None
                comment8 = None
        try:
                comment9 = cleanComment(str(commentsRaw[8]))
                username9 = comment9[1]
                comment9 = comment9[0]
        except IndexError:
                username9 = None
                comment9 = None
        try:
                comment10 = cleanComment(str(commentsRaw[9]))
                username10 = comment10[1]
                comment10 = comment10[0]
        except IndexError:
                username10 = None
                comment10 = None
        ## NEED TO PROCESS COMMENTSRAW USING SPACING
        ##TO GENERATE A LIST OF USERNAMES, COMMENTS, THEN PASS TO HTML PAGE
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='neo'")
        l = c.fetchall()
        l2 = str(l)
        neoUp = l2
        neoUp = cleanDBStringInt(neoUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='neo'")
        l = c.fetchall()
        l2 = str(l)
        neoDown = l2
        neoDown = cleanDBStringInt(neoDown)
        db.close()
        labels.reverse()
        values.reverse()
        colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
        line_labels=labels
        line_values=values        
        if 'username' in session:
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                if request.method == 'POST':
                        comment_form  = request.form['comment']
                        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                        c = db.cursor()
                        c.execute("USE bitcoin;")
                        comment_form = comment_form.replace("'", "")
                        addCommentString = "INSERT INTO comments values('%s', '%s', 'neo');" % (unicode(comment_form), unicode(username_session))
                        addCommentString = addCommentString.replace("&#39;", "'")
                        addCommentString = h.unescape(addCommentString)
                        c.execute(addCommentString)
                        db.commit()
                        c.execute("SELECT * FROM comments WHERE currency='neo';")
                        l = c.fetchall()
                        #l2 = str(l)
                        commentsRaw = l
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment6 = cleanComment(str(commentsRaw[5]))
                                username6 = comment6[1]
                                comment6 = comment6[0]
                        except IndexError:
                                username6 = None
                                comment6 = None
                        try:
                                comment7 = cleanComment(str(commentsRaw[6]))
                                username7 = comment7[1]
                                comment7 = comment7[0]
                        except IndexError:
                                username7 = None
                                comment7 = None
                        try:
                                comment8 = cleanComment(str(commentsRaw[7]))
                                username8 = comment8[1]
                                comment8 = comment8[0]
                        except IndexError:
                                username8 = None
                                comment8 = None
                        try:
                                comment9 = cleanComment(str(commentsRaw[8]))
                                username9 = comment9[1]
                                comment9 = comment9[0]
                        except IndexError:
                                username9 = None
                                comment9 = None
                        try:
                                comment10 = cleanComment(str(commentsRaw[9]))
                                username10 = comment10[1]
                                comment10 = comment10[0]
                        except IndexError:
                                username10 = None
                                comment10 = None
                        c.execute("SELECT upvotes FROM userfeedback WHERE currency='neo'")
                        l = c.fetchall()
                        l2 = str(l)
                        neoUp = l2
                        neoUp = cleanDBStringInt(neoUp)
                        c.execute("SELECT downvotes FROM userfeedback WHERE currency='neo'")
                        l = c.fetchall()
                        l2 = str(l)
                        neoDown = l2
                        neoDown = cleanDBStringInt(neoDown)
                        db.close()
                        return render_template('neo.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, neoUp = neoUp, neoDown= neoDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='NEO Price in USD', max = max(line_values), labels= line_labels, values=line_values)
                return render_template('neo.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5,  neoUp = neoUp, neoDown= neoDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='NEO Price in USD', max = max(line_values), labels= line_labels, values=line_values)
        return render_template('neo.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10,  username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, neoUp = neoUp, neoDown= neoDown, commentsRaw=commentsRaw, title='NEO Price in USD', max = max(line_values), labels= line_labels, values=line_values)

@app.route('/ontology', methods=['GET', 'POST'])
def ontology():
        labels = []
        values = []
        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
        c = db.cursor()
        for x in range (1, 31):
                c.execute('SELECT Date FROM ontology2 LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message2 = l2
                message2 = cleanDBString(message2)
                labels.append(message2)
        for x in range (1, 31):
                c.execute('SELECT Price FROM ontology LIMIT '+str(x)+', 1;')
                l = c.fetchall()
                l2 = str(l)
                message = l2
                message = cleanDBString(message)
                values.append(message)
        c.execute("SELECT COUNT(*) FROM comments WHERE currency='ontology'")
        l = c.fetchall()
        l2 = str(l)
        numberComments = l2
        c.execute("SELECT * FROM comments WHERE currency='ontology';")
        l = c.fetchall()
        #l2 = str(l)
        commentsRaw = l
        try:
                comment1 = cleanComment(str(commentsRaw[0]))
                username1 = comment1[1]
                comment1 = comment1[0]
        except IndexError:
                username1 = None
                comment1 = None
        try:
                comment2 = cleanComment(str(commentsRaw[1]))
                username2 = comment2[1]
                comment2 = comment2[0]
        except IndexError:
                username2 = None
                comment2 = None
        try:
                comment3 = cleanComment(str(commentsRaw[2]))
                username3 = comment3[1]
                comment3 = comment3[0]
        except IndexError:
                username3 = None
                comment3 = None
        try:
                comment4 = cleanComment(str(commentsRaw[3]))
                username4 = comment4[1]
                comment4 = comment4[0]
        except IndexError:
                username4 = None
                comment4 = None
        try:
                comment5 = cleanComment(str(commentsRaw[4]))
                username5 = comment5[1]
                comment5 = comment5[0]
        except IndexError:
                username5 = None
                comment5 = None
        try:
                comment6 = cleanComment(str(commentsRaw[5]))
                username6 = comment6[1]
                comment6 = comment6[0]
        except IndexError:
                username6 = None
                comment6 = None
        try:
                comment7 = cleanComment(str(commentsRaw[6]))
                username7 = comment7[1]
                comment7 = comment7[0]
        except IndexError:
                username7 = None
                comment7 = None
        try:
                comment8 = cleanComment(str(commentsRaw[7]))
                username8 = comment8[1]
                comment8 = comment8[0]
        except IndexError:
                username8 = None
                comment8 = None
        try:
                comment9 = cleanComment(str(commentsRaw[8]))
                username9 = comment9[1]
                comment9 = comment9[0]
        except IndexError:
                username9 = None
                comment9 = None
        try:
                comment10 = cleanComment(str(commentsRaw[9]))
                username10 = comment10[1]
                comment10 = comment10[0]
        except IndexError:
                username10 = None
                comment10 = None
        ## NEED TO PROCESS COMMENTSRAW USING SPACING
        ##TO GENERATE A LIST OF USERNAMES, COMMENTS, THEN PASS TO HTML PAGE
        c.execute("SELECT upvotes FROM userfeedback WHERE currency='ontology'")
        l = c.fetchall()
        l2 = str(l)
        ontologyUp = l2
        ontologyUp = cleanDBStringInt(ontologyUp)
        c.execute("SELECT downvotes FROM userfeedback WHERE currency='ontology'")
        l = c.fetchall()
        l2 = str(l)
        ontologyDown = l2
        ontologyDown = cleanDBStringInt(ontologyDown)
        db.close()
        labels.reverse()
        values.reverse()
        colors = ["#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1","#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]
        line_labels=labels
        line_values=values        
        if 'username' in session:
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                if request.method == 'POST':
                        comment_form  = request.form['comment']
                        db = pymysql.connect(host="104.155.161.212", user='root', password='arpeggiated', db='bitcoin')
                        c = db.cursor()
                        c.execute("USE bitcoin;")
                        comment_form = comment_form.replace("'", "")
                        addCommentString = "INSERT INTO comments values('%s', '%s', 'ontology');" % (unicode(comment_form), unicode(username_session))
                        addCommentString = addCommentString.replace("&#39;", "'")
                        addCommentString = h.unescape(addCommentString)
                        c.execute(addCommentString)
                        db.commit()
                        c.execute("SELECT * FROM comments WHERE currency='ontology';")
                        l = c.fetchall()
                        #l2 = str(l)
                        commentsRaw = l
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment1 = cleanComment(str(commentsRaw[0]))
                                username1 = comment1[1]
                                comment1 = comment1[0]
                        except IndexError:
                                username1 = None
                                comment1 = None
                        try:
                                comment2 = cleanComment(str(commentsRaw[1]))
                                username2 = comment2[1]
                                comment2 = comment2[0]
                        except IndexError:
                                username2 = None
                                comment2 = None
                        try:
                                comment3 = cleanComment(str(commentsRaw[2]))
                                username3 = comment3[1]
                                comment3 = comment3[0]
                        except IndexError:
                                username3 = None
                                comment3 = None
                        try:
                                comment4 = cleanComment(str(commentsRaw[3]))
                                username4 = comment4[1]
                                comment4 = comment4[0]
                        except IndexError:
                                username4 = None
                                comment4 = None
                        try:
                                comment5 = cleanComment(str(commentsRaw[4]))
                                username5 = comment5[1]
                                comment5 = comment5[0]
                        except IndexError:
                                username5 = None
                                comment5 = None
                        try:
                                comment6 = cleanComment(str(commentsRaw[5]))
                                username6 = comment6[1]
                                comment6 = comment6[0]
                        except IndexError:
                                username6 = None
                                comment6 = None
                        try:
                                comment7 = cleanComment(str(commentsRaw[6]))
                                username7 = comment7[1]
                                comment7 = comment7[0]
                        except IndexError:
                                username7 = None
                                comment7 = None
                        try:
                                comment8 = cleanComment(str(commentsRaw[7]))
                                username8 = comment8[1]
                                comment8 = comment8[0]
                        except IndexError:
                                username8 = None
                                comment8 = None
                        try:
                                comment9 = cleanComment(str(commentsRaw[8]))
                                username9 = comment9[1]
                                comment9 = comment9[0]
                        except IndexError:
                                username9 = None
                                comment9 = None
                        try:
                                comment10 = cleanComment(str(commentsRaw[9]))
                                username10 = comment10[1]
                                comment10 = comment10[0]
                        except IndexError:
                                username10 = None
                                comment10 = None
                        c.execute("SELECT upvotes FROM userfeedback WHERE currency='ontology'")
                        l = c.fetchall()
                        l2 = str(l)
                        ontologyUp = l2
                        ontologyUp = cleanDBStringInt(ontologyUp)
                        c.execute("SELECT downvotes FROM userfeedback WHERE currency='ontology'")
                        l = c.fetchall()
                        l2 = str(l)
                        ontologyDown = l2
                        ontologyDown = cleanDBStringInt(ontologyDown)
                        db.close()
                        return render_template('ontology.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, ontologyUp = ontologyUp, ontologyDown= ontologyDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Ontology Price in USD', max = max(line_values), labels= line_labels, values=line_values)
                return render_template('ontology.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10, adminActive = adminActive, username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5,  ontologyUp = ontologyUp, ontologyDown= ontologyDown, comment1 = comment1, comment2 = comment2,comment3 = comment3, comment4 = comment4,comment5 = comment5, commentsRaw = commentsRaw, session_user_name=username_session, title='Ontology Price in USD', max = max(line_values), labels= line_labels, values=line_values)
        return render_template('ontology.html', username6 = username6, username7 = username7, username8 = username8, username9 = username9, username10 = username10, comment6 = comment6, comment7 = comment7, comment8= comment8, comment9=comment9, comment10=comment10,  username1 = username1,username2 = username2,username3 = username3,username4 = username4,username5 = username5, ontologyUp = ontologyUp, ontologyDown= ontologyDown, commentsRaw=commentsRaw, title='Ontology Price in USD', max = max(line_values), labels= line_labels, values=line_values)


@app.route('/testing')
def testing():
        if 'username' in session:
                username_session = escape(session['username'])
                adminActive = None
                if username_session == 'Admin':
                        adminActive = 1
                return render_template('database.html', session_user_name=username_session)
        return render_template('database.html')


if __name__ == '__main__':
	app.run(host='127.0.0.1', port=8080, debug=True, threaded=True)
