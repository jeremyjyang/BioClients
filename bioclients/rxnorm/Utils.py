#!/usr/bin/env python3
"""
https://mor.nlm.nih.gov/download/rxnav/RxNormAPIs.html
https://www.nlm.nih.gov/research/umls/rxnorm/docs/
"""
###
import sys,os,re,json,logging,urllib.parse,tqdm
import pandas as pd

from ..util import rest

#
API_HOST='rxnav.nlm.nih.gov'
API_BASE_PATH='/REST'
BASE_URL='https://'+API_HOST+API_BASE_PATH
#
NDFRT_TYPES=('DISEASE','INGREDIENT','MOA','PE','PK') ## NDFRT drug class types
#
#############################################################################
def List_IDTypes(base_url=BASE_URL, fout=None):
  rval = rest.GetURL(base_url+'/idtypes.json', parse_json=True)
  logging.debug(json.dumps(rval, indent=2))
  df = pd.DataFrame({"idTypeList":rval['idTypeList']['idName']})
  logging.info(f"n_out: {df.shape[0]}")
  if fout is not None: df.to_csv(fout, sep="\t", index=False)
  else: return df

#############################################################################
def List_SourceTypes(base_url=BASE_URL, fout=None):
  rval = rest.GetURL(base_url+'/sourcetypes.json', parse_json=True)
  df = pd.DataFrame({"sourceType":rval['sourceTypeList']['sourceName']})
  logging.info(f"n_out: {df.shape[0]}")
  if fout is not None: df.to_csv(fout, sep="\t", index=False)
  else: return df

#############################################################################
def List_RelationTypes(base_url=BASE_URL, fout=None):
  rval = rest.GetURL(base_url+'/relatypes.json', parse_json=True)
  df = pd.DataFrame({"relationType":rval['relationTypeList']['relationType']})
  logging.info(f"n_out: {df.shape[0]}")
  if fout is not None: df.to_csv(fout, sep="\t", index=False)
  else: return df

#############################################################################
def List_TermTypes(base_url=BASE_URL, fout=None):
  rval = rest.GetURL(base_url+'/termtypes.json', parse_json=True)
  df = pd.DataFrame({"termType":rval['termTypeList']['termType']})
  logging.info(f"n_out: {df.shape[0]}")
  if fout is not None: df.to_csv(fout, sep="\t", index=False)
  else: return df

#############################################################################
def List_PropNames(base_url=BASE_URL, fout=None):
  rval = rest.GetURL(base_url+'/propnames.json', parse_json=True)
  df = pd.DataFrame({"propName":rval['propNameList']['propName']})
  logging.info(f"n_out: {df.shape[0]}")
  if fout is not None: df.to_csv(fout, sep="\t", index=False)
  else: return df

#############################################################################
def List_PropCategories(base_url=BASE_URL, fout=None):
  rval = rest.GetURL(base_url+'/propCategories.json', parse_json=True)
  df = pd.DataFrame({"propCategory":rval['propCategoryList']['propCategory']})
  logging.info(f"n_out: {df.shape[0]}")
  if fout is not None: df.to_csv(fout, sep="\t", index=False)
  else: return df

#############################################################################
def List_ClassTypes(base_url=BASE_URL, fout=None):
  rval = rest.GetURL(base_url+'/rxclass/classTypes.json', parse_json=True)
  df = pd.DataFrame({"classType":rval['classTypeList']['classTypeName']})
  logging.info(f"n_out: {df.shape[0]}")
  if fout is not None: df.to_csv(fout, sep="\t", index=False)
  else: return df

#############################################################################
def List_Classes(class_types, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=pd.DataFrame(); tq=None;
  url = (f'{base_url}/rxclass/allClasses.json')
  if class_types: url+=("?classTypes="+urllib.parse.quote(' '.join(class_types)))
  rval = rest.GetURL(url, parse_json=True)
  logging.debug(json.dumps(rval, indent=4))
  clss = rval["rxclassMinConceptList"]["rxclassMinConcept"] if "rxclassMinConceptList" in rval and "rxclassMinConcept" in rval["rxclassMinConceptList"] else []
  for cls in clss:
    if not tq: tq = tqdm.tqdm(total=len(clss), unit="classes")
    tq.update()
    if not tags: tags = list(cls.keys())
    df_this = pd.DataFrame({tags[j]:[cls[tags[j]]] for j in range(len(tags))})
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  if fout is None: return df

#############################################################################
def Get_Name2RxCUI(names, base_url=BASE_URL, fout=None):
  n_out=0; df=pd.DataFrame();
  for name in names:
    rval = rest.GetURL(f'{base_url}/rxcui.json?name={urllib.parse.quote(name)}', parse_json=True)
    logging.debug(json.dumps(rval, indent=4))
    idGroup = rval["idGroup"] if "idGroup" in rval else None
    rxnormIds = idGroup["rxnormId"] if idGroup and "rxnormId" in idGroup else []
    for rxnormId in rxnormIds:
      df_this = pd.DataFrame({"name":[idGroup["name"]], "rxnormId":rxnormId})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  if fout is None: return df

#############################################################################
def Get_Name(names, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=pd.DataFrame();
  for name in names:
    rval = rest.GetURL(f'{base_url}/drugs.json?name={urllib.parse.quote(name)}', parse_json=True)
    logging.debug(json.dumps(rval, indent=4))
    conceptGroups = rval["drugGroup"]["conceptGroup"] if "drugGroup" in rval and "conceptGroup" in rval["drugGroup"] else []
    for cgroup in conceptGroups:
      cprops = cgroup["conceptProperties"] if "conceptProperties" in cgroup else []
      if not cprops: continue
      for cprop in cprops:
        if not tags: tags = list(cprop.keys())
        df_this = pd.DataFrame({tags[j]:[cprop[tags[j]]] for j in range(len(tags))})
        if fout is None: df = pd.concat([df, df_this])
        else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
        n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  if fout is None: return df

#############################################################################
def Get_ID2RxCUI(ids, idtype, base_url=BASE_URL, fout=None):
  """For mapping external ID, for supported ID types, to RxNorm ID."""
  n_out=0; df=pd.DataFrame();
  for id_this in ids:
    rval = rest.GetURL(f'{base_url}/rxcui.json?idtype={idtype}&id={id_this}', parse_json=True)
    logging.debug(json.dumps(rval, indent=4))
    for rxcui in rval['idGroup']['rxnormId']:
      df_this = pd.DataFrame({"idtype":idtype, "id":[id_this], "rxnormId":rxcui})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  if fout is None: return df

#############################################################################
def Get_RxCUI_Status(ids, base_url=BASE_URL, fout=None):
  n_out=0;
  tags = ["rxcui", "name", "tty"]
  fout.write('\t'.join(tags)+"\tstatus\tremappedDate\n")
  for rxcui in ids:
    rval = rest.GetURL(f'{base_url}/rxcui/{rxcui}/status.json', parse_json=True)
    logging.debug(json.dumps(rval, indent=4))
    if "rxcuiStatus" not in rval :
      logging.error(f"Bad record: {rval}")
      continue
    status = rval["rxcuiStatus"]["status"] if "status" in rval["rxcuiStatus"] else ""
    remappedDate = rval["rxcuiStatus"]["remappedDate"] if "remappedDate" in rval["rxcuiStatus"] else ""
    minConcepts = rval["rxcuiStatus"]["minConceptGroup"]["minConcept"] if "minConceptGroup" in rval["rxcuiStatus"] and "minConcept" in rval["rxcuiStatus"]["minConceptGroup"] else []
    for minConcept in minConcepts:
      vals = [minConcept[tag] if tag in minConcept else '' for tag in tags]
      fout.write('\t'.join(vals+[status, remappedDate])+"\n")
    n_out+=1
  logging.info(f"n_out: {n_out}")

#############################################################################
def Get_RxCUI_Properties(ids, base_url=BASE_URL, fout=None):
  n_out=0; tags=None;
  for rxcui in ids:
    rval = rest.GetURL(f'{base_url}/rxcui/{rxcui}/properties.json', parse_json=True)
    logging.debug(json.dumps(rval, indent=4))
    props = rval["properties"] if "properties" in rval else []
    if not tags:
      tags = props.keys()
      fout.write('\t'.join(tags)+'\n')
    vals = [props[tag] if tag in props else '' for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info(f"n_out: {n_out}")

#############################################################################
def Get_RxCUI_AllProperties(ids, base_url=BASE_URL, fout=None):
  n_out=0; tags=None;
  for rxcui in ids:
    rval = rest.GetURL(f'{base_url}/rxcui/{rxcui}/allProperties.json?prop=all', parse_json=True)
    logging.debug(json.dumps(rval, indent=4))
    props = rval["propConceptGroup"]["propConcept"] if "propConceptGroup" in rval and "propConcept" in rval["propConceptGroup"] else {}
    for prop in props:
      if not tags:
        tags = list(prop.keys())
        fout.write('\t'.join(['RxCui']+tags)+'\n')
      vals = [prop[tag] if tag in prop else '' for tag in tags]
      fout.write('\t'.join([rxcui]+vals)+'\n')
      n_out+=1
  logging.info(f"n_out: {n_out}")

#############################################################################
def Get_RxCUI_AllRelated(ids, base_url=BASE_URL, fout=None):
  n_out=0; tags=None;
  for rxcui in ids:
    rval = rest.GetURL(f'{base_url}/rxcui/{rxcui}/allrelated.json', parse_json=True)
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
  logging.info(f"n_out: {n_out}")

#############################################################################
def Get_RxCUI_NDCs(ids, base_url=BASE_URL, fout=None):
  n_out=0;
  fout.write('rxcui\tndc\n')
  for rxcui in ids:
    rval = rest.GetURL(f'{base_url}/rxcui/{rxcui}/ndcs.json', parse_json=True)
    ndcs = rval['ndcGroup']['ndcList']['ndc'] if 'ndcGroup' in rval and 'ndcList' in rval['ndcGroup'] and rval['ndcGroup']['ndcList'] and 'ndc' in rval['ndcGroup']['ndcList'] else []
    for ndc in ndcs:
      fout.write('%s\t%s\n'%(rxcui, ndc))
      n_out+=1
  logging.info(f"n_out: {n_out}")

#############################################################################
def Get_RxCUI_Classes(ids, base_url=BASE_URL, fout=None):
  n_out=0;
  tags = ["classId", "classType", "className" ]
  for rxcui in ids:
    rval = rest.GetURL(f'{base_url}/rxcui/{rxcui}/classes.json', parse_json=True)
    logging.debug(json.dumps(rval, indent=4))

#############################################################################
def Get_Class_Members(class_id, rel_src, base_url=BASE_URL, fout=None):
  n_out=0;
  url = (f'{base_url}/rxclass/classMembers.json?classId={class_id}&relaSource={rel_src}')
  rval = rest.GetURL(url, parse_json=True)
  logging.debug(json.dumps(rval, indent=4))
  #???
  logging.info(f"n_out: {n_out}")

#############################################################################
def Get_SpellingSuggestions(name, base_url=BASE_URL, fout=None):
  rval = rest.GetURL(f'{base_url}/spellingsuggestions.json?name={urllib.parse.quote(name)}', parse_json=True)
  logging.debug(json.dumps(rval, indent=4))
  #???

#############################################################################
def RawQuery(rawquery, base_url=BASE_URL, fout=None):
  rval = rest.GetURL(base_url+rawquery, parse_json=True)
  logging.debug(json.dumps(rval, indent=4))
  #???

