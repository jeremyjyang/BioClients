#!/usr/bin/env python3
"""
TCRD db client utility (see also Pharos GraphQL API)
"""
import os,sys,argparse,re,time,json,logging

from ...idg import tcrd
from ...util import yaml as util_yaml

#############################################################################
if __name__=='__main__':
  PARAM_FILE = os.environ['HOME']+"/.tcrd.yaml"
  idtypes=['TID', 'GENEID', 'UNIPROT', 'GENESYMB', 'ENSP']
  epilog = "default param_file: {}".format(PARAM_FILE)
  parser = argparse.ArgumentParser(description='TCRD MySql client utility', epilog=epilog)
  ops = ['info', 'listTables', 'listColumns', 'tableRowCounts', 'tdlCounts', 
	'listTargets', 'listXrefTypes', 'listXrefs', 'listDatasets',
	'listTargetFamilies',
	'getTargets', 'getTargetsByXref',
	'getTargetPage',
	'getTargetpathways']
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--i", dest="ifile", help="input target ID file")
  parser.add_argument("--ids", help="input IDs")
  parser.add_argument("--idtype", choices=idtypes, default='TID', help='target ID type')
  parser.add_argument("--xreftypes", help='Xref types, comma-separated')
  parser.add_argument("--tdls", help="TDLs, comma-separated ({})".format('|'.join(tcrd.TDLS)))
  parser.add_argument("--tfams", help="target families, comma-separated")
  parser.add_argument("--param_file", default=PARAM_FILE)
  parser.add_argument("--dbhost")
  parser.add_argument("--dbport")
  parser.add_argument("--dbusr")
  parser.add_argument("--dbpw")
  parser.add_argument("--dbname")
  parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

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

  if args.op=='listColumns':
    tcrd.Utils.ListColumns(dbcon, fout)

  elif args.op=='info':
    tcrd.Utils.Info(dbcon, fout)

  elif args.op=='tableRowCounts':
    tcrd.Utils.TableRowCounts(dbcon, fout)

  elif args.op=='tdlCounts':
    tcrd.Utils.TDLCounts(dbcon, fout)

  elif args.op=='listTables':
    tcrd.Utils.ListTables(dbcon, fout)

  elif args.op=='listTargets':
    tdls = re.split(r'\s*,\s*', args.tdls) if args.tdls else []
    tfams = re.split(r'\s*,\s*', args.tfams) if args.tfams else []
    tcrd.Utils.ListTargets(dbcon, tdls, tfams, fout)

  elif args.op=='getTargets':
    if not ids:
      parser.error(f'IDs required for operation: {args.op}')
    tcrd.Utils.GetTargets(dbcon, ids, args.idtype, fout)

  elif args.op=='getTargetPage':
    if not ids:
      parser.error(f'Target ID required for operation: {args.op}')
    tcrd.Utils.GetTargetPage(dbcon, ids[0], fout)

  elif args.op=='getTargetsByXrefs':
    if not ids:
      parser.error(f'IDs required for operation: {args.op}')
    tcrd.Utils.GetTargetsByXrefs(dbcon, ids, args.xreftypes, fout)

  elif args.op=='getTargetpathways':
    if not ids:
      parser.error(f'IDs required for operation: {args.op}')
    tids = tcrd.Utils.GetTargets(dbcon, ids, args.idtype, None)
    tcrd.Utils.GetPathways(dbcon, tids, fout)

  elif args.op=='listXrefTypes':
    tcrd.Utils.ListXrefTypes(dbcon, fout)

  elif args.op=='listXrefs':
    if args.xreftypes:
      xreftypes = re.split(r'\s*,\s*', args.xreftypes.strip())
      xreftypes_all = tcrd.Utils.ListXrefTypes(dbcon).iloc[:,0]
      for xreftype in xreftypes:
        if xreftype not in list(xreftypes_all):
          parser.error('xreftype "{}" invalid.  Available xreftypes: {}'.format(xreftype, str(list(xreftypes_all))))
    else:
      xreftypes = []
    tcrd.Utils.ListXrefs(dbcon, xreftypes, fout)

  elif args.op=='listTargetFamilies':
    tcrd.Utils.ListTargetFamilies(dbcon, fout)

  elif args.op=='listDatasets':
    tcrd.Utils.ListDatasets(dbcon, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")
    parser.print_help()
