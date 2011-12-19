#!/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import sqlite3

LibraryPath = '/home/liuhui/Code'
#LibraryPath = '/misc/Book/Book/Linux开发'
DataBase = '/tmp/library.dat'

def CheckFileType(filename):
    """Check the file type whether it be know as ebook.
        filename    the file's name you want to check
    """
    FileType = ['pdf', 'djvu', 'chm', 'exe', 'epub', 'doc', 'odt']
    filetype = filename.split('.')
    if len(filetype) == 1:
        return False
    try:
        FileType.index(filetype[-1])
        return ('.'.join(filetype[0:-1]), filetype[-1])
    except ValueError:
        return False

def guessTag(string):
    tmp = string.replace(LibraryPath, '').split('\\')
    if len(tmp) == 1:
        return tmp[0]
    tag = ''
    for item in tmp:
        tag = tag + ' %s' % item
    print tag
    return tag

def SqlInsert(filename, pathname):
    """ Generate insert SQL sentence, the special characater need to be escape.
        If the filename or pathname has some characater need to be escape
    """
    fname = ''
    fformat = ''
    #escape = ["'", '"', '\\' '%', '_']
    # use sqlite3 test sql, just ' need to be escape "''"
    filename = filename.replace("'", "''")
    #filename = filename.replace("_", "\_")

    # May be some files hasn't suffix type
    filetype = CheckFileType(filename)
    if not filetype:
        fname = filename
        fformat = ''
    else:
        fname, fformat = filetype

    tag = catalog = guessTag(pathname)
    record = "INSERT INTO library VALUES('%s', '%s', '%s', '%s', '%s', \
                '%s', '%s', '%s', '%s', '%s', '%s', '%s', %d, %d)" % \
                (fname, "", "", "", "", fformat, "", "", tag, catalog, \
                pathname, "", 1, 5)
#   print record
    return record

def GetBook(path):
    """List all book in the Library
        path    the absolute path. such as /home/liuhui/Library
    """
    sqlinsert = []
    for dirpath, dirname, filenames in os.walk(path):
        if not len(filenames):
            continue
        else:
            for filename in filenames:
                #print filename, dirpath
                #print SqlInsert(filename, dirpath)
                sqlinsert.append(SqlInsert(filename, dirpath))
    return sqlinsert

def SqlOperate(cur, sql):
    for item in sql:
        cur.execute(item)

def CreateLibrary():
    """Create Library DataBase and Insert the book.
    """
    CreateTable = """CREATE TABLE library(
                    bookname    TEXT,
                    author      TEXT,
                    press       TEXT,
                    publishdate TEXT,
                    lauguage    TEXT,
                    format      TEXT,
                    isbn        TEXT,
                    barcode     TEXT,
                    tag         TEXT,
                    catalog     TEXT,
                    path        TEXT,
                    note        TEXT,
                    reader      integer,
                    score       integer)"""
    CreateCatalog = """CREATE TABLE catalog(
                    lib         TEXT,
                    catalogname TEXT,
                    catalonumber integer,
                    memberlist TEXT)"""

    BookList = GetBook(LibraryPath)

    conn = sqlite3.connect(DataBase)
    c = conn.cursor()
    try:
        c.execute(CreateTable)
        c.execute(CreateCatalog)
    except sqlite3.OperationalError:
        print "The table has exist!"
    SqlOperate(c, BookList)
    conn.commit()
    conn.close()

def FindBook(keyword, flag):
    """The Most Import feature. search the library to find the book you want
        keyword     the word you want to find and multiword split by space.
        flag        use to special which colume would be check.
    """
    columeName = ''
    tableName = 'library'
    #DataBase = '/tmp/library.dat'

    key = keyword.split()
    regex = '%' + '%'.join(key) + '%'

    if flag == 1:
        columeName = 'bookname'
    elif flag == 2:
        columeName = 'publishdate'
    elif flag == 3:
        columeName = 'author'
    elif flag == 4:
        columeName = 'lauguage'
    elif flag == 5:
        columeName = 'format'
    elif flag == 6:
        columeName = 'tag'
    elif flag == 7:
        columeName = 'pathname'
    elif flag == 8:
        columeName = 'note'
        
    #sql = """SELECT bookname FROM %s WHERE %s LIKE '%s'""" % \
    sql = """SELECT * FROM %s WHERE %s LIKE '%s'""" % \
                (tableName, columeName, regex)
    
    conn = sqlite3.connect(DataBase)
    c = conn.cursor()
    # the method of object cursor fetchall() return a list construct of tuple
    # even thought the you just choose one colume
    result = c.execute(sql).fetchall()
    conn.commit()
    conn.close()
    return result
    
def updateCatalog():
    """Catalog the book by the prespecial classification, such as lauguage 
        type, publish date, tag, author and so on.
    """
    columeName = ['tag', 'catalog', 'lauguage', 'format', 'press']
    catalog = {}
    conn = sqlite3.connect(DataBase)
    c = conn.cursor()
    for item in columeName:
        sql = "SELECT bookname, %s FROM library WHERE %s != ''" % (item, item)
        catalog[item] = c.execute(sql).fetchall()
        #print item, catalog[item]

    # key       The columne name of the library table
    # value     [(bookname, keyvalue), (bookname, keyvalue)......]
    for key, value in catalog.items():
        hasinsert = ''
        print "Key, Value:", key, value
        # I want to use the iternate find the same tag (may be press, lauguage, and so on)
        #for i, item in enumerate(value):
        for item in value:
        # item is a tuple (bookname, columneValue)
            if item[1] == hasinsert:
                print 'hello'
                continue
            n = 0
            booklist = []
            #for j, tmp in enumerate(value):
            for tmp in value:
                if item[1] == tmp[1]:
                    #print item[0], item[1]
                    n += 1
                    booklist.append(tmp[0])
            bList = str(booklist).replace("'", '"')
            print "blist", bList
            insert = "INSERT INTO catalog VALUES ('%s', '%s', %d, '%s')" % (key, item[1], n, bList)
            print insert
            hasinsert = item[1]
            c.execute(insert)
    conn.commit()
    conn.close()
    
if __name__ == '__main__':
    CreateLibrary()
    #print FindBook('00 queue', 1)
    updateCatalog()
