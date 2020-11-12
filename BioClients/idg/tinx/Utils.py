#!/usr/bin/env python3
"""
TIN-X (Target Importance and Novelty Explorer) REST API client
https://www.newdrugtargets.org/
https://api.newdrugtargets.org/docs
https://api.newdrugtargets.org/targets/
"""
###
import sys,os,re,json,time,logging,tqdm
import pandas as pd
import urllib,urllib.parse
#
from ...util import rest
#
API_HOST="api.newdrugtargets.org"
API_BASE_PATH=""
BASE_URL = 'https://'+API_HOST+API_BASE_PATH
#
NCHUNK=100;
#
##############################################################################
def ListTargets(skip=0, nmax=None, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; tq=None; df=None;
  url_next = (base_url+'/targets/?limit={}&offset={}'.format(NCHUNK, skip))
  while True:
    rval = rest.Utils.GetURL(url_next, parse_json=True)
    targets = rval["results"] if "results" in rval else []
    if not tq: tq = tqdm.tqdm(total=(nmax if nmax else rval["count"]), unit="targets")
    for target in targets:
      tq.update()
      logging.debug(json.dumps(target, sort_keys=True, indent=2))
      if not tags: tags = list(target.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[target[tags[j]]] for j in range(len(tags))})])
      n_out+=1
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    url_next = rval["next"] if "next" in rval else None
    if not url_next: break
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_out: {}".format(n_out))
  return(df)

##############################################################################
def SearchTargets(query_term, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  url_next = (base_url+'/targets/?search='+urllib.parse.quote(query_term))
  while True:
    rval = rest.Utils.GetURL(url_next, parse_json=True)
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    targets = rval["results"] if "results" in rval else []
    for target in targets:
      logging.debug(json.dumps(target, sort_keys=True, indent=2))
      if not tags: tags = list(target.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[target[tags[j]]] for j in range(len(tags))})])
      n_out+=1
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    url_next = rval["next"] if "next" in rval else None
    if not url_next: break
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_out: {}".format(n_out))
  return(df)

##############################################################################
def ListDiseases(skip=0, nmax=None, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; tq=None; df=None;
  url_next = (base_url+'/diseases/?limit={}&offset={}'.format(NCHUNK, skip))
  while True:
    rval = rest.Utils.GetURL(url_next, parse_json=True)
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    diseases = rval["results"] if "results" in rval else []
    if not tq: tq = tqdm.tqdm(total=(nmax if nmax else rval["count"]), unit="dtos")
    for disease in diseases:
      tq.update()
      logging.debug(json.dumps(disease, sort_keys=True, indent=2))
      if not tags: tags = list(disease.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[disease[tags[j]]] for j in range(len(tags))})])
      n_out+=1
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    url_next = rval["next"] if "next" in rval else None
    if not url_next: break
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_out: {}".format(n_out))
  return(df)

##############################################################################
def ListArticles(skip=0, nmax=None, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; tq=None; df=None;
  url_next = (base_url+'/articles/?limit={}&offset={}'.format(NCHUNK, skip))
  while True:
    rval = rest.Utils.GetURL(url_next, parse_json=True)
    articles = rval["results"] if "results" in rval else []
    if not tq: tq = tqdm.tqdm(total=(nmax if nmax else rval["count"]), unit="articles")
    for article in articles:
      tq.update()
      logging.debug(json.dumps(article, sort_keys=True, indent=2))
      if not tags: tags = list(article.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[article[tags[j]]] for j in range(len(tags))})])
      n_out+=1
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    url_next = rval["next"] if "next" in rval else None
    if not url_next: break
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_out: {}".format(n_out))
  return(df)

##############################################################################
def ListDTO(skip=0, nmax=None, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; tq=None; df=None;
  url_next = (base_url+'/dto/?limit={}&offset={}'.format(NCHUNK, skip))
  while True:
    rval = rest.Utils.GetURL(url_next, parse_json=True)
    dtos = rval["results"] if "results" in rval else []
    if not tq: tq = tqdm.tqdm(total=(nmax if nmax else rval["count"]), unit="dtos")
    for dto in dtos:
      tq.update()
      logging.debug(json.dumps(dto, sort_keys=True, indent=2))
      if not tags: tags = list(dto.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[dto[tags[j]]] for j in range(len(tags))})])
      n_out+=1
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    url_next = rval["next"] if "next" in rval else None
    if not url_next: break
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_out: {}".format(n_out))
  return(df)

##############################################################################
def GetDisease(ids, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  """IDs should be TIN-X disease IDs, e.g. 5391."""
  n_in=0; n_out=0; tags=None; df=None;
  for id_this in ids:
    n_in+=1
    if skip and skip>n_in: continue
    disease = rest.Utils.GetURL((base_url+'/diseases/{}/'.format(id_this)), parse_json=True)
    logging.debug(json.dumps(disease, sort_keys=True, indent=2))
    if not tags: tags = list(disease.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[disease[tags[j]]] for j in range(len(tags))})])
    n_out+=1
    if nmax and n_in>=nmax: break
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_in: {}; n_out: {}".format(n_in, n_out))
  return(df)

##############################################################################
def GetDiseaseByDOId(ids, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  """IDs should be Disease Ontology IDs, e.g. DOID:9297."""
  n_in=0; n_out=0; tags=None; df=None;
  for id_this in ids:
    n_in+=1
    if skip and skip>n_in: continue
    rval = rest.Utils.GetURL((base_url+'/diseases/?doid='+id_this), parse_json=True)
    diseases = rval["results"] if "results" in rval else []
    for disease in diseases:
      logging.debug(json.dumps(disease, sort_keys=True, indent=2))
      if not tags: tags = list(disease.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[disease[tags[j]]] for j in range(len(tags))})])
      n_out+=1
    if nmax and n_in>=nmax: break
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_in: {}; n_out: {}".format(n_in, n_out))
  return(df)

##############################################################################
def GetTarget(ids, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  """IDs should be TIN-X target IDs, e.g. 10027."""
  n_in=0; n_out=0; tags=None; df=None;
  for id_this in ids:
    n_in+=1
    if skip and skip>n_in: continue
    target = rest.Utils.GetURL((base_url+'/targets/{}/'.format(id_this)), parse_json=True)
    logging.debug(json.dumps(target, sort_keys=True, indent=2))
    if not tags: tags = list(target.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[target[tags[j]]] for j in range(len(tags))})])
    n_out+=1
    if nmax and n_in>=nmax: break
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_in: {}; n_out: {}".format(n_in, n_out))
  return(df)

##############################################################################
def GetTargetByUniprot(ids, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  """IDs should be UniProt IDs, e.g. Q9H4B4."""
  n_in=0; n_out=0; tags=None; df=None;
  for id_this in ids:
    n_in+=1
    if skip and skip>n_in: continue
    rval = rest.Utils.GetURL((base_url+'/targets/?uniprot='+id_this), parse_json=True)
    targets = rval["results"] if "results" in rval else []
    for target in targets:
      logging.debug(json.dumps(target, sort_keys=True, indent=2))
      if not tags: tags = list(target.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[target[tags[j]]] for j in range(len(tags))})])
      n_out+=1
    if nmax and n_in>=nmax: break
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_in: {}; n_out: {}".format(n_in, n_out))
  return(df)

##############################################################################
def GetTargetDiseases(ids, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  """IDs should be TIN-X target IDs, e.g. 10027."""
  n_in=0; n_out=0; tags=None; tq=None; df=None;
  for id_this in ids:
    n_in+=1
    if skip and skip>n_in: continue
    while True:
      url_next = (base_url+'/targets/{}/diseases'.format(id_this))
      rval = rest.Utils.GetURL(url_next, parse_json=True)
      diseases = rval["results"] if "results" in rval else []
      if not tq: tq = tqdm.tqdm(total=(nmax if nmax else rval["count"]), unit="diseases")
      for disease in diseases:
        tq.update()
        logging.debug(json.dumps(disease, sort_keys=True, indent=2))
        phenotype = disease["disease"] if "disease" in disease else {}
        if not tags:
          tags = list(disease.keys())
          tags.remove("disease")
          phenotype_tags = list(phenotype.keys())
        data_this = {"tinx_target_id":id_this}
        data_this.update({tags[j]:[disease[tags[j]]] for j in range(len(tags))})
        data_this.update({phenotype_tags[j]:[phenotype[phenotype_tags[j]]] for j in range(len(phenotype_tags))})
        df = pd.concat([df, pd.DataFrame(data_this)])
        n_out+=1
        if nmax and n_out>=nmax: break
      if nmax and n_out>=nmax: break
      url_next = rval["next"] if "next" in rval else None
      if not url_next: break
      if n_out>=rval["count"]: break #url_next may be wrong.
    if nmax and n_out>=nmax: break
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_in: {}; n_out: {}".format(n_in, n_out))
  return(df)

##############################################################################
def GetDiseaseTargets(ids, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  """IDs should be TIN-X disease IDs, e.g. 5391."""
  n_in=0; n_out=0; tags=None; tq=None; df=None;
  for id_this in ids:
    n_in+=1
    if skip and skip>n_in: continue
    while True:
      url_next = (base_url+f'/diseases/{id_this}/targets')
      rval = rest.Utils.GetURL(url_next, parse_json=True)
      logging.debug(json.dumps(rval, sort_keys=True, indent=2))
      targets = rval["results"] if "results" in rval else []
      if not tq: tq = tqdm.tqdm(total=(nmax if nmax else rval["count"]), unit="targets")
      for target in targets:
        tq.update()
        logging.debug(json.dumps(target, sort_keys=True, indent=2))
        protein = target["target"] if "target" in target else {}
        if not tags:
          tags = list(target.keys())
          tags.remove("target")
          protein_tags = list(protein.keys())
        data_this = {"tinx_disease_id":id_this}
        data_this.update({tags[j]:[target[tags[j]]] for j in range(len(tags))})
        data_this.update({protein_tags[j]:[protein[protein_tags[j]]] for j in range(len(protein_tags))})
        df = pd.concat([df, pd.DataFrame(data_this)])
        n_out+=1
        if nmax and n_out>=nmax: break
      if nmax and n_out>=nmax: break
      url_next = rval["next"] if "next" in rval else None
      if not url_next: break
      if n_out>=rval["count"]: break #url_next may be wrong.
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_in: {}; n_out: {}".format(n_in, n_out))
  return(df)

##############################################################################
def GetDiseaseTargetArticles(disease_ids, ids, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  """IDs should be TIN-X disease and target IDs and, e.g. 5391, 12203."""
  n_out=0; tags=None; df=None;
  for did in disease_ids:
    for tid in ids:
      url_next = (base_url+'/diseases/{}/targets/{}/articles'.format(did, tid))
      while True:
        rval = rest.Utils.GetURL(url_next, parse_json=True)
        articles = rval["results"] if "results" in rval else []
        for article in articles:
          logging.debug(json.dumps(article, sort_keys=True, indent=2))
          if not tags: tags = list(article.keys())
          df = pd.concat([df, pd.DataFrame({tags[j]:[article[tags[j]]] for j in range(len(tags))})])
          n_out+=1
        url_next = rval["next"] if "next" in rval else None
        if not url_next: break
        if n_out>=rval["count"]: break #url_next may be wrong.
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_out: {}".format(n_out))
  return(df)

##############################################################################
def SearchDiseases(query_term, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  """Search names; begins-with search logic."""
  n_out=0; tags=None; df=None;
  url_next = (base_url+'/diseases/?search='+urllib.parse.quote(query_term))
  while True:
    rval = rest.Utils.GetURL(url_next, parse_json=True)
    diseases = rval["results"] if "results" in rval else []
    for disease in diseases:
      logging.debug(json.dumps(disease, sort_keys=True, indent=2))
      if not tags: tags = list(disease.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[disease[tags[j]]] for j in range(len(tags))})])
      n_out+=1
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    url_next = rval["next"] if "next" in rval else None
    if not url_next: break
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_out: {}".format(n_out))
  return(df)

##############################################################################
def SearchTargets(query_term, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  """Search names."""
  n_out=0; tags=None; df=None;
  url_next = (base_url+'/targets/?search='+urllib.parse.quote(query_term))
  while True:
    rval = rest.Utils.GetURL(url_next, parse_json=True)
    targets = rval["results"] if "results" in rval else []
    for target in targets:
      logging.debug(json.dumps(target, sort_keys=True, indent=2))
      if not tags: tags = list(target.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[target[tags[j]]] for j in range(len(tags))})])
      n_out+=1
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    url_next = rval["next"] if "next" in rval else None
    if not url_next: break
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_out: {}".format(n_out))
  return(df)

##############################################################################
def SearchArticles(terms, skip=0, nmax=None, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  for term in terms:
    url_next = (base_url+'/articles/?search='+urllib.parse.quote(term))
    while True:
      rval = rest.Utils.GetURL(url_next, parse_json=True)
      logging.debug(json.dumps(rval, sort_keys=True, indent=2))
      articles = rval["results"] if "results" in rval else []
      for article in articles:
        logging.debug(json.dumps(article, sort_keys=True, indent=2))
        if not tags: tags = list(article.keys())
        df = pd.concat([df, pd.DataFrame({tags[j]:[article[tags[j]]] for j in range(len(tags))})])
        n_out+=1
        if nmax and n_out>=nmax: break
      if nmax and n_out>=nmax: break
      url_next = rval["next"] if "next" in rval else None
      if not url_next: break
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info("n_out: {}".format(n_out))
  return(df)

