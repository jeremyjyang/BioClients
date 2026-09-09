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
def ListTargets(base_url=BASE_URL, fout=None):
  n_out=0; tags=None; tq=None; df=None; offset=0;
  while True:
    url_next = (base_url+f'/targets/?limit={NCHUNK}&offset={offset}')
    rval = rest.Utils.GetURL(url_next, parse_json=True)
    targets = rval["results"] if "results" in rval else []
    if not tq: tq = tqdm.tqdm(total=rval["count"], unit="targets")
    for target in targets:
      tq.update()
      logging.debug(json.dumps(target, sort_keys=True, indent=2))
      if not tags: tags = list(target.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[target[tags[j]]] for j in range(len(tags))})])
      n_out+=1
    url_next = rval["next"] if "next" in rval else None #Full URL suboptimal.
    if not url_next: break
    offset += NCHUNK
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info("n_out: {}".format(n_out))
  return(df)

##############################################################################
def SearchTargets(query_term, base_url=BASE_URL, fout=None):
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
    url_next = rval["next"] if "next" in rval else None
    if not url_next: break
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info("n_out: {}".format(n_out))
  return(df)

##############################################################################
def ListDiseases(base_url=BASE_URL, fout=None):
  n_out=0; tags=None; tq=None; df=None; offset=0;
  while True:
    url_next = (base_url+f'/diseases/?limit={NCHUNK}&offset={offset}')
    rval = rest.Utils.GetURL(url_next, parse_json=True)
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    diseases = rval["results"] if "results" in rval else []
    if not tq: tq = tqdm.tqdm(total=rval["count"], unit="dtos")
    for disease in diseases:
      tq.update()
      logging.debug(json.dumps(disease, sort_keys=True, indent=2))
      if not tags: tags = list(disease.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[disease[tags[j]]] for j in range(len(tags))})])
      n_out+=1
    url_next = rval["next"] if "next" in rval else None
    if not url_next: break
    offset += NCHUNK
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info("n_out: {}".format(n_out))
  return(df)

##############################################################################
def ListArticles(base_url=BASE_URL, fout=None):
  n_out=0; tags=None; tq=None; df=None; offset=0;
  while True:
    url_next = (base_url+f'/articles/?limit={NCHUNK}&offset={offset}')
    rval = rest.Utils.GetURL(url_next, parse_json=True)
    articles = rval["results"] if "results" in rval else []
    if not tq: tq = tqdm.tqdm(total=rval["count"], unit="articles")
    for article in articles:
      tq.update()
      logging.debug(json.dumps(article, sort_keys=True, indent=2))
      if not tags: tags = list(article.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[article[tags[j]]] for j in range(len(tags))})])
      n_out+=1
    url_next = rval["next"] if "next" in rval else None
    if not url_next: break
    offset += NCHUNK
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info("n_out: {}".format(n_out))
  return(df)

##############################################################################
def ListDTO(base_url=BASE_URL, fout=None):
  n_out=0; tags=None; tq=None; df=None; offset=0;
  while True:
    url_next = (base_url+f'/dto/?limit={NCHUNK}&offset={offset}')
    rval = rest.Utils.GetURL(url_next, parse_json=True)
    dtos = rval["results"] if "results" in rval else []
    if not tq: tq = tqdm.tqdm(total=rval["count"], unit="dtos")
    for dto in dtos:
      tq.update()
      logging.debug(json.dumps(dto, sort_keys=True, indent=2))
      if not tags: tags = list(dto.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[dto[tags[j]]] for j in range(len(tags))})])
      n_out+=1
    url_next = rval["next"] if "next" in rval else None
    if not url_next: break
    offset += NCHUNK
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info("n_out: {}".format(n_out))
  return(df)

##############################################################################
def GetDisease(ids, base_url=BASE_URL, fout=None):
  """IDs should be TIN-X disease IDs, e.g. 5391."""
  n_in=0; n_out=0; tags=None; df=None;
  for id_this in ids:
    n_in+=1
    disease = rest.Utils.GetURL(base_url+f'/diseases/{id_this}/', parse_json=True)
    logging.debug(json.dumps(disease, sort_keys=True, indent=2))
    if not tags: tags = list(disease.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[disease[tags[j]]] for j in range(len(tags))})])
    n_out+=1
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_in: {n_in}; n_out: {n_out}")
  return(df)

##############################################################################
def GetDiseaseByDOId(ids, base_url=BASE_URL, fout=None):
  """IDs should be Disease Ontology IDs, e.g. DOID:9297."""
  n_in=0; n_out=0; tags=None; df=None;
  for id_this in ids:
    n_in+=1
    rval = rest.Utils.GetURL(base_url+f'/diseases/?doid={id_this}', parse_json=True)
    diseases = rval["results"] if "results" in rval else []
    for disease in diseases:
      logging.debug(json.dumps(disease, sort_keys=True, indent=2))
      if not tags: tags = list(disease.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[disease[tags[j]]] for j in range(len(tags))})])
      n_out+=1
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_in: {n_in}; n_out: {n_out}")
  return(df)

##############################################################################
def GetTarget(ids, base_url=BASE_URL, fout=None):
  """IDs should be TIN-X target IDs, e.g. 10027."""
  n_in=0; n_out=0; tags=None; df=None;
  for id_this in ids:
    n_in+=1
    target = rest.Utils.GetURL(base_url+f'/targets/{id_this}/', parse_json=True)
    logging.debug(json.dumps(target, sort_keys=True, indent=2))
    if not tags: tags = list(target.keys())
    df = pd.concat([df, pd.DataFrame({tags[j]:[target[tags[j]]] for j in range(len(tags))})])
    n_out+=1
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info("n_in: {}; n_out: {}".format(n_in, n_out))
  return(df)

##############################################################################
def GetTargetByUniprot(ids, base_url=BASE_URL, fout=None):
  """IDs should be UniProt IDs, e.g. Q9H4B4."""
  n_in=0; n_out=0; tags=None; df=None;
  for id_this in ids:
    n_in+=1
    rval = rest.Utils.GetURL(base_url+f'/targets/?uniprot={id_this}', parse_json=True)
    targets = rval["results"] if "results" in rval else []
    for target in targets:
      logging.debug(json.dumps(target, sort_keys=True, indent=2))
      if not tags: tags = list(target.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[target[tags[j]]] for j in range(len(tags))})])
      n_out+=1
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info("n_in: {}; n_out: {}".format(n_in, n_out))
  return(df)

##############################################################################
def GetTargetDiseases(ids, base_url=BASE_URL, fout=None):
  """IDs should be TIN-X target IDs, e.g. 10027."""
  n_in=0; n_out=0; tags=None; tq=None; df=None;
  for id_this in ids:
    n_in+=1
    offset=0;
    while True:
      url_next = (base_url+f'/targets/{id_this}/diseases?limit={NCHUNK}&offset={offset}')
      rval = rest.Utils.GetURL(url_next, parse_json=True)
      diseases = rval["results"] if "results" in rval else []
      if not tq: tq = tqdm.tqdm(total=rval["count"], unit="diseases")
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
      url_next = rval["next"] if "next" in rval else None
      if not url_next: break
      if n_out>=rval["count"]: break #url_next may be wrong.
      offset += NCHUNK
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_in: {n_in}; n_out: {n_out}")
  return(df)

##############################################################################
def GetDiseaseTargets(ids, base_url=BASE_URL, fout=None):
  """IDs should be TIN-X disease IDs, e.g. 5391."""
  n_in=0; n_out=0; tags=None; tq=None; df=None;
  for id_this in ids:
    n_in+=1
    offset=0;
    while True:
      url_next = (base_url+f'/diseases/{id_this}/targets?limit={NCHUNK}&offset={offset}')
      rval = rest.Utils.GetURL(url_next, parse_json=True)
      logging.debug(json.dumps(rval, sort_keys=True, indent=2))
      targets = rval["results"] if "results" in rval else []
      if not tq: tq = tqdm.tqdm(total=rval["count"], unit="targets")
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
      url_next = rval["next"] if "next" in rval else None
      if not url_next: break
      if n_out>=rval["count"]: break #url_next may be wrong.
      offset += NCHUNK
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info("n_in: {n_in}; n_out: {n_out}")
  return(df)

##############################################################################
def GetDiseaseTargetArticles(disease_ids, ids, base_url=BASE_URL, fout=None):
  """IDs should be TIN-X disease and target IDs and, e.g. 5391, 12203."""
  n_out=0; tags=None; df=None;
  for did in disease_ids:
    for tid in ids:
      offset=0;
      while True:
        url_next = (base_url+'/diseases/{did}/targets/{tid}/articles?limit={NCHUNK}&offset={offset}')
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
        offset += NCHUNK
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info("n_out: {}".format(n_out))
  return(df)

##############################################################################
def SearchDiseases(query_term, base_url=BASE_URL, fout=None):
  """Search names; begins-with search logic."""
  n_out=0; tags=None; df=None; offset=0;
  while True:
    url_next = (base_url+'/diseases/?search={}&limit={}&offset={}'.format(urllib.parse.quote(query_term), NCHUNK, offset))
    rval = rest.Utils.GetURL(url_next, parse_json=True)
    diseases = rval["results"] if "results" in rval else []
    for disease in diseases:
      logging.debug(json.dumps(disease, sort_keys=True, indent=2))
      if not tags: tags = list(disease.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[disease[tags[j]]] for j in range(len(tags))})])
      n_out+=1
    url_next = rval["next"] if "next" in rval else None
    if not url_next: break
    offset += NCHUNK
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info("n_out: {}".format(n_out))
  return(df)

##############################################################################
def SearchTargets(query_term, base_url=BASE_URL, fout=None):
  """Search names."""
  n_out=0; tags=None; df=None; offset=0;
  while True:
    url_next = (base_url+'/targets/?search={}&limit={}&offset={}'.format(urllib.parse.quote(query_term), NCHUNK, offset))
    rval = rest.Utils.GetURL(url_next, parse_json=True)
    targets = rval["results"] if "results" in rval else []
    for target in targets:
      logging.debug(json.dumps(target, sort_keys=True, indent=2))
      if not tags: tags = list(target.keys())
      df = pd.concat([df, pd.DataFrame({tags[j]:[target[tags[j]]] for j in range(len(tags))})])
      n_out+=1
    url_next = rval["next"] if "next" in rval else None
    if not url_next: break
    offset += NCHUNK
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info("n_out: {}".format(n_out))
  return(df)

##############################################################################
def SearchArticles(terms, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None; offset=0;
  for term in terms:
    while True:
      url_next = (base_url+'/articles/?search={}&limit={}&offset={}'.format(urllib.parse.quote(query_term), NCHUNK, offset))
      rval = rest.Utils.GetURL(url_next, parse_json=True)
      logging.debug(json.dumps(rval, sort_keys=True, indent=2))
      articles = rval["results"] if "results" in rval else []
      for article in articles:
        logging.debug(json.dumps(article, sort_keys=True, indent=2))
        if not tags: tags = list(article.keys())
        df = pd.concat([df, pd.DataFrame({tags[j]:[article[tags[j]]] for j in range(len(tags))})])
        n_out+=1
      url_next = rval["next"] if "next" in rval else None
      if not url_next: break
      offset += NCHUNK
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info("n_out: {}".format(n_out))
  return(df)

