#!/usr/bin/env python3
"""
OpenFDA Adverse Events Reports REST API utility functions.

 Reports include multiple reactions with multiple drugs, i.e. many-to-many
 drug-reaction associations.  It is inherently unknown which drug or drug
 combination is explanatory.

 My API key: ==SEE $HOME/.fda.yaml==
 My email: ==SEE $HOME/.fda.yaml==
 
 Query params:
   search	(e.g. search=patient.drug.drugindication:"multiple+myeloma")
   count	(e.g. count=patient.drug.drugindication)
   limit	(e.g. limit=25)
   skip	(e.g. skip=100)
 
 https://api.fda.gov/drug/event.json?search=patient.drug.openfda.pharm_class_epc:"nonsteroidal+anti-inflammatory+drug"&count=patient.reaction.reactionmeddrapt.exact
 
 patient.reaction.reactionmeddrapt  - MedDRA term(s) for the reaction(s).
 
 patient.reaction.reactionmeddraversionpt - The MedDRA version that patient.reaction.reactionmeddrapt uses.
 
 patient.reaction.reactionoutcome - Outcome of the reaction/event at the time of last observation
	1 = recovered/resolved
	2 = recovering/resolving
	3 = not recovered/not resolved
	4 = recovered/resolved with sequelae
	5 = fatal
	6 = unknown
"""
import sys,os,re,time,json,logging
import pandas as pd
#
from ...util import rest
#
REST_RETRY_NMAX=10
REST_RETRY_WAIT=5

DRUG_ID_FIELDS = ['unii','rxcui','nui','spl_id','product_ndc','package_ndc']
DRUG_NAME_FIELDS = ['generic_name','brand_name','substance_name']

API_HOST='api.fda.gov'
API_BASE_PATH='/drug/event.json'
API_BASE_URL='https://'+API_HOST+API_BASE_PATH

##############################################################################
def GetCounts(tfrom, tto, base_url=API_BASE_URL):
  txt=''
  try:
    rval=rest.Utils.GetURL(base_url+f"?search=receivedate:[{tfrom}+TO+{tto}]&count=receivedate")
    txt+=(f"{rval}\n")
  except Exception as e:
    logging.error(str(e))
  return txt

#############################################################################
def Info(base_url=API_BASE_URL):
  url=(base_url+'?search=(serious:1)&limit=1')
  try:
    rval=rest.Utils.GetURL(url,parse_json=True)
  except Exception as e:
    logging.error(str(e))
    return None
  meta = rval['meta']
  return meta

#############################################################################
def GetFields(base_url=API_BASE_URL):
  '''Show fields where value is either (1) string, or (2) list of strings.
Sample first n records.  However no guarantee sampling contains all fields.
'''
  n=100
  url = (base_url+f"?search=(serious:1)&limit={n}")
  try:
    rval=rest.Utils.GetURL(url,parse_json=True)
  except Exception as e:
    logging.error(str(e))
    return None

  logging.info(f"Fields from sampled records, N = {n}")
  fields=set()
  for result in rval['results']:
    fields |= GetFieldsIn(result,'')

  return sorted(list(fields))

#############################################################################
def GetFieldsIn(obj, path):
  fields=set()
  if type(obj) is str: return
  elif type(obj) is list:
    if len(obj)==0 or type(obj[0]) is str: return
    for obj2 in obj:
      fields|=GetFieldsIn(obj2,path)
  elif type(obj) is dict:
    for field in obj.keys():
      path_this = (f"{path}{'.' if path else ''}{field}")
      if type(obj[field]) is str:
        fields.add(path_this)
      elif type(obj[field]) is list:
        if len(obj[field])>0:
          if type(obj[field][0]) is str:
            fields.add(path_this)
          else:
            for obj2 in obj[field]:
              fields|=(GetFieldsIn(obj2, path_this))
      else:
        fields|=GetFieldsIn(obj[field], path_this)
  return fields

#############################################################################
def DrugName(drug):
  name=''
  if 'openfda' in drug :
    for name_field in DRUG_NAME_FIELDS:
      if name_field in drug['openfda'] :
        if len(drug['openfda'][name_field])>0:
          name=drug['openfda'][name_field][0]
          break
    if not name:
      for id_field in DRUG_ID_FIELDS:
        if id_field in drug['openfda']:
          if len(drug['openfda'][id_field])>0:
            name = (f"{id_field}={drug['openfda'][id_field][0]}")
            break
  else:
    if 'medicinalproduct' in drug :
      name=drug['medicinalproduct']
  return name

#############################################################################
def DrugID(drug, id_field):
  if 'openfda' in drug :
    if id_field in drug['openfda'] :
      if len(drug['openfda'][id_field])>0:
        return drug['openfda'][id_field][0]
  return ''

#############################################################################
def Search(drug_cl, drug_ind, drug_unii, drug_ndc, drug_spl, tfrom, tto, serious, fatal, rawquery, nmax, api_key, base_url=API_BASE_URL, fout=None):
  '''The API seems to disallow limit exceeding 100.  So we need to iterate using skip.'''
  rval=None
  url = (base_url+f"?api_key={api_key}&search=")
  qrys=[]
  if drug_cl:	qrys.append(f"(patient.drug.openfda.pharm_class_epc:{drug_cl.replace(' ','+')})")
  if drug_ind:	qrys.append(f"(patient.drug.drugindication:{drug_ind.replace(' ','+')})")
  if drug_unii:	qrys.append(f"(patient.drug.openfda.unii:{drug_unii})")
  if drug_ndc:	qrys.append(f"(patient.drug.openfda.ndc:{drug_ndc})")
  if drug_spl:	qrys.append(f"(patient.drug.openfda.spl:{drug_spl})")
  if fatal:	qrys.append(f"(seriousnessdeath:1)")
  if serious:	qrys.append(f"(serious:1)")
  if tfrom:	qrys.append(f"(receivedate:[{tfrom}+TO+{tto}])")
  if rawquery:	qrys.append(f"({rawquery.replace(' ','+')})")
  if len(qrys)==0:
    logging.error('No query specified.')
    return rval

  url+=('+AND+'.join(qrys))

  drugnames_all = set()
  uniis_all = set()
  rxns_all = set()

  fout.write('ReportID,ReceiptDate,Drugname,UNII,ProductNDC,Seriousness,Event\n')

  ser_counts =  {s:0 for s in ('F','H','S','')}

  fromtime = time.localtime()
  totime = time.strptime('19000101','%Y%m%d')

  ndone=0; nchunk=100; n_report=0;
  while nmax==0 or ndone<nmax:
    if nmax>ndone: nchunk = min(nchunk, nmax-ndone)
    url_this = url+(f"&limit={nchunk}")+(f"&skip={ndone}" if ndone>0 else '')
    try:
      rval = rest.Utils.GetURL(url_this, parse_json=True)
    except Exception as e:
      logging.error(str(e))
      break
    if not rval: break

    results = rval['results']
    logging.debug(f"results: {len(results)}")

    for result in results:
      report_id = result['safetyreportid']
      if not 'drug' in result['patient']:
        logging.error(f"report [ID={report_id}] missing drug[s].")
        continue
      n_report+=1
      reactions = result['patient']['reaction']
      recdate=result['receiptdate']
      rec_time = time.strptime(recdate,'%Y%m%d')
      fromtime = min(fromtime,rec_time)
      totime = max(totime,rec_time)

      drugs = result['patient']['drug']
      ser=('F' if 'seriousnessdeath' in result else ('H' if 'seriousnesshospitalization' in result else ('S' if 'serious' in result else '')))

      ser_counts[ser]+=1

      drugnames = set()
      uniis = set()
      rxns = set()

      for drug in drugs:
        drugname=DrugName(drug)
        unii=DrugID(drug,'unii')
        ndc=DrugID(drug,'product_ndc')
        drugnames.add(drugname)
        uniis.add(unii)

        for reaction in reactions:
          rxn=reaction['reactionmeddrapt']
          fout.write('%s,%s,"%s","%s","%s","%s","%s"\n'%(report_id,recdate,drugname,unii,ndc,ser,rxn))
          rxns.add(rxn)

      logging.debug(f"{n_report}. Report: {report_id} [{recdate}] seriousness: {ser}")
      logging.debug(f"\treactions: {(', '.join(list(rxns)))}")
      logging.debug(f"\tdrugs: {(', '.join(list(drugnames)))}")

      uniis_all |= uniis
      drugnames_all |= drugnames
      rxns_all |= rxns

    logging.debug(json.dumps(rval,indent=2))
    ndone+=nchunk
    if nmax>0 and ndone>=nmax: break

  logging.info(f"reports: {n_report}; drugs: {len(uniis_all)}; reactions: {len(rxns_all)}")
  logging.info(f"report seriousness: {str(ser_counts)} ; total: {sum(ser_counts.values())}")
  logging.info(f"report date range: ({time.strftime('%d %b %Y',fromtime)} - {time.strftime('%d %b %Y',totime)})")
  return
