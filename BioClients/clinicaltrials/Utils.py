#!/usr/bin/env python3
"""
ClinicalTrials.gov
https://clinicaltrials.gov/api/gui/ref/api_urls
"""
import sys,os,re,time,json,logging,requests,tqdm
import urllib,urllib.parse
import pandas as pd
#
API_HOST='clinicaltrials.gov'
API_BASE_PATH='/api'
API_BASE_URL='https://'+API_HOST+API_BASE_PATH
#
##############################################################################
def ListStudyFields(base_url=API_BASE_URL, fout=None):
  response = requests.get(f"{base_url}/info/study_fields_list?fmt=JSON")
  logging.debug(response.text)
  result = response.json()
  df = pd.DataFrame({'StudyFields': result['StudyFields']['Fields']})
  if fout is not None: df.to_csv(fout, "\t", index=False)
  logging.info(f"n_out: {df.shape[0]}")
  return df

##############################################################################
def DataVersion(base_url=API_BASE_URL, fout=None):
  response = requests.get(f"{base_url}/info/data_vrs?fmt=JSON")
  result = response.json()
  val = result['DataVrs']
  fout.write(f"{val}\n")
  return val

##############################################################################
def ApiVersion(base_url=API_BASE_URL, fout=None):
  response = requests.get(f"{base_url}/info/api_vrs?fmt=JSON")
  result = response.json()
  val = result['APIVrs']
  fout.write(f"{val}\n")
  return val

##############################################################################
def SearchStudies(query, min_rnk, max_rnk, base_url=API_BASE_URL, fout=None):
  study_tags=None; n_out=0; df=None;
  url = f"{base_url}/query/full_studies?expr={urllib.parse.quote(query)}&fmt=JSON"
  url += f"&min_rnk={min_rnk}&max_rnk={max_rnk}"
  response = requests.get(url)
  result = response.json()
  meta = result["FullStudiesResponse"]
  meta_tags = [tag for tag in list(meta.keys()) if type(meta[tag]) not in (list,dict)]
  df_meta = pd.DataFrame({tag:[meta[tag]] for tag in meta_tags})
  df_meta.transpose().to_csv(sys.stderr, "\t", index=True, header=False)
  studies = result["FullStudiesResponse"]["FullStudies"]
  for study in studies:
    logging.debug(json.dumps(study, indent=2))
    if not study_tags:
      study_tags = list(study.keys())
      for tag in study_tags[:]:
        if type(study[tag]) in (list, dict):
          logging.info(f"Ignoring field: {tag}")
          study_tags.remove(tag)

    # Need to flatten and include these modules:
    protocol = study["Study"]["ProtocolSection"]
    identification_module = protocol["IdentificationModule"]
    description_module = protocol["DescriptionModule"]
    conditions_module = protocol["ConditionsModule"]
    design_module = protocol["DesignModule"]
    status_module = protocol["StatusModule"]
    arms_interventions_module = protocol["ArmsInterventionsModule"]
    outcomes_module = protocol["OutcomesModule"]
    eligibility_module = protocol["EligibilityModule"]
    references_module = protocol["ReferencesModule"] if "ReferencesModule" in protocol else None
    derived = study["Study"]["DerivedSection"]
    condition_browse_module = derived["ConditionBrowseModule"]
    intervention_browse_module = derived["InterventionBrowseModule"] if "InterventionBrowseModule" in derived else None

    nct_id = identification_module["NCTId"]
    brief_title = identification_module["BriefTitle"]
    official_title = identification_module["OfficialTitle"]

    df_this = pd.DataFrame({tag:[study[tag]] for tag in study_tags})
    df_this = pd.concat([df_this, pd.DataFrame({"NCTId":[nct_id], "BriefTitle":[brief_title], "OfficialTitle":[official_title]})], axis=1)
    if fout is None: df = pd.concat([df, df_this])
    else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
    n_out += df_this.shape[0]
  logging.info(f"n_out: {n_out}")
  return df

##############################################################################
