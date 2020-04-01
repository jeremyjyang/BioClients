#!/usr/bin/env python3
"""
https://mor.nlm.nih.gov/download/rxnav/RxNormAPIs.html
"""
#############################################################################
### https://rxnav.nlm.nih.gov/RxNormAPIs.html
### https://rxnav.nlm.nih.gov/RxNormAPIREST.html
#############################################################################
### https://rxnav.nlm.nih.gov/REST/version.json
### https://rxnav.nlm.nih.gov/REST/drugs.json?name=prozac
### https://rxnav.nlm.nih.gov/REST/rxcui/131725/properties.json
### https://rxnav.nlm.nih.gov/REST/rxcui.json?idtype=NDC&id=0781-1506-10
### https://rxnav.nlm.nih.gov/REST/rxcui/213269/ndcs.json
#############################################################################
### https://rxnav.nlm.nih.gov/RxClassAPIs.html
#############################################################################
### https://rxnav.nlm.nih.gov/REST/rxclass/classMembers?classId=A12CA&relaSource=ATC
#############################################################################
### data["allRelatedGroup"]["conceptGroup"] (list of concept)
### concept["tty"]
### concept["conceptProperties"] (list of conceptproperty)
### conceptproperty["rxcui"]
### conceptproperty["name"]
### conceptproperty["synonym"]
### conceptproperty["language"]
### "tty": "BN" ?
### "tty": "IN" ?
### "tty": "PIN" ?
#############################################################################
import sys,os,re,argparse,time,logging,urllib,json

#from ..util import rest_utils

from .. import rxnorm

#
API_HOST='rxnav.nlm.nih.gov'
API_BASE_PATH='/REST'

NDFRT_TYPES=('DISEASE','INGREDIENT','MOA','PE','PK') ## NDFRT drug class types

##############################################################################
if __name__=='__main__':
  ATC_LEVELS="1-4"
  epilog='''\
get_spellingsuggestions requires --name.
get_rxcui_by_name requires --names.
get_class_members requires --class_id and --rel_src.
Example RXCUIs: 131725, 213269.
Example names: "prozac", "tamiflu".
'''
  parser = argparse.ArgumentParser(description='RxNorm API client utility', epilog=epilog)
  ops = [
	"version", "rawquery",
	"list_sourcetypes", "list_relationtypes", "list_termtypes",
	"list_propnames", "list_propcategories", "list_idtypes",
	"list_class_types", "list_classes_atc", "list_classes_mesh",
	"get_drug_by_name", "get_rxcui_by_name",
	"get_rxcui",
	"get_status", "get_rxcui_properties", "get_ndcs", "get_allrelated",
	"get_classes_atc", "get_classes_mesh", "get_classes_ndfrt",
	"get_class_members", "get_spellingsuggestions"
	]
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="external drug IDs or RXCUIs")
  parser.add_argument("--ids", help="drug IDs or RXCUIs (comma-separated)")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--names", help="drug name (e.g. Minoxidil) (comma-separated)")
  parser.add_argument("--idtype", help="drug ID type")
  parser.add_argument("--rel_src", help="relationship source")
  parser.add_argument("--class_id", help="drug class ID")
  parser.add_argument("--atc", help="ATC drug classes")
  parser.add_argument("--atc_levels", default=ATC_LEVELS, help="ATC levels, currently only supporting '1-4'")
  parser.add_argument("--meshpa", help="MeSH pharmacologic actions (classtype 'MESHPA'")
  parser.add_argument("--ndfrt_type", choices=NDFRT_TYPES, help="NDFRT drug class types")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("--api_key")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  if args.ofile:
    fout = open(args.ofile, "w+")
  else:
    fout = sys.stdout

  BASE_URL='https://'+args.api_host+args.api_base_path

  t0=time.time()
  
  ids = re.split(r'[,\s]+', args.ids.strip()) if args.ids else []
  names = re.split(r'[,\s]+', args.names.strip()) if args.names else []

  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    logging.info('input IDs: %d'%(len(ids)))
    fin.close()

  if args.op == 'version':
    rval = rest_utils.GetURL(BASE_URL+'/version.json', parse_json=True)
    print(rval['version'])

  elif args.op == 'list_idtypes':
    rxnorm.Utils.List_IDTypes(BASE_URL, fout)

  elif args.op == 'list_sourcetypes':
    rxnorm.Utils.List_SourceTypes(BASE_URL, fout)

  elif args.op == 'list_relationtypes':
    rxnorm.Utils.List_RelationTypes(BASE_URL, fout)

  elif args.op == 'list_termtypes':
    rxnorm.Utils.List_TermTypes(BASE_URL, fout)

  elif args.op == 'list_propnames':
    rxnorm.Utils.List_PropNames(BASE_URL, fout)

  elif args.op == 'list_propcategories':
    rxnorm.Utils.List_PropCategories(BASE_URL, fout)

  elif args.op == 'list_class_types':
    rxnorm.Utils.List_ClassTypes(BASE_URL, fout)

  elif args.op == 'list_classes_atc':
    rxnorm.Utils.List_Classes_ATC(BASE_URL, args.atc_levels, fout)

  elif args.op == 'list_classes_mesh':
    rxnorm.Utils.List_Classes_MESH(BASE_URL, fout)

  elif args.op == 'get_status':
    rxnorm.Utils.Get_Status(BASE_URL, ids, fout)

  elif args.op == 'get_rxcui':
    if not (args.ids and args.idtype): parser.error('%s requires --ids and --idtype'%args.op)
    rxnorm.Utils.Get_RxCUI(BASE_URL, ids, args.idtype, fout)

  elif args.op == 'get_rxcui_properties':
    rxnorm.Utils.Get_RxCUI_Properties(BASE_URL, ids, fout)

  elif args.op == 'get_ndcs':
    rxnorm.Utils.Get_NDCs(BASE_URL, ids, fout)

  elif args.op == 'get_allrelated':
    rxnorm.Utils.Get_AllRelated(BASE_URL, ids, fout)

  elif args.op == 'get_class_members':
    rxnorm.Utils.Get_Class_Members(BASE_URL, ids, fout)

  elif args.op == 'get_spellingsuggestions':
    rxnorm.Utils.Get_SpellingSuggestions(BASE_URL, ids, fout)

  elif args.op == 'get_drug_by_name':
    if not args.names: parser.error('%s requires --names'%args.op)
    rxnorm.Utils.Get_Drug_By_Name(BASE_URL, names, fout)

  elif args.op == 'get_rxcui_by_name':
    if not args.names: parser.error('%s requires --names'%args.op)
    rxnorm.Utils.Get_RxCUI_By_Name(BASE_URL, names, fout)

  elif args.op == 'rawquery':
    rxnorm.Utils.RawQuery(BASE_URL, args.rawquery, fout)

  else:
    parser.error("Invalid operation: %s"%args.op)

  logging.info(('Elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))
