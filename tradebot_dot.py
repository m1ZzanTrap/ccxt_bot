import sqlite3 as sq
import ccxt
import config
import time

bybit = ccxt.bybit({
            'apiKey': config.apikey,
            'secret': config.secret
        })
con = sq.connect("markets.db")
with con:
       con.execute("""CREATE TABLE IF NOT EXISTS dot(
                        price REAL);
       """)
con.commit()

def buy_or_sell(symbol, amount, currency, orders, tick):
    balance = bybit.fetch_balance({"type":"spot"})[currency]
    usdc = bybit.fetch_balance({"type":"spot"})["USDC"]
    if not orders:
        if usdc["free"] > tick*amount:
            return bybit.create_order(symbol, 'limit', 'buy', amount, tick - 0.0005)
            with con:
                sql = con.execute("INSERT INTO dot (price) VALUES(?)")
                data = [tick]
                con.execute(sql, data)
            con.commit()
        elif balance["free"] > amount:
            with con:
                market=con.execute("SELECT * FROM dot").fetchone()[0]
            return bybit.create_order(symbol, 'limit', 'sell', amount, market + 0.0075)
            con.execute("DELETE FROM markets")
            con.commit()
def cancel_order(symbol, orders, tick):
    for order in orders:
        if tick < order["price"] and order['side'] == 'sell':
            time.sleep(15)
            bybit.cancel_order(order["id"], symbol)
        if tick > order["price"] and order["side"] == "buy":
            time.sleep(15)
            bybit.cancel_order(order["id"], symbol)

def main():
     while True:
        symbol = "DOT/USDC"
        currency = "DOT"
        amount = 0.4
        orders=bybit.fetch_open_orders(symbol)
        tick=bybit.fetch_ticker(symbol)["last"]
        buy_or_sell(symbol, amount, currency, orders, tick)
        cancel_order(symbol, orders, tick)
        time.sleep(45)


if __name__=="__main__":
    main()
