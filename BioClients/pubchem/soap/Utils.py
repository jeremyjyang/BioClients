#!/usr/bin/env python3
"""
Utility functions for PUG-SOAP API (pre-REST) (~2010).
https://pubchemdocs.ncbi.nlm.nih.gov/pug-soap
See Save Query button for template XML at
https://pubchem.ncbi.nlm.nih.gov/search/search.cgi
And at
https://pubchem.ncbi.nlm.nih.gov/standardize/standardize.cgi
"""
import sys,os,io,re,urllib.request,time,logging

from xml.etree import ElementTree
#from xml.parsers import expat

from ...util import rest_utils
from ...util import xml_utils

XMLHEADER=("""\
<?xml version="1.0"?>
<!DOCTYPE PCT-Data PUBLIC "-//NCBI//NCBI PCTools/EN" "https://pubchem.ncbi.nlm.nih.gov/pug/pug.dtd">
""")

SOAP_ACTIONS = {
	"exact":"http://pubchem.ncbi.nlm.nih.gov/SubstructureSearch",
	"substructure":"http://pubchem.ncbi.nlm.nih.gov/SubstructureSearch",
	"similarity":"http://pubchem.ncbi.nlm.nih.gov/SimilaritySearch2D",
	"standardize":"http://pubchem.ncbi.nlm.nih.gov/Standardize"
	}

#############################################################################
class PugSoapRequest:
  """
Normal status values: "success", "queued", "running"
Error status values: "server-error"
  """

  def __init__(self, pugurl, pugxml):

    self.pugurl = pugurl
    self.pugxml = pugxml
    self.reqid = None
    self.status = None
    self.url = None
    self.qkey = None
    self.wenv = None
    self.error = None
    self.ntries = None
    self.out_smi = None
    self.parsePugXml(pugxml)
    self.qxml_template="""\
<PCT-Data><PCT-Data_input>
  <PCT-InputData><PCT-InputData_request>
    <PCT-Request>
      <PCT-Request_reqid>{REQID}</PCT-Request_reqid>
      <PCT-Request_type value="{MODE}"/>
    </PCT-Request>
  </PCT-InputData_request></PCT-InputData>
</PCT-Data_input></PCT-Data>
"""

  def getStatus(self):
    logging.debug("Connecting {}...".format(self.pugurl))
    pugxml = rest_utils.PostURL(self.pugurl, data=(XMLHEADER+self.qxml_template.format(REQID=self.reqid, MODE="status")), headers={"Accept":"text/soap+xml; charset=utf-8", "SOAPAction":"http://pubchem.ncbi.nlm.nih.gov/GetOperationStatus"})
    self.parsePugXml(pugxml)

  def cancel(self):
    logging.debug("Connecting {}...".format(self.pugurl))
    pugxml = rest_utils.PostURL(self.pugurl, data=(XMLHEADER+qxml_template.format(REQID=self.reqid, MODE="cancel")), headers={"Accept":"text/soap+xml; charset=utf-8", "SOAPAction":"http://pubchem.ncbi.nlm.nih.gov/GetOperationStatus"})
    self.parsePugXml(pugxml)

  def parsePugXml(self, pugxml):
    logging.debug(pugxml)
    try:
      elt = ElementTree.parse(io.StringIO(pugxml)) #ElementTree instance
    except Exception as e:
      logging.info('XML parse error: {}; xml="{}"'.format(e, pugxml))
      sys.exit(1)
    statuss = xml_utils.DOM_GetAttr(elt, 'PCT-Status', 'value')
    self.status = statuss[0] if statuss else None
    errors = xml_utils.DOM_GetLeafValsByTagName(elt, 'PCT-Status-Message_message')
    self.error = errors[0] if errors else None
    reqids = xml_utils.DOM_GetLeafValsByTagName(elt, 'PCT-Waiting_reqid')
    self.reqid = int(reqids[0]) if reqids else None
    urls = xml_utils.DOM_GetLeafValsByTagName(elt, 'PCT-Download-URL_url')
    self.url=urls[0] if urls else None
    qkeys = xml_utils.DOM_GetLeafValsByTagName(elt, 'PCT-Entrez_query-key')
    self.qkey = qkeys[0] if qkeys else None
    wenvs = xml_utils.DOM_GetLeafValsByTagName(elt, 'PCT-Entrez_webenv')
    self.wenv = wenvs[0] if wenvs else None
    #Standardize:
    out_smis = xml_utils.DOM_GetLeafValsByTagName(elt, 'PCT-Structure_structure_string')
    self.out_smi = out_smis[0] if out_smis else None

#############################################################################
def SubmitQuery_Structural(pugurl, smiles, searchtype, sim_cutoff, active=False, mlsmr=False, nmax=10000):
  qxml="""\
<PCT-Data><PCT-Data_input><PCT-InputData><PCT-InputData_query><PCT-Query>
  <PCT-Query_type><PCT-QueryType><PCT-QueryType_css>
    <PCT-QueryCompoundCS>
    <PCT-QueryCompoundCS_query>
      <PCT-QueryCompoundCS_query_data>{SMILES}</PCT-QueryCompoundCS_query_data>
    </PCT-QueryCompoundCS_query>
    <PCT-QueryCompoundCS_type>
""".format(SMILES=smiles)
  if searchtype.lower()=='similarity':
    qxml+="""\
<PCT-QueryCompoundCS_type_similar><PCT-CSSimilarity>
  <PCT-CSSimilarity_threshold>{SIM_CUTOFF:d}</PCT-CSSimilarity_threshold>
</PCT-CSSimilarity></PCT-QueryCompoundCS_type_similar>
""".format(SIM_CUTOFF=(int(sim_cutoff*100)))
  elif searchtype.lower()=='substructure':
    qxml+="""\
<PCT-QueryCompoundCS_type_subss><PCT-CSStructure>
  <PCT-CSStructure_isotopes value="false"/>
  <PCT-CSStructure_charges value="false"/>
  <PCT-CSStructure_tautomers value="false"/>
  <PCT-CSStructure_rings value="false"/>
  <PCT-CSStructure_bonds value="true"/>
  <PCT-CSStructure_chains value="true"/>
  <PCT-CSStructure_hydrogen value="false"/>
</PCT-CSStructure></PCT-QueryCompoundCS_type_subss>
"""
  else: #exact
    qxml+="""\
<PCT-QueryCompoundCS_type_identical>
  <PCT-CSIdentity value="same-stereo-isotope">5</PCT-CSIdentity>
</PCT-QueryCompoundCS_type_identical>
"""
  qxml+="""\
</PCT-QueryCompoundCS_type>
<PCT-QueryCompoundCS_results>{NMAX}</PCT-QueryCompoundCS_results>
</PCT-QueryCompoundCS>
</PCT-QueryType_css></PCT-QueryType>
""".format(NMAX=nmax)
  if active:
    qxml+="""\
<PCT-QueryType><PCT-QueryType_cel><PCT-QueryCompoundEL>
<PCT-QueryCompoundEL_activity>
<PCT-CLByBioActivity value="active">2</PCT-CLByBioActivity>
</PCT-QueryCompoundEL_activity>
</PCT-QueryCompoundEL></PCT-QueryType_cel></PCT-QueryType>
"""
  if mlsmr:
    qxml+="""\
<PCT-QueryType><PCT-QueryType_cel><PCT-QueryCompoundEL>
<PCT-QueryCompoundEL_source><PCT-CLByString>
<PCT-CLByString_qualifier value="must">1</PCT-CLByString_qualifier>
<PCT-CLByString_category>MLSMR</PCT-CLByString_category>
</PCT-CLByString></PCT-QueryCompoundEL_source>
</PCT-QueryCompoundEL></PCT-QueryType_cel></PCT-QueryType>
"""
  qxml+="""\
</PCT-Query_type></PCT-Query>
</PCT-InputData_query></PCT-InputData></PCT-Data_input></PCT-Data>
"""
  logging.debug("Requesting: pugurl: {}; searchtype: {}; smiles: {}".format(pugurl, searchtype, smiles))
  if searchtype.lower()=='similarity':
    logging.debug("Similarity cutoff: {}".format(sim_cutoff))
  pugxml = rest_utils.PostURL(pugurl, data=(XMLHEADER+qxml), headers={"Accept":"text/soap+xml; charset=utf-8", "SOAPAction":SOAP_ACTIONS[searchtype]})
  return PugSoapRequest(pugurl, pugxml)

#############################################################################
def SubmitQuery_Standardize(pugurl, smiles):
  qxml="""\
<PCT-Data>
  <PCT-Data_input>
    <PCT-InputData>
      <PCT-InputData_standardize>
        <PCT-Standardize>
          <PCT-Standardize_structure>
            <PCT-Structure>
              <PCT-Structure_structure>
                <PCT-Structure_structure_string>{SMILES}</PCT-Structure_structure_string>
              </PCT-Structure_structure>
              <PCT-Structure_format>
                <PCT-StructureFormat value="smiles"/>
              </PCT-Structure_format>
            </PCT-Structure>
          </PCT-Standardize_structure>
          <PCT-Standardize_oformat>
            <PCT-StructureFormat value="smiles"/>
          </PCT-Standardize_oformat>
        </PCT-Standardize>
      </PCT-InputData_standardize>
    </PCT-InputData>
  </PCT-Data_input>
</PCT-Data>
""".format(SMILES=smiles)
  logging.debug("Requesting: pugurl: {}; smiles: {}".format(pugurl, smiles))
  pugxml = rest_utils.PostURL(pugurl, data=(XMLHEADER+qxml), headers={"Accept":"text/soap+xml; charset=utf-8", "SOAPAction":SOAP_ACTIONS["standardize"]})
  return PugSoapRequest(pugurl, pugxml)

#############################################################################
def MonitorQuery(pugurl, qkey, webenv, fmt='smiles', do_gz=False):
  qxml="""\
<PCT-Data><PCT-Data_input><PCT-InputData>
  <PCT-InputData_download><PCT-Download> 
    <PCT-Download_uids><PCT-QueryUids>
      <PCT-QueryUids_entrez><PCT-Entrez>
        <PCT-Entrez_db>pccompound</PCT-Entrez_db>
        <PCT-Entrez_query-key>{QKEY}</PCT-Entrez_query-key>
        <PCT-Entrez_webenv>{WEBENV}</PCT-Entrez_webenv>
      </PCT-Entrez></PCT-QueryUids_entrez>
    </PCT-QueryUids></PCT-Download_uids>
    <PCT-Download_format value="{FMT}"/>
    <PCT-Download_compression value="{COMPRES}"/>
  </PCT-Download></PCT-InputData_download>
</PCT-InputData></PCT-Data_input></PCT-Data>
""".format(QKEY=qkey, WEBENV=webenv, FMT=fmt, COMPRES=('gzip' if do_gz else 'none'))
  logging.info('Requesting: pugurl: {}; qkey: {}'.format(pugurl, qkey))
  pugxml = rest_utils.PostURL(pugurl, data=(XMLHEADER+qxml), headers={"Accept":"text/soap+xml; charset=utf-8", "SOAPAction":"http://pubchem.ncbi.nlm.nih.gov/Download"})
  return PugSoapRequest(pugurl, pugxml)

#############################################################################
def DownloadResults(pugurl, fout, ntries=10):
  pugout = rest_utils.GetURL(pugurl, nmax_retry=ntries, headers={"Accept":"text/soap+xml; charset=utf-8", "SOAPAction":"http://pubchem.ncbi.nlm.nih.gov/Download"})
  if fout == sys.stdout:
    fout.write(pugout)
  elif type(pugout) is bytes:
    fout.write(pugout)
  elif type(pugout) is str:
    fout.write(pugout.encode("utf-8"))
  else: # ?
    fout.write(pugout)

#############################################################################
