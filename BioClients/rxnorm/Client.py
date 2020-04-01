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

from ..util import rest_utils

#
API_HOST='rxnav.nlm.nih.gov'
API_BASE_PATH='/REST'

NDFRT_TYPES=('DISEASE','INGREDIENT','MOA','PE','PK') ## NDFRT drug class types

##############################################################################
if __name__=='__main__':
  epilog='''\
get_spellingsuggestions requires --name.
name2rxcuis requires --name.
get_class_members requires --class_id and --rel_src.
Example RXCUIs: 131725, 213269.
Example names: "prozac", "tamiflu".
'''
  parser = argparse.ArgumentParser(description='RxNorm API client utility', epilog=epilog)
  ops = ["version",
	"list_sourcetypes", "list_relatypes", "list_termtypes", "list_propnames", "list_propcategories", "list_idtypes",
	"list_class_types", "list_classes_atc", "list_classes_mesh",
	"get_rxcui", "get_drug_by_name",
	"get_status", "get_rxcui_properties", "get_ndcs", "get_allrelated",
	"get_classes_atc", "get_classes_mesh", "get_classes_ndfrt",
	"get_class_members",
	"get_spellingsuggestions", "name2rxcuis", "rawquery"]
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="external drug IDs or RXCUIs")
  parser.add_argument("--ids", help="drug IDs or RXCUIs (comma-separated)")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--name", help="drug name (e.g. Minoxidil)")
  parser.add_argument("--idtype", help="drug ID type")
  parser.add_argument("--rel_src", help="relationship source")
  parser.add_argument("--class_id", help="drug class ID")
  parser.add_argument("--atc", help="ATC drug classes")
  parser.add_argument("--mesh", help="MeSH pharmacologic actions")
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

  API_BASE_URL='https://'+args.api_host+args.api_base_path

  t0=time.time()
  
  ids = re.split(r'[,\s]+', args.ids.strip()) if args.ids else []

  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    logging.info('input IDs: %d'%(len(ids)))
    fin.close()

  if args.op == 'version':
    rval = rest_utils.GetURL(API_BASE_URL+'/version.json', parse_json=True)
    print(rval['version'])

  elif args.op == 'get_rxcui':
    if not (args.ids and args.idtype): parser.error('%s requires --ids and --idtype'%args.op)
    fout.write('%s\trxcui\n'%(args.idtype))
    for id_this in ids:
      rval = rest_utils.GetURL(API_BASE_URL+'/rxcui.json?idtype=%s&id=%s'%(args.idtype, id_this), parse_json=True)
      for rxcui in rval['idGroup']['rxnormId']:
        fout.write('%s\t%s\n'%(id_this, rxcui))

  elif args.op == 'get_drug_by_name':
    if not args.name: parser.error('%s requires --name'%args.op)
    rval = rest_utils.GetURL(API_BASE_URL+'/drugs.json?name=%s'%urllib.parse.quote(args.name, ''), parse_json=True)
    print(json.dumps(rval, indent=4))

  elif args.op == 'list_idtypes':
    rval = rest_utils.GetURL(API_BASE_URL+'/idtypes.json', parse_json=True)
    for idtype in rval['idTypeList']['idName']:
      fout.write('%s\n'%idtype)

  elif args.op == 'list_sourcetypes':
    rval = rest_utils.GetURL(API_BASE_URL+'/sourcetypes.json', parse_json=True)
    for sourcetype in rval['sourceTypeList']['sourceName']:
      fout.write('%s\n'%sourcetype)

  elif args.op == 'list_relatypes':
    rval = rest_utils.GetURL(API_BASE_URL+'/relatypes.json', parse_json=True)
    for relatype in rval['relationTypeList']['relationType']:
      fout.write('%s\n'%relatype)

  elif args.op == 'list_termtypes':
    rval = rest_utils.GetURL(API_BASE_URL+'/termtypes.json', parse_json=True)
    for termtype in rval['termTypeList']['termType']:
      fout.write('%s\n'%termtype)

  elif args.op == 'list_propnames':
    rval = rest_utils.GetURL(API_BASE_URL+'/propnames.json', parse_json=True)
    for propname in rval['propNameList']['propName']:
      fout.write('%s\n'%propname)

  elif args.op == 'list_propcategories':
    rval = rest_utils.GetURL(API_BASE_URL+'/propCategories.json', parse_json=True)
    for propcat in rval['propCategoryList']['propCategory']:
      fout.write('%s\n'%propcat)

  elif args.op == 'list_class_types':
    rval = rest_utils.GetURL(API_BASE_URL+'/rxclass/classTypes.json', parse_json=True)
    logging.debug(json.dumps(rval, indent=4))
    for classtype in rval['classTypeList']['classTypeName']:
      fout.write('%s\n'%classtype)

  elif args.op == 'list_classes_atc':
    rval = rest_utils.GetURL(API_BASE_URL+'/rxclass/allClasses.json?classTypes=ATC1-4', parse_json=True)
    print(json.dumps(rval, indent=4))

  elif args.op == 'list_classes_mesh':
    rval = rest_utils.GetURL(API_BASE_URL+'/rxclass/allClasses.json?classTypes=MESHPA', parse_json=True)
    print(json.dumps(rval, indent=4))

  elif args.op == 'get_status':
    if not ids: parser.error('%s requires RXCUIs via --i or --ids'%args.op)
    for rxcui in ids:
      rval = rest_utils.GetURL(API_BASE_URL+'/rxcui/%s/status.json'%rxcui,parse_json=True)
      print(json.dumps(rval, indent=4))

  elif args.op == 'get_rxcui_properties':
    if not ids: parser.error('%s requires RXCUIs via --i or --ids'%args.op)
    for rxcui in ids:
      rval = rest_utils.GetURL(API_BASE_URL+'/rxcui/%s/properties.json'%rxcui,parse_json=True)
      print(json.dumps(rval, indent=4))

  elif args.op == 'get_ndcs':
    if not ids: parser.error('%s requires RXCUIs via --i or --ids'%args.op)
    fout.write('rxcui\tndc\n')
    for rxcui in ids:
      rval = rest_utils.GetURL(API_BASE_URL+'/rxcui/%s/ndcs.json'%rxcui,parse_json=True)
      for ndc in rval['ndcGroup']['ndcList']['ndc']:
        fout.write('%s\t%s\n'%(rxcui, ndc))

  elif args.op == 'get_allrelated':
    if not ids: parser.error('%s requires RXCUIs via --i or --ids'%args.op)
    for rxcui in ids:
      rval = rest_utils.GetURL(API_BASE_URL+'/rxcui/%s/allrelated.json'%rxcui,parse_json=True)
      print(json.dumps(rval, indent=4))

  elif args.op == 'get_class_members':
    if not args.class_id: parser.error('%s requires --class_id'%args.op)
    if not args.rel_src: parser.error('%s requires --rel_src'%args.op)
    url = (API_BASE_URL+'/rxclass/%s/classMembers.json?classId=%s&relaSource=%s'%(args.class_id,args.rel_src))
    rval = rest_utils.GetURL(url, parse_json=True)
    print(json.dumps(rval, indent=4))

  elif args.op == 'get_spellingsuggestions':
    if not args.name: parser.error('ERROR: requires --name')
    rval = rest_utils.GetURL(API_BASE_URL+'/spellingsuggestions.json?name=%s'%urllib.parse.quote(args.name, ''), parse_json=True)
    print(json.dumps(rval, indent=4))

  elif args.op == 'name2rxcuis':
    if not args.name: parser.error('ERROR: requires --name')
    rval = rest_utils.GetURL(API_BASE_URL+'/rxcui.json?name=%s'%urllib.parse.quote(args.name, ''), parse_json=True)
    print(json.dumps(rval, indent=4))

  elif args.op == 'rawquery':
    rval = rest_utils.GetURL(API_BASE_URL+rawquery, parse_json=True)
    print(json.dumps(rval, indent=4))

  else:
    parser.error("No operation specified.")

  logging.info(('Elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))
