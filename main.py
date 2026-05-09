#!.\venv\Scripts\python.exe
import sqlite3

from flask import Flask, render_template, jsonify, request
import json
#import time
import threading
from core import *
import os
import sys
import logging
import config

app = Flask(__name__, static_folder="assets")
global prodConnection
global testConnection
connection = ""

@app.route("/")
def gestionale():
    return render_template('./gestionale/gestionale-popolare.html')


#send the menu list
@app.route("/api/menu")
def menu():
    #f = open("./data/lista_menu.json", "r")
    #data = f.read()
    #f.close()
    menu = buildMenu(connection)
#   build from database
    return jsonify(menu)

#send the menu list (not used)
@app.route("/api/menu-bar")
def menu_bar():
    #f = open("./data/lista_menu.json", "r")
    #data = f.read()
    #f.close()
    menu = buildMenu(connection)
#   build from database
    return jsonify(menu)

#send open orders to display
@app.route("/api/ordersList")
def orderList():
    data = retrieveOrderList(connection)
    return jsonify(data)


#send open orders to display
@app.route("/api/completedOrdersList")
def completedOrderList():
    data = retrieveRecentCompletedOrderList(connection)
    return jsonify(data)


#send open orders to display
@app.route("/api/requestOrderNumber")
def getOrderNumber():
    data = {'orderId': "", 'status': ""}
    try:
        data['orderId'] = retrieveOrderNumber(connection)
        data['status'] = "success"
        app.logger.info("Retrieved order number: %s", data['orderId'])
    except sqlite3.OperationalError as e:
        app.logger.error("Could not get order number")
        data['status'] = "error"
    return jsonify(data)


#retrieve items of an order
@app.route("/api/getItemsByOrderId")
def getOrderItems():
    orderId = request.args.get('orderId')
    orderType = request.args.get('orderType')
    data = {'items': [], 'status': ""}
    try:
        data['items'] = retrieveOrderItems(connection, orderId, orderType)
        data['status'] = "success"
        app.logger.info("Items for order %s retrieved", orderId)
    except sqlite3.OperationalError as e:
        data['status'] = "error"
        app.logger.error("Could not retrieve items for order %s", orderId)
    return jsonify(data)


#register order to database (fill the order data)
@app.route("/api/orders", methods=['POST'])
def orders():
    responseData = {'status': ""}
    if request.method == 'POST':
        order = request.get_json()
        order["operatorId"] = request.remote_addr.replace(".", "")
        dbStatus = registerOrderToDatabase(connection, order)
        if (dbStatus == 0):
            #start print thread
            t = threading.Thread(target=printCommand, args=(connection, order), daemon=True)
            t.start()
            responseData["status"] = "success"
        else:
            responseData["status"] = "error"
        print(order)
    return jsonify(responseData)

#update inventory data for an item
@app.route("/api/updateInventory", methods=['POST'])
def updateInventoryWeb():
    responseData = {'status': ""}
    if request.method == 'POST':
        update = request.get_json()
        print(update)
        dbStatus = updateInventoryItem(prodConnection, update)
        if (dbStatus == 0):
            responseData["status"] = "success"
        else:
            responseData["status"] = "error"
    return jsonify(responseData)


#update an order status and/or table id
@app.route("/api/orderDataUpdate", methods=['POST'])
def orderDataUpdate():
    responseData = {'status': ""}
    if request.method == 'POST':
        r = request.get_json()
        print(r)
        status = updateData(connection, r)
        if status == 0:
            responseData["status"] = "success"
        else:
            responseData["status"] = "error"
    return jsonify(responseData)


@app.route("/api/orderRequestReprint", methods=['POST'])
def orderRequestReprint():
    responseData = {'status': ""}
    if request.method == 'POST':
        r = request.get_json()
        orderId = request.args.get('orderId')
        orderType = request.args.get('orderType')
        print(r)
        status = requestReprint(connection, orderId, orderType)
        if status == 0:
            responseData["status"] = "success"
        else:
            responseData["status"] = "error"
    return jsonify(responseData)


@app.route("/ordini")
def getOrders():
    return render_template('./gestionale/gestionale-popolare-gestione-ordini.html')

@app.route("/inventario")
def getInventarioInterface():
    return render_template('./gestionale/gestionale-popolare-inventario.html')

@app.route("/summary")
def getSummary():
    return render_template('./gestionale/gestionale-popolare-summary.html')


#send summary data to display
@app.route("/api/summaryData")
def summaryData():
    data = []
    try:
        data = retrieveSummaryData(connection)
    except sqlite3.OperationalError as e:
        pass
    return jsonify(data)

@app.route("/api/getAppMode")
def appMode():
    data = {"mode": getAppMode()}
    return jsonify(data)

@app.route("/api/changeMode")
def chnageMode():
    data = {}
    mode = request.args.get('mode')
    setAppMode(mode)
    return jsonify(data)

#archive order and items
@app.route("/api/close_archive", methods=['POST'])
def archive():
    responseData = {'status': ""}
    if request.method == 'POST':
        dbStatus = archiveDatabaseData(connection)
        if (dbStatus == 0):
            setAppMode("test") #mette in modalità test l'applicazione
            responseData["status"] = "success"
        elif (dbStatus == 1):
            responseData["status"] = "orderOpen"
        elif (dbStatus == 2):
            responseData["status"] = "noOrder"
    return jsonify(responseData)


#print daily report
@app.route("/api/print_report", methods=['POST'])
def print_report():
    responseData = {'status': ""}
    if request.method == 'POST':
        selectedDate = request.get_json()
        printername = config.nomeStampanteCucina
        printStatus = printReport(prodConnection, selectedDate, printername)
        if printStatus == 0:
            responseData["status"] = "success"
        else:
            responseData["status"] = "error"
    return jsonify(responseData)

#utility function, not used
def jsonMenu():
    f = open("./data/lista_menu.json", "r+")
    data = json.loads(f.read())
    i = 1
    for category in data:
        for item in data[category]:
            item["productId"] = i
            print(item)
            i += 1
    f.write(data)
    f.close()

#utility function, not used
def fillMenu():
    f = open("./data/lista_menu.json", "r")
    data = json.loads(f.read())
    for category in data:
        for item in data[category]:
            item["category"] = category
            sql = ''' INSERT INTO itemProp(name, itemId, itemClass, unitPrice, description)
                              VALUES(:name, :productId, :category, :price, :desc) '''
            cur = connection.cursor()
            cur.execute(sql, item)
            connection.commit()
    f.close()

def setAppMode(value):
    data = {'mode': value}
    global connection
    json_str = json.dumps(data)
    with open("config.json", "w") as f:
        f.write(json_str)
    if (value == "test"):
        connection = testConnection
        app.logger.removeHandler(prodFileHandler)
        app.logger.addHandler(testFileHandler)
        app.logger.info("App changed to TEST mode")
    elif (value == "prod"):
        connection = prodConnection
        app.logger.removeHandler(testFileHandler)
        app.logger.addHandler(prodFileHandler)
        app.logger.info("App changed to PRODUCTION mode")

def getAppMode():
    with open("config.json", "r") as f:
        data = json.load(f)
    return data["mode"]

if __name__ == '__main__':
    directory = os.path.dirname(os.path.abspath(__file__))
    print(os.getcwd())
    #open connection to test or production database
    prodConnection = sqlite3.connect("./data/myDatabase.db", timeout=7, check_same_thread=False, isolation_level=None)
    testConnection = sqlite3.connect("./data/testDatabase.db", timeout=7, check_same_thread=False, isolation_level=None)
    if (getAppMode() == "test"):
        connection = testConnection
    elif (getAppMode() == "prod"):
        connection = prodConnection
    #set threadsafety to serialized mode to share same db connections across threads and void corruption
    sqlite3.threadsafety = 3
    assert sqlite3.threadsafety == 3, "wrong thread safety (when sharing same connection across threads)"
    #Logger configs
    app.logger.setLevel(logging.DEBUG)
    prod_log_file_path = './data/logs/server.log'
    test_log_file_path = "./data/logs/test.log"
    stdout = logging.StreamHandler(stream=sys.stdout)
    prodFileHandler = logging.FileHandler(prod_log_file_path)
    testFileHandler = logging.FileHandler(test_log_file_path)
    stdout.setLevel(logging.INFO)
    prodFileHandler.setLevel(logging.DEBUG)
    testFileHandler.setLevel(logging.DEBUG)
    fmt = logging.Formatter(
        "%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s >>> %(message)s"
    )
    prodFileHandler.setFormatter(fmt)
    testFileHandler.setFormatter(fmt)
    stdout.setFormatter(fmt)
    app.logger.addHandler(stdout)
    if getAppMode() == "prod":
        app.logger.addHandler(prodFileHandler)
    elif getAppMode() == "test":
        app.logger.addHandler(testFileHandler)
    app.logger.info("Server started in %s mode", "PRODUCTION" if (getAppMode() == "prod") else ">>TEST<<")

    #prod server
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000, threads=16)
    #app.run(threaded=True, debug=True, host="0.0.0.0")
