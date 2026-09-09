#!/usr/bin/env python3
"""
"""
import sys,os,re,time,json,logging,requests,tqdm
import urllib,urllib.parse
import pandas as pd
#
RESOLVER_API_HOST='resolver.api.identifiers.org'
RESOLVER_API_BASE_PATH=''
RESOLVER_API_BASE_URL='https://'+RESOLVER_API_HOST+RESOLVER_API_BASE_PATH
#
REGISTRY_API_HOST='registry.api.identifiers.org'
REGISTRY_API_BASE_PATH='/restApi'
REGISTRY_API_BASE_URL='https://'+REGISTRY_API_HOST+REGISTRY_API_BASE_PATH
#
NCHUNK=100
#
##############################################################################
def Resolve(ids, base_url=RESOLVER_API_BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  for id_this in ids:
    response = requests.get(f"{base_url}/{id_this}")
    logging.debug(response.text)
    results = response.json()
    resources = results['payload']['resolvedResources']
    for resource in resources:
      if not tags:
        tags = list(resource.keys())
        for tag in tags[:]:
          if type(resource[tag]) in (list, dict):
            logging.info(f"Ignoring field: {tag}")
            tags.remove(tag)
      df_this = pd.DataFrame({tag:[resource[tag]] for tag in tags})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
def ListEntities(entityname, base_url=REGISTRY_API_BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  page=0; size=NCHUNK;
  while True:
    url_this = f"{base_url}/{entityname}s?page={page}&size={size}"
    response = requests.get(url_this)
    logging.debug(response.text)
    if response.status_code!=200: break
    results = response.json()
    things = results['_embedded'][f"{entityname}s"]
    if not things: break
    for thing in things:
      if not tags:
        tags = list(thing.keys())
        for tag in tags[:]:
          if type(thing[tag]) in (list, dict):
            logging.info(f"Ignoring field: {tag}")
            tags.remove(tag)
      df_this = pd.DataFrame({tag:[thing[tag]] for tag in tags})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
    page+=1
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
def ListNamespaces(base_url=REGISTRY_API_BASE_URL, fout=None):
  return ListEntities("namespace", base_url, fout)

def ListResources(base_url=REGISTRY_API_BASE_URL, fout=None):
  return ListEntities("resource", base_url, fout)

def ListInstitutions(base_url=REGISTRY_API_BASE_URL, fout=None):
  return ListEntities("institution", base_url, fout)

##############################################################################
def SearchEntities(query, search_logic, entityname, base_url=REGISTRY_API_BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  page=0; size=NCHUNK;
  url = f"{base_url}/{entityname}s/search/findByName?name={urllib.parse.quote(query)}" if search_logic=="exact" else f"{base_url}/{entityname}s/search/findByNameContaining?nameContent={urllib.parse.quote(query)}"
  while True:
    url_this = f"{url}&page={page}&size={size}"
    response = requests.get(url_this)
    logging.debug(response.text)
    if response.status_code!=200: break
    results = response.json()
    things = results['_embedded'][f"{entityname}s"]
    if not things: break
    for thing in things:
      if not tags:
        tags = list(thing.keys())
        for tag in tags[:]:
          if type(thing[tag]) in (list, dict):
            logging.info(f"Ignoring field: {tag}")
            tags.remove(tag)
      df_this = pd.DataFrame({tag:[thing[tag]] for tag in tags})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
    page+=1
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
def SearchNamespaces(query, search_logic, base_url=REGISTRY_API_BASE_URL, fout=None):
  return SearchEntities(query, search_logic, "namespace", base_url, fout)

def SearchInstitutions(query, search_logic, base_url=REGISTRY_API_BASE_URL, fout=None):
  return SearchEntities(query, search_logic, "institution", base_url, fout)

##############################################################################
