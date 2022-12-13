#!/usr/bin/env python3
"""
TCRD db client utility (see also Pharos GraphQL API)
"""
import os,sys,argparse,re,time,json,logging

from ...idg import tcrd
from ...util import yaml as util_yaml
from ...util import db as util_db

#############################################################################
if __name__=='__main__':
  PARAM_FILE = os.environ['HOME']+"/.tcrd.yaml"
  idtypes=['TID', 'GENEID', 'UNIPROT', 'GENESYMB', 'ENSP']
  epilog = f"default param_file: {PARAM_FILE}"
  parser = argparse.ArgumentParser(description='TCRD MySql client utility', epilog=epilog)
  ops = ['info', 'listTables', 'listColumns', 'tableRowCounts', 'tdlCounts', 
	'listTargets', 'listXrefTypes', 'listXrefs', 'listDatasets',
	'listTargetsByDTO', 'listTargetFamilies',
	'listPhenotypes', 'listPhenotypeTypes',
	'listPublications',
	'listCompounds', 'listDrugs',
	'getTargets', 'getTargetsByXref', 'getTargetPage',
	'listDiseases', 'listDiseaseTypes',
	'getDiseaseAssociations', 'getDiseaseAssociationsPage',
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
  parser.add_argument("-q", "--quiet", action="store_true", help="Suppress progress notification.")
  args = parser.parse_args()

  # logging.PROGRESS = 15 (custom)
  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>0 else logging.ERROR if args.quiet else 15))

  params = util_yaml.ReadParamFile(args.param_file) if os.path.isfile(args.param_file) else {}
  if args.dbhost is not None: params['DBHOST'] = args.dbhost 
  if args.dbport is not None: params['DBPORT'] = args.dbport 
  if args.dbusr is not None: params['DBUSR'] = args.dbusr 
  if args.dbpw is not None: params['DBPW'] = args.dbpw
  if args.dbname is not None: params['DBNAME'] = args.dbname 

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  ids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    logging.info(f"Input IDs: {len(ids)}")
    fin.close()
  elif args.ids:
    ids = re.split(r'[,\s]+', args.ids)

  try:
    dbcon = util_db.MySqlConnect(dbhost=params['DBHOST'], dbport=params['DBPORT'], dbusr=params['DBUSR'], dbpw=params['DBPW'], dbname=params['DBNAME'])
  except Exception as e:
    logging.error(f"{e}")
    dbcon = None
  if dbcon is None:
    logging.error(f"""Failed: MySqlConnect(dbhost="{params['DBHOST']}", dbport={params['DBPORT']}, dbusr="{params['DBUSR']}", dbpw="{params['DBPW']}", dbname="{params['DBNAME']}")""")
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
          parser.error(f"xreftype '{xreftype}' invalid.  Available xreftypes: {str(list(xreftypes_all))}")
    else:
      xreftypes = []
    tcrd.Utils.ListXrefs(dbcon, xreftypes, fout)

  elif args.op=='listTargetFamilies':
    tcrd.Utils.ListTargetFamilies(dbcon, fout)

  elif args.op=='listTargetsByDTO':
    tcrd.Utils.ListTargetsByDTO(dbcon, fout)

  elif args.op=='listDiseases':
    tcrd.Utils.ListDiseases(dbcon, fout)

  elif args.op=='listDiseaseTypes':
    tcrd.Utils.ListDiseaseTypes(dbcon, fout)

  elif args.op=='getDiseaseAssociations':
    if not ids:
      parser.error(f'IDs required for operation: {args.op}')
    tcrd.Utils.GetDiseaseAssociations(dbcon, ids, fout)

  elif args.op=='getDiseaseAssociationsPage':
    if not ids:
      parser.error(f'ID required for operation: {args.op}')
    tcrd.Utils.GetDiseaseAssociationsPage(dbcon, ids[0], fout)

  elif args.op=='listPhenotypes':
    tcrd.Utils.ListPhenotypes(dbcon, fout)

  elif args.op=='listPhenotypeTypes':
    tcrd.Utils.ListPhenotypeTypes(dbcon, fout)

  elif args.op=='listPublications':
    tcrd.Utils.ListPublications(dbcon, fout)

  elif args.op=='listDatasets':
    tcrd.Utils.ListDatasets(dbcon, fout)

  elif args.op=='listCompounds':
    tcrd.Utils.ListCompounds(dbcon, fout)

  elif args.op=='listDrugs':
    tcrd.Utils.ListDrugs(dbcon, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")
    parser.print_help()
