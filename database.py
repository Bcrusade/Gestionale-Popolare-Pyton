import sqlite3


def test_conn():
    pass


def insertOrder(conn, order):
    sql = ''' INSERT INTO orders(orderId, totalValue, operatorId, paymentType, datetime, customerType, tableId) 
                      VALUES(:orderId, :totalValue, :operatorId, :paymentType, :datetime, :customerType, :tableId) '''
    cur = conn.cursor()
    cur.execute(sql, order)
    return 0

def insertItem(conn, item):
    sql = ''' INSERT INTO items(orderId, itemId, quantity, notes)
                  VALUES(:orderId, :itemId, :quantity, :notes) '''
    cur = conn.cursor()
    cur.execute(sql, item)
    return 0

def insertStatus(conn, orderId, orderType, value):
    sql = ''' INSERT INTO orderStatus(orderId, orderType, status)
                      VALUES(?, ?, ?) '''
    cur = conn.cursor()
    try:
        cur.execute(sql, (orderId, orderType, value, ))
    except sqlite3.OperationalError as e:

        return 11
    return 0

#get order id to use for a new order
def getOrderId(conn):
    sql = ''' UPDATE sqlite_sequence SET seq = seq + 1 WHERE name = "orders" '''
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    sql2 = ''' SELECT seq from sqlite_sequence WHERE name = "orders" '''
    cur = conn.cursor()
    cur.execute(sql2)
    conn.commit()
    return cur.fetchone()[0]

#select all orders with pending status, query only relevant data (status, tableId, orderId, datetime)
def getOrderList(conn):
    sql = ''' SELECT orderId, tableId, datetime FROM orders'''
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()

#get total number of orders
def getTotalOrderNumber(conn):
    sql = ''' SELECT count(*) FROM orders'''
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchone()[0]

#get total cash collection
def getTotalCash(conn):
    sql = ''' SELECT SUM(totalValue) FROM orders where paymentType = "cash"'''
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchone()[0]

#get total pos collection
def getTotalPos(conn):
    sql = ''' SELECT SUM(totalValue) FROM orders where paymentType = "pos"'''
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchone()[0]

# filter out status = 3
def getOrderStatusById(conn, orderId):
    sql = ''' SELECT * FROM orderStatus WHERE orderId = ? AND status IN (0, 1, 2)'''
    cur = conn.cursor()
    cur.execute(sql, (orderId, ))
    return cur.fetchall()

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
    sql = ''' SELECT * FROM orderStatus WHERE status = 3 ORDER BY orderId DESC LIMIT 50'''
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

def resolveItemCategoryById(conn, id):
    sql = ''' SELECT category FROM itemProp WHERE itemId = ? '''
    cur = conn.cursor()
    cur.execute(sql, (id,))
    return cur.fetchone()[0]

#-------------------archive functions------------------------------
def checkOrderOpen(conn):
    sql = ''' SELECT count(*) FROM orderStatus WHERE status IN (0, 1, 2)'''
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchone()[0]

def getHotOrders(conn):
    sql = ''' SELECT * FROM orders'''
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()

def getHotItems(conn):
    sql = ''' SELECT * FROM items'''
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchall()

def insertArchiveOrder(conn, order):
    sql = ''' INSERT INTO orderArchive(displayId, totalValue, paymentType, datetime, customerType, dayId) 
                      VALUES(:displayId, :totalValue, :paymentType, :datetime, :customerType, :dayId) '''
    cur = conn.cursor()
    cur.execute(sql, order)
    conn.commit()
    return 0

def insertArchiveItem(conn, item):
    sql = ''' INSERT INTO itemArchive(dayId, displayId, itemId, quantity, notes) 
                      VALUES(:dayId, :displayId, :itemId, :quantity, :notes) '''
    cur = conn.cursor()
    cur.execute(sql, item)
    conn.commit()
    return 0

def deleteHotOrders(conn):
    sql = ''' DELETE FROM orders'''
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    return

def deleteHotItems(conn):
    sql = ''' DELETE FROM items'''
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    return

def deleteHotOrdersStatuses(conn):
    sql = ''' DELETE FROM orderStatus'''
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    return

def resetSqlSequence(conn):
    sql = ''' UPDATE sqlite_sequence SET seq = 0 WHERE name = "orders" '''
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    return

def getDayId(conn):
    sql = ''' UPDATE sqlite_sequence SET seq = seq + 1 WHERE name = "day" '''
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    sql2 = ''' SELECT seq from sqlite_sequence WHERE name = "day" '''
    cur = conn.cursor()
    cur.execute(sql2)
    conn.commit()
    return cur.fetchone()[0]

def getOrderByDayId(conn, dayId):
    sql = ''' SELECT * FROM orderArchive WHERE dayId = ?'''
    cur = conn.cursor()
    cur.execute(sql, dayId)
    return cur.fetchall()

#get total data contanti
def getTotalOrdini(conn, paymentType, customerType, selectedDate):
    sql = ''' SELECT count(*), SUM(totalValue) FROM orderArchive WHERE paymentType = ? AND customerType = ? AND datetime LIKE ?'''
    cur = conn.cursor()
    cur.execute(sql, (paymentType, customerType, selectedDate))
    return cur.fetchone()

def getTotalOrderNumberVol(conn):
    sql = ''' SELECT count(*) FROM orders WHERE customerType = "Guest" OR customerType = "Volounteer" '''
    cur = conn.cursor()
    cur.execute(sql)
    return cur.fetchone()[0]
