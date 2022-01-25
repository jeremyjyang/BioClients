#!/usr/bin/env python3
"""
Utility functions for PUG SOAP web services, including:
  - PubChem Identifier Exchange Service (PIES), https://pubchem.ncbi.nlm.nih.gov/idexchange/idexchange.cgi
  - PubChem Standardization Service, https://pubchem.ncbi.nlm.nih.gov/standardize/standardize.cgi
  - PubChem Structure Search, https://pubchem.ncbi.nlm.nih.gov/search/search.cgi
See Save Query button for template XML.
https://pubchemdocs.ncbi.nlm.nih.gov/pug-soap
https://pubchemdocs.ncbi.nlm.nih.gov/pug-soap-reference
https://pubchem.ncbi.nlm.nih.gov/pug_soap/pug_soap.cgi?wsdl
"""
import sys,os,io,re,requests,urllib.request,time,logging

from xml.etree import ElementTree

from ...util import xml

XMLHEADER = """\
<?xml version="1.0"?>
<!DOCTYPE PCT-Data PUBLIC "-//NCBI//NCBI PCTools/EN" "NCBI_PCTools.dtd">"""
#
SOAP_ACTIONS = {
	"standardize":	"http://pubchem.ncbi.nlm.nih.gov/Standardize",
	"idexchange":	"http://pubchem.ncbi.nlm.nih.gov/IDExchange",
	"search_exact":	"http://pubchem.ncbi.nlm.nih.gov/SubstructureSearch",
	"search_substructure":	"http://pubchem.ncbi.nlm.nih.gov/SubstructureSearch",
	"search_similarity":	"http://pubchem.ncbi.nlm.nih.gov/SimilaritySearch2D",
	}
#
API_HOST="pubchem.ncbi.nlm.nih.gov"
API_BASE_PATH="/pug/pug.cgi"
API_BASE_URL=f"https://{API_HOST}{API_BASE_PATH}"
POLL_WAIT=10
MAX_WAIT=300
SIM_CUTOFF=0.80
RETRY_NMAX=10;
#
#############################################################################
class PugSoapRequest:
  """
Normal status values: "success", "hit-limit", "queued", "running"
Error status values: "server-error"
  """
  def __init__(self, pugxml, base_url):
    self.base_url = base_url
    self.pugxml = pugxml
    self.reqid = None
    self.status = None
    self.url = None
    self.qkey = None
    self.wenv = None
    self.error = None
    self.ntries = None
    self.out_struct = None
    self.parsePugXml(pugxml)
    self.qxml_template="""\
{header}
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
    logging.debug(f"Connecting {self.base_url}...")
    response = requests.post(self.base_url, data=(self.qxml_template.format(header=XMLHEADER, REQID=self.reqid, MODE="status")), headers={"Accept":"text/soap+xml; charset=utf-8", "SOAPAction":"http://pubchem.ncbi.nlm.nih.gov/GetOperationStatus"})
    self.parsePugXml(response.text)

  def cancel(self):
    logging.debug(f"Connecting {self.base_url}...")
    response = requests.post(self.base_url, data=(self.qxml_template.format(header=XMLHEADER, REQID=self.reqid, MODE="cancel")), headers={"Accept":"text/soap+xml; charset=utf-8", "SOAPAction":"http://pubchem.ncbi.nlm.nih.gov/GetOperationStatus"})
    self.parsePugXml(response.text)

  def parsePugXml(self, pugxml):
    logging.debug(pugxml)
    try:
      elt = ElementTree.parse(io.StringIO(pugxml))
    except Exception as e:
      logging.error(f"XML parse error: {e}; xml={pugxml}")
      sys.exit(1)
    statuss = xml.Utils.GetAttr(elt, 'PCT-Status', 'value')
    self.status = statuss[0] if statuss else None
    errors = xml.Utils.GetLeafValsByTagName(elt, 'PCT-Status-Message_message')
    self.error = errors[0] if errors else None
    reqids = xml.Utils.GetLeafValsByTagName(elt, 'PCT-Waiting_reqid')
    self.reqid = int(reqids[0]) if reqids else None
    urls = xml.Utils.GetLeafValsByTagName(elt, 'PCT-Download-URL_url')
    self.url = urls[0] if urls else None
    qkeys = xml.Utils.GetLeafValsByTagName(elt, 'PCT-Entrez_query-key')
    self.qkey = qkeys[0] if qkeys else None
    wenvs = xml.Utils.GetLeafValsByTagName(elt, 'PCT-Entrez_webenv')
    self.wenv = wenvs[0] if wenvs else None
    #Standardize:
    out_structs = xml.Utils.GetLeafValsByTagName(elt, 'PCT-Structure_structure_string')
    self.out_struct = out_structs[0].rstrip() if out_structs else None #smiles or inchi
    if self.out_struct is None:
      out_struct_lines = xml.Utils.GetLeafValsByTagName(elt, 'PCT-Structure_structure_strings_E')
      self.out_struct = ('\n'.join(out_struct_lines)) if out_struct_lines else None #sdf

  def waitForResult(self, poll_wait, max_wait):
    t0=time.time()
    while True:
      time.sleep(poll_wait)
      if time.time()-t0>max_wait:
        logging.error(f"Max wait exceeded ({max_wait} sec); quitting.")
        self.cancel()
      logging.info(f"Polling PUG [reqid={self.reqid}]...")
      self.getStatus()
      if self.status in ("success", "hit-limit"): 
        if self.url is not None:
          logging.info(f"{self.status}: Got url [reqid={self.reqid}]: {self.url}")
        elif self.qkey is not None:
          logging.info(f"{self.status}: Got qkey [reqid={self.reqid}]: {self.qkey}")
        elif self.out_struct is not None:
          logging.info(f"{self.status}: Got out_struct [reqid={self.reqid}]: {self.out_struct}")
        else:
          logging.error(f"Aaack! status={self.status} but no url, qkey, or out_struct??? [reqid={self.reqid}]")
        break
      logging.info(f"{time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))} elapsed; {poll_wait} sec wait; status={self.status}")
      if self.error:
        logging.info(self.error)
        if re.search('No result found', self.error, re.I):
          logging.info(f"No result found [reqid={self.reqid}].")
          break

#############################################################################
def SubmitRequest_StructuralSearch(query, searchtype, sim_cutoff, active=False,
nmax=10000, base_url=API_BASE_URL):
  qxml=f"""{XMLHEADER}
<PCT-Data>
  <PCT-Data_input>
    <PCT-InputData>
      <PCT-InputData_query>
        <PCT-Query>
          <PCT-Query_type>
            <PCT-QueryType>
              <PCT-QueryType_css>
                <PCT-QueryCompoundCS>
                  <PCT-QueryCompoundCS_query>
                    <PCT-QueryCompoundCS_query_data>{query}</PCT-QueryCompoundCS_query_data>
                  </PCT-QueryCompoundCS_query>
                  <PCT-QueryCompoundCS_type>
"""
  if searchtype.lower()=='search_similarity':
    qxml+=f"""\
                    <PCT-QueryCompoundCS_type_similar>
                      <PCT-CSSimilarity>
                        <PCT-CSSimilarity_threshold>{int(sim_cutoff*100):d}</PCT-CSSimilarity_threshold>
                      </PCT-CSSimilarity>
                    </PCT-QueryCompoundCS_type_similar>
"""
  elif searchtype.lower()=='search_substructure':
    qxml+="""\
                    <PCT-QueryCompoundCS_type_subss>
                      <PCT-CSStructure>
                        <PCT-CSStructure_isotopes value="false"/>
                        <PCT-CSStructure_charges value="false"/>
                        <PCT-CSStructure_tautomers value="false"/>
                        <PCT-CSStructure_rings value="false"/>
                        <PCT-CSStructure_bonds value="true"/>
                        <PCT-CSStructure_chains value="true"/>
                        <PCT-CSStructure_hydrogen value="false"/>
                      </PCT-CSStructure>
                    </PCT-QueryCompoundCS_type_subss>
"""
  else: #search_exact
    qxml+="""\
                    <PCT-QueryCompoundCS_type_identical>
                      <PCT-CSIdentity value="same-stereo-isotope">5</PCT-CSIdentity>
                    </PCT-QueryCompoundCS_type_identical>
"""
  qxml+=f"""\
                  </PCT-QueryCompoundCS_type>
                  <PCT-QueryCompoundCS_results>{nmax}</PCT-QueryCompoundCS_results>
                </PCT-QueryCompoundCS>
              </PCT-QueryType_css></PCT-QueryType>
"""
  if active:
    qxml+="""\
            <PCT-QueryType>
              <PCT-QueryType_cel>
                <PCT-QueryCompoundEL>
                  <PCT-QueryCompoundEL_activity>
                    <PCT-CLByBioActivity value="active">2</PCT-CLByBioActivity>
                  </PCT-QueryCompoundEL_activity>
                </PCT-QueryCompoundEL>
              </PCT-QueryType_cel>
            </PCT-QueryType>
"""
  qxml+="""\
          </PCT-Query_type>
        </PCT-Query>
      </PCT-InputData_query>
    </PCT-InputData>
  </PCT-Data_input>
</PCT-Data>
"""
  logging.debug(f"qxml: {qxml}")
  logging.info(f"StructuralSearch: base_url: {base_url}; searchtype: {searchtype}{'(sim>='+str(sim_cutoff)+')' if searchtype.lower()=='search_similarity' else '' }; query: {query}")
  response = requests.post(base_url, data=qxml, headers={"Accept":"text/soap+xml; charset=utf-8", "SOAPAction":SOAP_ACTIONS[searchtype]})
  return PugSoapRequest(response.text, base_url)

#############################################################################
def SubmitRequest_IDExchange(ids, ifmt, ofmt, operator, do_gz, base_url=API_BASE_URL):
  # Input formats: cid, sid, smiles, inchi, inchikey
  # Output formats: cid, sid, smiles, inchi, inchikey
  # Operators: same (same cid), parent (parent cid), samepar (same parent compound)
  fmt2tag = {"cid":"cid", "sid":"sid", "smiles":"smiles", "inchi":"inchis", "inchikey":"inchikeys"}
  qxml=(f"""{XMLHEADER}
<PCT-Data>
  <PCT-Data_input>
    <PCT-InputData>
      <PCT-InputData_query>
        <PCT-Query>
          <PCT-Query_type>
            <PCT-QueryType>
              <PCT-QueryType_id-exchange>
                <PCT-QueryIDExchange>
                  <PCT-QueryIDExchange_input>
                    <PCT-QueryUids>
""")
  if ifmt in ("cid", "sid"):
    qxml+=(f"""\
                      <PCT-QueryUids_ids>
                        <PCT-ID-List>
                          <PCT-ID-List_db>{"pccompound" if ifmt=="cid" else "pcsubstance"}</PCT-ID-List_db>
                          <PCT-ID-List_uids>
""")
    for id_this in ids:
      qxml+=(f"""\
                            <PCT-ID-List_uids_E>{id_this}</PCT-ID-List_uids_E>
""")
    qxml+=(f"""\
                          </PCT-ID-List_uids>
                        </PCT-ID-List>
                      </PCT-QueryUids_ids>
""")
  else:
    qxml+=(f"""\
                      <PCT-QueryUids_{fmt2tag[ifmt]}>
""")
    for id_this in ids:
      qxml+=(f"""\
                        <PCT-QueryUids_{fmt2tag[ifmt]}_E>{id_this}</PCT-QueryUids_{fmt2tag[ifmt]}_E>
""")
    qxml+=(f"""\
                      </PCT-QueryUids_{fmt2tag[ifmt]}>
""")
  qxml+=(f"""\
                    </PCT-QueryUids>
                  </PCT-QueryIDExchange_input>
                  <PCT-QueryIDExchange_operation-type value="{operator}"/>
                  <PCT-QueryIDExchange_output-type value="{ofmt}"/>
                  <PCT-QueryIDExchange_output-method value="file-pair"/>
                  <PCT-QueryIDExchange_compression value="{'gzip' if do_gz else 'none'}"/>
                </PCT-QueryIDExchange>
              </PCT-QueryType_id-exchange>
            </PCT-QueryType>
          </PCT-Query_type>
        </PCT-Query>
      </PCT-InputData_query>
    </PCT-InputData>
  </PCT-Data_input>
</PCT-Data>
""")
  logging.debug(f"qxml: {qxml}")
  logging.debug(f"IDExchange: base_url: {base_url}: IDs: {len(ids)}")
  response = requests.post(base_url, data=qxml, headers={"Accept":"text/soap+xml; charset=utf-8", "SOAPAction":SOAP_ACTIONS["idexchange"]})
  if response.status_code!=200:
    logging.error(f"(status_code={response.status_code})")
  logging.debug(f"(response.text={response.text})")
  return PugSoapRequest(response.text, base_url)

#############################################################################
def SubmitRequest_Standardize(id_this, ifmt, ofmt, do_gz, base_url=API_BASE_URL):
  """Only one per request allowed."""
  qxml=(f"""{XMLHEADER}
<PCT-Data>
  <PCT-Data_input>
    <PCT-InputData>
      <PCT-InputData_standardize>
        <PCT-Standardize>
          <PCT-Standardize_structure>
            <PCT-Structure>
              <PCT-Structure_structure>
                <PCT-Structure_structure_string>{id_this}</PCT-Structure_structure_string>
              </PCT-Structure_structure>
              <PCT-Structure_format>
                <PCT-StructureFormat value="{ifmt}"/>
              </PCT-Structure_format>
            </PCT-Structure>
          </PCT-Standardize_structure>
          <PCT-Standardize_oformat>
            <PCT-StructureFormat value="{ofmt}"/>
          </PCT-Standardize_oformat>
        </PCT-Standardize>
      </PCT-InputData_standardize>
    </PCT-InputData>
  </PCT-Data_input>
</PCT-Data>
""")
  logging.debug(f"qxml: {qxml}")
  logging.debug(f"Standardize: base_url: {base_url}")
  response = requests.post(base_url, data=qxml, headers={"Accept":"text/soap+xml; charset=utf-8", "SOAPAction":SOAP_ACTIONS["standardize"]})
  return PugSoapRequest(response.text, base_url)

#############################################################################
def MonitorQuery(qkey, webenv, fmt='smiles', do_gz=False, base_url=API_BASE_URL):
  qxml=(f"""{XMLHEADER}
<PCT-Data><PCT-Data_input><PCT-InputData>
  <PCT-InputData_download><PCT-Download> 
    <PCT-Download_uids><PCT-QueryUids>
      <PCT-QueryUids_entrez><PCT-Entrez>
        <PCT-Entrez_db>pccompound</PCT-Entrez_db>
        <PCT-Entrez_query-key>{qkey}</PCT-Entrez_query-key>
        <PCT-Entrez_webenv>{webenv}</PCT-Entrez_webenv>
      </PCT-Entrez></PCT-QueryUids_entrez>
    </PCT-QueryUids></PCT-Download_uids>
    <PCT-Download_format value="{fmt}"/>
    <PCT-Download_compression value="{'gzip' if do_gz else 'none'}"/>
  </PCT-Download></PCT-InputData_download>
</PCT-InputData></PCT-Data_input></PCT-Data>
""")
  logging.debug(f"qxml: {qxml}")
  logging.debug(f"[MonitorQuery] Requesting: base_url: {base_url}; qkey: {qkey}")
  response = requests.post(base_url, data=qxml, headers={"Accept":"text/soap+xml; charset=utf-8", "SOAPAction":"http://pubchem.ncbi.nlm.nih.gov/Download"})
  return PugSoapRequest(response.text, base_url)

#############################################################################
def DownloadResults(download_url, ofmt, do_gz=False, fout=sys.stdout):
  """FTP urls not handled by requests package?!"""

#  response = requests.get(download_url, headers={"Accept":"text/soap+xml; charset=utf-8", "SOAPAction":"http://pubchem.ncbi.nlm.nih.gov/Download"})
#  if response.status_code!=200:
#    logging.error(f"[DownloadResults] (status_code={response.status_code})")
#  if type(response.content) is bytes:
#    fout.write(response.content)
#  else:
#    fout.write(response.content.encode("utf-8"))
#  logging.info(f"Data downloaded to {fout.name}")

  request = urllib.request.Request(url=download_url)
  logging.debug(f"request type = {request.type}")
  logging.debug(f"request host = {request.host}")
  logging.debug(f"request method = {request.get_method()}")
  for i_try in range(RETRY_NMAX):
    try:
      with urllib.request.urlopen(request, timeout=POLL_WAIT) as response:
        fbytes = response.read()
        fout.write(fbytes if do_gz else fbytes.decode("utf-8"))
    except Exception as e:
      logging.warn(f"RETRY({i_try+1}/{RETRY_NMAX}): {e}")
      if i_try<RETRY_NMAX:
        time.sleep(POLL_WAIT)
        continue
    break

#############################################################################
