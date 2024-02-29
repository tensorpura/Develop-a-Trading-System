import sys
import random
from datetime import datetime
import quickfix as fix
import time

class Application(fix.Application):
    orderID = 0
    execID = 0
    orders = {}
    trades = []
    sessionID = None
    MY_CUSTOM_SHORT_INDICATOR_FIELD = 5001

    def handleExecutionReport(self, message):
        execType = fix.ExecType()
        message.getField(execType)

        if execType.getValue() == fix.ExecType_FILL or execType.getValue() == fix.ExecType_PARTIAL_FILL:
            clOrdID = fix.ClOrdID()
            message.getField(clOrdID)
            symbol = fix.Symbol()
            message.getField(symbol)
            side = fix.Side()
            message.getField(side)
            lastShares = fix.LastShares()
            message.getField(lastShares)
            lastPx = fix.LastPx()
            message.getField(lastPx)

            tradeInfo = {
                "symbol": symbol.getValue(),
                "side": side.getValue(),
                "quantity": lastShares.getValue(),
                "price": lastPx.getValue()
            }
            self.trades.append(tradeInfo)

            orderID = clOrdID.getValue()
            if orderID in self.orders:
                self.orders[orderID]["status"] = "FILLED"
                self.orders[orderID]["filled_quantity"] = lastShares.getValue()
                self.orders[orderID]["filled_price"] = lastPx.getValue()
            else:
                self.orders[orderID] = {
                    "symbol": symbol.getValue(),
                    "side": side.getValue(),
                    "quantity": lastShares.getValue(),
                    "price": lastPx.getValue(),
                    "status": "FILLED"
                }

        self.calculateStats()

    def calculateStats(self):
        totalVolume = 0
        totalValue = 0
        pnl = 0
        instruments = {}

        for trade in self.trades:
            symbol = trade["symbol"]
            quantity = trade["quantity"]
            price = trade["price"]
            tradeType = trade["side"]

            totalVolume += quantity
            totalValue += quantity * price

            if symbol not in instruments:
                instruments[symbol] = {"volume": 0, "value": 0, "cost": 0, "pnl": 0}

            instruments[symbol]["volume"] += quantity
            instruments[symbol]["value"] += quantity * price

            if tradeType == "BUY":
                instruments[symbol]["cost"] += quantity * price
            elif tradeType == "SELL":
                pnlFromTrade = quantity * price - instruments[symbol]["cost"]
                instruments[symbol]["pnl"] += pnlFromTrade
                pnl += pnlFromTrade

        vwaps = {symbol: data["value"] / data["volume"] for symbol, data in instruments.items() if data["volume"] > 0}

        print("\n=== Trading Statistics ===")
        print(f"Total Trading Volume (USD): {totalVolume}")
        print(f"Total PNL Generated from Trading: {pnl}")
        print("VWAP of the Fills for Each Instrument:")
        for symbol, vwap in vwaps.items():
            print(f" - {symbol}: VWAP = {vwap}, PNL = {instruments[symbol]['pnl']}")

    def gen_ord_id(self):
        self.orderID += 1
        return self.orderID

    def onCreate(self, sessionID):
        return

    def onLogon(self, sessionID):
        self.sessionID = sessionID
        print("Successful Logon to session '%s'." % sessionID.toString())
        return

    def onLogout(self, sessionID):
        return

    def toAdmin(self, sessionID, message):
        return

    def fromAdmin(self, sessionID, message):
        return

    def toApp(self, sessionID, message):
        print("Received the following message: %s" % message.toString())
        return

    def fromApp(self, message, sessionID):
        msgType = fix.MsgType()
        message.getHeader().getField(msgType)

        if msgType.getValue() == "8":
            self.printExecutionReport(message)
        elif msgType.getValue() == "3":
            self.handleReject(message)
        elif msgType.getValue() == "9":
            self.handleCancelReject(message)
        else:
            print("Received unknown message type: %s" % msgType.getValue())

    def printExecutionReport(self, message):
        print("Received Execution Report: %s" % message.toString())

    def handleReject(self, message):
        print("Received Reject: %s" % message.toString())

    def handleCancelReject(self, message):
        print("Received Order Cancel Reject: %s" % message.toString())

    def genExecID(self):
        self.execID += 1
        return str(random.randint(1, 100000))

    @staticmethod
    def MyCustomShortIndicator(data=None):
        return fix.StringField(Application.MY_CUSTOM_SHORT_INDICATOR_FIELD, data)

    def put_order(self):
        symbol = random.choice(['MSFT', 'AAPL', 'BAC'])
        side = random.choice(['BUY', 'SELL', 'SHORT'])
        order_type = fix.OrdType_LIMIT if random.choice([True, False]) else fix.OrdType_MARKET
        quantity = random.randint(1, 100)
        price = random.uniform(10.0, 100.0) if order_type == fix.OrdType_LIMIT else None

        print("Creating the following order: ")
        trade = fix.Message()
        trade.getHeader().setField(fix.BeginString(fix.BeginString_FIX42))
        trade.getHeader().setField(fix.MsgType(fix.MsgType_NewOrderSingle))
        clOrdID = self.genExecID()
        trade.setField(fix.ClOrdID(clOrdID))
        trade.setField(fix.HandlInst(fix.HandlInst_MANUAL_ORDER_BEST_EXECUTION))
        trade.setField(fix.Symbol(symbol))

        if side == 'BUY':
            trade.setField(fix.Side(fix.Side_BUY))
        elif side == 'SELL':
            trade.setField(fix.Side(fix.Side_SELL))
        elif side == 'SHORT':
            trade.setField(fix.Side(fix.Side_SELL))
            trade.setField(Application.MyCustomShortIndicator('YES'))

        trade.setField(fix.OrdType(order_type))
        trade.setField(fix.OrderQty(quantity))
        if order_type == fix.OrdType_LIMIT:
            trade.setField(fix.Price(price))
        trade.setField(fix.TransactTime(int(datetime.utcnow().strftime("%s"))))
        print(trade.toString())
        fix.Session.sendToTarget(trade, self.sessionID)

        self.orders[clOrdID] = trade  # Keep track of the order


    def cancel_order(self, order_id):
        cancel = fix.Message()
        cancel.getHeader().setField(fix.BeginString(fix.BeginString_FIX42))
        cancel.getHeader().setField(fix.MsgType(fix.MsgType_OrderCancelRequest))

        cancel.setField(fix.ClOrdID(self.genExecID()))
        cancel.setField(fix.OrigClOrdID(order_id))

        cancel.setField(fix.Symbol('MSFT'))
        cancel.setField(fix.Side(random.choice([fix.Side_BUY, fix.Side_SELL])))
        cancel.setField(fix.TransactTime(int(datetime.utcnow().strftime("%s"))))

        print(cancel.toString())
        fix.Session.sendToTarget(cancel, self.sessionID)

    def send_random_orders(self, num_orders=1000, time_limit=300):
        start_time = time.time()
        while time.time() - start_time < time_limit and len(self.orders) < num_orders:
            self.put_order()
            time.sleep(random.uniform(0.1, 0.5))

    def cancel_random_orders(self, time_limit=300):
        start_time = time.time()
        while time.time() - start_time < time_limit:
            if self.orders:
                order_id_to_cancel = random.choice(list(self.orders.keys()))
                self.cancel_order(order_id_to_cancel)
                time.sleep(random.uniform(0.1, 0.5))

def main(config_file):
    try:
        settings = fix.SessionSettings(config_file)
        application = Application()
        storeFactory = fix.FileStoreFactory(settings)
        logFactory = fix.FileLogFactory(settings)
        initiator = fix.SocketInitiator(application, storeFactory, settings, logFactory)
        initiator.start()
        
        # Start sending orders
        application.send_random_orders(time_limit=300)  # 5 minutes to send orders

        # Start cancelling orders
        application.cancel_random_orders(time_limit=300)  # 5 minutes to cancel orders

        while True:
            user_input = input()
            if user_input == '1':
                print("Putting Order")
                application.put_order()
            elif user_input == '2':
                sys.exit(0)
            else:
                print("Valid input is 1 for order, 2 for exit")
                continue
    except (fix.ConfigError, fix.RuntimeError) as e:
        print(e)

if __name__ == '__main__':
    config_file = 'client.cfg'
    main(config_file)

