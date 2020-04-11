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
#
from ...util import rest_utils
#
REST_RETRY_NMAX=10
REST_RETRY_WAIT=5

DRUG_ID_FIELDS = ['unii','rxcui','nui','spl_id','product_ndc','package_ndc']
DRUG_NAME_FIELDS = ['generic_name','brand_name','substance_name']

##############################################################################
def GetCounts(base_url, tfrom, tto):
  txt=''
  try:
    rval=rest_utils.GetURL(base_url+'?search=receivedate:[%s+TO+%s]&count=receivedate'%(tfrom,tto))
    txt+=('%s\n'%(str(rval)))
  except Exception as e:
    logging.error('%s'%(e))
  return txt

#############################################################################
def Info(base_url):
  url=(base_url+'?search=(serious:1)&limit=1')
  try:
    rval=rest_utils.GetURL(url,parse_json=True)
  except Exception as e:
    logging.error('%s'%(e))
    return None
  meta = rval['meta']
  return meta

#############################################################################
def GetFields(base_url):
  '''Show fields where value is either (1) string, or (2) list of strings.
Sample first n records.  However no guarantee sampling contains all fields.
'''
  n=100
  url=(base_url+'?search=(serious:1)&limit=%d'%n)
  try:
    rval=rest_utils.GetURL(url,parse_json=True)
  except Exception as e:
    logging.error('%s'%(e))
    return None

  logging.info('NOTE: Fields from sampled records, N = %d'%n)
  fields=set()
  for result in rval['results']:
    fields |= GetFieldsIn(result,'')

  return sorted(list(fields))

#############################################################################
def GetFieldsIn(obj,path):
  fields=set()
  if type(obj) is str: return
  elif type(obj) is list:
    if len(obj)==0 or type(obj[0]) is str: return
    for obj2 in obj:
      fields|=GetFieldsIn(obj2,path)
  elif type(obj) is dict:
    for field in obj.keys():
      path_this=('%s%s%s'%(path,('.' if path else ''),field))
      if type(obj[field]) is str:
        fields.add(path_this)
      elif type(obj[field]) is list:
        if len(obj[field])>0:
          if type(obj[field][0]) is str:
            fields.add(path_this)
          else:
            for obj2 in obj[field]:
              fields|=(GetFieldsIn(obj2,path_this))
      else:
        fields|=GetFieldsIn(obj[field],path_this)
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
        if id_field in drug['openfda'] :
          if len(drug['openfda'][id_field])>0:
            name=('%s=%s'%(id_field,drug['openfda'][id_field][0]))
            break
  else:
    if 'medicinalproduct' in drug :
      name=drug['medicinalproduct']
  return name

#############################################################################
def DrugID(drug,id_field):
  if 'openfda' in drug :
    if id_field in drug['openfda'] :
      if len(drug['openfda'][id_field])>0:
        return drug['openfda'][id_field][0]
  return ''

#############################################################################
def Search(drug_cl, drug_ind, drug_unii, drug_ndc, drug_spl, tfrom, tto, serious, fatal, rawquery, nmax, fout, base_url, api_key):
  '''The API seems to disallow limit exceeding 100.  So we need to iterate using skip.'''
  rval=None
  url=(base_url+'?api_key=%s&search='%api_key)
  qrys=[]
  if drug_cl:	qrys.append('(patient.drug.openfda.pharm_class_epc:%s)'%(drug_cl.replace(' ','+')))
  if drug_ind:	qrys.append('(patient.drug.drugindication:%s)'%(drug_ind.replace(' ','+')))
  if drug_unii:	qrys.append('(patient.drug.openfda.unii:%s)'%(drug_unii))
  if drug_ndc:	qrys.append('(patient.drug.openfda.ndc:%s)'%(drug_ndc))
  if drug_spl:	qrys.append('(patient.drug.openfda.spl:%s)'%(drug_spl))
  if fatal:	qrys.append('(seriousnessdeath:1)')
  if serious:	qrys.append('(serious:1)')
  if tfrom:	qrys.append('(receivedate:[%s+TO+%s])'%(tfrom,tto))
  if rawquery:	qrys.append('(%s)'%rawquery.replace(' ','+'))
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
    if nmax>ndone: nchunk=min(nchunk,nmax-ndone)
    url_this=url+('&limit=%d'%(nchunk))+('&skip=%d'%ndone if ndone>0 else '')

    logging.debug('url="%s"'%url_this)
    try:
      rval=rest_utils.GetURL(url_this,parse_json=True)
    except Exception as e:
      logging.error('%s'%(e))
      break
    if not rval: break

    results = rval['results']
    logging.debug('results: %d'%len(results))

    for result in results:
      report_id = result['safetyreportid']
      if not 'drug' in result['patient'] :
        logging.error('report [ID=%s] missing drug[s].'%(report_id))
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

      logging.debug('%d. Report: %s [%s] seriousness: %s'%(n_report,report_id,recdate,ser))
      logging.debug('\treactions: %s'%(', '.join(list(rxns))))
      logging.debug('\tdrugs: %s'%(', '.join(list(drugnames))))

      uniis_all |= uniis
      drugnames_all |= drugnames
      rxns_all |= rxns

    logging.debug(json.dumps(rval,indent=2))
    ndone+=nchunk
    if nmax>0 and ndone>=nmax: break

  logging.info('reports: %d ; drugs: %d ; reactions: %d'%(n_report,len(uniis_all),len(rxns_all)))
  logging.info('report seriousness: %s ; total: %d'%(str(ser_counts),sum(ser_counts.values())))
  logging.info('report date range: (%s - %s)'%(time.strftime('%d %b %Y',fromtime),time.strftime('%d %b %Y',totime)))

  return
