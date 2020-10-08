#!/usr/bin/env python3
"""
TIN-X (Target Importance and Novelty Explorer) REST API client
https://www.newdrugtargets.org/
https://api.newdrugtargets.org/docs
https://api.newdrugtargets.org/targets/
"""
###
import sys,os,re,json,time,logging
import urllib,urllib.parse
#
from ..util import rest
#
NCHUNK=100;
#
##############################################################################
def ListTargets(base_url, skip, nmax, fout):
  n_out=0; tags=None;
  url_next = (base_url+'/targets/?limit=%d&offset=%d'%(NCHUNK, skip))
  while True:
    rval = rest.Utils.GetURL(url_next, parse_json=True)
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    targets = rval["results"] if "results" in rval else []
    for target in targets:
      logging.debug(json.dumps(target, sort_keys=True, indent=2))
      if not tags:
        tags = list(target.keys())
        fout.write('\t'.join(tags)+'\n')
      vals = [(str(target[tag]) if tag in target else '') for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    count = rval["count"] if "count" in rval else None
    if n_out%1000==0: logging.info("%d/%s done"%(n_out, count))
    url_next = rval["next"] if "next" in rval else None
    if not url_next: break
  logging.info("n_out: %d"%(n_out))

##############################################################################
def SearchTargets(base_url, terms, skip, nmax, fout):
  n_out=0; tags=None;
  for term in terms:
    url_next = (base_url+'/targets/?search=%s'%(urllib.parse.quote(term)))
    while True:
      rval = rest.Utils.GetURL(url_next, parse_json=True)
      logging.debug(json.dumps(rval, sort_keys=True, indent=2))
      targets = rval["results"] if "results" in rval else []
      for target in targets:
        logging.debug(json.dumps(target, sort_keys=True, indent=2))
        if not tags:
          tags = list(target.keys())
          fout.write('\t'.join(tags)+'\n')
        vals = [(str(target[tag]) if tag in target else '') for tag in tags]
        fout.write('\t'.join(vals)+'\n')
        n_out+=1
        if nmax and n_out>=nmax: break
      if nmax and n_out>=nmax: break
      url_next = rval["next"] if "next" in rval else None
      if not url_next: break
  logging.info("n_out: %d"%(n_out))

##############################################################################
def ListDiseases(base_url, skip, nmax, fout):
  n_out=0; tags=None;
  url_next = (base_url+'/diseases/?limit=%d&offset=%d'%(NCHUNK, skip))
  while True:
    rval = rest.Utils.GetURL(url_next, parse_json=True)
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    diseases = rval["results"] if "results" in rval else []
    for disease in diseases:
      logging.debug(json.dumps(disease, sort_keys=True, indent=2))
      if not tags:
        tags = list(disease.keys())
        fout.write('\t'.join(tags)+'\n')
      vals = [(str(disease[tag]) if tag in disease else '') for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    count = rval["count"] if "count" in rval else None
    if n_out%1000==0: logging.info("%d/%s done"%(n_out, count))
    url_next = rval["next"] if "next" in rval else None
    if not url_next: break
  logging.info("n_out: %d"%(n_out))

##############################################################################
def ListArticles(base_url, skip, nmax, fout):
  n_out=0; tags=None;
  url_next = (base_url+'/articles/?limit=%d&offset=%d'%(NCHUNK, skip))
  while True:
    rval = rest.Utils.GetURL(url_next, parse_json=True)
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    articles = rval["results"] if "results" in rval else []
    for article in articles:
      logging.debug(json.dumps(article, sort_keys=True, indent=2))
      if not tags:
        tags = list(article.keys())
        fout.write('\t'.join(tags)+'\n')
      vals = [(str(article[tag]) if tag in article else '') for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    count = rval["count"] if "count" in rval else None
    if n_out%1000==0: logging.info("%d/%s done"%(n_out, count))
    url_next = rval["next"] if "next" in rval else None
    if not url_next: break
  logging.info("n_out: %d"%(n_out))

##############################################################################
def ListDTO(base_url, skip, nmax, fout):
  n_out=0; tags=None;
  url_next = (base_url+'/dto/?limit=%d&offset=%d'%(NCHUNK, skip))
  while True:
    rval = rest.Utils.GetURL(url_next, parse_json=True)
    logging.debug(json.dumps(rval, sort_keys=True, indent=2))
    dtos = rval["results"] if "results" in rval else []
    for dto in dtos:
      logging.debug(json.dumps(dto, sort_keys=True, indent=2))
      if not tags:
        tags = list(dto.keys())
        fout.write('\t'.join(tags)+'\n')
      vals = [(str(dto[tag]) if tag in dto else '') for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
      if nmax and n_out>=nmax: break
    if nmax and n_out>=nmax: break
    count = rval["count"] if "count" in rval else None
    if n_out%1000==0: logging.info("%d/%s done"%(n_out, count))
    url_next = rval["next"] if "next" in rval else None
    if not url_next: break
  logging.info("n_out: %d"%(n_out))

##############################################################################
def GetDisease(base_url, ids, skip, nmax, fout):
  """IDs should be TIN-X disease IDs, e.g. 5391."""
  n_in=0; n_out=0; tags=None;
  for id_this in ids:
    n_in+=1
    if skip and skip>n_in: continue
    disease = rest.Utils.GetURL((base_url+'/diseases/%s/'%id_this), parse_json=True)
    logging.debug(json.dumps(disease, sort_keys=True, indent=2))
    if not tags:
      tags = list(disease.keys())
      fout.write('\t'.join(tags)+'\n')
    vals = [(str(disease[tag]) if tag in disease else '') for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
    if nmax and n_in>=nmax: break
  logging.info("n_in: %d; n_out: %d"%(n_in, n_out))

##############################################################################
def GetDiseaseByDOId(base_url, ids, skip, nmax, fout):
  """IDs should be Disease Ontology IDs, e.g. DOID:9297."""
  n_in=0; n_out=0; tags=None;
  for id_this in ids:
    n_in+=1
    if skip and skip>n_in: continue
    rval = rest.Utils.GetURL((base_url+'/diseases/?doid=%s'%id_this), parse_json=True)
    diseases = rval["results"] if "results" in rval else []
    for disease in diseases:
      logging.debug(json.dumps(disease, sort_keys=True, indent=2))
      if not tags:
        tags = list(disease.keys())
        fout.write('\t'.join(tags)+'\n')
      vals = [(str(disease[tag]) if tag in disease else '') for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
    if nmax and n_in>=nmax: break
  logging.info("n_in: %d; n_out: %d"%(n_in, n_out))

##############################################################################
def GetTarget(base_url, ids, skip, nmax, fout):
  """IDs should be TIN-X target IDs, e.g. 10027."""
  n_in=0; n_out=0; tags=None;
  for id_this in ids:
    n_in+=1
    if skip and skip>n_in: continue
    target = rest.Utils.GetURL((base_url+'/targets/%s/'), parse_json=True)
    logging.debug(json.dumps(target, sort_keys=True, indent=2))
    if not tags:
      tags = list(target.keys())
      fout.write('\t'.join(tags)+'\n')
    vals = [(str(target[tag]) if tag in target else '') for tag in tags]
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
    if nmax and n_in>=nmax: break
  logging.info("n_in: %d; n_out: %d"%(n_in, n_out))

##############################################################################
def GetTargetByUniprot(base_url, ids, skip, nmax, fout):
  """IDs should be UniProt IDs, e.g. Q9H4B4."""
  n_in=0; n_out=0; tags=None;
  for id_this in ids:
    n_in+=1
    if skip and skip>n_in: continue
    rval = rest.Utils.GetURL((base_url+'/targets/?uniprot=%s'), parse_json=True)
    targets = rval["results"] if "results" in rval else []
    for target in targets:
      logging.debug(json.dumps(target, sort_keys=True, indent=2))
      if not tags:
        tags = list(target.keys())
        fout.write('\t'.join(tags)+'\n')
      vals = [(str(target[tag]) if tag in target else '') for tag in tags]
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
    if nmax and n_in>=nmax: break
  logging.info("n_in: %d; n_out: %d"%(n_in, n_out))

##############################################################################
def GetTargetDiseases(base_url, ids, skip, nmax, fout):
  """IDs should be TIN-X target IDs, e.g. 10027."""
  n_in=0; n_out=0; tags=None;
  for id_this in ids:
    n_in+=1
    if skip and skip>n_in: continue
    while True:
      url_next = (base_url+'/targets/%s/diseases'%id_this)
      rval = rest.Utils.GetURL(url_next, parse_json=True)
      diseases = rval["results"] if "results" in rval else []
      for disease in diseases:
        logging.debug(json.dumps(disease, sort_keys=True, indent=2))
        phenotype = disease["disease"] if "disease" in disease else {}
        if not tags:
          tags = list(disease.keys())
          tags.remove("disease")
          phenotype_tags = list(phenotype.keys())
          fout.write('\t'.join(["tinx_target_id"]+tags+phenotype_tags)+'\n')
        vals = [id_this]
        vals.extend([(str(disease[tag]) if tag in disease else '') for tag in tags])
        vals.extend([(str(phenotype[tag]) if tag in phenotype else '') for tag in phenotype_tags])
        fout.write('\t'.join(vals)+'\n')
        n_out+=1
      url_next = rval["next"] if "next" in rval else None
      if not url_next: break
    if nmax and n_in>=nmax: break
  logging.info("n_in: %d; n_out: %d"%(n_in, n_out))

##############################################################################
def GetDiseaseTargets(base_url, ids, skip, nmax, fout):
  """IDs should be TIN-X disease IDs, e.g. 5391."""
  n_in=0; n_out=0; tags=None;
  for id_this in ids:
    n_in+=1
    if skip and skip>n_in: continue
    while True:
      url_next = (base_url+'/diseases/%s/targets'%id_this)
      rval = rest.Utils.GetURL(url_next, parse_json=True)
      targets = rval["results"] if "results" in rval else []
      for target in targets:
        logging.debug(json.dumps(target, sort_keys=True, indent=2))
        protein = target["target"] if "target" in target else {}
        if not tags:
          tags = list(target.keys())
          tags.remove("target")
          protein_tags = list(protein.keys())
          fout.write('\t'.join(["tinx_disease_id"]+tags+protein_tags)+'\n')
        vals = [id_this]
        vals.extend([(str(target[tag]) if tag in target else '') for tag in tags])
        vals.extend([(str(protein[tag]) if tag in protein else '') for tag in protein_tags])
        fout.write('\t'.join(vals)+'\n')
        n_out+=1
      url_next = rval["next"] if "next" in rval else None
      if not url_next: break
    if nmax and n_in>=nmax: break
  logging.info("n_in: %d; n_out: %d"%(n_in, n_out))

##############################################################################
def GetDiseaseTargetArticles(base_url, disease_ids, ids, skip, nmax, fout):
  """IDs should be TIN-X disease and target IDs and, e.g. 5391, 12203."""
  n_out=0; tags=None;
  for did in disease_ids:
    for tid in ids:
      url_next = (base_url+'/diseases/%s/targets/%s/articles'%(did, tid))
      while True:
        rval = rest.Utils.GetURL(url_next, parse_json=True)
        articles = rval["results"] if "results" in rval else []
        for article in articles:
          logging.debug(json.dumps(article, sort_keys=True, indent=2))
        if not tags:
          tags = list(article.keys())
          fout.write('\t'.join(tags)+'\n')
        vals = [(str(article[tag]) if tag in article else '') for tag in tags]
        fout.write('\t'.join(vals)+'\n')
        n_out+=1
        url_next = rval["next"] if "next" in rval else None
        if not url_next: break
  logging.info("n_out: %d"%(n_out))

##############################################################################
def SearchDiseases(base_url, terms, skip, nmax, fout):
  """Search names; begins-with search logic."""
  n_out=0; tags=None;
  for term in terms:
    url_next = (base_url+'/diseases/?search=%s'%(urllib.parse.quote(term)))
    while True:
      rval = rest.Utils.GetURL(url_next, parse_json=True)
      logging.debug(json.dumps(rval, sort_keys=True, indent=2))
      diseases = rval["results"] if "results" in rval else []
      for disease in diseases:
        logging.debug(json.dumps(disease, sort_keys=True, indent=2))
        if not tags:
          tags = list(disease.keys())
          fout.write('\t'.join(tags)+'\n')
        vals = [(str(disease[tag]) if tag in disease else '') for tag in tags]
        fout.write('\t'.join(vals)+'\n')
        n_out+=1
        if nmax and n_out>=nmax: break
      if nmax and n_out>=nmax: break
      url_next = rval["next"] if "next" in rval else None
      if not url_next: break
  logging.info("n_out: %d"%(n_out))

##############################################################################
def SearchTargets(base_url, terms, skip, nmax, fout):
  """Search names."""
  n_out=0; tags=None;
  for term in terms:
    url_next = (base_url+'/targets/?search=%s'%(urllib.parse.quote(term)))
    while True:
      rval = rest.Utils.GetURL(url_next, parse_json=True)
      logging.debug(json.dumps(rval, sort_keys=True, indent=2))
      targets = rval["results"] if "results" in rval else []
      for target in targets:
        logging.debug(json.dumps(target, sort_keys=True, indent=2))
        if not tags:
          tags = list(target.keys())
          fout.write('\t'.join(tags)+'\n')
        vals = [(str(target[tag]) if tag in target else '') for tag in tags]
        fout.write('\t'.join(vals)+'\n')
        n_out+=1
        if nmax and n_out>=nmax: break
      if nmax and n_out>=nmax: break
      url_next = rval["next"] if "next" in rval else None
      if not url_next: break
  logging.info("n_out: %d"%(n_out))

##############################################################################
def SearchArticles(base_url, terms, skip, nmax, fout):
  n_out=0; tags=None;
  for term in terms:
    url_next = (base_url+'/articles/?search=%s'%(urllib.parse.quote(term)))
    while True:
      rval = rest.Utils.GetURL(url_next, parse_json=True)
      logging.debug(json.dumps(rval, sort_keys=True, indent=2))
      articles = rval["results"] if "results" in rval else []
      for article in articles:
        logging.debug(json.dumps(article, sort_keys=True, indent=2))
        if not tags:
          tags = list(article.keys())
          fout.write('\t'.join(tags)+'\n')
        vals = [(str(article[tag]) if tag in article else '') for tag in tags]
        fout.write('\t'.join(vals)+'\n')
        n_out+=1
        if nmax and n_out>=nmax: break
      if nmax and n_out>=nmax: break
      url_next = rval["next"] if "next" in rval else None
      if not url_next: break
  logging.info("n_out: %d"%(n_out))

