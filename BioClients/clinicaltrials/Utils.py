#!/usr/bin/env python3
"""
ClinicalTrials.gov
https://clinicaltrials.gov/api/gui/ref/api_urls (to be retired June 2024)
API v2.0: https://clinicaltrials.gov/data-api/api
"""
import sys,os,re,time,json,logging,requests,tqdm
import urllib,urllib.parse
import pandas as pd
#
API_HOST='clinicaltrials.gov'
API_BASE_PATH='/api/v2'
API_BASE_URL='https://'+API_HOST+API_BASE_PATH
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
def SearchStudies(query, base_url=API_BASE_URL, fout=None):
  study_tags=None; n_out=0; df=None;
  url_base = f"{base_url}/studies?query.cond={urllib.parse.quote(query)}"
  url_base += "&pageSize=50"
  url_base += "&countTotal=true"
  while True:
    url = url_base
    if nextPageToken: url += f"&pageToken={nextPageToken}"
    response = requests.get(url)
    result = response.json()
    studies = result["studies"]
    totalCount = result["totalCount"]
    logging.debug(f"totalCount: {totalCount}")
    nextPageToken = result["nextPageToken"] if "nextPageToken" in result else None
    for study in studies:
      logging.debug(json.dumps(study, indent=2))
      if not study_tags:
        study_tags = list(study.keys())
        for tag in study_tags[:]:
          if type(study[tag]) in (list, dict):
            logging.info(f"Ignoring field: {tag}")
            study_tags.remove(tag)
  
      # Need to flatten and include these modules:
      protocol = study["protocolSection"]
      identification_module = protocol["identificationModule"]
      status_module = protocol["statusModule"]
      sponsor_collaborators_module = protocol["sponsorCollaboratorsModule"]
      oversight_module = protocol["oversightModule"]
      description_module = protocol["descriptionModule"]
      conditions_module = protocol["conditionsModule"]
      design_module = protocol["designModule"]
      arms_interventions_module = protocol["armsInterventionsModule"]
      outcomes_module = protocol["outcomesModule"]
      eligibility_module = protocol["eligibilityModule"]
      references_module = protocol["referencesModule"] if "referencesModule" in protocol else None
  
      derived = study["derivedSection"]
      condition_browse_module = derived["conditionBrowseModule"]
      intervention_browse_module = derived["interventionBrowseModule"] if "interventionBrowseModule" in derived else None
  
      nct_id = identification_module["nctId"]
      brief_title = identification_module["briefTitle"]
      official_title = identification_module["officialTitle"]
  
      organization = identification_module["organization"]
      org_name = organization["fullName"]
      org_class = organization["class"]
  
      has_results = study["hasResults"]
  
      df_this = pd.DataFrame({tag:[study[tag]] for tag in study_tags})
      df_this = pd.concat([df_this,
          pd.DataFrame({
              "nctId":[nct_id],
              "briefTitle":[brief_title],
              "officialTitle":[official_title],
              "orgName":[org_name],
              "orgClass":[org_class],
              "hasResults":[has_results]
              })], axis=1)
  
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += df_this.shape[0]


  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
