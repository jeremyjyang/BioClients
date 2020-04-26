#!/usr/bin/env python3
"""
https://mor.nlm.nih.gov/download/rxnav/RxNormAPIs.html
https://www.nlm.nih.gov/research/umls/rxnorm/docs/
"""
###
import sys,os,re,json,logging,urllib.parse

from ..util import rest_utils

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
def List_Classes(base_url, class_types, fout):
  n_out=0;
  tags = ["classId", "classType", "className" ]
  url = (base_url+'/rxclass/allClasses.json')
  if class_types: url+=("?classTypes=%s"%urllib.parse.quote(' '.join(class_types)))
  rval = rest_utils.GetURL(url, parse_json=True)
  logging.debug(json.dumps(rval, indent=4))
  clss = rval["rxclassMinConceptList"]["rxclassMinConcept"] if "rxclassMinConceptList" in rval and "rxclassMinConcept" in rval["rxclassMinConceptList"] else []
  for cls in clss:
    vals = [cls[tag] if tag in cls else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def Get_Name2RxCUI(base_url, names, fout):
  n_out=0;
  fout.write('Name\tRxCUI\n')
  for name in names:
    rval = rest_utils.GetURL(base_url+'/rxcui.json?name=%s'%urllib.parse.quote(name), parse_json=True)
    logging.debug(json.dumps(rval, indent=4))
    rxnormIds = rval["idGroup"]["rxnormId"] if "idGroup" in rval and "rxnormId" in rval["idGroup"] else []
    for rxnormId in rxnormIds:
      fout.write("%s\t%s\n"%(name, rxnormId))
      n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def Get_Name(base_url, names, fout):
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
def Get_ID2RxCUI(base_url, ids, idtype, fout):
  """For mapping external ID, for supported ID types, to RxNorm ID."""
  n_out=0;
  fout.write('%s\trxcui\n'%(idtype))
  for id_this in ids:
    rval = rest_utils.GetURL(base_url+'/rxcui.json?idtype=%s&id=%s'%(idtype, id_this), parse_json=True)
    for rxcui in rval['idGroup']['rxnormId']:
      fout.write('%s\t%s\n'%(id_this, rxcui))
      n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def Get_RxCUI_Status(base_url, ids, fout):
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
    rval = rest_utils.GetURL(base_url+'/rxcui/%s/properties.json'%rxcui, parse_json=True)
    logging.debug(json.dumps(rval, indent=4))
    props = rval["properties"] if "properties" in rval else []
    if not tags:
      tags = props.keys()
      fout.write('\t'.join(tags)+'\n')
    vals = [props[tag] if tag in props else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def Get_RxCUI_AllProperties(base_url, ids, fout):
  n_out=0; tags=None;
  for rxcui in ids:
    rval = rest_utils.GetURL(base_url+'/rxcui/%s/allProperties.json?prop=all'%rxcui, parse_json=True)
    logging.debug(json.dumps(rval, indent=4))
    props = rval["propConceptGroup"]["propConcept"] if "propConceptGroup" in rval and "propConcept" in rval["propConceptGroup"] else {}
    for prop in props:
      if not tags:
        tags = list(prop.keys())
        fout.write('\t'.join(['RxCui']+tags)+'\n')
      vals = [prop[tag] if tag in prop else '' for tag in tags]
      fout.write('\t'.join([rxcui]+vals)+'\n')
      n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def Get_RxCUI_AllRelated(base_url, ids, fout):
  n_out=0; tags=None;
  for rxcui in ids:
    rval = rest_utils.GetURL(base_url+'/rxcui/%s/allrelated.json'%rxcui, parse_json=True)
    logging.debug(json.dumps(rval, indent=4))
    conceptGroups = rval["allRelatedGroup"]["conceptGroup"] if "allRelatedGroup" in rval and "conceptGroup" in rval["allRelatedGroup"] else []
    for cgroup in conceptGroups:
      props = cgroup["conceptProperties"] if "conceptProperties" in cgroup else []
      for prop in props:
        if not tags:
          tags = list(prop.keys())
          fout.write('\t'.join(['RxCui']+tags)+'\n')
        vals = [prop[tag] if tag in prop else '' for tag in tags]
        fout.write("\t".join([rxcui]+vals)+"\n")
        n_out+=1
  logging.info("n_out: %d"%(n_out))

#############################################################################
def Get_RxCUI_NDCs(base_url, ids, fout):
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
def Get_RxCUI_Classes(base_url, ids, fout):
  n_out=0;
  tags = ["classId", "classType", "className" ]
  for rxcui in ids:
    rval = rest_utils.GetURL(base_url+'/rxcui/%s/classes.json'%rxcui, parse_json=True)
    logging.debug(json.dumps(rval, indent=4))

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

