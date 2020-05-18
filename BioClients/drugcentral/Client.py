#!/usr/bin/env python3
"""
DrugCentral PostgreSql db client.
"""
import os,sys,argparse,re,time,yaml,logging

from .. import drugcentral

#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description="DrugCentral PostgreSql client utility", epilog="Search via --ids as regular expressions, e.g.  \"^Alzheimer\"")
  ops = [
	"describe",
	"counts",
	"version",
	"get_structure",
	"get_structure_by_synonym",
	"get_structure_by_indication",
	"get_structure_ids",
	"get_structure_products",
	"get_product",
	"get_product_structures",
	"get_indication_structures",
	"list_products",
	"list_structures",
	"list_structures2smiles",
	"list_structures2molfile",
	"list_active_ingredients",
	"list_indications",
	"search_indications",
	"search_products"
	]
  parser.add_argument("op", choices=ops, help="operation")
  parser.add_argument("--i", dest="ifile", help="input ID file")
  parser.add_argument("--ids", help="input IDs (comma-separated)")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--dbhost")
  parser.add_argument("--dbport")
  parser.add_argument("--dbname")
  parser.add_argument("--dbusr")
  parser.add_argument("--dbpw")
  parser.add_argument("--param_file", default=os.environ['HOME']+"/.drugcentral.yaml")
  parser.add_argument("--dbschema", default="public")
  parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))


  params={};
  with open(args.param_file, 'r') as fh:
    for param in yaml.load_all(fh, Loader=yaml.BaseLoader):
      for k,v in param.items():
        params[k] = v
  if args.dbhost: params['DBHOST'] = args.dbhost 
  if args.dbport: params['DBPORT'] = args.dbport 
  if args.dbname: params['DBNAME'] = args.dbname 
  if args.dbusr: params['DBUSR'] = args.dbusr 
  if args.dbpw: params['DBPW'] = args.dbpw 

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
    dbcon = drugcentral.Utils.Connect(params['DBHOST'], params['DBPORT'], params['DBNAME'], params['DBUSR'], params['DBPW'])
  except Exception as e:
    logging.error("Connect failed.")
    parser.error("{0}".format(str(e)))

  if args.op=='describe':
    drugcentral.Utils.Describe(dbcon, args.dbschema, fout)

  elif args.op=='counts':
    drugcentral.Utils.Counts(dbcon, args.dbschema, fout)

  elif args.op=='version':
    drugcentral.Utils.Version(dbcon, args.dbschema, fout)

  elif args.op=='list_structures':
    drugcentral.Utils.ListStructures(dbcon, args.dbschema, fout)

  elif args.op=='list_structures2smiles':
    drugcentral.Utils.ListStructures2Smiles(dbcon, args.dbschema, fout)

  elif args.op=='list_structures2molfile':
    drugcentral.Utils.ListStructures2Molfile(dbcon, args.dbschema, fout)

  elif args.op=='list_products':
    drugcentral.Utils.ListProducts(dbcon, args.dbschema, fout)

  elif args.op=='list_active_ingredients':
    drugcentral.Utils.ListActiveIngredients(dbcon, args.dbschema, fout)

  elif args.op=='list_indications':
    drugcentral.Utils.ListIndications(dbcon, fout)

  elif args.op=='get_structure':
    drugcentral.Utils.GetStructure(dbcon, ids, fout)

  elif args.op=='get_structure_by_synonym':
    drugcentral.Utils.GetStructureBySynonym(dbcon, ids, fout)

  elif args.op=='get_structure_ids':
    drugcentral.Utils.GetStructureIds(dbcon, ids, fout)

  elif args.op=='get_structure_products':
    drugcentral.Utils.GetStructureProducts(dbcon, ids, fout)

  elif args.op=='get_product_structures':
    drugcentral.Utils.GetProductStructures(dbcon, ids, fout)

  elif args.op=='search_products':
    drugcentral.Utils.SearchProducts(dbcon, ids, fout)

  elif args.op=='search_indications':
    drugcentral.Utils.SearchIndications(dbcon, ids, fout)

  elif args.op=='get_indication_structures':
    drugcentral.Utils.GetIndicationStructures(dbcon, ids, fout)

  else:
    parser.error("Invalid operation: {0}".format(args.op))

  dbcon.close()
