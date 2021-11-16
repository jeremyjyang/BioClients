#!/usr/bin/env python3
"""
 https://www.disgenet.org/api/
 https://www.disgenet.org/dbinfo
 DisGeNET Disease Types : disease, phenotype, group
 DisGeNET Metrics:
   GDA Score
   VDA Score
   Disease Specificity Index (DSI)
   Disease Pleiotropy Index (DPI)
   Evidence Level (EL)
   Evidence Index (EI)
 GNOMAD pLI (Loss-of-function Intolerant)

 DisGeNET Association Types:
   Therapeutic
   Biomarker
   Genomic Alterations
   GeneticVariation
   Causal Mutation
   Germline Causal Mutation
   Somatic Causal Mutation
   Chromosomal Rearrangement
   Fusion Gene
   Susceptibility Mutation
   Modifying Mutation
   Germline Modifying Mutation
   Somatic Modifying Mutation
   AlteredExpression
   Post-translational Modification
"""
###
import sys,os,io,re,time,requests,json,logging
import pandas as pd
#
API_HOST='www.disgenet.org'
API_BASE_PATH='/api'
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
def GetVersion(user_email, user_password, base_url=BASE_URL, fout=None):
  session = requests.Session()
  api_key = GetApiKey(session, user_email, user_password, base_url)
  if api_key is None: return
  url = f"{base_url}/version/"
  response = session.get(url, params={'format':'tsv'})
  df = pd.read_csv(io.StringIO(response.text), sep='\t')
  if fout is not None: df.to_csv(fout, sep='\t', index=False)
  return df

##############################################################################
def GetGeneGDAs(ids, source, user_email, user_password, base_url=BASE_URL, fout=None):
  '''NCBI Entrez Identifier or HGNC Symbol'''
  tags=[]; n_out=0; df=None;
  session = requests.Session()
  api_key = GetApiKey(session, user_email, user_password, base_url)
  if api_key is None: return
  params = {'source': source}
  for id_this in ids:
    url = f"{base_url}/gda/gene/{id_this}"
    response = session.get(url, params=params)
    gdas = response.json()
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
  session.close()
  logging.info(f"IDs: {len(ids)}; GDAs: {n_out}")
  return df

##############################################################################
def GetDiseaseGDAs(ids, source, user_email, user_password, base_url=BASE_URL, fout=None):
  tags=[]; n_out=0; df=None;
  session = requests.Session()
  api_key = GetApiKey(session, user_email, user_password, base_url)
  if api_key is None: return
  logging.debug(f"HEADERS: {session.headers}")
  params = {'source': source}
  for id_this in ids:
    url = f"{base_url}/gda/disease/{id_this}"
    response = session.get(url, params=params)
    gdas = response.json()
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
def GetProteinGDAs(ids, source, user_email, user_password, base_url=BASE_URL, fout=None):
  """Uniprot protein accession."""
  tags=[]; n_out=0; df=None;
  session = requests.Session()
  api_key = GetApiKey(session, user_email, user_password, base_url)
  if api_key is None: return
  for id_this in ids:
    url = f"{base_url}/gda/uniprot/{id_this}?source={source}"
    response = requests.get(url, headers=headers)
    gdas = response.json()
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
def ListDiseases(user_email, user_password, base_url=BASE_URL, fout=None):
  tags=[]; n_out=0; df=None;
  session = requests.Session()
  api_key = GetApiKey(session, user_email, user_password, base_url)
  if api_key is None: return
  for source in SOURCES:
    url = f"{base_url}/disease/source/{source}"
    params = {'format':'tsv'}
    response = session.get(url, params=params)
    if (response.status_code!=200):
      logging.error(f"(status_code={response.status_code}): source: {source}")
      continue
    df_this = pd.read_csv(io.StringIO(response.text), sep='\t')
    if fout is not None: df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
    else: df = pd.concat([df, df_this])
    n_out+=df_this.shape[0]
  logging.info(f"Diseases: {n_out}")

##############################################################################
def GetDiseases(source, dtype, dclass, nmax, user_email, user_password, base_url=BASE_URL, fout=None):
  tags=[]; n_out=0; df=None;
  session = requests.Session()
  api_key = GetApiKey(session, user_email, user_password, base_url)
  if api_key is None: return
  url = f"{base_url}/disease/source/{source}"
  params = {'format':'tsv'}
  if dtype is not None: params['type'] = dtype
  if dclass is not None: params['disease_class'] = dclass
  if nmax is not None: params['limit'] = nmax
  response = session.get(url, params=params)
  #logging.debug(response.text)
  df = pd.read_csv(io.StringIO(response.text), sep='\t')
  if fout is not None: df.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
  n_out+=df.shape[0]
  logging.info(f"Diseases: {n_out}")

##############################################################################
