#!/usr/bin/env python3
"""
Utility functions for the PubChem PUG REST API.

* https://pubchemdocs.ncbi.nlm.nih.gov/pug-rest

	<DOMAIN>/<NAMESPACE>/<IDENTIFIERS>

	compound/{cid|name|smiles|inchi|inchikey|listkey}
	compound/substructure/{smiles|inchi}
	substance/{sid|name|listkey}
	substance/sourceid/<source name> 
	substance/sourceall/<source name> 
	substance/sid/<SID>/cids/JSON
	substance/sid/<SID>/cids/XML?cids_type=all
	assay/{aid|listkey} 
 	assay/type/{all|confirmatory|doseresponse|onhold|panel|rnai|screening|summary}
 	assay/sourceall/<source name>
	sources/{substance|assay}

  <IDENTIFIERS> = comma-separated list of positive integers (cid, sid, aid) or
  strings (source, inchikey, listkey); single identifier string
  (name, smiles; inchi by POST only)
"""
###
import sys,os,io,re,csv,json,pandas,math,time,logging,tempfile,tqdm,tqdm.auto
from xml.etree import ElementTree
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import urllib.request,urllib.parse
import pandas as pd
#
OUTCOME_CODES = {
        'inactive':1,
        'active':2,
        'inconclusive':3,
        'unspecified':4,
        'probe':5}
#
API_HOST='pubchem.ncbi.nlm.nih.gov'
API_BASE_PATH='/rest/pug'
BASE_URL="https://"+API_HOST+API_BASE_PATH
#
NCHUNK=100
#
#############################################################################
def OutcomeCode(txt):
  return OUTCOME_CODES[txt.lower()] if txt.lower() in OUTCOME_CODES else OUTCOME_CODES['unspecified']

#############################################################################
def ListSources(src_type, base_url=BASE_URL, fout=None):
  rval = requests.get(base_url+f"/sources/{src_type}/JSON").json()
  logging.debug(json.dumps(rval,indent=2))
  sources = rval['InformationList']['SourceName'] if 'InformationList' in rval and 'SourceName' in rval['InformationList'] else []
  n_src=0;
  for source in sorted(sources):
    fout.write(f"{source}\n")
    n_src+=1
  logging.info(f"n_src ({src_type}): {n_src}")

##############################################################################
def GetSID2SDF(id_query, base_url=BASE_URL):
  url = (base_url+f"/substance/sid/{id_query}/SDF")
  txt = requests.get(url).text
  return txt

#############################################################################
def GetSID2CID(sids, base_url=BASE_URL, fout=None):
  cids=set(); tq=None; df=None;
  if fout: fout.write("SID\tCID\n")
  for sid in sids:
    rval = requests.get(base_url+f"/substance/sid/{sid}/cids/JSON?cids_type=standardized").json()
    infos = rval['InformationList']['Information'] if 'InformationList' in rval and 'Information' in rval['InformationList'] else []
    for info in infos:
      cids_this = info['CID'] if 'CID' in info else []
      for cid in cids_this:
        cids.add(str(cid))
        if fout: fout.write(f"{sid}\t{cid}\n")
  return list(cids)

#############################################################################
def GetSID2Smiles(sids, base_url=BASE_URL, fout=None):
  cids = GetSID2CID(sids, base_url)
  GetCID2Smiles(cids, base_url, fout)

#############################################################################
def GetCID2SID(cids, base_url=BASE_URL, fout=None):
  sids=set(); df=None;
  if fout: fout.write("CID\tSID\n")
  for cid in cids:
    time.sleep(0.01) #Kludge fix: requests.exceptions.ConnectionError: ('Connection aborted.', ConnectionResetError(104, 'Connection reset by peer'))
    url_this = f"{base_url}/compound/cid/{cid}/sids/JSON"
    response = requests.get(url_this)
    if response.status_code!=200:
      logging.debug(f"status_code: {response.status_code}; {url_this}")
      continue
    try:
      rval = response.json()
    except Exception as e:
      logging.error(f"{str(e)}")
      continue
    infos = rval['InformationList']['Information'] if 'InformationList' in rval and 'Information' in rval['InformationList'] else []
    for info in infos:
      sids_this = info['SID'] if 'SID' in info else []
      for sid in sids_this:
        sids.add(str(sid))
        if fout: fout.write(f"{cid}\t{sid}\n")
  return list(sids)

#############################################################################
### Must quote forward slash '/' in smiles.  2nd param in quote()
### specifies "safe" chars to not quote, '/' being the default, so specify
### '' for no safe chars.
#############################################################################
def GetSmiles2CID(smis, base_url=BASE_URL, fout=None):
  n_out=0; tq=None; df=None;
  for i_smi in tqdm.auto.trange(len(smis)):
    smi = smis[i_smi]
    name = re.sub(r'^[\S]+\s', '', smi) if re.search(r'^[\S]+\s', smi) else ""
    smi = re.sub(r'\s.*$', '', smi)
    try:
      response = requests.get(base_url+f"/compound/smiles/{urllib.parse.quote(smi, '')}/cids/JSON")
    except Exception as e:
      logging.error(f"{smi} REST request failed: {e}")
      continue
    if response.status_code!=200:
      logging.error(f"status_code: {response.status_code}")
      continue
    result = response.json()
    logging.debug(json.dumps(result, indent=2))
    cids = result['IdentifierList']['CID'] if 'IdentifierList' in result and 'CID' in result['IdentifierList'] else []
    if 0 in cids: cids.remove(0)
    if None in cids: cids.remove(None)
    if len(cids)==0:
      logging.warning(f"CID not found for SMI: \"{smi}\"")
      continue
    df_this = pd.DataFrame({"CID":cids, "SMILES":smi, "Name":name})
    if fout is not None: df_this.to_csv(fout, "\t", header=bool(n_out==0), index=False)
    else: df = pd.concat([df, df_this])
    n_out+=len(cids)
  logging.info(f"SMIs: {len(smis)}; CIDs out: {n_out}")
  return df

#############################################################################
def GetCID2AssaySummary(ids, base_url=BASE_URL, fout=None):
  """Example CIDs: 2519 (caffeine), 3034034 (quinine)"""
  n_out=0; df=None;
  for i_cid in tqdm.auto.trange(len(ids), desc="CIDs"):
    id_this = ids[i_cid]
    rval = requests.get(base_url+f"/compound/cid/{id_this}/assaysummary/CSV").text
    if not rval: continue
    df_this = pandas.read_csv(io.StringIO(rval), sep=',')
    if fout is not None: df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
    else: df = pd.concat([df, df_this])
    n_out += df_this.shape[0]
  logging.info(f"CIDs: {len(ids)}; assay summaries out: {n_out}")
  return df

#############################################################################
def GetSID2AssaySummary(ids, base_url=BASE_URL, fout=None):
  n_out=0; df=None;
  for i_sid in tqdm.auto.trange(len(ids), desc="SIDs"):
    id_this = ids[i_sid]
    rval = requests.get(base_url+f"/substance/sid/{id_this}/assaysummary/CSV").text
    if not rval: continue
    df_this = pandas.read_csv(io.StringIO(rval), sep=',')
    if fout is not None: df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
    else: df = pd.concat([df, df_this])
    n_out += df_this.shape[0]
  logging.info(f"SIDs: {len(ids)}; assay summaries out: {n_out}")
  return df

#############################################################################
def GetCID2Inchi(ids, base_url=BASE_URL, fout=None):
  nskip_this=0; n_out=0; tq=None; df=None;
  PROPTAGS = ["InChIKey", "InChI"]
  HEADERS = {'Accept':'text/CSV', 'Content-type':'application/x-www-form-urlencoded'}
  url = f"{base_url}/compound/cid/property/{','.join(PROPTAGS)}/CSV"
  while True:
    if tq is None: tq = tqdm.tqdm(total=len(ids), unit="cids")
    if nskip_this>=len(ids): break
    ids_this = ids[nskip_this:nskip_this+NCHUNK]
    ids_this_dict = {'cid':(','.join(map(lambda x:str(x), ids_this)))}
    response = requests.post(url, headers=HEADERS, data=ids_this_dict)
    df_this = pandas.read_csv(io.StringIO(response.text), sep=',')
    if fout is None: df = pd.concat([df, df_this], axis=0)
    else: df_this.to_csv(fout, sep='\t', index=False, header=bool(nskip_this==0))
    nskip_this+=NCHUNK
    n_out += df_this.shape[0]
    tq.update(n=len(ids_this))
  tq.close()
  logging.info(f"Input IDs: {len(ids)}; Output InChIs: {n_out}")
  return df

##############################################################################
def GetCID2SDF(ids, base_url=BASE_URL, fout=None):
  """Request in chunks.  Works for 50, and not for 200 (seems to be a limit)."""
  nskip_this=0; n_out=0; tq=None; txt_out="";
  while True:
    if tq is None: tq = tqdm.tqdm(total=len(ids), unit="cids")
    if nskip_this>=len(ids): break
    ids_this = ids[nskip_this:nskip_this+NCHUNK]
    idstr = (','.join(map(lambda x:str(x), ids_this)))
    response = requests.post(base_url+'/compound/cid/SDF', data={'cid':idstr})
    if fout is not None: fout.write(response.text)
    else: txt_out += response.text
    n_out += len(re.findall(r'^\$\$\$\$$', response.text, re.M))
    nskip_this+=NCHUNK
    tq.update(n=len(ids_this))
  tq.close()
  logging.info(f"SDFs out: {n_out}")
  return txt_out

#############################################################################
def GetSID2SDF(ids, skip, nmax, base_url=BASE_URL, fout=None):
  """Faster via POST(?). Request in chunks.  Works for 50, and not
  for 200 (seems to be a limit)."""
  n_out=0; tq=None; txt_out="";
  if skip: logging.debug(f"skip: [1-{skip}]")
  nskip_this=skip;
  while True:
    if tq is None: tq = tqdm.tqdm(total=len(ids), unit="cids")
    if nskip_this>=len(ids): break
    nchunk = min(NCHUNK, nmax-(nskip_this-skip))
    n_sid_in+=nchunk
    ids_this = ids[nskip_this:nskip_this+NCHUNK]
    idstr = (','.join(map(lambda x:str(x), ids_this)))
    #rval = rest.Utils.PostURL(base_url+'/substance/sid/SDF', data={'sid':idstr})
    response = requests.post(base_url+'/substance/sid/SDF', data={'sid':idstr})
    if fout is not None: fout.write(response.text)
    else: txt_out += response.text
    n_out += len(re.findall(r'^\$\$\$\$$', response.text, re.M))
    nskip_this+=nchunk
    if nmax and (nskip_this-skip)>=nmax:
      logging.info(f"NMAX limit reached: {nmax}")
      break
    tq.update(n=len(ids_this))
  tq.close()
  logging.info(f"SIDs: {len(sids)}; SDFs out: {n_out}")
  return txt_out

#############################################################################
def GetCID2Smiles(ids, base_url=BASE_URL, fout=None):
  """Returns Canonical and Isomeric SMILES."""
  PROPTAGS = ['CanonicalSMILES', 'IsomericSMILES']
  url = (base_url+"/compound/cid/property/{}/CSV".format(','.join(PROPTAGS)))
  nskip_this=0; df=None; tq=None;
  n_in=0; n_out=0; n_err=0; results=[];
  while True:
    if tq is None: tq = tqdm.tqdm(total=len(ids), unit="mols")
    if nskip_this>=len(ids): break
    ids_this = ids[nskip_this:nskip_this+NCHUNK]
    n_in+=len(ids_this)
    idstr = (','.join(map(lambda x:str(x), ids_this)))
    response = requests.post(url, data={'cid':idstr})
    df_this = pandas.read_csv(io.StringIO(response.text), sep=',')
    if fout is not None:
      df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
    else:
      df = pd.concat([df, df_this])
    nskip_this+=NCHUNK
    n_out+=len(ids_this)
    tq.update(n=len(ids_this))
  tq.close()
  logging.info(f"Input IDs: {len(ids)}; Output records: {n_out}")
  return df

#############################################################################
def GetCID2Properties(ids, base_url=BASE_URL, fout=None):
  PROPTAGS = ["CanonicalSMILES", "IsomericSMILES", "InChIKey", "InChI", "MolecularFormula", "HeavyAtomCount", "MolecularWeight", "XLogP", "TPSA"]
  url = (base_url+"/compound/cid/property/{}/CSV".format(','.join(PROPTAGS)))
  nskip_this=0; df=None; tq=None;
  n_in=0; n_out=0; n_err=0; results=[];
  while True:
    if tq is None: tq = tqdm.tqdm(total=len(ids), unit="mols")
    if nskip_this>=len(ids): break
    ids_this = ids[nskip_this:nskip_this+NCHUNK]
    n_in+=len(ids_this)
    idstr = (','.join(map(lambda x:str(x), ids_this)))
    response = requests.post(url, headers={'Accept':'text/CSV', 'Content-type':'application/x-www-form-urlencoded'}, data={'cid':idstr})
    try:
      df_this = pandas.read_csv(io.StringIO(response.text), sep=',')
    except Exception as e:
      logging.error(f"{e}")
      logging.debug(response.text)
      continue
    if fout is not None:
      df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
    else:
      df = pd.concat([df, df_this])
    nskip_this+=NCHUNK
    n_out+=len(ids_this)
    tq.update(n=len(ids_this))
  tq.close()
  logging.info(f"Input IDs: {len(ids)}; Output records: {n_out}")
  return df

#############################################################################
def GetCID2Descriptions(ids, base_url=BASE_URL, fout=None):
  n_out=0; tags=None; df=None;
  for i in tqdm.tqdm(range(len(ids))):
    id_this = ids[i]
    response = requests.get(base_url+f"/compound/cid/{id_this}/description/JSON")
    if response.status_code!=200:
      logging.error(f"status_code: {response.status_code}")
      continue
    rval = response.json()
    infos = rval['InformationList']['Information'] if 'InformationList' in rval and 'Information' in rval['InformationList'] else []
    for info in infos:
      if 'Description' not in info: continue
      if not tags:
        tags = list(info)
      df_this = pd.DataFrame({tag:([info[tag]] if tag in info else ['']) for tag in tags})

      if fout is not None: df_this.to_csv(fout, "\t", header=bool(n_out==0), index=False)
      else: df = pd.concat([df, df_this])
      n_out+=df_this.shape[0]
  logging.info(f"Input IDs: {len(ids)}; Output records: {n_out}")
  return df

#############################################################################
def Inchi2CID(inchis, base_url=BASE_URL, fout=None):
  '''	Must be POST with "Content-Type: application/x-www-form-urlencoded"
	or "Content-Type: multipart/form-data" with the POST body formatted accordingly.
	See: http://pubchem.ncbi.nlm.nih.gov/pug_rest/PUG_REST.html and
	http://pubchem.ncbi.nlm.nih.gov/pug_rest/PUG_REST_Tutorial.html
  '''
  n_out=0; tq=None; df=None;
  url = base_url+"/compound/inchi/cids/TXT"
  for inchi in inchis:
    if tq is None: tq = tqdm.tqdm(total=len(ids), unit="inchis")
    logging.info(f"inchi='{inchi}'")
    body_dict={'inchi':urllib.parse.quote(inchi)}
    #rval = rest.Utils.PostURL(url=url, headers={'Content-Type':'application/x-www-form-urlencoded','Accept':'text/plain'}, data=body_dict)
    response = requests.post(url=url, headers={'Content-Type':'application/x-www-form-urlencoded','Accept':'text/plain'}, data=body_dict)
    lines = response.text.splitlines()
    cids_this=set() 
    for line in lines:
      if re.match(r'[\d]+$', line.strip()):
        cid = line.strip()
        cids_this.add(cid)
    df_this = pd.DataFrame({"InChI":inchi, "CID":list(cids_this)})
    if fout is not None: df_this.to_csv(fout, "\t", header=bool(n_out==0))
    else: df = pd.concat([df, df_this])
    n_out += len(cids_this)
    tq.update(n=1)
  tq.close()
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
def GetAssayName(aids, base_url=BASE_URL, fout=None):
  n_out=0; tq=None; df=None;
  for aid in aids:
    if tq is None: tq = tqdm.tqdm(total=len(ids), unit="assays")
    xmlstr = requests.get(base_url+f"/assay/aid/{aid}/description/XML").text
    name, source = AssayXML2NameAndSource(xmlstr)
    df_this = pd.DataFrame({"AID":[aid], "Name":[name], "Source":[source]})
    if fout is not None: df_this.to_csv(fout, "\t", header=bool(n_out==0))
    else: df = pd.concat([df, df_this])
    n_out+=1
    tq.update(n=1)
  tq.close()
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
def GetAssayDescriptions(ids, skip, nmax, base_url=BASE_URL, fout=None):
  """Example AIDs: 527,159014"""
  n_in=0; n_out=0; tq=None; df=None;
  for aid in ids:
    n_in+=1
    if skip and n_in<skip: continue
    if nmax and n_out==nmax: break
    if tq is None: tq = tqdm.tqdm(total=len(ids), unit="assays")
    url = (base_url+f"/assay/aid/{aid}/description/JSON")
    rval = requests.get(url).json()
    logging.debug(json.dumps(rval, indent=2))
    assays = rval['PC_AssayContainer'] if 'PC_AssayContainer' in rval else []
    for assay in assays:
      descr = assay['assay']['descr'] if 'assay' in assay and 'descr'  in assay['assay'] else None
      if not descr: continue
      #aid = str(descr['aid']['id'])
      name = descr['name']
      source = descr['aid_source']['db']['name']
      revision = str(descr['revision'])
      project_category = str(descr['project_category'])
      activity_outcome_method = str(descr['activity_outcome_method'])
      assay_group = descr['assay_group'] if 'assay_group' in descr else '' #list of PMIDs
      description_lines = descr['description'] #list of lines
      comment_lines = descr['comment'] #list of lines
      description = (' ').join(description_lines)
      comment = (' ').join(comment_lines)
      df_this = pd.DataFrame({
	"aid":[aid],
	"name":[name],
	"source":[source],
	"revision":[revision],
	"assay_group":[(';'.join(assay_group))],
	"project_category":[project_category],
	"activity_outcome_method":[activity_outcome_method],
	"description":[description],
	"comment":[comment]
	})
      if fout is not None: df_this.to_csv(fout, "\t", header=bool(n_out==0), index=False)
      else: df = pd.concat([df, df_this])
      n_out+=1
    tq.update(n=1)
  tq.close()
  logging.info(f"n_out: {n_out}")
  return df

#############################################################################
def GetAssaySIDs(aids, skip, nmax, base_url=BASE_URL, fout=None):
  if skip: logging.info(f"SKIP: [1-{skip}]")
  if nmax: logging.info(f"NMAX: {nmax}")
  n_aid_in=0; n_aid_done=0; n_out=0; nchunk_sid=100; df=None; tags=None;
  tqa=None;
  for aid in aids:
    if tqa is None: tqa = tqdm.tqdm(total=len(aids), unit="assays")
    n_aid_in+=1
    if skip and n_aid_in<skip: continue
    if nmax and n_aid_done>=nmax: break
    n_aid_done+=1
    logging.debug(f"Request: ({n_aid_done}) [AID={aid}]")
    url = base_url+f"/assay/aid/{aid}/concise/JSON"
    rval = requests.get(url).json()
    logging.debug(json.dumps(rval, indent=2))
    tags_this = rval["Table"]["Columns"]["Column"]
    logging.debug(f"tags_this = {str(tags_this)}")
    j_sid=None; j_cid=None; 
    if not tags:
      tags = tags_this
      j_sid = tags.index("SID") if "SID" in tags else None
      j_cid = tags.index("CID") if "CID" in tags else None
    rows = rval["Table"]["Row"]
    logging.info(f"[AID={aid}] results/activities: {len(rows)}")
    tqb=None;
    for row in rows:
      if tqb is None: tqb = tqdm.tqdm(total=len(rows), unit="results")
      cells = row["Cell"]
      sid = cells[j_sid]
      cid = cells[j_cid]
      df_this = pd.DataFrame({"AID":[aid], "SID":[sid], "CID":[cid]})
      df = pd.concat([df, df_this])
      tqb.update()
    tqb.close()
    tqa.update()
  tqa.close()
  logging.info(f"AIDs: {df.AID.nunique()}; SIDs: {df.SID.nunique()}; CIDs: {df.CID.nunique()}")
  df.drop_duplicates(inplace=True)
  df.sort_values(by=["AID", "SID"], inplace=True)
  if fout is not None: df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
def GetAssaySIDResults(aids, sids, skip, nmax, base_url=BASE_URL, fout=None):
  '''One CSV line for each activity.  skip and nmax applied to AIDs.
In this version of the function, use the "concise" mode to download full data
for each AID, then iterate through SIDs and use local hash.
'''
  if skip: logging.info(f"skip: [1-{skip}]")
  if nmax: logging.info(f"NMAX: {nmax}")
  n_aid_in=0; n_aid_done=0; n_out=0; df=None; tqa=None;
  j_tag={};
  tags = None
  for aid in aids:
    if tqa is None: tqa = tqdm.tqdm(total=len(aids), unit="assays")
    n_aid_in+=1
    n_out_this=0;
    if skip and n_aid_in<skip: continue
    if nmax and n_aid_done>=nmax: break
    n_aid_done+=1
    logging.debug(f"Request: ({n_aid_done}) [AID={aid}] SID count: {len(sids)}")
    url = base_url+f"/assay/aid/{aid}/concise/JSON"
    rval = requests.get(url).json()
    if not tags:
      tags = rval["Table"]["Columns"]["Column"]
      logging.debug(f"tags= {str(tags)}")
      for tag in tags:
        j_tag[tag] = tags.index(tag)
    rows = rval["Table"]["Row"]
    tqb=None;
    for row in rows:
      if tqb is None: tqb = tqdm.tqdm(total=len(rows), unit="results")
      cells = row["Cell"]
      logging.debug(json.dumps(cells, indent=2))
      df_this = pd.DataFrame({tag:[cells[j_tag[tag]]] for tag in tags})
      df = pd.concat([df, df_this])
      tqb.update()
    tqb.close()
    tqa.update()
  tqa.close()
  logging.info(f"AIDs: {df.AID.nunique()}; SIDs: {df.SID.nunique()}; CIDs: {df.CID.nunique()}; Activity results: {df.shape[0]}")
  for key,val in df['Bioactivity Outcome'].value_counts().iteritems():
    logging.info(f'Bioactivity_Outcome = {key:>12}: {val:6d}')
  df.drop_duplicates(inplace=True)
  df.sort_values(by=["AID", "SID"], inplace=True)
  if fout is not None: df.to_csv(fout, "\t", index=False)
  return df

#############################################################################
def AssayXML2NameAndSource(xmlstr):
  '''Required: xpath - XPath Queries For DOM Trees, http://py-dom-xpath.googlecode.com/'''
  logging.debug(xmlstr)
  root = ElementTree.fromstring(xmlstr)
  ns = { "pc":"http://www.ncbi.nlm.nih.gov" }
  name = root.find("pc:PC-AssaySubmit/pc:PC-AssaySubmit_assay/pc:PC-AssaySubmit_assay_descr/pc:PC-AssayDescription/pc:PC-AssayDescription_name", ns).text  ##1st
  source = root.find("pc:PC-AssaySubmit/pc:PC-AssaySubmit_assay/pc:PC-AssaySubmit_assay_descr/pc:PC-AssayDescription/pc:PC-AssayDescription_aid-source/pc:PC-Source/pc:PC-Source_db/pc:PC-DBTracking/pc:PC-DBTracking_name",
ns).text
  return name,source

#############################################################################
def GetSID2Synonyms(ids, base_url=BASE_URL, fout=None):
  n_out=0; df=None;

  retry_strategy = Retry(
	total=30,
	backoff_factor=2,
	status_forcelist=[413, 429, 500, 502, 503, 504],
	method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE"]
	)
  adapter = HTTPAdapter(max_retries=retry_strategy)
  session = requests.Session()
  session.mount("https://", adapter)
  session.mount("http://", adapter)

  for i_sid in range(len(ids)):
    id_this = ids[i_sid]
    url_this = f"{base_url}/substance/sid/{id_this}/synonyms/JSON"
    response = session.get(url_this)
    if response.status_code!=200: #404 is normal
      logging.debug(f"Status code: {response.status_code}; url_this: {url_this}")
      continue
    rval = response.json()
    infos = rval['InformationList']['Information'] if 'InformationList' in rval and 'Information' in rval['InformationList'] else []
    for info in infos:
      synonyms_this = info['Synonym'] if 'Synonym' in info else []
      df_this = pd.DataFrame({"SID":id_this, "Synonym":synonyms_this})
      if fout is not None: df_this.to_csv(fout, "\t", header=bool(n_out==0), index=False)
      else: df = pd.concat([df, df_this])
      n_out+=len(synonyms_this)
  return df

#############################################################################
def GetCID2Synonyms(ids, skip, nmax, nmax_per_cid, base_url=BASE_URL, fout=None):
  sids_all = set([])
  i_cid=0; n_out=0; df=None;
  for i_cid in tqdm.auto.trange(len(ids), desc="CIDs"):
    id_this = ids[i_cid]
    if skip and i_cid<skip: continue
    sids_this = GetCID2SID([id_this], base_url)
    sids_all |= set(sids_this)
    synonyms_this_cid = set()
    for i_sid in tqdm.auto.trange(len(sids_this), desc="SIDs", leave=False):
      sid = sids_this[i_sid]
      synonyms_this_sid = GetSID2Synonyms([sid], base_url)
      if synonyms_this_sid is None: continue
      synonyms_this_sid = synonyms_this_sid.Synonym.tolist()
      synonyms_this_cid |= set(synonyms_this_sid)
    synonyms_this_cid_nice = SortCompoundNamesByNiceness(list(synonyms_this_cid))
    df_this = pd.DataFrame({"CID":id_this, "Synonym":synonyms_this_cid_nice}) 
    if df_this.shape[0]>nmax_per_cid:
      df_this = df_this[:nmax_per_cid]
      logging.debug(f"{i_cid+1}. CID={id_this}: synonyms out+truncated=all: {nmax_per_cid}+{len(synonyms_this_cid_nice)-nmax_per_cid}={len(synonyms_this_cid_nice)}")
    if fout is not None:
      df_this.to_csv(fout, "\t", header=bool(n_out==0), index=False)
      fout.flush()
    else: df = pd.concat([df, df_this])
    n_out+=len(synonyms_this_cid_nice)
    logging.debug(f"{i_cid+1}. CID={id_this}: SIDs: {len(sids_this)}; synonyms: {len(synonyms_this_cid)} ({min(len(synonyms_this_cid_nice), nmax_per_cid)})")
    if nmax and (i_cid+1)>=(skip+nmax): break
  logging.info(f"Totals: CIDs: {len(ids)}; SIDs: {len(sids_all)}; Synonyms: {n_out}")
  return df

#############################################################################
def GetCID2Nicename(ids, skip, nmax, base_url=BASE_URL, fout=None):
  return GetCID2Synonyms(ids, skip, nmax, 1, base_url, fout)

#############################################################################
def GetName2SID(names, skip, nmax, base_url=BASE_URL, fout=None):
  n_sid=0; sids_all=set(); df=None;
  for i_name in tqdm.auto.trange(len(names), leave=False):
    name = names[i_name]
    if skip and (i_name+1)<=skip: continue
    rval = requests.get(base_url+f"/substance/name/{urllib.parse.quote(name)}/sids/JSON").json()
    sids_this = rval['IdentifierList']['SID'] if 'IdentifierList' in rval and 'SID' in rval['IdentifierList'] else []
    for sid in sids_this:
      df_this = pd.DataFrame({"Name":[name], "SID":[sid]})
      if fout is not None: df_this.to_csv(fout, "\t", header=bool(n_sid==0), index=False)
      else: df = pd.concat([df, df_this])
      n_sid+=1
    sids_all |= set(sids_this)
    if nmax and (i_name+1)>=(skip+nmax): break
  logging.info(f"n_name: {len(names)}; n_sid: {n_sid}; n_sid_unique: {len(sids_all)}")
  return df

#############################################################################
def GetName2CID(names, skip, nmax, base_url=BASE_URL, fout=None):
  n_cid=0; cids_all=set(); n_sid=0; sids_all=set(); df=None;
  for i_name in tqdm.auto.trange(len(names), leave=False):
    name = names[i_name]
    if skip and (i_name+1)<=skip: continue
    #sids_this = GetName2SID([name], base_url)
    rval = requests.get(base_url+f"/substance/name/{urllib.parse.quote(name)}/sids/JSON").json()
    sids_this = rval['IdentifierList']['SID'] if 'IdentifierList' in rval and 'SID' in rval['IdentifierList'] else []
    sids_all |= set(sids_this)
    for sid in sids_this:
      n_sid+=1
      cids_this = list(set(GetSID2CID([sid], base_url)) )
      for cid in cids_this:
        df_this = pd.DataFrame({"Name":[name], "SID":[sid], "CID":[cid]})
        if fout is not None: df_this.to_csv(fout, "\t", header=bool(n_cid==0), index=False)
        else: df = pd.concat([df, df_this])
        n_cid+=1
      cids_all |= set(cids_this)
    if nmax and (i_name+1)>=(skip+nmax): break
  logging.info(f"n_name: {len(names)}; n_sid: {n_sid}; n_sid_unique: {len(sids_all)}; n_cid: {n_cid}; n_cid_unique: {len(cids_all)}")
  return df

#############################################################################
def GetName2Synonyms(names, skip, nmax, base_url=BASE_URL, fout=None):
  n_synonym=0; sids_all=set(); synonyms_all=set(); df=None;
  if fout: fout.write("Name\tSID\tSynonym\n")
  for i_name in tqdm.auto.trange(len(names), leave=False):
    name = names[i_name]
    sids_this = GetName2SID([name], 0, None, base_url)
    sids_all |= set(sids_this)
    for sid in sids_this:
      rval = requests.get(base_url+f"/substance/sid/{sid}/synonyms/JSON").json()
      infos = rval['InformationList']['Information'] if 'InformationList' in rval and 'Information' in rval['InformationList'] else []
      synonyms_this_sid = set()
      for info in infos:
        synonyms_this = info['Synonym'] if 'Synonym' in info else []
        synonyms_this_sid |= set(synonyms_this)
        for synonym in synonyms_this:
          n_synonym+=1
          if fout: fout.write(f"{name}\t{sid}\t{synonym}\n")
      synonyms_all |= set(synonyms_this_sid)
  logging.info(f"n_name: {len(names)}; n_synonym: {n_synonym}; n_synonym_unique: {len(synonyms_all)}; n_sids_unique: {len(sids_all)}")

#############################################################################
def NameNicenessScore(name, len_optimal=9):
  """Heuristic for human comprehensibility. In PubChem, a 'name' may be
any ID, often not useful."""
  score=0;
  pat_proper = re.compile(r'^[A-Z][a-z]+$')
  pat_text = re.compile(r'^[A-Za-z ]+$')
  if pat_proper.match(name): score+=100
  elif pat_text.match(name): score+=50
  elif re.match(r'^[A-z][A-z][A-z][A-z][A-z][A-z][A-z].*$', name): score+=10
  if re.search(r'[\[\]\{\}]', name): score-=50
  if re.search(r'[_/\(\)]', name): score-=10
  if re.search(r'\d', name): score-=10
  score -= math.fabs(len_optimal-len(name))
  return score

#############################################################################
def SortCompoundNamesByNiceness(names):
  names_scored = {n:NameNicenessScore(n) for n in names}
  names_ranked = [[score,name] for name,score in names_scored.items()]
  names_ranked.sort()
  names_ranked.reverse()
  return [name for score,name in names_ranked]

#############################################################################
def GetCpdAssayStats(cid, smiles, aidset, aidhash, base_url, fout_mol, fout_act):
  """
THIS FUNCTION NEEDS WORK.
From PubChem PUG REST API, determine activity stats for compounds.
 
 Input: smiles and CIDs
 Output (1):
   SMILES CID SID aTested aActive wTested wActive 
     where:
   aTested - how many assays where that cpd has been tested
   aActive - how many assays where that cpd has been tested active
   wTested - how many samples (wells) with that cpd have been tested
   wActive - how many samples (wells) with that cpd have been tested active
 
 Output (2): activity file, each line:
   CID SID AID Outcome
     where:
   1 = inactive
   2 = active
   3 = inconclusive
   4 = unspecified
   5 = probe
   multiple, differing 1, 2 or 3 = discrepant
   not 4 = tested
"""
  aids_tested=set(); aids_active=set();
  sids_tested=set(); sids_active=set();
  n_sam=0; n_sam_active=0; mol_active=False; mol_found=False;

  try:
    fcsv = requests.get(base_url+f"/compound/cid/{cid}/assaysummary/CSV").text
  except Exception as e:
    logging.error(f"[{cid}] REST request failed; {e}")
    fout_mol.write(f"{smiles}\t{cid}\n")
    return mol_found,mol_active,n_sam,n_sam_active
  mol_found=True

  try:
    csvReader=csv.DictReader(fcsv.splitlines(),fieldnames=None,restkey=None,restval=None,dialect='excel',delimiter=',',quotechar='"')
    csvrow = csvReader.next()    ## must do this to get fieldnames
  except Exception as e:
    logging.error(f"[CID={cid}] CSV problem:{e}")
    fout_mol.write(f"{smiles}\t{cid}\n")
    return mol_found,mol_active,n_sam,n_sam_active

  for field in ('AID','CID','SID','Bioactivity Outcome','Bioassay Type'):
    if field not in csvReader.fieldnames:
      logging.error(f"[CID={cid}] bad CSV header, no '{field}' field.")
      logging.debug("fieldnames: "+(','.join(map((lambda x:'"%s"'%x),csvReader.fieldnames))))
      fout_mol.write(f"{smiles}\t{cid}\n")
      return mol_found,mol_active,n_sam,n_sam_active

  n_in=0
  while True:
    try:
      csvrow=csvReader.next()
    except:
      break  ## EOF
    n_in+=1

    try:
      aid=int(csvrow['AID'])
      sid=int(csvrow['SID'])
      csvrow_cid=int(csvrow['CID'])
    except:
      logging.error(f"[CID={cid}] bad CSV line; problem parsing: '{str(csvrow)}'")
      continue
    if cid!=csvrow_cid:
      logging.error(f"Aaack! [CID={cid}] CID mismatch: != {csvrow_cid}")
      return mol_found,mol_active,n_sam,n_sam_active

    if aidset:
      if aid not in aidset:
        continue
      #logging.debug(f"AID [{aid}] ok (pre-selected).")

    ## Assay filtering done; now update statistics (sTested, sActive).
    n_sam+=1
    aidhash[aid]=True
    act_outcome=csvrow['Bioactivity Outcome'].lower()
    if act_outcome in OUTCOME_CODES:
      fout_act.write(f"{cid}\t{sid}\t{aid}\t{OUTCOME_CODES[act_outcome]}\n")
    else:
      logging.debug(f"[{n_in}] unrecognized outcome (CID={cid},AID={aid}): '{act_outcome}'")
    aids_tested.add(aid)
    sids_tested.add(sid)
    if act_outcome=='active':
      n_sam_active+=1
      mol_active=True
      aids_active.add(aid)
      sids_active.add(sid)

  logging.debug(f"[CID={cid}] CSV data lines: {n_in}")
  fout_mol.write(f"{smiles}\t{cid}\t{len(sids_tested)}\t{len(sids_active)}\t{len(aids_tested)}\t{len(aids_active)}\t{n_sam}\t{n_sam_active}\n")
  logging.debug("cid={cid},sTested={len(sids_tested)},sActive={len(sids_active)},aTested={len(aids_tested)},aActive={len(aids_active)},wTested={n_sam},wActive={n_sam_active}")
  return mol_found,mol_active,n_sam,n_sam_active

#############################################################################
def GetCpdAssayData(cid_query, aidset, base_url=BASE_URL, fout=None):
  """This function needs fixing."""
  try:
    fcsv = requests.get(base_url+f"/compound/cid/{cid_query}/assaysummary/CSV").text
  except Exception as e:
    logging.error(f"[{cid_query}] REST request failed; {e}")
    return False

  if not fcsv:
    return False

  try:
    csvReader=csv.DictReader(fcsv.splitlines(),fieldnames=None,restkey=None,restval=None,dialect='excel',delimiter=',',quotechar='"')
    csvrow=csvReader.next()    ## must do this to get fieldnames
  except Exception as e:
    logging.error(f"[CID={cid_query}] CSV problem: {e}")
    return True

  for field in ('CID','SID','AID','Bioactivity Outcome','Activity Value [uM]'):
    if field not in csvReader.fieldnames:
      logging.error(f"[CID={cid_query}] bad CSV header, no '{field}' field.")
      logging.debug("fieldnames: "+(','.join(map((lambda x:'"%s"'%x),csvReader.fieldnames))))
      return True

  n_in=0; n_act=0;
  while True:
    try:
      csvrow=csvReader.next()
    except:
      break  ## EOF
    n_in+=1
    try:
      aid=int(csvrow['AID'])
      sid=int(csvrow['SID'])
      cid=int(csvrow['CID'])
      outcome=csvrow['Bioactivity Outcome']
    except:
      logging.error(f"[CID={cid}] bad CSV line; problem parsing.")
      logging.debug(f"csvrow = {str(csvrow)}")
      continue
    if cid_query!=cid:
      logging.error(f"Aaack! [CID={cid}] CID mismatch: != {int(csvrow['CID'])}")
      return True
    if aid not in aidset:
      continue
      logging.debug(f"AID [{aid}] ok (pre-selected).")

    if not csvrow['Activity Value [uM]']:
      continue

    try:
      actval=float(csvrow['Activity Value [uM]'])
    except:
      logging.error(f"[CID={cid}] bad CSV line; problem parsing activity: '{csvrow['Activity Value [uM]']}'")
      continue

    n_act+=1
    outcome_code = OUTCOME_CODES[outcome.lower()] if outcome.lower() in OUTCOME_CODES else 0

    fout.write(f"{cid}\t{sid}\t{aid}\t{outcome_code}\t{actval:.3f}\n")

  logging.info(f"[CID={cid_query}] records: {n_in}; activities: {n_act}")
  return True

#############################################################################
