#!/usr/bin/env python3
"""
DrugCentral PostgreSql db client.
"""
import os,sys,argparse,re,time,logging

from .. import drugcentral
from ..util import yaml as util_yaml
from ..util import db as util_db

#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description="DrugCentral PostgreSql client utility", epilog="Example struct_id: 2561 (Tamoxifen); search via --ids as regular expressions, e.g.  \"^Alzheimer\"")
  ops = [
	"list_tables",
	"list_columns",
	"list_tables_rowCounts",
	"version",
	"get_structure",
	"get_structure_by_synonym",
	"get_structure_by_xref",
	"get_structure_xrefs",
	"get_structure_products",
	"get_structure_orangebook_products",
	"get_structure_atcs",
	"get_structure_synonyms",
	"get_structure_targets",
	"get_product",
	"get_product_structures",
	"get_indication_structures",
	"get_drugpage",
	"get_drugsummary",
	"list_products",
	"list_structures",
	"list_structures2smiles",
	"list_structures2molfile",
	"list_structures2pubchem",
	"list_structures2chembl",
	"list_synonyms",
	"list_active_ingredients",
	"list_indications",
	"list_indication_targets",
	"list_ddis",
	"list_atcs",
	"list_xrefs",
	"list_xref_types",
	"search_indications",
	"search_products",
	"meta_listdbs"
	]
  parser.add_argument("op", choices=ops, help="OPERATION (select one)")
  parser.add_argument("--i", dest="ifile", help="input ID file")
  parser.add_argument("--ids", help="input IDs (comma-separated)")
  parser.add_argument("--xref_type", help="xref ID type")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--dbhost")
  parser.add_argument("--dbport")
  parser.add_argument("--dbname")
  parser.add_argument("--dbusr")
  parser.add_argument("--dbpw")
  parser.add_argument("--param_file", default=os.environ['HOME']+"/.drugcentral.yaml")
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
    logging.info('Input IDs: %d'%(len(ids)))
    fin.close()
  elif args.ids:
    ids = re.split(r'[,\s]+', args.ids)

  try:
    #dbcon = drugcentral.Connect(params['DBHOST'], params['DBPORT'], params['DBNAME'], params['DBUSR'], params['DBPW'])
    dbcon = util_db.PostgreSqlConnect(dbhost=params['DBHOST'], dbport=params['DBPORT'], dbusr=params['DBUSR'], dbpw=params['DBPW'], dbname=params['DBNAME'])
  except Exception as e:
    logging.error(f"Connect failed: {e}")
    sys.exit(1)

  if args.op=='list_tables':
    drugcentral.ListTables(dbcon, args.dbschema, fout)

  elif args.op=='list_tables_rowCounts':
    drugcentral.ListTablesRowCounts(dbcon, args.dbschema, fout)

  elif args.op=='list_columns':
    drugcentral.ListColumns(dbcon, args.dbschema, fout)

  elif args.op=='version':
    drugcentral.Version(dbcon, args.dbschema, fout)

  elif args.op=='list_structures':
    drugcentral.ListStructures(dbcon, args.dbschema, fout)

  elif args.op=='list_structures2smiles':
    drugcentral.ListStructures2Smiles(dbcon, args.dbschema, fout)

  elif args.op=='list_structures2molfile':
    drugcentral.ListStructures2Molfile(dbcon, args.dbschema, fout)

  elif args.op=='list_structures2pubchem':
    drugcentral.ListStructures2Pubchem(dbcon, args.dbschema, fout)

  elif args.op=='list_structures2chembl':
    drugcentral.ListStructures2Chembl(dbcon, args.dbschema, fout)

  elif args.op=='list_products':
    drugcentral.ListProducts(dbcon, args.dbschema, fout)

  elif args.op=='list_active_ingredients':
    drugcentral.ListActiveIngredients(dbcon, args.dbschema, fout)

  elif args.op=='list_indications':
    drugcentral.ListIndications(dbcon, fout)

  elif args.op=='list_indication_targets':
    drugcentral.ListIndicationTargets(dbcon, fout)

  elif args.op=='list_ddis':
    drugcentral.ListDrugdruginteractions(dbcon, fout)

  elif args.op=='list_atcs':
    drugcentral.ListAtcs(dbcon, fout)

  elif args.op=='list_synonyms':
    drugcentral.ListSynonyms(dbcon, fout)

  elif args.op=='list_xref_types':
    drugcentral.ListXrefTypes(dbcon, fout)

  elif args.op=='list_xrefs':
    drugcentral.ListXrefs(dbcon, fout)

  elif args.op=='get_structure':
    drugcentral.GetStructure(dbcon, ids, fout)

  elif args.op=='get_structure_by_synonym':
    drugcentral.GetStructureBySynonym(dbcon, ids, fout)

  elif args.op=="get_structure_by_xref":
    drugcentral.GetStructureByXref(dbcon, ids, args.xref_type, fout)

  elif args.op=='get_structure_xrefs':
    drugcentral.GetStructureXrefs(dbcon, ids, fout)

  elif args.op=='get_structure_products':
    drugcentral.GetStructureProducts(dbcon, ids, fout)

  elif args.op=='get_structure_orangebook_products':
    drugcentral.GetStructureOBProducts(dbcon, ids, fout)

  elif args.op=='get_structure_atcs':
    drugcentral.GetStructureAtcs(dbcon, ids, fout)

  elif args.op=='get_structure_synonyms':
    drugcentral.GetStructureSynonyms(dbcon, ids, fout)

  elif args.op=='get_structure_targets':
    drugcentral.GetStructureTargets(dbcon, ids, fout)

  elif args.op=='get_product_structures':
    drugcentral.GetProductStructures(dbcon, ids, fout)

  elif args.op=='search_products':
    drugcentral.SearchProducts(dbcon, ids, fout)

  elif args.op=='search_indications':
    drugcentral.SearchIndications(dbcon, ids, fout)

  elif args.op=='get_indication_structures':
    drugcentral.GetIndicationStructures(dbcon, ids, fout)

  elif args.op=='meta_listdbs':
    drugcentral.MetaListdbs(dbcon, fout)

  elif args.op=='get_drugpage':
    drugcentral.GetDrugPage(dbcon, ids[0], fout)

  elif args.op=='get_drugsummary':
    drugcentral.GetDrugSummary(dbcon, ids, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  dbcon.close()
  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))}")

