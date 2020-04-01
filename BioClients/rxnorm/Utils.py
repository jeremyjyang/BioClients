#!/usr/bin/env python3
"""
https://mor.nlm.nih.gov/download/rxnav/RxNormAPIs.html
"""
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
###
import sys,os,re,json,logging,urllib,urllib.parse

from ..util import rest_utils

NDFRT_TYPES=('DISEASE','INGREDIENT','MOA','PE','PK') ## NDFRT drug class types

#############################################################################
def Get_RxCUI(base_url, ids, idtype, fout):
  fout.write('%s\trxcui\n'%(idtype))
  for id_this in ids:
    rval = rest_utils.GetURL(BASE_URL+'/rxcui.json?idtype=%s&id=%s'%(args.idtype, id_this), parse_json=True)
    for rxcui in rval['idGroup']['rxnormId']:
      fout.write('%s\t%s\n'%(id_this, rxcui))

#############################################################################
def Get_RxCUI_By_Name(base_url, ids, fout):
  rval = rest_utils.GetURL(base_url+'/rxcui.json?name=%s'%urllib.parse.quote(args.name, ''), parse_json=True)
  logging.debug(json.dumps(rval, indent=4))

#############################################################################
def Get_Drug_By_Name(base_url, names, fout):
  for name in names:
    rval = rest_utils.GetURL(BASE_URL+'/drugs.json?name=%s'%urllib.parse.quote(name), parse_json=True)
    logging.debug(json.dumps(rval, indent=4))

#############################################################################
def List_IDTypes(base_url, fout):
  rval = rest_utils.GetURL(BASE_URL+'/idtypes.json', parse_json=True)
  for idtype in rval['idTypeList']['idName']:
    fout.write('%s\n'%idtype)

#############################################################################
def List_SourceTypes(base_url, fout):
  rval = rest_utils.GetURL(BASE_URL+'/sourcetypes.json', parse_json=True)
  for sourcetype in rval['sourceTypeList']['sourceName']:
    fout.write('%s\n'%sourcetype)

#############################################################################
def List_RelationTypes(base_url, fout):
  rval = rest_utils.GetURL(BASE_URL+'/relatypes.json', parse_json=True)
  for relatype in rval['relationTypeList']['relationType']:
    fout.write('%s\n'%relatype)

#############################################################################
def List_TermTypes(base_url, fout):
  rval = rest_utils.GetURL(BASE_URL+'/termtypes.json', parse_json=True)
  for termtype in rval['termTypeList']['termType']:
    fout.write('%s\n'%termtype)

#############################################################################
def List_PropNames(base_url, fout):
  rval = rest_utils.GetURL(BASE_URL+'/propnames.json', parse_json=True)
  for propname in rval['propNameList']['propName']:
    fout.write('%s\n'%propname)

#############################################################################
def List_PropCategories(base_url, fout):
  rval = rest_utils.GetURL(BASE_URL+'/propCategories.json', parse_json=True)
  for propcat in rval['propCategoryList']['propCategory']:
    fout.write('%s\n'%propcat)

#############################################################################
def List_ClassTypes(base_url, fout):
  rval = rest_utils.GetURL(BASE_URL+'/rxclass/classTypes.json', parse_json=True)
  logging.debug(json.dumps(rval, indent=4))
  for classtype in rval['classTypeList']['classTypeName']:
    fout.write('%s\n'%classtype)

#############################################################################
def List_Classes_ATC(base_url, fout):
  rval = rest_utils.GetURL(BASE_URL+'/rxclass/allClasses.json?classTypes=ATC1-4', parse_json=True)
  logging.debug(json.dumps(rval, indent=4))

#############################################################################
def List_Classes_MESH(base_url, fout):
  rval = rest_utils.GetURL(BASE_URL+'/rxclass/allClasses.json?classTypes=MESHPA', parse_json=True)
  logging.debug(json.dumps(rval, indent=4))

#############################################################################
def Get_Status(base_url, ids, fout):
  for rxcui in ids:
    rval = rest_utils.GetURL(BASE_URL+'/rxcui/%s/status.json'%rxcui,parse_json=True)
    logging.debug(json.dumps(rval, indent=4))

#############################################################################
def Get_RxCUI_Properties(base_url, ids, fout):
  for rxcui in ids:
    rval = rest_utils.GetURL(BASE_URL+'/rxcui/%s/properties.json'%rxcui,parse_json=True)
    logging.debug(json.dumps(rval, indent=4))

#############################################################################
def Get_NDCs(base_url, ids, fout):
  fout.write('rxcui\tndc\n')
  for rxcui in ids:
    rval = rest_utils.GetURL(BASE_URL+'/rxcui/%s/ndcs.json'%rxcui,parse_json=True)
    for ndc in rval['ndcGroup']['ndcList']['ndc']:
      fout.write('%s\t%s\n'%(rxcui, ndc))

#############################################################################
def Get_AllRelated(base_url, ids, fout):
  for rxcui in ids:
    rval = rest_utils.GetURL(BASE_URL+'/rxcui/%s/allrelated.json'%rxcui,parse_json=True)
    logging.debug(json.dumps(rval, indent=4))

#############################################################################
def Get_Class_Members(base_url, class_id, rel_src, fout):
  url = (BASE_URL+'/rxclass/%s/classMembers.json?classId=%s&relaSource=%s'%(class_id, rel_src))
  rval = rest_utils.GetURL(url, parse_json=True)
  logging.debug(json.dumps(rval, indent=4))

#############################################################################
def Get_SpellingSuggestions(base_url, name, fout):
  rval = rest_utils.GetURL(BASE_URL+'/spellingsuggestions.json?name=%s'%urllib.parse.quote(name), parse_json=True)
  logging.debug(json.dumps(rval, indent=4))

#############################################################################
def RawQuery(base_url, rawquery, fout):
  rval = rest_utils.GetURL(base_url+rawquery, parse_json=True)
  logging.debug(json.dumps(rval, indent=4))

