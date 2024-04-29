import sqlite3


def test_conn():
    pass


def insertOrder(conn, order):
    sql = ''' UPDATE orders
              SET totalValue=?, orderStatus=?, operatorId=?, paymentType=?, datetime=?, customerType = ? WHERE orderId = ?'''
    cur = conn.cursor()
    cur.execute(sql, order)
    conn.commit()

    return cur.lastrowid


def insertItem(conn, item):
    sql = ''' INSERT INTO items(orderId, itemId, quantity, notes)
                  VALUES(:orderId, :itemId, :quantity, :notes) '''
    cur = conn.cursor()
    cur.execute(sql, item)
    conn.commit()
    return


#get order id to use for a new order by inserting an empty order into db (orderStatus = 0)
def getOrderId(conn):
    #sql = '''UPDATE sqlite_sequence SET seq = seq + 1 WHERE name = "orders" '''
    sql = ''' INSERT INTO orders(displayId, totalValue, orderStatus, operatorId, paymentType, datetime, tableId)
                  VALUES(0, 0, -1, 0, 0, 0, 0) '''
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    return cur.lastrowid


#select all orders with pending status, query only relevant data (status, tableId, orderId, datetime)
def getOrderList(conn):
    sql = ''' SELECT orderId, totalValue, orderStatus, tableId, datetime FROM orders WHERE orderStatus in (0,1,2,3) '''
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()


def updateOrderStatus(conn, data):
    sql = ''' UPDATE orders SET orderStatus = ? WHERE orderId = ? '''
    cur = conn.cursor()
    cur.execute(sql, (data['orderStatus'], data['orderId']))
    conn.commit()
    return


def updateOrderTable(conn, data):
    sql = ''' UPDATE orders SET tableId = ? WHERE orderId = ? '''
    cur = conn.cursor()
    cur.execute(sql, (data['tableId'], data['orderId']))
    conn.commit()
    return

def getOrderItemsById(conn, id):
    sql = ''' SELECT itemId, quantity, notes FROM items WHERE orderId = ? '''
    cur = conn.cursor()
    cur.execute(sql, (id, ))
    return cur.fetchall()

def resolveItemNameById(conn, id):
    sql = ''' SELECT name FROM itemProp WHERE itemId = ? '''
    cur = conn.cursor()
    cur.execute(sql, (id, ))
    return cur.fetchone()[0]