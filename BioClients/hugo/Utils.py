#!/usr/bin/env python3
"""
Utility functions for HUGO REST API.
See: https://www.genenames.org/help/rest-web-service-help
"""
import sys,os,re,requests,json,time,logging
import pandas as pd

#
API_HOST="rest.genenames.org"
API_BASE_PATH=""
BASE_URL="http://"+API_HOST+API_BASE_PATH
#
HEADERS={"Accept":"application/json"}
#
##############################################################################
def Info(base_url=BASE_URL, fout=None):
  response = requests.get(base_url+"/info", headers=HEADERS)
  result = response.json()
  logging.debug(json.dumps(result, sort_keys=True, indent=2))
  if "searchableFields" in result:
    for f in result["searchableFields"]:
      print(f"{f}")
  if "storedFields" in result:
    for f in result["storedFields"]:
      print(f"{f}")

##############################################################################
def ListSearchableFields(base_url=BASE_URL, fout=None):
  response = requests.get(base_url+'/info', headers=HEADERS)
  result = response.json()
  fields = result['searchableFields'] if 'searchableFields' in result else None
  fields.sort()
  df = pd.DataFrame({'fields':fields})
  if fout: df.to_csv(fout, "\t", index=False)
  return df

##############################################################################
def ListStoredFields(base_url=BASE_URL, fout=None):
  response = requests.get(base_url+'/info', headers=HEADERS)
  result = response.json()
  fields = result['storedFields'] if 'storedFields' in result else None
  fields.sort()
  df = pd.DataFrame({'fields':fields})
  if fout: df.to_csv(fout, "\t", index=False)
  return df

##############################################################################
def GetGenes(qrys, ftypes, skip=0, base_url=BASE_URL, fout=None):
  '''The API can return multiple hits for each query, though should not 
for exact SYMBOL fetch.  One case is for RPS15P5, status "Entry Withdrawn".'''
  n_in=0; n_found=0; n_notfound=0; n_ambig=0; n_gene=0;
  tags=[]; df=None;
  logging.debug(f"ftypes[{len(ftypes)}]: {str(ftypes)}")
  for qry in qrys:
    n_in+=1
    if n_in<skip: continue
    logging.debug(f"{n_in}. query: {qry}")
    numFound=0; genes=[];
    ftype_hit=None
    for ftype in ftypes:
      response = requests.get(base_url+f"/fetch/{ftype.lower()}/{qry}", headers=HEADERS)
      result = response.json()
      logging.debug(json.dumps(result, indent=2))
      if result is None: continue
      ftype_hit=ftype
      numFound = result['response']['numFound'] if 'numFound' in result['response'] else 0
      genes = result['response']['docs']
      if numFound>0:
        logging.debug(f"Not found: {ftype_hit} = {qry}")
        break
    if numFound==0:
      n_notfound+=1
      logging.debug(f"Not found: {ftype_hit} = {qry}")
      continue
    elif numFound>0:
      n_found+=1
    if len(genes)>1:
      logging.warning(f"Multiple ({len(genes)}) hits, {ftype_hit} = {qry} (Duplicate may be status=withdrawn.)")
      n_ambig+=1
    for gene in genes:
      for tag in list(gene.keys())[:]:
        if tag in ("prev_symbol", "prev_name", "alias_symbol"):
          gene[tag] = [";".join(gene[tag])]
        elif type(gene[tag]) in (list, dict):
          del gene[tag]
        else:
          gene[tag] = [gene[tag]]
      gene['query'] = [qry]
      gene['field'] = [ftype_hit]
      df_this = pd.DataFrame(gene)
      if fout: df_this.to_csv(fout, "\t", index=False)
      else: df = pd.concat([df, df_this])
      n_gene+=1
  logging.info(f"queries: {n_in-skip}; found: {n_found}; not found: {n_notfound}; ambiguous: {n_ambig}; total genes returned: {n_gene}")
  return df

##############################################################################
def SearchGenes(qrys, ftypes, base_url=BASE_URL, fout=None):
  n_in=0; n_found=0; tags=[]; df=None;
  for qry in qrys:
    n_in+=1
    logging.debug(f"{n_in}. query: {qry}")
    found_this=False
    for ftype in ftypes:
      url = (base_url+'/search{}/*{}*'.format((('/'+ftype.lower()) if ftype else ''), qry))
      response = requests.get(url, headers=HEADERS)
      result = response.json()
      numFound = result['response']['numFound'] if 'numFound' in result['response'] else 0
      if numFound==0: continue
      found_this=True
      docs = result['response']['docs'] if 'docs' in result['response'] else []
      for doc in docs:
        logging.debug(json.dumps(doc, sort_keys=True, indent=2)+'\n')
        if not tags: tags = list(doc.keys())
        data_this = {'query':qry, 'field':ftype}
        data_this.update({tags[j]:[doc[tags[j]]] for j in range(len(tags))})
        df = pd.concat([df, pd.DataFrame(data_this)])
    if found_this: n_found+=1
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"queries: {n_in}; found: {n_found}")
  return df

