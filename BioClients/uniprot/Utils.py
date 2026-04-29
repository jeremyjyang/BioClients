#!/usr/bin/env python3
##############################################################################
### Utility functions for access to Uniprot REST API.
### UniprotKB = Uniprot Knowledge Base
### https://www.uniprot.org/api-documentation/uniprotkb
##############################################################################
import sys,os,re,json,logging
#
import requests,tqdm
import pandas as pd
#
API_HOST='rest.uniprot.org'
API_BASE_PATH='/uniprotkb'
DEFAULT_SEARCH_FIELDS='accession,protein_name,organism_name_field,cc_function,reviewed'
#
#############################################################################
def GetNames(base_uri, ids, fout):
  n_out=0; n_err=0; df = None;
  tags_pro = ["entryType", "primaryAccession"]
  params = { "fields": [ "accession", "protein_name" ] }
  headers = { "accept": "application/json" }

  for id_this in ids:
    response = requests.get(f"{base_uri}/{id_this}", headers=headers, params=params)
    #logging.debug(response.text)
    result = response.json()
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    if not response.ok or response.status_code != 200:
      response.raise_for_status()
      logging.error(f"status_code: {response.status_code}")
      n_err+=1
      continue

    df_this_base = pd.DataFrame({tag:([str(result[tag])] if tag in result else ['']) for tag in tags_pro})

    proDes = result['proteinDescription'] if 'proteinDescription' in result else {}

    flag = proDes['flag'] if 'flag' in proDes else None
    df_this_0 = pd.DataFrame({ 'queryId':[id_this], 'flag':[flag] })

    recNam = proDes['recommendedName'] if 'recommendedName' in proDes else {}
    fullNam = recNam['fullName']['value'] if 'fullName' in recNam and 'value' in recNam['fullName'] else None
    shortNams = recNam['shortNames'] if 'shortNames' in recNam else []
    shortNams_str = ";".join([sN['value'] for sN in shortNams])
    altNams = proDes['alternativeNames'] if 'alternativeNames' in proDes else []
    altNams_str = ";".join([(aN['fullName']['value'] if 'fullName' in aN and 'value' in aN['fullName'] else '') for aN in altNams])
    df_this_names = pd.DataFrame({
        'fullName':[fullNam],
        'shortNames':[shortNams_str],
        'altNames':[altNams_str]
        })
    df_this = pd.concat([df_this_0, df_this_base, df_this_names], axis=1)
    if fout is not None:
      df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
      n_out += 1
    if fout is None: df = pd.concat([df, df_this])

  logging.info(f"n_in: {len(ids)}; n_out: {n_out}; n_err: {n_err}")
  return df

#############################################################################
def GetFunctions(base_uri, ids, fout):
  n_out=0; n_err=0; df = None;
  n_comment=0; n_text=0; n_evidence=0;
  tags_pro = ["entryType", "primaryAccession"]
  params = { "fields": [ "accession", "cc_function" ] }
  headers = { "accept": "application/json" }

  for id_this in ids:
    response = requests.get(f"{base_uri}/{id_this}", headers=headers, params=params)
    #logging.debug(response.text)
    result = response.json()
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    if not response.ok or response.status_code != 200:
      response.raise_for_status()
      logging.error(f"status_code: {response.status_code}")
      n_err+=1
      continue

    df_this_base = pd.DataFrame({tag:([str(result[tag])] if tag in result else ['']) for tag in tags_pro})

    df_this_0 = pd.DataFrame({ 'queryId':[id_this] })

    comments = result['comments'] if 'comments' in result else []
    n_out_this=0
    for comment in comments:
      n_comment += 1
      cType = comment['commentType'] if 'commentType' in comment else None
      molecule = comment['molecule'] if 'molecule' in comment else None
      texts = comment['texts'] if 'texts' in comment else []
      for text in texts:
        value = text['value'] if 'value' in text else None
        if not value: continue
        n_text += 1
        evidences = text['evidences'] if 'evidences' in text else []
        for evidence in evidences:
          n_evidence += 1
          evC = evidence['evidenceCode'] if 'evidenceCode' in evidence else None
          evSource = evidence['source'] if 'source' in evidence else None
          evId = evidence['id'] if 'id' in evidence else None
          df_this_ev = pd.DataFrame({
              'commentType':[cType],
              'molecule':[molecule],
              'value':[value],
              'evidenceCode':[evC],
              'evidenceSource':[evSource],
              'evidenceId':[evId]
              })

          df_this = pd.concat([df_this_0, df_this_base, df_this_ev], axis=1)
          if fout is not None:
            df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
            n_out_this+=1
          if fout is None: df = pd.concat([df, df_this])
    if n_out_this>0: n_out+=1

  logging.info(f"n_in: {len(ids)}; n_out: {n_out}; n_comment: {n_comment}; n_text: {n_text}; n_evidence: {n_evidence}; n_err: {n_err}")
  return df

#############################################################################
def ListSearchFields(base_uri, fout):
  df=None; n_out=0;
  tags_base=["id", "groupName", "isDataBaseGroup"];
  tags_field=["id", "label", "name", "isMultiValueCrossReference"];
  headers = { "accept": "application/json" }
  response = requests.get(f"https://{API_HOST}/configure/uniprotkb/result-fields", headers=headers)
  result = response.json()
  logging.debug(json.dumps(result, sort_keys=True, indent=2))
  if not response.ok or response.status_code != 200:
    response.raise_for_status()
    logging.error(f"status_code: {response.status_code}")
  sfs = result
  for sf in sfs:
    #if not tags: tags = [key if type(sf[key]) not in (list, dict) else None for key in sf.keys()]
    df_this_base = pd.DataFrame({tag:[sf[tag]] if tag in sf else None for tag in tags_base})
    df_this_base.columns = ["group_id", "groupName", "isDataBaseGroup"]
    fields = sf['fields'] if 'fields' in sf else []
    for field in fields:
      df_this_field = pd.DataFrame({tag:[field[tag]] if tag in field else None for tag in tags_field})
      df_this_field.columns = ["field_id", "label", "name", "isMultiValueCrossReference"]
      df_this = pd.concat([df_this_base, df_this_field], axis=1)
      if fout is not None:
        df_this.to_csv(fout, sep="\t", index=False, header=bool(n_out==0))
        n_out+=1
    if fout is None: df = pd.concat([df, df_this])
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
def Search(base_uri, query, search_fields, fout):
  n_out=0; n_err=0; df = None;
  n_page=100;
  tags_pro = ["entryType", "primaryAccession"]
  params = { "query": query,
            "size": f"{n_page}",
            "sort": "accession desc",
          "fields": [ "accession", "protein_name", "cc_funtion", "ft_binding" ] }
  headers = { "accept": "application/json" }

  response = requests.get(f"{base_uri}/search", headers=headers, params=params)


#############################################################################
# Probably should discontinue this function.
def GetData(base_uri, ids, fout):
  n_prot=0; n_err=0;
  params = {
    "fields": [
      "accession",
      "protein_name",
      "cc_function",
      "ft_binding"
    ]
  }
  headers = { "accept": "application/json" }

  for id_this in ids:
    response = requests.get(f"{base_uri}/{id_this}", headers=headers, params=params)
    #logging.debug(response.text)
    result = response.json()
    logging.debug(json.dumps(result, sort_keys=True, indent=2))
    if not response.ok or response.status_code != 200:
      response.raise_for_status()
      logging.error(f"status_code: {response.status_code}")
      n_err+=1
      continue

    n_prot+=1
  logging.info(f"n_in: {len(ids)}; n_prot: {n_prot}; n_err: {n_err}")

#############################################################################
