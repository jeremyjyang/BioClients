#!/usr/bin/env python3
"""
CFChemDb PostgreSql db client.
"""
import os,sys,argparse,re,time,logging

from ...cfde import cfchemdb
from ...util import yaml as util_yaml
from ...util import db as util_db

#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description="CFChemDb PostgreSql client utility", epilog="")
  ops = [
	"list_tables",
	"list_columns",
	"list_tables_rowCounts",
	"version",
	"get_structure",
	"get_structure_by_smiles",
	"list_structures",
	"list_structures2smiles",
	"meta_listdbs"
	]
  parser.add_argument("op", choices=ops, help="OPERATION (select one)")
  parser.add_argument("--i", dest="ifile", help="input ID file")
  parser.add_argument("--ids", help="input IDs (comma-separated)")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--dbhost")
  parser.add_argument("--dbport")
  parser.add_argument("--dbname")
  parser.add_argument("--dbusr")
  parser.add_argument("--dbpw")
  parser.add_argument("--param_file", default=os.environ['HOME']+"/.cfchemdb.yaml")
  parser.add_argument("--dbschema", default="public")
  parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0)
  parser.add_argument("-q", "--quiet", action="store_true", help="Suppress progress notification.")
  args = parser.parse_args()

  # logging.PROGRESS = 15 (custom)
  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>0 else logging.ERROR if args.quiet else 15))

  if os.path.isfile(args.param_file):
    params = util_yaml.ReadParamFile(args.param_file)
  if args.dbhost: params['DBHOST'] = args.dbhost 
  if args.dbport: params['DBPORT'] = args.dbport 
  if args.dbname: params['DBNAME'] = args.dbname 
  if args.dbusr: params['DBUSR'] = args.dbusr 
  if args.dbpw: params['DBPW'] = args.dbpw 

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  t0 = time.time()

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
    dbcon = util_db.PostgreSqlConnect(dbhost=params['DBHOST'], dbport=params['DBPORT'], dbusr=params['DBUSR'], dbpw=params['DBPW'], dbname=params['DBNAME'])
  except Exception as e:
    logging.error(f"Connect failed: {e}")
    sys.exit(1)

  if args.op=='list_tables':
    cfchemdb.ListTables(dbcon, args.dbschema, fout)

  elif args.op=='list_tables_rowCounts':
    cfchemdb.ListTablesRowCounts(dbcon, args.dbschema, fout)

  elif args.op=='list_columns':
    cfchemdb.ListColumns(dbcon, args.dbschema, fout)

  elif args.op=='version':
    cfchemdb.Version(dbcon, args.dbschema, fout)

  elif args.op=='list_structures':
    cfchemdb.ListStructures(dbcon, args.dbschema, fout)

  elif args.op=='list_structures2smiles':
    cfchemdb.ListStructures2Smiles(dbcon, args.dbschema, fout)

  elif args.op=='get_structure':
    cfchemdb.GetStructure(dbcon, ids, fout)

  elif args.op=='get_structure_by_smiles':
    cfchemdb.GetStructureBySmiles(dbcon, ids, fout)

  elif args.op=='meta_listdbs':
    cfchemdb.MetaListdbs(dbcon, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  dbcon.close()
  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))}")

