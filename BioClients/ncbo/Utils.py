#!/usr/bin/env python3
"""
http://data.bioontology.org/documentation
The National Center for Biomedical Ontology was founded as one of the National Centers for Biomedical Computing, supported by the NHGRI, the NHLBI, and the NIH Common Fund.

An API Key is required to access any API call. It can be provided in three ways:

1. Using the apikey query string parameter.
2. Providing an Authorization header: Authorization: apikey token=your_apikey (replace `your_apikey` with your actual key)
3. When using a web browser to explore the API, if you provide your API Key once using method 1, it will be stored in a cookie for subsequent requests. You can override this by providing a different API Key in a new call.
"""
###
import sys,os,re,json,requests,urllib.parse,logging,time
import pandas as pd
#
from ..util import rest
#
API_HOST="data.bioontology.org"
API_BASE_PATH=""
#
#############################################################################
def RecommendOntologies(base_url, api_key, terms, fout):
  tags=[]; df=pd.DataFrame(); n_err=0;
  headers = {"Authorization":f"apikey token={api_key}"}
  for term in terms:
    url_this = base_url+f"/recommender?input={urllib.parse.quote(term)}"
    logging.debug(url_this)
    rval = requests.get(url_this, headers=headers)
    if not rval.ok:
      logging.error(f'{rval.status_code} : "{term}"')
      n_err+=1
      continue
    recos = rval.json()
    for reco in recos:
      logging.debug(json.dumps(reco, indent=2))
      evaluationScore = reco["evaluationScore"] if "evaluationScore" in reco else []
      ontos = reco["ontologies"] if "ontologies" in reco else []
      for onto in ontos:
        if not tags:
          for tag in onto.keys():
            if type(onto[tag]) not in (list, dict): tags.append(tag) #Only simple metadata.
        df_this = pd.DataFrame({tags[j]:([str(onto[tags[j]])] if tags[j] in onto else ['']) for j in range(len(tags))})
        df_this["evaluationScore"] = [evaluationScore]
        df = pd.concat([df, df_this])
  if fout: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_terms: {len(terms)}; n_out: {df.shape[0]}; n_err: {n_err}")
  return df


#############################################################################
