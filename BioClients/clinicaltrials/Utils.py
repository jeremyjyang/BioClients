#!/usr/bin/env python3
"""
ClinicalTrials.gov
https://clinicaltrials.gov/api/gui/ref/api_urls (to be retired June 2024)
API v2.0:
https://clinicaltrials.gov/data-api/about-api
https://clinicaltrials.gov/data-api/api
https://clinicaltrials.gov/find-studies/constructing-complex-search-queries
"""
import sys,os,re,time,json,logging,requests,tqdm
import urllib,urllib.parse
import pandas as pd
#
API_HOST='clinicaltrials.gov'
API_BASE_PATH='/api/v2'
API_BASE_URL='https://'+API_HOST+API_BASE_PATH
API_PAGE_SIZE=50
#
##############################################################################
def Version(base_url=API_BASE_URL, fout=None):
  response = requests.get(f"{base_url}/version")
  result = response.json()
  df = pd.DataFrame(result, index=[0])
  if fout is not None: df.to_csv(fout, sep="\t", index=False)
  return df

##############################################################################
def ListStudyFields(base_url=API_BASE_URL, fout=None):
  response = requests.get(f"{base_url}/studies/metadata")
  logging.debug(response.text)
  result = response.json()
  df = pd.DataFrame(result)
  if fout is not None: df.to_csv(fout, sep="\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

##############################################################################
def ListSearchAreas(base_url=API_BASE_URL, fout=None):
  n_out=0; df=None;
  response = requests.get(f"{base_url}/studies/search-areas")
  logging.debug(response.text)
  result = response.json()
  areas = result[0]["areas"]
  for area in areas:
    name = area["name"]
    param = area["param"] if "param" in area else None
    parts = [part["pieces"][0] for part in area["parts"]]
    df_this = pd.DataFrame({
	"name":[name],
	"param":[param],
	"parts":[";".join(parts)],
	})
    if fout is not None: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    else: pd.concat([df, df_this])
    n_out+=1
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
def ListEnums(base_url=API_BASE_URL, fout=None):
  n_out=0; df=None;
  response = requests.get(f"{base_url}/studies/enums")
  logging.debug(response.text)
  result = response.json()
  enums = result
  for enum in enums:
    values = [value["value"] for value in enum["values"]]
    legacyValues = [value["legacyValue"] for value in enum["values"]]
    #exceptions = enum["exceptions"] if "exceptions" in enum else None #hash
    df_this = pd.DataFrame({
	"type":[enum["type"] for value in values],
	"value":values,
	"legacyValue":legacyValues,
	})
    if fout is not None: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    else: pd.concat([df, df_this])
    n_out+=df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
def SearchStudies(query_cond, query_term, base_url=API_BASE_URL, fout=None):
  study_tags=None; n_out=0; df=None; nextPageToken=None; totalCount=None; tq=None;
  url_base = f"{base_url}/studies?pageSize={API_PAGE_SIZE}"
  if query_cond: url_base += f"&query.cond={urllib.parse.quote(query_cond)}"
  if query_term: url_base += f"&query.term={urllib.parse.quote(query_term)}"
  while True:
    url = url_base
    if not totalCount: url += "&countTotal=true"
    if nextPageToken: url += f"&pageToken={nextPageToken}"
    response = requests.get(url)
    result = response.json()
    if not totalCount: totalCount = result["totalCount"]
    logging.debug(f"totalCount: {totalCount}")
    if not tq: tq = tqdm.tqdm(total=totalCount)
    studies = result["studies"]
    for study in studies:
      logging.debug(json.dumps(study, indent=2))
      tq.update()
      df_this = Study2DataFrame(study)
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]
    nextPageToken = result["nextPageToken"] if "nextPageToken" in result else None
    if not nextPageToken: break
  if tq is not None: tq.close()
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
def GetStudies(ids, base_url=API_BASE_URL, fout=None):
  n_out=0; df=None; tq=None;
  for id_this in ids:
    if not tq: tq = tqdm.tqdm(total=len(ids))
    url = f"{base_url}/studies/{id_this}"
    response = requests.get(url)
    result = response.json()
    study = result
    tq.update()
    logging.debug(json.dumps(study, indent=2))
    df_this = Study2DataFrame(study)
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
    n_out+=1
  if tq is not None: tq.close()
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
def Study2DataFrame(study):
  # What to include? 
  protocol = study["protocolSection"]
  identification_module = protocol["identificationModule"]
  status_module = protocol["statusModule"]
  sponsor_collaborators_module = protocol["sponsorCollaboratorsModule"]
  description_module = protocol["descriptionModule"]
  conditions_module = protocol["conditionsModule"] if "conditionsModule" in protocol else None
  design_module = protocol["designModule"]
  arms_interventions_module = protocol["armsInterventionsModule"] if "armsInterventionsModule" in protocol else None
  outcomes_module = protocol["outcomesModule"] if "outcomesModule" in protocol else None
  eligibility_module = protocol["eligibilityModule"]
  oversight_module = protocol["oversightModule"] if "oversightModule" in protocol else None
  references_module = protocol["referencesModule"] if "referencesModule" in protocol else None
  
  derived = study["derivedSection"]
  condition_browse_module = derived["conditionBrowseModule"] if "conditionBrowseModule" in derived else None
  intervention_browse_module = derived["interventionBrowseModule"] if "interventionBrowseModule" in derived else None
  
  nct_id = identification_module["nctId"]
  brief_title = identification_module["briefTitle"]
  official_title = identification_module["officialTitle"] if "officialTitle" in identification_module else None
  
  organization = identification_module["organization"]
  org_name = organization["fullName"]
  org_class = organization["class"]
  
  has_results = study["hasResults"]
  
  df_this = pd.DataFrame({
          "nctId":[nct_id],
          "briefTitle":[brief_title],
          "officialTitle":[official_title],
          "orgName":[org_name],
          "orgClass":[org_class],
          "hasResults":[has_results]
          })
  return df_this

##############################################################################
