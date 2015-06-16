#! /usr/bin/env python

# PyDumpy - a tool for easy partial and sorted MySQL database dumping.
#
# Github fork: https://github.com/miebach/pydumpy
# Original source: https://code.google.com/p/pydumpy/source/browse/trunk/src/pydumpy.py

import os
import sys
import re
from optparse import OptionParser
import MySQLdb

def getCommandLineOptions():
    usage = "Usage: %prog [OPTION]..."
    version = "%prog 0.2"
    
    parser = OptionParser(usage=usage, version=version)
    parser.add_option("-H", "--hostname", dest = "hostname", help = "Database hostname.", default = False)
    parser.add_option("-P", "--port", dest = "port", help = "Database port.", default = 3306)
    parser.add_option("-u", "--username", dest = "username", help = "Database username.", default = False)
    parser.add_option("-p", "--password", dest = "password", help = "Database password.", default = False)
    parser.add_option("-n", "--name", dest = "dbname", help = "Database name.", default = False)
    parser.add_option("-e", "--options", dest = "flags", help = "Additional mysqldump options.", default = "")
    parser.add_option("-f", "--file", dest = "file", help = "File to dump to.", default = "")
    parser.add_option("-r", "--limit", type="int", dest = "rows", help = "Max number of rows per table. Default 100000.", default = 100000)
    parser.add_option("-l", "--ask-to-limit", action="store_true", dest = "askToLimit", help = "Ask to provide a row limit for each table. Default false.", default = False)
    parser.add_option("-s", "--ask-to-sort", action="store_true", dest = "askToSort", help = "Ask to provide sorting keys for each table. Default false.", default = False)
    parser.add_option("-i", "--ignore", dest = "ignore", help = "Regular expression pattern used to ignore tables.", default = False)
    parser.add_option("-a", "--accept", dest = "accept", help = "Regular expression pattern used to accept tables.", default = False)
    parser.add_option("-d", "--dry-run", action="store_true", dest = "dryRun", help = "Output all statements without executing them.", default = False)
    
    (options, args) = parser.parse_args()

    options.port = int(options.port)

    if options.hostname == False:
        parser.error('Use -H or --hostname to specify database hostname');
        
    if options.username == False:
        parser.error('Use -u or --username to specify database username');
        
    if options.password == False:
        parser.error('Use -p or --password to specify database password');
        
    if options.dbname == False:
        parser.error('Use -n or --name to specify database name');
        
    return options

def addLimitedRows(table, limit):
    output = " " + table + " --where=\"1 LIMIT " + str(limit) + "\""
    
    return output
    
def addLimitedRowsByKey(table, key, limit):
    output = " " + table + " --where=\"1 ORDER BY " + key + " DESC LIMIT " + str(limit) + "\""

    return output

def getTableMetaData(options):
    result = []

    conn = MySQLdb.connect (host = options.hostname,
                           port = options.port,
                           user = options.username,
                           passwd = options.password,
                           db = "information_schema")
    
    cursor = conn.cursor()
    cursor.execute("SELECT TABLE_NAME, TABLE_ROWS FROM TABLES WHERE TABLE_SCHEMA = '" + options.dbname + "'")
    tables = cursor.fetchall() 
    cursor.close()
    conn.close()

    for table in tables:
        (tableName, estimatedRows) = table

        if options.ignore and re.search(options.ignore, tableName):
            continue

        if options.accept and not re.search(options.accept, tableName):
            continue

        result.append(table)

    return result

def getTableColumnsMetaData(options):
    columns = {}

    conn = MySQLdb.connect (host = options.hostname,
                           port = options.port,
                           user = options.username,
                           passwd = options.password,
                           db = "information_schema")
    
    cursor = conn.cursor()
    cursor.execute("SELECT TABLE_NAME,COLUMN_NAME FROM COLUMNS WHERE TABLE_SCHEMA = '" + options.dbname + "' ORDER BY TABLE_NAME ASC, ORDINAL_POSITION ASC")
    rows = cursor.fetchall() 
    cursor.close()
    conn.close()

    for row in rows:
        (tableName, columnName) = row

        if tableName not in columns:
            columns[tableName] = []

        columns[tableName].append(columnName);

    return columns

def getTableLimit(options, tableName):
    limit = False
    
    if not options.askToLimit:
        limit = options.rows
    else:    
        limit = raw_input('Table \''+ tableName +'\' has more than ' + str(options.rows) + ' records. Add limit? [N - no / d - row limit / input value] ')

        if 'd' == limit:
            limit = options.rows
        elif '' == limit:
            limit = False
        elif 'N' == limit:
            limit = False
        else:
            try:
                limit = int(limit)
            except ValueError:
                print "error: limit must be an integer"
                exit()
        
    return limit

def getColumnNames(columns):
    names = "";

    i = 0
    for column in columns:
        i = i + 1
        names = names + column
        if i != len(columns):
            names = names + "/"

    return names

def getTableSortKey(options, tableName, columns):
    key = False
    
    if not options.askToSort:
        key = False
    else:
        key = raw_input('Sort table by key? [N/' + getColumnNames(columns) + '] ')
    
        if key:
            if key not in columns:
                print "error: unknown key specified"
                exit()
            else:
                key = key.lower()
        
    return key

def getTableLimits(options, tables, columns):
    limits = {}
    
    for table in tables:
        (tableName, estimatedRows) = table
        
        if estimatedRows > options.rows:
            
            limit = getTableLimit(options, tableName)

            if limit is not False:
                limits[tableName] = {'limit': limit}
                
                key = getTableSortKey(options, tableName, columns[tableName])
                
                if key:
                    limits[tableName]['sortKey'] = key
    return limits;

def getTableDumpCommand(options, limits, table):
    mainDumpCmd = "mysqldump -h" + options.hostname + " --port=" + str(options.port) + " -u" + options.username + " -p" + options.password + " " + options.dbname + " " + options.flags
    
    (tableName, estimatedRows) = table
        
    if tableName in limits:
        
        if 'sortKey' in limits[tableName]:
            dumpCmd = mainDumpCmd + addLimitedRowsByKey(tableName, limits[tableName]['sortKey'], limits[tableName]['limit'])
        else:
            dumpCmd = mainDumpCmd + addLimitedRows(tableName, limits[tableName]['limit'])
    else:
        dumpCmd = mainDumpCmd + " " + tableName
        
    if options.file:
        dumpCmd = dumpCmd + " >> " + options.file
        
    return dumpCmd;

def main():
    options = getCommandLineOptions()
    tables = getTableMetaData(options)
    columns = getTableColumnsMetaData(options);
    limits = getTableLimits(options, tables, columns)
    
    if options.file:
        os.system("touch " + options.file);
    
    for table in tables:
        dumpCmd = getTableDumpCommand(options, limits, table)

        if options.dryRun:
            print dumpCmd
        else:
            os.system(dumpCmd)

if __name__ == '__main__':
    main()

