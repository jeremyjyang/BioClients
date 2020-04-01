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
  n_out=0;
  fout.write('%s\trxcui\n'%(idtype))
  for id_this in ids:
    rval = rest_utils.GetURL(base_url+'/rxcui.json?idtype=%s&id=%s'%(idtype, id_this), parse_json=True)
    for rxcui in rval['idGroup']['rxnormId']:
      fout.write('%s\t%s\n'%(id_this, rxcui))
      n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def Get_RxCUI_By_Name(base_url, names, fout):
  n_out=0;
  fout.write('RxCUI\n')
  for name in names:
    rval = rest_utils.GetURL(base_url+'/rxcui.json?name=%s'%urllib.parse.quote(name, ''), parse_json=True)
    logging.debug(json.dumps(rval, indent=4))
    rxnormIds = rval["idGroup"]["rxnormId"] if "idGroup" in rval and "rxnormId" in rval["idGroup"] else []
    for rxnormId in rxnormIds:
      fout.write(rxnormId+"\n")
      n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def Get_Drug_By_Name(base_url, names, fout):
  n_out=0;
  tags = ["rxcui", "name", "synonym", "tty", "language", "suppress", "umlscui"]
  fout.write("rxcui\tname\tsynonym\ttty\tlanguage\tsuppress\tumlscui\n")
  for name in names:
    rval = rest_utils.GetURL(base_url+'/drugs.json?name=%s'%urllib.parse.quote(name), parse_json=True)
    logging.debug(json.dumps(rval, indent=4))
    conceptGroups = rval["drugGroup"]["conceptGroup"] if "drugGroup" in rval and "conceptGroup" in rval["drugGroup"] else []
    for cgroup in conceptGroups:
      cprops = cgroup["conceptProperties"] if "conceptProperties" in cgroup else []
      if not cprops: continue
      for cprop in cprops:
        vals = [cprop[tag] if tag in cprop else '' for tag in tags]
        fout.write("\t".join(vals)+"\n")
        n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def List_IDTypes(base_url, fout):
  n_out=0;
  rval = rest_utils.GetURL(base_url+'/idtypes.json', parse_json=True)
  fout.write('IDType\n')
  for idtype in rval['idTypeList']['idName']:
    fout.write('%s\n'%idtype)
    n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def List_SourceTypes(base_url, fout):
  n_out=0;
  rval = rest_utils.GetURL(base_url+'/sourcetypes.json', parse_json=True)
  for sourcetype in rval['sourceTypeList']['sourceName']:
    fout.write('%s\n'%sourcetype)
    n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def List_RelationTypes(base_url, fout):
  n_out=0;
  rval = rest_utils.GetURL(base_url+'/relatypes.json', parse_json=True)
  for relatype in rval['relationTypeList']['relationType']:
    fout.write('%s\n'%relatype)
    n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def List_TermTypes(base_url, fout):
  n_out=0;
  rval = rest_utils.GetURL(base_url+'/termtypes.json', parse_json=True)
  for termtype in rval['termTypeList']['termType']:
    fout.write('%s\n'%termtype)
    n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def List_PropNames(base_url, fout):
  n_out=0;
  rval = rest_utils.GetURL(base_url+'/propnames.json', parse_json=True)
  for propname in rval['propNameList']['propName']:
    fout.write('%s\n'%propname)
    n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def List_PropCategories(base_url, fout):
  n_out=0;
  rval = rest_utils.GetURL(base_url+'/propCategories.json', parse_json=True)
  for propcat in rval['propCategoryList']['propCategory']:
    fout.write('%s\n'%propcat)
    n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def List_ClassTypes(base_url, fout):
  n_out=0;
  rval = rest_utils.GetURL(base_url+'/rxclass/classTypes.json', parse_json=True)
  logging.debug(json.dumps(rval, indent=4))
  for classtype in rval['classTypeList']['classTypeName']:
    fout.write('%s\n'%classtype)
    n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def List_Classes_ATC(base_url, atc_levels, fout):
  n_out=0;
  tags = ["classId", "classType", "className" ]
  rval = rest_utils.GetURL(base_url+'/rxclass/allClasses.json?classTypes=ATC%s'%(atc_levels), parse_json=True)
  logging.debug(json.dumps(rval, indent=4))
  atcs = rval["rxclassMinConceptList"]["rxclassMinConcept"] if "rxclassMinConceptList" in rval and "rxclassMinConcept" in rval["rxclassMinConceptList"] else []
  for atc in atcs:
    vals = [atc[tag] if tag in atc else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def List_Classes_MESH(base_url, fout):
  n_out=0;
  tags = ["classId", "classType", "className" ]
  rval = rest_utils.GetURL(base_url+'/rxclass/allClasses.json?classTypes=MESHPA', parse_json=True)
  logging.debug(json.dumps(rval, indent=4))
  meshs = rval["rxclassMinConceptList"]["rxclassMinConcept"] if "rxclassMinConceptList" in rval and "rxclassMinConcept" in rval["rxclassMinConceptList"] else []
  for mesh in meshs:
    vals = [mesh[tag] if tag in mesh else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def Get_Status(base_url, ids, fout):
  n_out=0;
  tags = ["rxcui", "name", "tty"]
  fout.write('\t'.join(tags)+"\tstatus\tremappedDate\n")
  for rxcui in ids:
    rval = rest_utils.GetURL(base_url+'/rxcui/%s/status.json'%rxcui,parse_json=True)
    logging.debug(json.dumps(rval, indent=4))
    if "rxcuiStatus" not in rval :
      logging.error("Bad record: %s"%str(rval))
      continue
    status = rval["rxcuiStatus"]["status"] if "status" in rval["rxcuiStatus"] else ""
    remappedDate = rval["rxcuiStatus"]["remappedDate"] if "remappedDate" in rval["rxcuiStatus"] else ""
    minConcepts = rval["rxcuiStatus"]["minConceptGroup"]["minConcept"] if "minConceptGroup" in rval["rxcuiStatus"] and "minConcept" in rval["rxcuiStatus"]["minConceptGroup"] else []
    for minConcept in minConcepts:
      vals = [minConcept[tag] if tag in minConcept else '' for tag in tags]
      fout.write('\t'.join(vals+[status, remappedDate])+"\n")
    n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def Get_RxCUI_Properties(base_url, ids, fout):
  n_out=0; tags=None;
  for rxcui in ids:
    rval = rest_utils.GetURL(base_url+'/rxcui/%s/properties.json'%rxcui,parse_json=True)
    logging.debug(json.dumps(rval, indent=4))
    properties = rval["properties"]
    if not tags:
      tags = properties.keys()
      fout.write('\t'.join(tags)+'\n')
    vals = [properties[tag] if tag in properties else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def Get_NDCs(base_url, ids, fout):
  n_out=0;
  fout.write('rxcui\tndc\n')
  for rxcui in ids:
    rval = rest_utils.GetURL(base_url+'/rxcui/%s/ndcs.json'%rxcui, parse_json=True)
    ndcs = rval['ndcGroup']['ndcList']['ndc'] if 'ndcGroup' in rval and 'ndcList' in rval['ndcGroup'] and rval['ndcGroup']['ndcList'] and 'ndc' in rval['ndcGroup']['ndcList'] else []
    for ndc in ndcs:
      fout.write('%s\t%s\n'%(rxcui, ndc))
      n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def Get_AllRelated(base_url, ids, fout):
  n_out=0;
  tags = ["rxcui", "name", "synonym", "tty", "language", "suppress", "umlscui"]
  fout.write("rxcui\trxcui_related\tname\tsynonym\ttty\tlanguage\tsuppress\tumlscui\n")
  for rxcui in ids:
    rval = rest_utils.GetURL(base_url+'/rxcui/%s/allrelated.json'%rxcui,parse_json=True)
    logging.debug(json.dumps(rval, indent=4))
    conceptGroups = rval["allRelatedGroup"]["conceptGroup"] if "allRelatedGroup" in rval and "conceptGroup" in rval["allRelatedGroup"] else []
    for cgroup in conceptGroups:
      cprops = cgroup["conceptProperties"] if "conceptProperties" in cgroup else []
      if not cprops: continue
      for cprop in cprops:
        vals = [cprop[tag] if tag in cprop else '' for tag in tags]
        fout.write("\t".join([rxcui]+vals)+"\n")
        n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def Get_Class_Members(base_url, class_id, rel_src, fout):
  n_out=0;
  url = (base_url+'/rxclass/%s/classMembers.json?classId=%s&relaSource=%s'%(class_id, rel_src))
  rval = rest_utils.GetURL(url, parse_json=True)
  logging.debug(json.dumps(rval, indent=4))
  #???
  logging.info("n_out: %d"%(n_out))

#############################################################################
def Get_SpellingSuggestions(base_url, name, fout):
  rval = rest_utils.GetURL(base_url+'/spellingsuggestions.json?name=%s'%urllib.parse.quote(name), parse_json=True)
  logging.debug(json.dumps(rval, indent=4))
  #???

#############################################################################
def RawQuery(base_url, rawquery, fout):
  rval = rest_utils.GetURL(base_url+rawquery, parse_json=True)
  logging.debug(json.dumps(rval, indent=4))
  #???

