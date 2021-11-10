from flask_wtf import FlaskForm
from wtforms import SelectField, FloatField, SubmitField
from wtforms.fields.core import DateField, StringField, TimeField
from wtforms.fields.simple import HiddenField
from wtforms.validators import DataRequired, NumberRange, EqualTo

options = [("EUR","Euro"),("ETH","Ethereum"),("LTC","Litecoin"),("BNB","Binance Coin"),("EOS","EOS"),("XLM","Stellar"),("TRX","TRON"),("BTC","Bitcoin"),
("XRP","XRP"),("BCH","Bitcoin Cash"),("USDT","Tether"),("BSV","Bitcoin SV"),("ADA","Cardano")]

class Validators(FlaskForm):
    date = StringField("Fecha de la transacción")
    time = StringField("Hora de la transacción")
    coin_from = SelectField("Moneda de Origen", choices=options)
    quantity_from = FloatField("Cantidad de origen", validators=[DataRequired(message="El monto no puede ser 0"),
                                                NumberRange(message="Debe informar superior a 0.000000000000001", min=0.000000000000001)])
    coin_to = SelectField("Moneda de Destino",  choices=options)
    quantity_to = HiddenField("Cantidad de Destino")
    convert = SubmitField("Calcular")
    buy = SubmitField("Comprar")
    calculate = SubmitField("Calcular")