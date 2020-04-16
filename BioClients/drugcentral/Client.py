#!/usr/bin/env python3
"""
DrugCentral db utility functions.
"""
import os,sys,argparse,re,time,json,logging
import psycopg2,psycopg2.extras

#############################################################################
def Connect(dbhost, dbname, dbusr, dbpw):
  dsn = ("host='%s' dbname='%s' user='%s' password='%s'"%(dbhost, dbname, dbusr, dbpw))
  dbcon = psycopg2.connect(dsn)
  dbcon.cursor_factory = psycopg2.extras.DictCursor
  return dbcon

#############################################################################
def Describe(dbcon, dbschema, fout):
  '''Return human readable text describing the schema.'''
  cur = dbcon.cursor(cursor_factory=psycopg2.extras.DictCursor)
  sql = ("select table_name from information_schema.tables where table_schema='%s'"%dbschema)
  cur.execute(sql)
  outtxt=""
  for row in cur:
    tablename=row[0]
    sql = ("select column_name,data_type from information_schema.columns where table_schema='%s' and table_name = '%s'"%(dbschema, tablename))
    cur2 = dbcon.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur2.execute(sql)
    outtxt+=("table: %s.%s\n"%(dbschema,tablename))
    for row in cur2:
      outtxt+=("\t%s\n"%str(row))
    cur2.close()
  cur.close()
  fout.write(outtxt+"\n")

#############################################################################
def Counts(dbcon, dbschema, fout):
  '''Return human readable text listing the table rowcounts.'''
  cur = dbcon.cursor()
  outtxt=""
  sql = ("select table_name from information_schema.tables where table_schema='%s' order by table_name"%dbschema)
  cur.execute(sql)
  outtxt+=("table rowcounts:\n")
  for row in cur:
    tablename = row[0]
    sql =(" select count(*) from %s.%s"%(dbschema,tablename))
    cur2 = dbcon.cursor()
    cur2.execute(sql)
    row = cur2.fetchone()
    outtxt+="%14s: %7d\n"%(tablename,row[0])
    cur2.close()
  cur.close()
  fout.write(outtxt)
  
#############################################################################
if __name__=='__main__':
  DBHOST='localhost'; DBSCHEMA='public'; DBNAME='drugcentral'; 
  DBUSR='drugman'; DBPW='dosage'; 
  parser = argparse.ArgumentParser(description='DrugCentral PostgreSql client utility')
  ops = ['describe', 'counts', 'get_drug', 'list_drugs']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="input ID file")
  parser.add_argument("--ids", help="input IDs (comma-separated)")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--dbhost", default=DBHOST)
  parser.add_argument("--dbname", default=DBNAME)
  parser.add_argument("--dbschema", default=DBSCHEMA)
  parser.add_argument("--dbusr", default=DBUSR)
  parser.add_argument("--dbpw", default=DBPW)
  parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  ids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    logging.info('Input IDs: %d'%(len(ids)))
    fin.close()
  elif args.ids:
    ids = re.split(r'[,\s]+', args.ids)

  try:
    dbcon = Connect(args.dbhost, args.dbname, args.dbusr, args.dbpw)
  except Exception as e:
    logging.error("{0}".format(str(e)))
    parser.print_help()

  if args.op=='describe':
    Describe(dbcon, args.dbschema, fout)

  elif args.op=='counts':
    Counts(dbcon, args.dbschema, fout)

  else:
    parser.error("Invalid operation: {0}".format(args.op))

  dbcon.close()
