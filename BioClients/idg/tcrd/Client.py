#!/usr/bin/env python3
"""
TCRD db client utility (see also Pharos GraphQL API)
"""
import os,sys,argparse,re,time,json,logging
import mysql.connector as mysql

from ...idg import tcrd

#############################################################################
if __name__=='__main__':
  qtypes=[ 'TID', 'GENEID', 'UNIPROT', 'GENESYMB', 'NCBI_GI', 'ENSP']
  parser = argparse.ArgumentParser(description='TCRD MySql client utility')
  ops = ['info', 'listTables', 'describeTables', 'tableRowCounts', 'tdlCounts', 
	'listTargets', 'listXreftypes', 'listXrefs',
	'getTargets', 'getTargetpathways']
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--i", dest="ifile", help="input ID or query file")
  parser.add_argument("--ids", help="IDs or queries")
  parser.add_argument("--qtype", choices=qtypes, default='TID', help='ID or query type')
  parser.add_argument("--tdl", choices=tcrd.TDLS, help="Target Development Level (TDL) %s"%('|'.join(tcrd.TDLS)))
  parser.add_argument("--fam", help="target family GPCR|Kinase|IC|NR|...|Unknown")
  parser.add_argument("--param_file", default=os.environ['HOME']+"/.tcrd.yaml")
  parser.add_argument("--dbhost")
  parser.add_argument("--dbport")
  parser.add_argument("--dbusr")
  parser.add_argument("--dbpw")
  parser.add_argument("--dbname")
  parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  if os.path.isfile(args.param_file):
    params = tcrd.Utils.ReadParamFile(args.param_file)
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

  dbcon = mysql.connect(host=params['DBHOST'], port=params['DBPORT'], user=params['DBUSR'], passwd=params['DBPW'], db=params['DBNAME'])

  if args.op=='describeTables':
    tcrd.Utils.DescribeTables(dbcon, fout)

  elif args.op=='info':
    tcrd.Utils.Info(dbcon, fout)

  elif args.op=='tableRowCounts':
    tcrd.Utils.TableRowCounts(dbcon, fout)

  elif args.op=='tdlCounts':
    tcrd.Utils.TDLCounts(dbcon, fout)

  elif args.op=='listTables':
    tcrd.Utils.ListTables(dbcon, fout)

  elif args.op=='listTargets':
    tcrd.Utils.ListTargets(dbcon, args.tdl, args.fam, fout)

  elif args.op=='getTargets':
    tcrd.Utils.GetTargets(dbcon, ids, args.qtype, fout)

  elif args.op=='getTargetpathways':
    tids = tcrd.Utils.GetTargets(dbcon, ids, args.qtype, None)
    tcrd.Utils.GetPathways(dbcon, tids, fout)

  elif args.op=='listXreftypes':
    xreftypes = tcrd.Utils.ListXreftypes(dbcon)
    print(str(xreftypes))

  elif args.op=='listXrefs':
    xreftypes = tcrd.Utils.ListXreftypes(dbcon)
    if qtype not in xreftypes:
      parser.error('qtype "%s" invalid.  Available xref types: %s'%(qtype, str(xreftypes)))
    tcrd.Utils.ListXrefs(dbcon, args.qtype, fout)

  else:
    parser.print_help()
