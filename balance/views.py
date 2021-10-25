from flask import render_template, request
from flask.helpers import url_for
from werkzeug.utils import redirect
from balance import app
from balance.forms import Validators
from balance.models import DBController, coins
from config import DATA_BASE, URL, URL_2, API_KEY
from datetime import datetime
import requests, sqlite3

dbroute = app.config.get(DATA_BASE)
dbcontroller = DBController(DATA_BASE)

@app.route("/")
def index():
    query = "SELECT id, date, time, coin_from, quantity_from, coin_to, quantity_to FROM criptobalance ORDER BY id"
    movements = dbcontroller.querySQL(query)
    return render_template("index.html", items=movements)

@app.route("/purchase", methods=["GET", "POST"])
def purchase():
    form = Validators()
    if request.method == "GET":
        return render_template("purchase.html", the_form=form)
    else:
        if form.validate():
            if form.data["convert"] == True:
                coin_from = form.data["coin_from"]
                coin_to = form.data["coin_to"]
                quantity_from = form.data["quantity_from"]
                answer = requests.get(URL.format(quantity_from, coin_from, coin_to, API_KEY)).json()
                quantity_to = answer["data"]["quote"][form.data["coin_to"]]["price"]
                form["quantity_to"].data = quantity_to
                form["date"].data = str(datetime.now().date())
                form["time"].data = str(datetime.now().time())
                return render_template("purchase.html", the_form=form, calculation=quantity_to, up=quantity_from/quantity_to)

            if form.data["buy"] == True:
                query = """INSERT INTO criptobalance (date, time, coin_from, quantity_from, coin_to, quantity_to) VALUES 
                        (:date, :time, :coin_from, :quantity_from, :coin_to, :quantity_to)"""
                try:
                    dbcontroller.changeSQL(query, form.data)
                except Exception as e:
                    print("Se ha producido un error:", Exception, e)
                    return render_template("purchase.html", the_form=form, calculation="No se ha podido acceder a la base de datos")           
                return redirect(url_for("index"))

            if form.data["buy"] == True and form["quantity_to"].data == "":
                return render_template("purchase.html", the_form=form, calculation="Primero debes calcular")
        else:
            return render_template("purchase.html", the_form=form)

@app.route("/status", methods=["GET", "POST"])
def status():
    form = Validators()
    if request.method == "GET":
        return render_template("status.html", the_form=form)
    else:
        query = "SELECT SUM (quantity_from) FROM criptobalance WHERE (coin_from) == '{}';"
        froms = []
        total_from = []
        try:
            for coin in coins:
                dbcontroller.querySQL(query.format(coin))
                froms.extend(dbcontroller.querySQL(query.format(coin)))
            for i in froms:
                total_from.append(i["SUM (quantity_from)"])
            total_quantities = dict(zip(coins, total_from))
            try:
                params = {
                "start":"1",
                "limit":"100",
                "convert":"EUR"
                }
                headers = {
                    "Accepts": "application/json",
                    "X-CMC_PRO_API_KEY": API_KEY,
                }
                my_response = requests.get(URL_2, headers=headers, params=params)
                dictionary = my_response.json()
                total_response = dictionary["data"]
            except:
                return render_template("status.html", the_form=form, worth="Se ha producido un error por favor consulte con su administrador")
            symbols = []
            prices = []
            for i in total_response:
                symbols.append(i["symbol"])
                prices.append(i["quote"]["EUR"]["price"])
            price_coin = dict(zip(symbols, prices))
            stock = []
            for key in total_quantities:
                if key in price_coin and total_quantities.get(key) != None:
                    stock.append(total_quantities.get(key) * price_coin.get(key))
            worth = sum(stock)
            x = dbcontroller.querySQL("SELECT SUM (quantity_to) FROM criptobalance WHERE (coin_to) == 'EUR';")
            status = x[0]["SUM (quantity_to)"]
            return render_template("status.html", the_form=form, total_fiat=total_quantities["EUR"], worth=worth+status)
        except Exception as e:
            print("Se ha producido un error:", Exception, e)
            return render_template("status.html", the_form=form, total_fiat="No se ha podido accedeer a la base de datos", 
            worth="No se ha podido accedeer a la base de datos")