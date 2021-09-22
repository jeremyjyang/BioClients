#!/usr/bin/env python3
"""
TIGA/TCRD db client utility 
"""
import os,sys,argparse,re,time,json,logging

from ...idg import tiga
from ...util import yaml as util_yaml

#############################################################################
if __name__=='__main__':
  PARAM_FILE = os.environ['HOME']+"/.tcrd.yaml"
  epilog = f"default param_file: {PARAM_FILE}"
  parser = argparse.ArgumentParser(description='TIGA/TCRD MySql client utility', epilog=epilog)
  ops = ['info',
	'listGenes',
	'listTraits',
	]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--i", dest="ifile", help="input target ID file")
  parser.add_argument("--ids", help="input IDs")
  parser.add_argument("--param_file", default=PARAM_FILE)
  parser.add_argument("--dbhost")
  parser.add_argument("--dbport")
  parser.add_argument("--dbusr")
  parser.add_argument("--dbpw")
  parser.add_argument("--dbname")
  parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0)
  parser.add_argument("-q", "--quiet", action="store_true", help="Suppress progress notification.")
  args = parser.parse_args()

  # logging.PROGRESS = 15 (custom)
  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>0 else logging.ERROR if args.quiet else 15))

  params = util_yaml.ReadParamFile(args.param_file) if os.path.isfile(args.param_file) else {}
  if args.dbhost: params['DBHOST'] = args.dbhost 
  if args.dbport: params['DBPORT'] = args.dbport 
  if args.dbusr: params['DBUSR'] = args.dbusr 
  if args.dbpw: params['DBPW'] = args.dbpw
  if args.dbname: params['DBNAME'] = args.dbname 

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
    import mysql.connector as mysql
    dbcon = mysql.connect(host=params['DBHOST'], port=params['DBPORT'], user=params['DBUSR'], passwd=params['DBPW'], db=params['DBNAME'])
  except Exception as e:
    logging.error(f'{e}')
    try:
      import MySQLdb as mysql
      dbcon = mysql.connect(host=params['DBHOST'], port=int(params['DBPORT']), user=params['DBUSR'], passwd=params['DBPW'], db=params['DBNAME'])
    except Exception as e2:
      logging.error(f'{e2}')
      sys.exit(1)

  if args.op=='info':
    tiga.Utils.Info(dbcon, fout)

  elif args.op=='listGenes':
    tiga.Utils.ListGenes(dbcon, fout)

  elif args.op=='listTraits':
    tiga.Utils.ListTraits(dbcon, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")
    parser.print_help()
