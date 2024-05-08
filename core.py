from database import *
from threading import Lock
from datetime import datetime
#printer imports
import uuid
import win32api
import win32print
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
    #divide menu in panino + fries
    #filter out beverages
    #send print instructions to printers with correct data
    cucinaItemList = []
    pizzeriaItemList = []
    for item in order['items']:
        itemClass = resolveItemClassById(conn, item["itemId"])
        if (itemClass == "cucina"):
            itemCategory = resolveItemCategoryById(conn, item["itemId"])
            if(itemCategory == "menu birra" or itemCategory == "menu bibita"):
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
        html_body += "<tr> <td>" + name + "</td><td>" + str(item['quantity']) + "</td><td>" + item['notes'] + "</td>"
    html_body += """
    </tbody>
    </table>
    """
    #fill the template
    html_template = html_template.format(body=html_body)
    randomName = str(uuid.uuid4())
    filename = r".\serverPrinter\tmp\a" + randomName
    infilename = filename + "input.html"
    #save to tmp file the filled html template
    with open(infilename, "wb") as file:
        file.write(str.encode(html_template))
    outfilename = filename + "output.pdf"
    commandText = """.\serverPrinter\weasyprint.exe -e utf-8 {} {}""".format(infilename, outfilename)
    #convert html to pdf
    os.popen(commandText)
    printfilename = ".\\serverPrinter\\tmp\\a" + randomName + "output.pdf"
    time.sleep(3)
    #wait for the pdf outfile before trying to print
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
        hinstance = win32api.ShellExecute(
            0,
            "printto",
            r"{}".format(printfilename),
            f'"{printername}"',
            ".",
            0
        )
        if (hinstance > 32): #print command success
            #update order status
            data = {'orderStatus': 1, 'orderId': orderId, 'orderType': orderType}
            updateOrderStatus(conn, data)
            #remove tmp files
            os.remove(infilename)
            os.remove(outfilename)
    except win32api.error as e:
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
    #print(data)
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
    #check if input exist and valid?
    updateOrderStatus(conn, data)
    updateOrderTable(conn, data)

def archiveDatabaseData(conn):
    dayId = getDayId(conn)
    hotOrders = getHotOrders(conn)
    for order in hotOrders:
        archiveOrder = {'displayId': order[0], 'totalValue': order[1], 'paymentType': order[3], 'datetime': order[4], 'customerType': order[6], 'dayId': dayId}
        insertArchiveOrder(conn, archiveOrder)
    #todo check for success before deleting
    deleteHotOrders(conn)
    deleteHotOrdersStatuses(conn)
    hotItems = getHotItems(conn)
    for item in hotItems:
        archiveItem = {'dayId': dayId, 'displayId': item[0], 'itemId': item[1], 'quantity': item[2], 'notes': item[3]}
        insertArchiveItem(conn, archiveItem)
    #todo check for success before deleting
    deleteHotItems(conn)
    resetSqlSequence(conn)

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
            if (itemCategory == "menu birra" or itemCategory == "menu bibita"): #if item is a menu
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
