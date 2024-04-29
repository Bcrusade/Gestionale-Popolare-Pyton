import sqlite3


def test_conn():
    pass


def insertOrder(conn, order):
    sql = ''' UPDATE orders
              SET totalValue=?, operatorId=?, paymentType=?, datetime=?, customerType = ? WHERE orderId = ?'''
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

def insertStatus(conn, orderId, orderType, value):
    sql = ''' INSERT INTO orderStatus(orderId, orderType, status)
                      VALUES(?, ?, ?) '''
    cur = conn.cursor()
    cur.execute(sql, (orderId, orderType, value, ))
    conn.commit()

#get order id to use for a new order by inserting an empty order into db (to filter out empty orders use datetime = 0) todo
def getOrderId(conn):
    sql = ''' INSERT INTO orders(displayId, totalValue, operatorId, paymentType, datetime, tableId)
                  VALUES(0, 0, 0, 0, 0, 0) '''
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    return cur.lastrowid


#select all orders with pending status, query only relevant data (status, tableId, orderId, datetime)
def getOrderList(conn):
    sql = ''' SELECT orderId, tableId, datetime FROM orders'''
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()


# filter out status = 3
def getOrderStatusById(conn, orderId):
    sql = ''' SELECT * FROM orderStatus WHERE orderId = ? AND status IN (0, 1, 2)'''
    cur = conn.cursor()
    cur.execute(sql, (orderId, ))
    return cur.fetchall()

#####todo
def updateOrderStatus(conn, data):
    sql = ''' UPDATE orderStatus SET status = ? WHERE orderId = ? AND orderType = ?'''
    cur = conn.cursor()
    cur.execute(sql, (data['orderStatus'], data['orderId'], data['orderType']))
    conn.commit()
    return

def makeOrderStatusCoherent(conn, orderId):
    sql = ''' UPDATE orderStatus SET status = 1 WHERE orderId = ? '''
    cur = conn.cursor()
    cur.execute(sql, (orderId, ))
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

def getRecentCompletedOrders(conn):
    sql = ''' SELECT * FROM orderStatus WHERE status = 3 ORDER BY orderId DESC LIMIT 30'''
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()

def getOrderInfoById(conn, orderId):
    sql = ''' SELECT totalValue, paymentType, datetime, tableId, customerType FROM orders WHERE orderId = ? '''
    cur = conn.cursor()
    cur.execute(sql, (orderId, ))
    return cur.fetchone()

def resolveItemNameById(conn, id):
    sql = ''' SELECT name FROM itemProp WHERE itemId = ? '''
    cur = conn.cursor()
    cur.execute(sql, (id, ))
    return cur.fetchone()[0]

def resolveItemClassById(conn, id):
    sql = ''' SELECT itemClass FROM itemProp WHERE itemId = ? '''
    cur = conn.cursor()
    cur.execute(sql, (id, ))
    return cur.fetchone()[0]