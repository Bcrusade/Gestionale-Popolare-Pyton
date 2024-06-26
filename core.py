import logging

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
#----------------
import logging

logger = logging.getLogger('main.core')

mutex = Lock()
registerOrderMutex = Lock()
updateDataMutex = Lock()
archiveDataMutex = Lock()


def registerOrderToDatabase(conn, order):
    order["status"] = 0  #status: "non stampato"
    orderId = order["orderId"]
    #datetime
    order["datetime"] = datetime.now()
    #operatorId(todo)
    order["operatorId"] = 0
    order["tableId"] = 0
    orderData = (order["orderId"], order["totalValue"], order["operatorId"], order["paymentType"], order["datetime"],
                 order["customerType"], order["tableId"])
    registerOrderMutex.acquire()
    try:
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
        #time.sleep(10)
        for item in order["items"]:
            item["orderId"] = orderId
            insertItem(conn, item)  # insert each item in items table
        conn.commit()
    except (sqlite3.OperationalError, sqlite3.IntegrityError, sqlite3.DatabaseError) as e:
        logger.error("Could not register order %s to db", orderId, exc_info=True)
        conn.rollback()
        registerOrderMutex.release()
        return 3
    registerOrderMutex.release()
    logger.info("Order %s registered successfully", orderId)
    return 0


def printCommand(conn, order):
    #divide by item class
    #filter out beverages
    #send print instructions to printers with correct data
    customerType = order["customerType"]
    cucinaItemList = []
    pizzeriaItemList = []
    for item in order['items']:
        itemClass = resolveItemClassById(conn, item["itemId"])
        if (itemClass == "cucina"):
            itemCategory = resolveItemCategoryById(conn, item["itemId"])
            if (itemCategory == "menu birra" or itemCategory == "menu bibita"):
                # divide menu in panino + fries
                cucinaItemList.append(
                    {"name": resolveItemNameById(conn, item['itemId']).split("- ")[1], "itemId": item['itemId'],
                     "quantity": item['quantity'], "notes": item['notes']})
                cucinaItemList.append(
                    {"name": "Patatine fritte", "itemId": item['itemId'], "quantity": item['quantity'], "notes": ""})
            else:
                cucinaItemList.append(item)
        elif (itemClass == "pizzeria"):
            pizzeriaItemList.append(item)
    orderId = order['orderId']
    if len(cucinaItemList) > 0:
        orderType = "cucina"
        printCommandType(conn, orderId, cucinaItemList, config.nomeStampanteCucina, orderType, customerType)
    if len(pizzeriaItemList) > 0:
        orderType = "pizzeria"
        printCommandType(conn, orderId, pizzeriaItemList, config.nomeStampantePizzeria, orderType, customerType)


def printCommandType(conn, orderId, printItemList, printername, orderType, customerType):
    #print(printItemList)
    #read the html template
    with open("./serverPrinter/template/invoice.html", "r") as file:
        html_template = file.read()
    html_body = """
    <table>
      <thead>
        <tr>
        <th colspan="3" style="border-bottom: 0; text-align: left;">
          <h1 id="topHeader">Ordine """ + str(orderType.capitalize()) + " Nr." + str(orderId) + """ </h1>    
        </th>
        </tr>"""
    html_body += """<tr>
               <th colspan="3" style="border-bottom: 0; text-align: left;">
                 <h2 style="color: #000000;">Volontari/Frati</h2> 
               </th>
        </tr>""" if customerType == "Volounteer" else ""
    html_body += """
        <tr>
          <th colspan="1" style="width: 40%;">NOME</th>
          <th colspan="1" style="width: 10%;">QUANTITÀ</th>
          <th colspan="1" style="width: 50%;">NOTE</th>
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
        html_body += "<tr> <td>" + name + "</td><td>" + str(item['quantity']) + '</td><td style="max-width: 50%;">' + \
                     item['notes'] + "</td></tr>"
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
            logger.error("Pdf order command not generated/found for order %s %s", orderId, orderType)
            return 11
        counter += 1
        time.sleep(1)
    #print the command to the right printer
    try:
        #set paper format to A5
        PRINTER_DEFAULTS = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS}
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
        structureOut = shell.ShellExecuteEx(fMask=256 + 64, lpVerb='printto', lpFile=r"{}".format(printfilename),
                                            lpParameters=f'"{printername}"', lpDirectory=".")
        hh = structureOut['hProcess']
        ret = win32event.WaitForSingleObject(hh, -1)
        if (
                ret == 0):  #print command success (the printer has to handle the actual print yet, the server just sent the command)
            #update order status
            data = {'orderStatus': 1, 'orderId': orderId, 'orderType': orderType}
            updateOrderStatus(conn, data)
            #print("STAMPA COMANDA OK")
            #remove tmp files
            os.remove(infilename)
            os.remove(outfilename)
            logger.info("Print command sent successfully for order %s %s", orderId, orderType)
    except win32api.error as e:
        logger.error("Server error in sending print command for order %s %s; error code: %s, %s", orderId, orderType,
                     e.args[0], e.args[2])
        return 11
    return 0


def retrieveOrderNumber(conn):
    mutex.acquire()
    try:
        orderId = getOrderId(conn)
    except sqlite3.OperationalError:
        mutex.release()
        raise sqlite3.OperationalError()
    mutex.release()
    return orderId


def retrieveOrderList(conn):
    data = getOrderList(conn)
    orderList = []
    for order in data:
        orderId = order[0]
        statuses = getOrderStatusById(conn, orderId)
        for status in statuses:
            orderList.append({"orderId": order[0], "tableId": order[1], "datetime": order[2], "orderType": status[1],
                              "orderStatus": status[2], "customerType": order[3]})
    return orderList


def retrieveRecentCompletedOrderList(conn):
    data = getRecentCompletedOrders(conn)
    orderList = []
    for order in data:
        orderId = order[0]
        info = getOrderInfoById(conn, orderId)
        orderList.append({"orderId": order[0], "tableId": info[3], "datetime": info[2], "orderType": order[1],
                          "orderStatus": order[2], "customerType": info[4]})
    #print(orderList)
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
    updateDataMutex.acquire()
    try:
        status1 = updateOrderStatus(conn, data)
        status2 = updateOrderTable(conn, data)
        conn.commit()
        updateDataMutex.release()
    except (sqlite3.OperationalError, sqlite3.IntegrityError, sqlite3.DatabaseError) as e:
        logger.error("Could not update data of order %s %s", data["orderId"], data["orderType"], exc_info=True)
        conn.rollback()
        updateDataMutex.release()
        return 11
    logger.info("Successfully updated data of order %s %s", data["orderId"], data["orderType"])
    return 0


def retrieveSummaryData(conn):
    totalOrderNumber = getTotalOrderNumber(conn)
    totalCash = getTotalCash(conn)
    totalPos = getTotalPos(conn)
    totalOrderNumberVol = getTotalOrderNumberVol(conn)
    orderSummary = []
    orderSummary.append(
        {"NumOrder": totalOrderNumber, "Cash": totalCash, "POS": totalPos, "NumOrderVolontari": totalOrderNumberVol})
    return orderSummary


def archiveDatabaseData(conn):
    archiveDataMutex.acquire()
    orderOpen = checkOrderOpen(conn)
    orderToArchive = getTotalOrderNumber(conn)
    if (orderToArchive == 0):
        archiveDataMutex.release()
        return 2
    if (orderOpen > 0):
        archiveDataMutex.release()
        return 1
    elif (orderOpen == 0):
        #backup database file
        source = r".\data\myDatabase.db"
        dest = r".\data\backup\dataBackup_" + datetime.now().strftime("%d.%m.%y-%H-%M-%S") + ".db"
        with open(source, 'rb') as src, open(dest, 'wb') as dst:
            try:
                dst.write(src.read())
            except OSError as e:
                logger.error("Errore scrittura backup database: %s", str(e))
                archiveDataMutex.release()
                return 135
        dayId = getDayId(conn)
        # -----------archive orders---------------
        hotOrders = getHotOrders(conn)
        ordersToArchive = len(hotOrders)
        counter = 0
        for order in hotOrders:
            archiveOrder = {'displayId': order[0], 'totalValue': order[1], 'paymentType': order[3],
                            'datetime': order[4], 'customerType': order[6], 'dayId': dayId}
            status = insertArchiveOrder(conn, archiveOrder)
            if status == 0:
                counter += 1
        if ordersToArchive == counter:
            deleteHotOrders(conn)
            deleteHotOrdersStatuses(conn)
        else:
            logger.error("Could not archive database")
            archiveDataMutex.release()
            return 12  #error
        #-------------archive items--------------
        hotItems = getHotItems(conn)
        itemsToArchive = len(hotItems)
        counter = 0
        for item in hotItems:
            archiveItem = {'dayId': dayId, 'displayId': item[0], 'itemId': item[1], 'quantity': item[2],
                           'notes': item[3]}
            status = insertArchiveItem(conn, archiveItem)
            if status == 0:
                counter += 1
        if itemsToArchive == counter:
            deleteHotItems(conn)
            resetSqlSequence(conn)
        else:
            logger.error("Could not archive database")
            archiveDataMutex.release()
            return 13  #error
        archiveDataMutex.release()
        logger.info("Archive database success")
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
        itemClass = resolveItemClassById(conn, item[0])  #item[0] = itemId
        if (itemClass == orderType):  #cucina or pizzeria
            itemCategory = resolveItemCategoryById(conn, item[0])
            if (
                    itemCategory == "menu birra" or itemCategory == "menu bibita"):  #if item is a menu, the name is the one of panino; add fries
                printItemList.append(
                    {"name": resolveItemNameById(conn, item[0]).split("- ")[1], "itemId": item[0],
                     "quantity": item[1], "notes": item[2]})
                printItemList.append(
                    {"name": "Patatine fritte", "itemId": item[0], "quantity": item[1], "notes": ""})
            else:  #item is not a menu
                printItemList.append({"name": resolveItemNameById(conn, item[0]), "itemId": item[0],
                                      "quantity": item[1], "notes": item[2]})
    customerType = getOrderInfoById(conn, orderId)[4]
    status = printCommandType(conn, orderId, printItemList, printername, orderType, customerType)
    if status == 0:
        logger.info("Reprint request success for order %s %s", orderId, orderType)
    else:
        logger.error("Reprint request error for order %s %s", orderId, orderType)
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
    datereport = datetime.strptime(selectedDate, '%Y-%m-%d').strftime("%d-%m-%Y")
    #read the html template
    with open("./serverPrinter/template/report.html", "r") as file:
        html_template = file.read()
    html_body = """
    <table>
      <thead>
        <tr>
        <th colspan="2" style="border-bottom: 0; text-align: left;">
          <h1 id="topHeader">Report """ + str(datereport) + """ </h1>
        </th>
        </tr>
        <tr>
          <th colspan="1" style="width: 80%;"></th>
          <th colspan="1" style="width: 20%;"></th>
        </tr>
      </thead>
      <tbody>
    """
    html_body += "<tr> <td>Totale Ordini contanti</td><td>" + str(contanti[0]) + "</td></tr>"
    html_body += "<tr> <td>Totale Incasso contanti</td><td>" + str(
        float(0 if contanti[1] is None else contanti[1])) + " €</td></tr>"
    html_body += "<tr> <td>Totale Ordini POS</td><td>" + str(pos[0]) + "</td></tr>"
    html_body += "<tr> <td>Totale Incasso POS</td><td>" + str(float(0 if pos[1] is None else pos[1])) + " €</td></tr>"
    html_body += "<tr> <td>Totale Ordini Clienti</td><td>" + str(contanti[0] + pos[0]) + "</td></tr>"
    html_body += "<tr> <td>Totale Incasso Clienti</td><td>" + str(
        float(0 if contanti[1] is None else contanti[1]) + float(0 if pos[1] is None else pos[1])) + " €</td></tr>"
    html_body += "<tr> <td>Totale Ordini Volontari</td><td>" + str(costoVolounteer[0]) + "</td></tr>"
    html_body += "<tr> <td>Totale Costo Volontari</td><td>" + str(
        float(0 if costoVolounteer[1] is None else costoVolounteer[1])) + " €</td></tr>"
    html_body += "<tr> <td>Totale Ordini Ospiti</td><td>" + str(costoGuest[0]) + "</td></tr>"
    html_body += "<tr> <td>Totale Costo Ospiti</td><td>" + str(
        float(0 if costoGuest[1] is None else costoGuest[1])) + " €</td></tr>"
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
            logger.error("Pdf report not generated/found for date %s", selectedDate)
            return 12
        counter += 1
        time.sleep(1)
    #print the command to the right printer
    try:
        #set paper format to A5
        PRINTER_DEFAULTS = {"DesiredAccess": win32print.PRINTER_ALL_ACCESS}
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
        structureOut = shell.ShellExecuteEx(fMask=256 + 64, lpVerb='printto', lpFile=r"{}".format(printfilename),
                                            lpParameters=f'"{printername}"', lpDirectory=".")
        hh = structureOut['hProcess']
        ret = win32event.WaitForSingleObject(hh, -1)
        if (ret == 0):  #print command success
            #update order status
            #print("STAMPA REPORT OK")
            #remove tmp files
            os.remove(infilename)
            #os.remove(outfilename)
            logger.info("Print report sent successfully for date %s", selectedDate)
    except win32api.error as e:
        logger.error("Server error in sending print report for date %s; error code: %s, %s", selectedDate, e.args[0],
                     e.args[2])
        return 11
    return 0
