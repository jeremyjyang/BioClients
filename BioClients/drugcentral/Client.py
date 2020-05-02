#!/usr/bin/env python3
"""
DrugCentral PostgreSql db client.
"""
import os,sys,argparse,re,time,logging

from .. import drugcentral

#############################################################################
if __name__=='__main__':
  DBHOST="localhost"; DBPORT="5432"; DBSCHEMA="public"; DBNAME="drugcentral"; 
  DBUSR="drugman"; DBPW="dosage"; 
  parser = argparse.ArgumentParser(description="DrugCentral PostgreSql client utility")
  ops = [
	"describe",
	"counts",
	"version",
	"get_structure",
	"get_structure_by_synonym",
	"get_structure_by_indication",
	"get_structure_products",
	"get_product",
	"get_product_structures",
	"get_indication_structures",
	"list_products",
	"list_structures",
	"list_active_ingredients",
	"list_indications",
	"search_indications",
	"search_products"
	]
  parser.add_argument("op", choices=ops, help="operation")
  parser.add_argument("--i", dest="ifile", help="input ID file")
  parser.add_argument("--ids", help="input IDs (comma-separated)")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--dbhost", default=DBHOST)
  parser.add_argument("--dbport", default=DBPORT)
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
    dbcon = drugcentral.Utils.Connect(args.dbhost, args.dbport, args.dbname, args.dbusr, args.dbpw)
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
