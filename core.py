from database import *
from threading import Lock
from datetime import datetime

mutex = Lock()

#todo remove orderStatus from orders table
def registerOrderToDatabase(conn, order):
    order["status"] = 0 #status: "non assegnato"
    orderId = order["orderId"]
    #datetime
    order["datetime"] = datetime.now()
    #operatorId & customerType(todo)
    order["operatorId"] = 0
    orderData = (order["totalValue"], order["operatorId"], order["paymentType"], order["datetime"], order["customerType"], order["orderId"])
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

#todo modify query (and javascript) to retrieve order statues
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

