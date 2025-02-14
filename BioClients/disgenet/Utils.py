#!/usr/bin/env python3
"""
 https://www.disgenet.org/api/
 https://www.disgenet.org/dbinfo
 DisGeNET Disease Types : disease, phenotype, group
"""
###
import sys,os,io,re,time,requests,json,logging
import pandas as pd
#
API_HOST='api.disgenet.com'
API_BASE_PATH='/api/v1'
BASE_URL='https://'+API_HOST+API_BASE_PATH
#
SOURCES = [
	"CURATED",
	"INFERRED",
	"ANIMAL_MODELS",
	"ALL",
	"BEFREE",
	"CGI",
	"CLINGEN",
	"CLINVAR",
	"CTD_human",
	"CTD_mouse",
	"CTD_rat",
	"GENOMICS_ENGLAND",
	"GWASCAT",
	"GWASDB",
	"HPO",
	"LHGDN",
	"MGD",
	"ORPHANET",
	"PSYGENET",
	"RGD",
	"UNIPROT" ]
DISEASE_TYPES = ["disease", "phenotype", "group"]
DISEASE_CLASSES = [ # MeSH Disease classes:
 "C01", # Bacterial Infections and Mycoses
 "C02", # Virus Diseases
 "C03", # Parasitic Diseases
 "C04", # Neoplasms
 "C05", # Musculoskeletal Diseases
 "C06", # Digestive System Diseases
 "C07", # Stomatognathic Diseases
 "C08", # Respiratory Tract Diseases
 "C09", # Otorhinolaryngologic Diseases
 "C10", # Nervous System Diseases
 "C11", # Eye Diseases
 "C12", # Male Urogenital Diseases
 "C13", # Female Urogenital Diseases and Pregnancy Complications
 "C14", # Cardiovascular Diseases
 "C15", # Hemic and Lymphatic Diseases
 "C16", # Congenital, Hereditary, and Neonatal Diseases and Abnormalities
 "C17", # Skin and Connective Tissue Diseases
 "C18", # Nutritional and Metabolic Diseases
 "C19", # Endocrine System Diseases
 "C20", # Immune System Diseases
 "C21", # Disorders of Environmental Origin
 "C22", # Animal Diseases
 "C23", # Pathological Conditions, Signs and Symptoms
 "C24", # Occupational Diseases
 "C25", # Substance-Related Disorders
 "C26", # Wounds and Injuries
 "F01", # Behavior and Behavior Mechanisms
 "F02", # Psychological Phenomena
 "F03", # Mental Disorders
	]
GENEID_TYPES = ["ncbi", "ensembl", "symbol", "uniprot"]
#
##############################################################################
def GetApiKey(session, user_email, user_password, base_url=BASE_URL):
  api_key=None;
  auth_params = {"email":user_email, "password":user_password}
  url = f"{base_url}/auth/"
  logging.debug(f"URL: {url}")
  try:
    response = session.post(url, data=auth_params)
    if (response.status_code==200):
      json_response = response.json()
      api_key = json_response.get("token")
      session.headers.update({"Authorization": f"Bearer {api_key}"})
    else:
      logging.error(f"GetApiKey failed (status_code={response.status_code}): {response.text}")
  except requests.exceptions.RequestException as e:
    logging.error(f"GetApiKey failed: {e}")
  logging.debug(f"api_key: {api_key}")
  return api_key

##############################################################################
def GetVersion(api_key, base_url=BASE_URL, fout=None):
  headers={'Authorization': api_key, 'Accept': 'application/json'}
  url = f"{base_url}/public/version"
  response = requests.get(url, headers=headers)
  #logging.debug(response.text)
  results = response.json()["payload"]
  logging.debug(json.dumps(results, indent=2))
  df = pd.DataFrame(results, index=[0])
  if fout is not None: df.to_csv(fout, sep='\t', index=False)
  return df

##############################################################################
def GetDiseaseGDAs(ids, source, api_key, base_url=BASE_URL, fout=None):
  tags=[]; n_out=0; df=None;
  headers={'Authorization': api_key, 'Accept': 'application/json'}
  url = f"{base_url}/gda/summary"
  params = {'source': source}
  for id_this in ids:
    params['disease'] = f"{id_this}"
    response = requests.get(url, params=params, headers=headers)
    results = response.json()
    logging.debug(json.dumps(results, indent=2))
    gdas = results["payload"]
    for gda in gdas:
      if not tags:
        tags = [tag for tag in gda.keys() if type(gda[tag]) not in (list,dict)]
      df_this = pd.DataFrame({tag:[gda[tag] if tag in gda else ""] for tag in tags})
      if fout is not None: df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
      else: df = pd.concat([df, df_this])
      n_out+=1
  logging.info(f"IDs: {len(ids)}; GDAs: {n_out}")
  return df

##############################################################################
def GetDiseases(ids, dtype, dclasses, nmax, api_key, base_url=BASE_URL, fout=None):
  n_out=0; df=None;
  tags = ["name", "type", "diseaseClasses_MSH", "diseaseClasses_UMLS_ST", "diseaseClasses_DO", "diseaseClasses_HPO", "diseaseCodes", "synonyms"];
  headers={'Authorization': api_key, 'Accept': 'application/json'}
  url = f"{base_url}/entity/disease"
  params = {}
  for id_this in ids:
    params['disease'] = f"{id_this}"
    if dtype is not None: params['type'] = dtype
    if dclasses is not None: params['dis_class_list'] = dclasses
    response = requests.get(url, params=params, headers=headers)
    if not response.ok:
      if response.status_code == 429:
        while response.ok is False:
          logging.info("Query limit reached; waiting {}s...".format(response.headers['x-rate-limit-retry-after-seconds']))
          time.sleep(int(response.headers['x-rate-limit-retry-after-seconds']))
          response = requests.get(url, params=params, headers=headers)
          if response.ok is True:
            break
          else:
            continue
    results = response.json()
    logging.debug(json.dumps(results, indent=2))
    diseases = results["payload"]
    for disease in diseases:
      d={}
      for tag in tags:
        if tag not in disease:
          d[tag] = None
        elif tag == "diseaseCodes":
            d[tag] = ";".join([f"{s['vocabulary']}:{s['code']}" for s in disease[tag]])
        elif tag == "synonyms":
          d[tag] = ";".join([s["name"] for s in disease[tag]])
        elif type(disease[tag]) not in (list,dict):
          d[tag] = disease[tag]
        elif type(disease[tag]) is list:
          d[tag] = ";".join([str(x) for x in disease[tag]])
      df_this = pd.DataFrame(d, index=[0])
      if df_this is None: continue
      if fout is not None: df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
      else: df = pd.concat([df, df_this])
      n_out+=df_this.shape[0]
  logging.info(f"Diseases: {n_out}")
  return df

##############################################################################
def GetGeneGDAs(ids, geneid_type, source, api_key, base_url=BASE_URL, fout=None):
  '''NCBI Entrez Identifier or HGNC Symbol'''
  tags=[]; n_out=0; df=None;
  headers={'Authorization': api_key, 'Accept': 'application/json'}
  url = f"{base_url}/gda/summary"
  params = {'source': source}
  for id_this in ids:
    if geneid_type == "ncbi":
      params["gene_ncbi_id"] = id_this
    elif geneid_type == "ensembl":
      params["gene_ensembl_id"] = id_this
    elif geneid_type == "uniprot":
      params["uniprot_id"] = id_this
    else:
      params["gene_symbol"] = id_this
    response = requests.get(url, params=params, headers=headers)
    results = response.json()
    logging.debug(json.dumps(results, indent=2))
    gdas = results["payload"]
    for gda in gdas:
      if not tags:
        tags = list(gda.keys())
        for tag in tags[:]:
          if type(gda[tag]) in (list,dict):
            tags.remove(tag)
            logging.info(f"Ignoring field: {tag}")
      df_this = pd.DataFrame({tag:[gda[tag] if tag in gda else ""] for tag in tags})
      if fout is not None: df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
      else: df = pd.concat([df, df_this])
      n_out+=1
  logging.info(f"IDs: {len(ids)}; GDAs: {n_out}")
  return df

##############################################################################
