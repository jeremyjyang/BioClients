#!/usr/bin/env python3
"""
https://mor.nlm.nih.gov/download/rxnav/RxNormAPIs.html
https://rxnav.nlm.nih.gov/RxNormAPIs.html
https://rxnav.nlm.nih.gov/RxNormAPIREST.html
https://www.nlm.nih.gov/research/umls/rxnorm/docs/

 TERM TYPES
 TTY	Name
 IN	Ingredient
 PIN	Precise Ingredient
 MIN	Multiple Ingredients
 SCDC	Semantic Clinical Drug Component
 SCDF	Semantic Clinical Drug Form
 SCDG	Semantic Clinical Dose Form Group
 SCD	Semantic Clinical Drug
 GPCK	Generic Pack
 BN	Brand Name
 SBDC	Semantic Branded Drug Component
 SBDF	Semantic Branded Drug Form
 SBDG	Semantic Branded Dose Form Group
 SBD	Semantic Branded Drug
 BPCK	Brand Name Pack
 PSN	Prescribable Name
 SY	Synonym
 TMSY	Tall Man Lettering Synonym
 DF	Dose Form
 ET	Dose Form Entry Term
 DFG	Dose Form Group
"""
###
import sys,os,re,argparse,time,logging

from .. import rxnorm
from ..util import rest
#
##############################################################################
if __name__=='__main__':
  epilog='''\
get_id2rxcui requires --idtype.
get_spellingsuggestions requires --name.
get_class_members requires --class_id and --rel_src.
Example names: "prozac", "tamiflu", "metformin".
Example RXCUIs: 131725, 213269.
Example IDs: C2709711 (UMLSCUI).
Note that RxCUIs generally refer to drug products. Term Types
"Ingredient" (IN) and "Precise Ingredient" (PIN) generally refer
to chemical compounds.
'''
  parser = argparse.ArgumentParser(description='RxNorm API client utility', epilog=epilog)
  ops = [
	"version", "rawquery",
	"list_sourcetypes", "list_relationtypes", "list_termtypes",
	"list_propnames", "list_propcategories", "list_idtypes",
	"list_class_types", "list_classes",
	"get_name", "get_name2rxcui",
	"get_id2rxcui",
	"get_rxcui_status", "get_rxcui_properties", "get_rxcui_allproperties",
	"get_rxcui_ndcs", "get_rxcui_allrelated",
	"get_rxcui_classes",
	"get_class_members", "get_spellingsuggestions"
	]
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="external drug IDs or RXCUIs")
  parser.add_argument("--ids", help="drug names, IDs, or RXCUIs (comma-separated)")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--idtype", help="drug ID type")
  parser.add_argument("--rel_src", help="relationship source")
  parser.add_argument("--class_id", help="drug class ID")
  parser.add_argument("--class_types", help="drug class (e.g. 'MESHPA', 'MESHPA,ATC1-4')")
  parser.add_argument("--atc", help="ATC drug classes")
  parser.add_argument("--meshpa", help="MeSH pharmacologic actions (classtype 'MESHPA'")
  parser.add_argument("--ndfrt_type", choices=rxnorm.NDFRT_TYPES, help="NDFRT drug class types")
  parser.add_argument("--tty", help="term type")
  parser.add_argument("--api_host", default=rxnorm.API_HOST)
  parser.add_argument("--api_base_path", default=rxnorm.API_BASE_PATH)
  parser.add_argument("--api_key")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  BASE_URL='https://'+args.api_host+args.api_base_path

  t0=time.time()

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout
  
  ids=[];
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    logging.info(f'input IDs: {len(ids)}')
    fin.close()
  elif args.ids:
    ids = re.split(r'[,\s]+', args.ids.strip())
  else:
    ids=[]

  if re.match(r'get_', args.op) and not ids:
    parser.error(f'{args.op} requires --i or --ids')

  if args.op == 'version':
    rval = rest.GetURL(BASE_URL+'/version.json', parse_json=True)
    print(rval['version'])

  elif args.op == 'list_idtypes':
    rxnorm.List_IDTypes(BASE_URL, fout)

  elif args.op == 'list_sourcetypes':
    rxnorm.List_SourceTypes(BASE_URL, fout)

  elif args.op == 'list_relationtypes':
    rxnorm.List_RelationTypes(BASE_URL, fout)

  elif args.op == 'list_termtypes':
    rxnorm.List_TermTypes(BASE_URL, fout)

  elif args.op == 'list_propnames':
    rxnorm.List_PropNames(BASE_URL, fout)

  elif args.op == 'list_propcategories':
    rxnorm.List_PropCategories(BASE_URL, fout)

  elif args.op == 'list_class_types':
    rxnorm.List_ClassTypes(BASE_URL, fout)

  elif args.op == 'list_classes':
    class_types = re.split(r'[,\s]+', args.class_types.strip()) if args.class_types else None
    rxnorm.List_Classes(class_types, BASE_URL, fout)

  elif args.op == 'get_id2rxcui':
    if not args.idtype: parser.error(f'{args.op} requires --idtype')
    rxnorm.Get_ID2RxCUI(ids, args.idtype, BASE_URL, fout)

  elif args.op == 'get_name':
    rxnorm.Get_Name(ids, BASE_URL, fout)

  elif args.op == 'get_name2rxcui':
    rxnorm.Get_Name2RxCUI(ids, BASE_URL, fout)

  elif args.op == 'get_rxcui_status':
    rxnorm.Get_RxCUI_Status(ids, BASE_URL, fout)

  elif args.op == 'get_rxcui_properties':
    rxnorm.Get_RxCUI_Properties(ids, BASE_URL, fout)

  elif args.op == 'get_rxcui_allproperties':
    rxnorm.Get_RxCUI_AllProperties(ids, BASE_URL, fout)

  elif args.op == 'get_rxcui_ndcs':
    rxnorm.Get_RxCUI_NDCs(ids, BASE_URL, fout)

  elif args.op == 'get_rxcui_allrelated':
    rxnorm.Get_RxCUI_AllRelated(ids, BASE_URL, fout)

  elif args.op == "get_rxcui_classes":
    rxnorm.Get_RxCUI_Classes(ids, BASE_URL, fout)

  elif args.op == 'get_class_members':
    rxnorm.Get_Class_Members(ids, BASE_URL, fout)

  elif args.op == 'get_spellingsuggestions':
    rxnorm.Get_SpellingSuggestions(ids, BASE_URL, fout)

  elif args.op == 'rawquery':
    rxnorm.RawQuery(args.rawquery, BASE_URL, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))}")
