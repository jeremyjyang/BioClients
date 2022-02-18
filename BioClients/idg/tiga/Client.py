#!/usr/bin/env python3
"""
TIGA/TCRD db client utility 
"""
import os,sys,argparse,re,time,json,logging

from ...idg import tiga
from ...util import yaml as util_yaml
from ...util import db as util_db

#############################################################################
if __name__=='__main__':
  PARAM_FILE = os.environ['HOME']+"/.tcrd.yaml"
  epilog = "Example IDs: EFO_0004541, ENSG00000160785, ENSG00000215021"
  parser = argparse.ArgumentParser(description='TIGA/TCRD MySql client utility', epilog=epilog)
  ops = ['info',
	'listGenes',
	'listTraits',
	'getTraitAssociations',
	'getGeneAssociations',
	'getGeneTraitAssociations',
	'getGeneTraitProvenance',
	]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--igene", dest="ifilegene", help="input gene ID file")
  parser.add_argument("--itrait", dest="ifiletrait", help="input trait ID file")
  parser.add_argument("--geneIds", help="input IDs, genes (ENSG)")
  parser.add_argument("--traitIds", help="input IDs, traits (EFO)")
  parser.add_argument("--param_file", default=PARAM_FILE, help=f"default param_file: {PARAM_FILE}")
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

  geneIds=None; traitIds=None;
  if args.ifilegene:
    fin = open(args.ifilegene)
    geneIds=[]
    while True:
      line = fin.readline()
      if not line: break
      geneIds.append(line.rstrip())
    logging.info(f"Input gene IDs: {len(geneIds)}")
    fin.close()
  elif args.geneIds:
    geneIds = re.split(r'[,\s]+', args.geneIds)

  if args.ifiletrait:
    fin = open(args.ifiletrait)
    traitIds=[]
    while True:
      line = fin.readline()
      if not line: break
      traitIds.append(line.rstrip())
    logging.info(f"Input trait IDs: {len(traitIds)}")
    fin.close()
  elif args.traitIds:
    traitIds = re.split(r'[,\s]+', args.traitIds)

#  try:
#    import mysql.connector as mysql
#    dbcon = mysql.connect(host=params['DBHOST'], port=params['DBPORT'], user=params['DBUSR'], passwd=params['DBPW'], db=params['DBNAME'])
#  except Exception as e:
#    logging.error(f'{e}')
#    try:
#      import MySQLdb as mysql
#      dbcon = mysql.connect(host=params['DBHOST'], port=int(params['DBPORT']), user=params['DBUSR'], passwd=params['DBPW'], db=params['DBNAME'])
#    except Exception as e2:
#      logging.error(f'{e2}')
#      sys.exit(1)

  try:
    dbcon = util_db.MySqlConnect(dbhost=params['DBHOST'], dbport=params['DBPORT'], dbusr=params['DBUSR'], dbpw=params['DBPW'], dbname=params['DBNAME'])
  except Exception as e:
    logging.error(f"Connect failed: {e}")
    sys.exit(1)

  if args.op=='info':
    tiga.Utils.Info(dbcon, fout)

  elif args.op=='listGenes':
    tiga.Utils.ListGenes(dbcon, fout)

  elif args.op=='listTraits':
    tiga.Utils.ListTraits(dbcon, fout)

  elif args.op=='getTraitAssociations':
    tiga.Utils.GetGeneTraitAssociations(None, traitIds, dbcon, fout)

  elif args.op=='getGeneAssociations':
    tiga.Utils.GetGeneTraitAssociations(geneIds, None, dbcon, fout)

  elif args.op=='getGeneTraitAssociations':
    tiga.Utils.GetGeneTraitAssociations(geneIds, traitIds, dbcon, fout)

  elif args.op=='getGeneTraitProvenance':
    tiga.Utils.GetGeneTraitProvenance(geneIds, traitIds, dbcon, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")
    parser.print_help()
