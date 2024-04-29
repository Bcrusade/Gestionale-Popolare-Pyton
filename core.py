from database import *
from threading import Lock
from datetime import datetime

mutex = Lock()

#
def registerOrderToDatabase(conn, order):
    order["status"] = 0 #status: "non assegnato"
    orderId = order["orderId"]
    #datetime
    order["datetime"] = datetime.now()
    #operatorId & customerType(todo)
    order["operatorId"] = 0
    orderData = (order["totalValue"], order["status"], order["operatorId"], order["paymentType"], order["datetime"], order["customerType"], order["orderId"])
    insertOrder(conn, orderData)  # insert order in orders table
    for item in order["items"]:
        item["orderId"] = orderId
        insertItem(conn, item)  # insert each item in items table
    return

def retrieveOrderNumber(conn):
    mutex.acquire(timeout=10) #probably useless mutex (there is a write to db)
    orderId = getOrderId(conn)
    mutex.release()
    return orderId

def retrieveOrderList(conn):
    data = getOrderList(conn)
    print(data)
    orderList = []
    for order in data:
        orderList.append({"orderId": order[0], "totalValue": order[1], "orderStatus": order[2], "tableId": order[3], "datetime": order[4]})
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
        data["orderStatus"] = 1 #aggiorna lo stato a 'in preparazione' se prima era 'non assegnato'
    updateOrderStatus(conn, data)
    updateOrderTable(conn, data)

