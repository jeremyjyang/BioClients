#!/usr/bin/env python3
'''
Utility functions for PUG-SOAP API (pre-REST) (~2010).
'''
import sys,os,io,re,urllib.request,time,logging

from xml.etree import ElementTree
#from xml.parsers import expat

from ...util import rest_utils
from ...util import xml_utils

XMLHEADER=("""<?xml version="1.0" encoding="UTF-8"?>""")

#############################################################################
def QueryPug_qkey(pugurl, qkey, webenv, fmt='smiles', do_gz=False):
  
  qxml='''\
<PCT-Data><PCT-Data_input><PCT-InputData>
  <PCT-InputData_download><PCT-Download> 
    <PCT-Download_uids><PCT-QueryUids>
      <PCT-QueryUids_entrez><PCT-Entrez>
        <PCT-Entrez_db>pccompound</PCT-Entrez_db>
        <PCT-Entrez_query-key>%(QKEY)s</PCT-Entrez_query-key>
        <PCT-Entrez_webenv>%(WEBENV)s</PCT-Entrez_webenv>
      </PCT-Entrez></PCT-QueryUids_entrez>
    </PCT-QueryUids></PCT-Download_uids>
    <PCT-Download_format value="%(FMT)s"/>
    <PCT-Download_compression value="%(COMPRES)s"/>
  </PCT-Download></PCT-InputData_download>
</PCT-InputData></PCT-Data_input></PCT-Data>
'''%{'QKEY':qkey, 'WEBENV':webenv, 'FMT':fmt, 'COMPRES':('gzip' if do_gz else 'none')}
  logging.info('Connecting {}...'.format(pugurl))
  logging.info('Submitting query for qkey: {} ...'.format(qkey))

  pugxml = rest_utils.PostURL(pugurl, data=(XMLHEADER+qxml),
	headers={"Accept":"text/soap+xml; charset=utf-8", "SOAPAction":"http://pubchem.ncbi.nlm.nih.gov/Download"})

  status,reqid,url,qkey,wenv,error = ParsePugXml(pugxml)
  return status,reqid,url,qkey,wenv,error

#############################################################################
def QueryPug_struct(pugurl, smiles, searchtype, sim_cutoff, active=False, mlsmr=False, nmax=10000):
  """	 <PCT-CSIdentity value="same-isotope">4</PCT-CSIdentity>
  """
  qxml='''\
<PCT-Data><PCT-Data_input><PCT-InputData><PCT-InputData_query><PCT-Query>
  <PCT-Query_type><PCT-QueryType><PCT-QueryType_css>
    <PCT-QueryCompoundCS>
    <PCT-QueryCompoundCS_query>
      <PCT-QueryCompoundCS_query_data>%(SMILES)s</PCT-QueryCompoundCS_query_data>
    </PCT-QueryCompoundCS_query>
    <PCT-QueryCompoundCS_type>
'''%{'SMILES':smiles}
  if searchtype[:3].lower()=='sim':
    qxml+='''\
      <PCT-QueryCompoundCS_type_similar><PCT-CSSimilarity>
        <PCT-CSSimilarity_threshold>%(SIM_CUTOFF)d</PCT-CSSimilarity_threshold>
      </PCT-CSSimilarity></PCT-QueryCompoundCS_type_similar>
'''%{'SIM_CUTOFF':sim_cutoff*100}
  elif searchtype[:3].lower()=='sub':
    qxml+='''\
      <PCT-QueryCompoundCS_type_subss><PCT-CSStructure>
        <PCT-CSStructure_isotopes value="false"/>
        <PCT-CSStructure_charges value="false"/>
        <PCT-CSStructure_tautomers value="false"/>
        <PCT-CSStructure_rings value="false"/>
        <PCT-CSStructure_bonds value="true"/>
        <PCT-CSStructure_chains value="true"/>
        <PCT-CSStructure_hydrogen value="false"/>
      </PCT-CSStructure></PCT-QueryCompoundCS_type_subss>
'''
  else: #exact
    qxml+='''\
      <PCT-QueryCompoundCS_type_identical>
        <PCT-CSIdentity value="same-stereo-isotope">5</PCT-CSIdentity>
      </PCT-QueryCompoundCS_type_identical>
'''
  qxml+='''\
    </PCT-QueryCompoundCS_type>
    <PCT-QueryCompoundCS_results>%(NMAX)d</PCT-QueryCompoundCS_results>
    </PCT-QueryCompoundCS>
  </PCT-QueryType_css></PCT-QueryType>
'''%{'NMAX':nmax}
  if active:
    qxml+='''\
  <PCT-QueryType><PCT-QueryType_cel><PCT-QueryCompoundEL>
    <PCT-QueryCompoundEL_activity>
      <PCT-CLByBioActivity value="active">2</PCT-CLByBioActivity>
    </PCT-QueryCompoundEL_activity>
  </PCT-QueryCompoundEL></PCT-QueryType_cel></PCT-QueryType>
'''
  if mlsmr:
    qxml+='''\
  <PCT-QueryType><PCT-QueryType_cel><PCT-QueryCompoundEL>
    <PCT-QueryCompoundEL_source><PCT-CLByString>
      <PCT-CLByString_qualifier value="must">1</PCT-CLByString_qualifier>
      <PCT-CLByString_category>MLSMR</PCT-CLByString_category>
    </PCT-CLByString></PCT-QueryCompoundEL_source>
  </PCT-QueryCompoundEL></PCT-QueryType_cel></PCT-QueryType>
'''
  qxml+='''\
  </PCT-Query_type></PCT-Query>
</PCT-InputData_query></PCT-InputData></PCT-Data_input></PCT-Data>
'''
  logging.debug('Connecting {}...'.format(pugurl))
  logging.info('Query [{}]: {}'.format(searchtype, smiles))
  if searchtype[:3].lower()=='sim':
    logging.info('Similarity cutoff: {}'.format(sim_cutoff))

  pugxml = rest_utils.PostURL(pugurl, data=(XMLHEADER+qxml),
	headers={"Accept":"text/soap+xml; charset=utf-8", "SOAPAction":"http://pubchem.ncbi.nlm.nih.gov/SubstructureSearch"})

  status,reqid,url,qkey,wenv,error = ParsePugXml(pugxml)
  return status,reqid,qkey,wenv,error

#############################################################################
def PollPug(pugurl, reqid, mode='status', ntries=20, poll_wait=10):
  qxml='''\
<PCT-Data><PCT-Data_input>
  <PCT-InputData><PCT-InputData_request>
    <PCT-Request>
      <PCT-Request_reqid>%(REQID)d</PCT-Request_reqid>
      <PCT-Request_type value="%(MODE)s"/>
    </PCT-Request>
  </PCT-InputData_request></PCT-InputData>
</PCT-Data_input></PCT-Data>
'''%{'REQID':reqid, 'MODE':mode}
  logging.debug('connecting %s...'%pugurl)

  pugxml = rest_utils.PostURL(pugurl, data=(XMLHEADER+qxml),
	headers={"Accept":"text/soap+xml; charset=utf-8", "SOAPAction":"http://pubchem.ncbi.nlm.nih.gov/GetOperationStatus"})

  status,reqid,url,qkey,wenv,error = ParsePugXml(pugxml)
  return status,reqid,url,qkey,wenv,error

#############################################################################
def ParsePugXml(pugxml):
  try:
    root = ElementTree.parse(io.StringIO(pugxml)) #ElementTree instance
  except Exception as e:
    logging.info('XML parse error: {}; xml="{}"'.format(e, pugxml))
    sys.exit(1)
  statuss = xml_utils.DOM_GetAttr(root, 'PCT-Status', 'value')
  status = statuss[0] if statuss else None
  errors = xml_utils.DOM_GetLeafValsByTagName(root, 'PCT-Status-Message_message')
  error = errors[0] if errors else None
  reqids = xml_utils.DOM_GetLeafValsByTagName(root, 'PCT-Waiting_reqid')
  reqid = int(reqids[0]) if reqids else None
  urls = xml_utils.DOM_GetLeafValsByTagName(root, 'PCT-Download-URL_url')
  url=urls[0] if urls else None
  qkeys = xml_utils.DOM_GetLeafValsByTagName(root, 'PCT-Entrez_query-key')
  qkey = qkeys[0] if qkeys else None
  wenvs = xml_utils.DOM_GetLeafValsByTagName(root, 'PCT-Entrez_webenv')
  wenv = wenvs[0] if wenvs else None
  return status,reqid,url,qkey,wenv,error

#############################################################################
def DownloadUrl(pugurl, fout, ntries=20, poll_wait=10):
  pugxml = rest_utils.GetURL(pugurl, nmax_retry=ntries,
	headers={"Accept":"text/soap+xml; charset=utf-8", "SOAPAction":"http://pubchem.ncbi.nlm.nih.gov/Download"})
  fout.write(pugxml)
  return len(pugxml)

#############################################################################
### error status values include: "server-error"
#############################################################################
def CheckStatus(status, error):
  if status not in ('success', 'queued', 'running'):
    logging.error('query failed; quitting (status="{}",error="{}").'.format(status, error))
    sys.exit(1)

#############################################################################
