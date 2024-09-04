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
def RecommendOntologies(base_url, api_key, texts, fout):
  """This API call designed for text, not necessarily single terms."""
  #input_type={1|2} // default = 1. 1 means that the input type is text. 2 means that the input type is a list of comma separated keywords.
  tags=[]; df=pd.DataFrame(); n_err=0;
  resultTags=["coverageResult", "specializationResult", "acceptanceResult", "detailResult"];
  headers = {"Authorization":f"apikey token={api_key}"}
  for text in texts:
    url_this = base_url+f"/recommender?input={urllib.parse.quote(text)}"
    url_this += "&input_type=2"
    url_this += "&display_context=false&display_links=false"
    logging.debug(url_this)
    rval = requests.get(url_this, headers=headers)
    if not rval.ok:
      logging.error(f'{rval.status_code} : "{text}"')
      n_err+=1
      continue
    results = rval.json()
    for result in results:
      logging.debug(json.dumps(result, indent=2))
      if not tags:
        tags = list(result.keys())
        df_this = pd.DataFrame({tags[j]:([str(result[tags[j]])] if tags[j] in result else ['']) for j in range(len(tags))})
        df = pd.concat([df, df_this])
  if fout: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_texts: {len(texts)}; n_out: {df.shape[0]}; n_err: {n_err}")
  return df

#############################################################################
