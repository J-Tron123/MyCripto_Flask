import sqlite3
from flask import render_template, request
from flask.helpers import flash, url_for
from werkzeug.utils import redirect
from balance import app
from balance.forms import Validators
from balance.models import DBController, coins
from config import DATA_BASE, URL, URL_2, API_KEY
from datetime import datetime
import requests

dbroute = app.config.get(DATA_BASE)
dbcontroller = DBController(DATA_BASE)

@app.route("/")
def index():
    try:
        query = "SELECT id, date, time, coin_from, quantity_from, coin_to, quantity_to FROM criptobalance ORDER BY id"
        movements = dbcontroller.querySQL(query)
        return render_template("index.html", items=movements)
    except sqlite3.Error as e:
        print(e)
        flash("No se ha podido acceder a la abse de datos por favor consulte con su administrador")
        return render_template("index.html", items=[""])

@app.route("/purchase", methods=["GET", "POST"])
def purchase():
    form = Validators()
    if request.method == "GET":
        return render_template("purchase.html", the_form=form)
    else:
        if form.validate():
            if form.data["convert"] == True:
                try:
                    coin_from = form.data["coin_from"]
                    query = "SELECT SUM (quantity_from) FROM criptobalance WHERE (coin_from) == '{}';"
                    query2 = "SELECT SUM (quantity_to) FROM criptobalance WHERE (coin_to) == '{}';"
                    validate_from = dbcontroller.querySQL(query.format(coin_from))
                    if validate_from[0]["SUM (quantity_from)"] == None:
                        validate_from[0]["SUM (quantity_from)"] = 0
                    validate_to = dbcontroller.querySQL(query2.format(coin_from))
                    if validate_to[0]["SUM (quantity_to)"] == None:
                        validate_to[0]["SUM (quantity_to)"] = 0
                    quantity_from = form.data["quantity_from"]
                    coin_to = form.data["coin_to"]
                    if coin_from == coin_to:
                        return render_template("purchase.html", the_form=form, 
                        calculation="No puedes calcular la misma moneda de origen que de destino")
                    if coin_from != "EUR" and quantity_from > validate_to[0]["SUM (quantity_to)"] - validate_from[0]["SUM (quantity_from)"]:
                            return render_template("purchase.html", the_form=form, 
                            calculation=f"No puedes calcular porque no tienes suficientes {coin_from},\
                            debes tener más que en la cantidad de destino")
                    else:
                        try:
                            answer = requests.get(URL.format(quantity_from, coin_from, coin_to, API_KEY)).json()
                            quantity_to = answer["data"]["quote"][form.data["coin_to"]]["price"]
                            form["quantity_to"].data = quantity_to
                            form["date"].data = str(datetime.now().date())
                            form["time"].data = str(datetime.now().time())
                            form["quantity_from_buy"].data = quantity_from
                            form["coin_from_buy"].data = coin_from
                            form["coin_to_buy"].data = coin_to
                            return render_template("purchase.html", the_form=form, calculation=quantity_to, up=quantity_from/quantity_to)
                        except:
                            return render_template("purchase.html", the_form=form, calculation="Se ha producido un error en la api\
                            por favor consulte con su administrador")
                except sqlite3.Error as e:
                    print(e)
                    return render_template("purchase.html", the_form=form, calculation="Se ha producido un error en la base de datos,\
                    porfavor consulte con su administrador")
            if form.data["buy"] == True and form.data["quantity_to"] != "":
                if (float(form["quantity_from_buy"].data) == form.data["quantity_from"] and form["coin_from_buy"].data == 
                form.data["coin_from"] and form["coin_to_buy"].data == form.data["coin_to"]):
                    query = """INSERT INTO criptobalance (date, time, coin_from, quantity_from, coin_to, quantity_to) VALUES 
                            (:date, :time, :coin_from, :quantity_from, :coin_to, :quantity_to)"""
                    try:
                        dbcontroller.changeSQL(query, form.data)
                        return redirect(url_for("index"))
                    except sqlite3.Error as e:
                        print(e)
                        return render_template("purchase.html", the_form=form, calculation="Se ha producido un error en la base de datos\
                        por favor consulte con su administrador")
                else:
                    return render_template("purchase.html", the_form=form, calculation="Haz cambiado datos,\
                        por favor vuelve a calcular")
            else:
                return render_template("purchase.html", the_form=form, calculation="Primero debes calcular")
        else:
            return render_template("purchase.html", the_form=form)

@app.route("/status", methods=["GET", "POST"])
def status():
    form = Validators()
    if request.method == "GET":
        return render_template("status.html", the_form=form)
    else:
        try:
            query = "SELECT SUM (quantity_from) FROM criptobalance WHERE (coin_from) == '{}';"
            query2 = "SELECT SUM (quantity_to) FROM criptobalance WHERE (coin_to) == '{}';"
            froms = []
            tos = []
            total_from = []
            total_to = []
            for coin in coins:
                dbcontroller.querySQL(query.format(coin))
                froms.extend(dbcontroller.querySQL(query.format(coin)))
                dbcontroller.querySQL(query2.format(coin))
                tos.extend(dbcontroller.querySQL(query2.format(coin)))
            for i in froms:
                if i["SUM (quantity_from)"] == None:
                    i["SUM (quantity_from)"] = 0
                total_from.append(i["SUM (quantity_from)"])
            for i in tos:
                if i["SUM (quantity_to)"] == None:
                    i["SUM (quantity_to)"] = 0
                total_to.append(i["SUM (quantity_to)"])
            totals = [m2 - m1 for m1, m2 in zip(total_from, total_to)]
            total_quantities = dict(zip(coins, totals))
            print(total_quantities)
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
                return render_template("status.html", the_form=form, worth="Se ha producido un error en la api\
                por favor consulte con su administrador")
            symbols = []
            prices = []
            for i in total_response:
                symbols.append(i["symbol"])
                prices.append(i["quote"]["EUR"]["price"])
            price_coin = dict(zip(symbols, prices))
            stock = []
            for key in total_quantities:
                if key in price_coin:
                    stock.append(total_quantities.get(key) * price_coin.get(key))
            worth = sum(stock)
            print(stock)
            print(worth)
            x = dbcontroller.querySQL("SELECT SUM (quantity_from) FROM criptobalance WHERE (coin_from) == 'EUR';")
            statusx = x[0]["SUM (quantity_from)"]
            y = dbcontroller.querySQL("SELECT SUM (quantity_to) FROM criptobalance WHERE (coin_to) == 'EUR';")
            statusy = y[0]["SUM (quantity_to)"]
            if statusx == None:
                statusx = 0
                statusy = 0
            z = statusx - statusy
            print(z)
            return render_template("status.html", the_form=form, total_fiat=statusx, worth=worth-z)
        except sqlite3.Error as e:
            print(e)
            return render_template("status.html", the_form=form, total_fiat="Se ha producido un error en la base de datos\
            por favor consulte con su administrador")