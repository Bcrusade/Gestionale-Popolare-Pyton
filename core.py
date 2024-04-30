from database import *
from threading import Lock
from datetime import datetime

mutex = Lock()

def registerOrderToDatabase(conn, order):
    order["status"] = 0 #status: "non assegnato"
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
        insertStatus(conn, orderId, "Cucina", 0)
    if (hasPizza):
        insertStatus(conn, orderId, "Pizzeria", 0)

    for item in order["items"]:
        item["orderId"] = orderId
        insertItem(conn, item)  # insert each item in items table
    return

def printCommand(order):
    #divide by item class
    #divide menu in panino + fries
    #filter out beverages
    #send print instructions to printers with correct data
    pass

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
    print(orderList)
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

def retrieveOrderItems(conn, id):
    data = getOrderItemsById(conn, id)
    itemList = []
    for item in data:
        name = resolveItemNameById(conn, item[0])
        itemList.append({"name": name, "quantity": item[1], "notes": item[2]})
    return itemList

def updateData(conn, data):
    print(data)
    #check if input exist and valid?
    if (data["tableId"] != 0 and data["orderStatus"] == 0):
        #aggiorna lo stato a 'in preparazione' se prima era 'non assegnato' quando metto il numero del tavolo
        makeOrderStatusCoherent(conn, data["orderId"])
    else:
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
