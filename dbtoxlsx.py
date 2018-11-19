import sqlite3
from xlsxwriter.workbook import Workbook
workbook = Workbook('database.xlsx')
worksheet = workbook.add_worksheet()

conn=sqlite3.connect('database.db')
c=conn.cursor()
c.execute("select * from datas")
mysel=c.execute("select * from datas")
for i, row in enumerate(mysel):
    for j, value in enumerate(row):
        worksheet.write(i, j, value)
workbook.close()
