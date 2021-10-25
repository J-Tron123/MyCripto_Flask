import sqlite3 as sq

class DBController():
    def __init__(self, database_route):
        self.database_route = database_route

    def querySQL(self, query, parameters=[]):
        con = sq.connect(self.database_route)
        cur = con.cursor()
        cur.execute(query, parameters)

        keys = []
        for item in cur.description:
            keys.append(item[0])

        transactions = []
        for transaction in cur.fetchall():
            ix_clave = 0
            d = {}
            for column in keys:
                d[column] = transaction[ix_clave]
                ix_clave += 1
            transactions.append(d)

        con.close()
        return transactions
    
    def changeSQL(self, query, parameters):
        con = sq.connect(self.database_route)
        cur = con.cursor()
        cur.execute(query, parameters)
        con.commit()
        con.close()

coins = ["EUR","ETH","LTC","BNB","EOS","XLM","TRX","BTC","XRP","BCH","USDT","BSV","ADA"]


