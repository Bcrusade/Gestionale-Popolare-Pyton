from database import *
from threading import Lock
from datetime import datetime
#printer imports
import uuid
import win32api
import win32print
import win32com.shell.shell as shell
import win32event
#----------------
import os
import time
import os.path
import config


mutex = Lock()

def registerOrderToDatabase(conn, order):
    order["status"] = 0 #status: "non stampato"
    orderId = order["orderId"]
    #datetime
    order["datetime"] = datetime.now()
    #operatorId(todo)
    order["operatorId"] = 0
    order["tableId"] = 0
    orderData = (order["orderId"], order["totalValue"], order["operatorId"], order["paymentType"], order["datetime"], order["customerType"], order["tableId"])
    insertOrder(conn, orderData)  # insert order in orders table
    #check if order has pizzeria and/or restaurant (filter out beverages), then put orderStatuses in the db
    hasCucina = False
    hasPizza = False
    for item in order["items"]:
        itemClass = resolveItemClassById(conn, item["itemId"])
        if (itemClass == "cucina"):
            hasCucina = True
        elif (itemClass == "pizzeria"):
            hasPizza = True
    if (hasCucina):
        insertStatus(conn, orderId, "cucina", 0)
    if (hasPizza):
        insertStatus(conn, orderId, "pizzeria", 0)

    for item in order["items"]:
        item["orderId"] = orderId
        insertItem(conn, item)  # insert each item in items table
    return 0

def printCommand(conn, order):
    #divide by item class
    #filter out beverages
    #send print instructions to printers with correct data
    cucinaItemList = []
    pizzeriaItemList = []
    for item in order['items']:
        itemClass = resolveItemClassById(conn, item["itemId"])
        if (itemClass == "cucina"):
            itemCategory = resolveItemCategoryById(conn, item["itemId"])
            if(itemCategory == "menu birra" or itemCategory == "menu bibita"):
                # divide menu in panino + fries
                cucinaItemList.append({"name": resolveItemNameById(conn, item['itemId']).split("- ")[1], "itemId": item['itemId'], "quantity": item['quantity'], "notes": item['notes']})
                cucinaItemList.append({"name": "Patatine fritte", "itemId": item['itemId'], "quantity": item['quantity'], "notes": ""})
            else:
                cucinaItemList.append(item)
        elif (itemClass == "pizzeria"):
            pizzeriaItemList.append(item)
    orderId = order['orderId']
    if len(cucinaItemList) > 0:
        orderType = "cucina"
        printCommandType(conn, orderId, cucinaItemList, config.nomeStampanteCucina, orderType)
    if len(pizzeriaItemList) > 0:
        orderType = "pizzeria"
        printCommandType(conn, orderId, pizzeriaItemList, config.nomeStampantePizzeria, orderType)

def printCommandType(conn, orderId, printItemList, printername, orderType):
    print(printItemList)
    #read the html template
    with open("./serverPrinter/template/invoice.html", "r") as file:
        html_template = file.read()
    html_body = "<h1>Ordine " + str(orderType.capitalize()) + " Nr." + str(orderId) + """
    </h1>
    <table>
      <thead>
        <tr>
          <th>Nome</th>
          <th>Quantità</th>
          <th>Note</th>
        </tr>
      </thead>
      <tbody>
    """
    for item in printItemList:
        itemCategory = resolveItemCategoryById(conn, item["itemId"])
        #do not resolve name if item is part of menu because name is already set
        name = ""
        if (itemCategory != "menu birra" and itemCategory != "menu bibita"):
            name = resolveItemNameById(conn, item['itemId'])
        else:
            name = item['name']
        html_body += "<tr> <td>" + name + "</td><td>" + str(item['quantity']) + "</td><td>" + item['notes'] + "</td></tr>"
    html_body += """
    </tbody>
    </table>
    """
    #fill the template
    html_template = html_template.format(body=html_body)
    randomName = str(uuid.uuid4())
    filename = r".\serverPrinter\tmp\a" + randomName
    infilename = filename + "input.html"
    #save to tmp file the formatted html template
    with open(infilename, "wb") as file:
        file.write(str.encode(html_template))
    outfilename = filename + "output.pdf"
    commandText = """.\serverPrinter\weasyprint.exe -e utf-8 {} {}""".format(infilename, outfilename)
    #convert html to pdf with weasyprint
    os.popen(commandText)
    printfilename = ".\\serverPrinter\\tmp\\a" + randomName + "output.pdf"
    time.sleep(3)
    #wait for the pdf outfile before trying to print (maximum 10 seconds)
    counter = 0
    while True:
        if (os.path.isfile(outfilename)):
            break
        if (counter > 10):
            break
        counter += 1
        time.sleep(1)
    #print the command to the right printer
    try:
        #set paper format to A5
        PRINTER_DEFAULTS = {"DesiredAccess":win32print.PRINTER_ALL_ACCESS}
        handle = win32print.OpenPrinter(printername, PRINTER_DEFAULTS)
        properties = win32print.GetPrinter(handle, 2)
        devmode = properties['pDevMode']
        DMPAPER_A5 = 11
        devmode.PaperSize = DMPAPER_A5
        win32print.SetPrinter(handle, 2, properties, 0)
        #---------------- check if the format is correct------
        properties = win32print.GetPrinter(handle, 2)
        devmode = properties['pDevMode']
        win32print.ClosePrinter(handle)
        #-----------------start printing----------------------
        structureOut = shell.ShellExecuteEx(fMask = 256 + 64, lpVerb='printto', lpFile=r"{}".format(printfilename), lpParameters=f'"{printername}"', lpDirectory=".")
        hh = structureOut['hProcess']
        ret = win32event.WaitForSingleObject(hh, -1)
        if (ret == 0): #print command success (the printer has to handle the actual print yet, the server just sent the command)
            #update order status
            data = {'orderStatus': 1, 'orderId': orderId, 'orderType': orderType}
            updateOrderStatus(conn, data)
            print("STAMPA COMANDA OK")
            #remove tmp files
            os.remove(infilename)
            os.remove(outfilename)
    except win32api.error as e:
        #logging here
        print(e.args[0])
        print(e.args[2])
    return


def retrieveOrderNumber(conn):
    mutex.acquire(timeout=10) #probably useless mutex (there is a write to db)
    orderId = getOrderId(conn)
    mutex.release()
    return orderId

def retrieveOrderList(conn):
    data = getOrderList(conn)
    orderList = []
    for order in data:
        orderId = order[0]
        statuses = getOrderStatusById(conn, orderId)
        for status in statuses:
            orderList.append({"orderId": order[0],  "tableId": order[1], "datetime": order[2], "orderType": status[1], "orderStatus": status[2]})
    return orderList

def retrieveRecentCompletedOrderList(conn):
    data = getRecentCompletedOrders(conn)
    orderList = []
    for order in data:
        orderId = order[0]
        info = getOrderInfoById(conn, orderId)
        orderList.append({"orderId": order[0],  "tableId": info[3], "datetime": info[2], "orderType": order[1], "orderStatus": order[2]})
    print(orderList)
    return orderList

def retrieveOrderItems(conn, orderId, orderType):
    data = getOrderItemsById(conn, orderId)
    itemList = []
    for item in data:
        name = resolveItemNameById(conn, item[0])
        if (resolveItemClassById(conn, item[0]) == orderType):
            itemList.append({"name": name, "quantity": item[1], "notes": item[2]})
    return itemList

def updateData(conn, data):
    print(data)
    updateOrderStatus(conn, data)
    updateOrderTable(conn, data)
    return 0

def retrieveSummaryData(conn):
    totalOrderNumber = getTotalOrderNumber(conn)
    totalCash = getTotalCash(conn)
    totalPos = getTotalPos(conn)
    totalOrderNumberVol = getTotalOrderNumberVol(conn)
    orderSummary = []
    orderSummary.append({"NumOrder": totalOrderNumber, "Cash": totalCash, "POS": totalPos, "NumOrderVolontari": totalOrderNumberVol})
    return orderSummary

def archiveDatabaseData(conn):
    orderOpen = checkOrderOpen(conn)
    orderToArchive = getTotalOrderNumber(conn)
    if (orderToArchive == 0):
        return 2
    if (orderOpen > 0):
        return 1
    elif (orderOpen == 0):
        #backup database file
        source = r".\data\myDatabase.db"
        dest = r".\data\backup\dataBackup_" + datetime.now().strftime("%d.%m.%y-%H-%M-%S") + ".db"
        with open(source, 'rb') as src, open(dest, 'wb') as dst:
            try:
                dst.write(src.read())
            except OSError as e:
                logging.error("Errore scrittura backup database: %s", str(e))
                return 135
        dayId = getDayId(conn)
        # -----------archive orders---------------
        hotOrders = getHotOrders(conn)
        ordersToArchive = len(hotOrders)
        counter = 0
        for order in hotOrders:
            archiveOrder = {'displayId': order[0], 'totalValue': order[1], 'paymentType': order[3], 'datetime': order[4], 'customerType': order[6], 'dayId': dayId}
            status = insertArchiveOrder(conn, archiveOrder)
            if status == 0:
                counter += 1
        if ordersToArchive == counter:
            deleteHotOrders(conn)
            deleteHotOrdersStatuses(conn)
        else:
            return 12 #error
        #-------------archive items--------------
        hotItems = getHotItems(conn)
        itemsToArchive = len(hotItems)
        counter = 0
        for item in hotItems:
            archiveItem = {'dayId': dayId, 'displayId': item[0], 'itemId': item[1], 'quantity': item[2], 'notes': item[3]}
            status = insertArchiveItem(conn, archiveItem)
            if status == 0:
                counter += 1
        if itemsToArchive == counter:
            deleteHotItems(conn)
            resetSqlSequence(conn)
        else:
            return 13 #error
        return 0

def requestReprint(conn, orderId, orderType):
    printername = ""
    if (orderType == "cucina"):
        printername = config.nomeStampanteCucina
    elif (orderType == "pizzeria"):
        printername = config.nomeStampantePizzeria
    printItemList = []
    items = getOrderItemsById(conn, orderId)
    for item in items:
        itemClass = resolveItemClassById(conn, item[0]) #item[0] = itemId
        if (itemClass == orderType): #cucina or pizzeria
            itemCategory = resolveItemCategoryById(conn, item[0])
            if (itemCategory == "menu birra" or itemCategory == "menu bibita"): #if item is a menu, the name is the one of panino; add fries
                printItemList.append(
                    {"name": resolveItemNameById(conn, item[0]).split("- ")[1], "itemId": item[0],
                     "quantity": item[1], "notes": item[2]})
                printItemList.append(
                    {"name": "Patatine fritte", "itemId": item[0], "quantity": item[1], "notes": ""})
            else: #item is not a menu
                printItemList.append({"name": resolveItemNameById(conn, item[0]), "itemId": item[0],
                     "quantity": item[1], "notes": item[2]})
    printCommandType(conn, orderId, printItemList, printername, orderType)
    return 0

def printReport(conn, selectedDate, printername):
    selectedDateWildCard = selectedDate + "%"
    paymentType = "cash"
    customerType = "Client"
    contanti = getTotalOrdini(conn, paymentType, customerType, selectedDateWildCard)
    paymentType = "pos"
    pos = getTotalOrdini(conn, paymentType, customerType, selectedDateWildCard)
    paymentType = "free"
    customerType = "Volounteer"
    costoVolounteer = getTotalOrdini(conn, paymentType, customerType, selectedDateWildCard)
    customerType = "Guest"
    costoGuest = getTotalOrdini(conn, paymentType, customerType, selectedDateWildCard)
    #read the html template
    with open("./serverPrinter/template/report.html", "r") as file:
        html_template = file.read()
    html_body = "<h1>Report Giorno " + str(selectedDate) + """
    </h1>
    <table>
      <thead>
        <tr>
          <th></th>
          <th></th>
        </tr>
      </thead>
      <tbody>
    """
    html_body += "<tr> <td>Totale Ordini contanti</td><td>" + str(contanti[0]) + "</td></tr>"
    html_body += "<tr> <td>Totale Incasso contanti</td><td>" + str(contanti[1]) + " €</td></tr>"
    html_body += "<tr> <td>Totale Ordini POS</td><td>" + str(pos[0]) + "</td></tr>"
    html_body += "<tr> <td>Totale Incasso POS</td><td>" + str(pos[1]) + " €</td></tr>"
    html_body += "<tr> <td>Totale Ordini Clienti</td><td>" + str(contanti[0]+pos[0]) + "</td></tr>"
    html_body += "<tr> <td>Totale Incasso Clienti</td><td>" + str(contanti[1]+pos[1]) + " €</td></tr>"
    html_body += "<tr> <td>Totale Ordini Volontari</td><td>" + str(costoVolounteer[0]) + "</td></tr>"
    html_body += "<tr> <td>Totale Costo Volontari</td><td>" + str(costoVolounteer[1]) + " €</td></tr>"
    html_body += "<tr> <td>Totale Ordini Ospiti</td><td>" + str(costoGuest[0]) + "</td></tr>"
    html_body += "<tr> <td>Totale Costo Ospiti</td><td>" + str(costoGuest[1]) + " €</td></tr>"
    html_body += """
    </tbody>
    </table>
    """
    #fill the template
    html_template = html_template.format(body=html_body)
    randomName = str(uuid.uuid4())
    filename = r".\serverPrinter\tmp\a" + randomName
    infilename = filename + "input.html"
    #save to tmp file the formatted html template
    with open(infilename, "wb") as file:
        file.write(str.encode(html_template))
    outfilename = filename + "report.pdf"
    commandText = """.\serverPrinter\weasyprint.exe -e utf-8 {} {}""".format(infilename, outfilename)
    #convert html to pdf with weasyprint
    os.popen(commandText)
    printfilename = ".\\serverPrinter\\tmp\\a" + randomName + "report.pdf"
    time.sleep(3)
    #wait for the pdf outfile before trying to print (maximum 10 seconds)
    counter = 0
    while True:
        if (os.path.isfile(outfilename)):
            break
        if (counter > 10):
            break
        counter += 1
        time.sleep(1)
    #print the command to the right printer
    try:
        #set paper format to A5
        PRINTER_DEFAULTS = {"DesiredAccess":win32print.PRINTER_ALL_ACCESS}
        handle = win32print.OpenPrinter(printername, PRINTER_DEFAULTS)
        properties = win32print.GetPrinter(handle, 2)
        devmode = properties['pDevMode']
        DMPAPER_A5 = 11
        devmode.PaperSize = DMPAPER_A5
        win32print.SetPrinter(handle, 2, properties, 0)
        #---------------- check if the format is correct------
        properties = win32print.GetPrinter(handle, 2)
        devmode = properties['pDevMode']
        win32print.ClosePrinter(handle)
        #-----------------start printing----------------------
        structureOut = shell.ShellExecuteEx(fMask = 256 + 64, lpVerb='printto', lpFile=r"{}".format(printfilename), lpParameters=f'"{printername}"', lpDirectory=".")
        hh = structureOut['hProcess']
        ret = win32event.WaitForSingleObject(hh, -1)
        if (ret == 0): #print command success
            #update order status
            print("STAMPA REPORT OK")
            #remove tmp files
            os.remove(infilename)
            #os.remove(outfilename)
    except win32api.error as e:
        #logging here
        print(e.args[0])
        print(e.args[2])
    return 0
