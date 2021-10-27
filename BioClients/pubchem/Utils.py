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
import sys,os,io,re,csv,json,pandas,math,time,logging,tempfile,tqdm
from xml.etree import ElementTree
import requests
import urllib.request,urllib.parse
import pandas as pd
#
from ..util import rest #replace PostURL with requests.post()
#
OUTCOME_CODES = {
        'inactive':1,
        'active':2,
        'inconclusive':3,
        'unspecified':4,
        'probe':5}
#
#############################################################################
def ListSources(base_url, src_type, fout):
  rval = requests.get(base_url+f"/sources/{src_type}/JSON").json()
  logging.debug(json.dumps(rval,indent=2))
  sources = rval['InformationList']['SourceName'] if 'InformationList' in rval and 'SourceName' in rval['InformationList'] else []
  n_src=0;
  for source in sorted(sources):
    fout.write(f"{source}\n")
    n_src+=1
  logging.info(f"n_src ({src_type}): {n_src}")

##############################################################################
def GetSID2SDF(base_url, id_query):
  url = (base_url+f"/substance/sid/{id_query}/SDF")
  txt = requests.get(url).text
  return txt

#############################################################################
def GetSID2CID(base_url, sids, fout):
  cids = set()
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
def GetSID2Smiles(base_url, sids, fout):
  cids = GetSID2CID(base_url, sids, None)
  GetCID2Smiles(base_url, cids, fout)

#############################################################################
def GetCID2SID(base_url, cids, fout):
  sids = set()
  if fout: fout.write("CID\tSID\n")
  for cid in cids:
    rval = requests.get(base_url+f"/compound/cid/{cid}/sids/JSON").json()
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
def GetSmiles2CID(base_url, smis, fout):
  n_out=0;
  fout.write("CID\tSMILES\tName\n")
  for smi in smis:
    name = re.sub(r'^[\S]+\s', '', smi) if re.search(r'^[\S]+\s', smi) else ""
    smi = re.sub(r'\s.*$', '', smi)
    rval = requests.get(base_url+f"/compound/smiles/{urllib.parse.quote(smi, '')}/cids/JSON").json()
    if not rval: continue
    cids = rval['IdentifierList']['CID'] if 'IdentifierList' in rval and 'CID' in rval['IdentifierList'] else []
    for cid in cids:
      fout.write(f"{cid}\t{smi}\t{name}\n")
      n_out+=1
  logging.info(f"SMIs: {len(smis)}; CIDs out: {n_out}")

#############################################################################
def GetCID2AssaySummary(base_url, ids, fout):
  """Example CIDs: 2519 (caffeine), 3034034 (quinine)"""
  n_out=0;
  for i,id_this in enumerate(ids):
    rval = requests.get(base_url+f"/compound/cid/{id_this}/assaysummary/CSV").text
    logging.debug(rval)
    if not rval: continue
    df = pandas.read_csv(io.StringIO(rval), sep=',')
    df.to_csv(fout, sep='\t', index=False, header=bool(i==0))
    n_out += df.shape[0]
  logging.info(f"CIDs: {len(ids)}; assay summaries out: {n_out}")

#############################################################################
def GetSID2AssaySummary(base_url, ids, fout):
  n_out=0;
  for id_this in ids:
    rval = requests.get(base_url+f"/substance/sid/{id_this}/assaysummary/CSV").text
    if not rval: continue
    df = pandas.read_csv(io.StringIO(rval), sep=',')
    df.to_csv(fout, sep='\t', index=False, header=bool(i==0))
    n_out += df.shape[0]
  logging.info(f"SIDs: {len(ids)}; assay summaries out: {n_out}")

#############################################################################
def GetCID2Inchi(base_url, ids, fout):
  PROPTAGS = [ "InChIKey", "InChI" ]
  ids_dict = {'cid':(','.join(map(lambda x:str(x), ids)))}
  url = (base_url+f"/compound/cid/property/{','.join(PROPTAGS)}/CSV")
  rval = rest.Utils.PostURL(url, headers={'Accept':'text/CSV', 'Content-type':'application/x-www-form-urlencoded'}, data=ids_dict)
  df = pandas.read_csv(io.StringIO(rval), sep=',')
  df.to_csv(fout, sep='\t', index=False)
  logging.info(f"Input IDs: {len(ids)}; Output InChIs: {df.shape[0]}")

##############################################################################
def GetCID2SDF(base_url, ids, fout):
  """Faster via POST(?). Request in chunks.  Works for 50, and not
  for 200 (seems to be a limit)."""
  nchunk=50; nskip_this=0; n_out=0;
  while True:
    if nskip_this>=len(ids): break
    idstr = (','.join(map(lambda x:str(x), ids[nskip_this:nskip_this+nchunk])))
    rval = rest.Utils.PostURL(base_url+'/compound/cid/SDF', data={'cid':idstr})
    fout.write(rval)
    n_out += len(re.findall(r'^\$\$\$\$$', rval, re.M))
    nskip_this+=nchunk
  logging.info(f"SDFs out: {n_out}")

#############################################################################
def GetSID2SDF(base_url, sids, skip, nmax, fout):
  """Faster via POST(?). Request in chunks.  Works for 50, and not
  for 200 (seems to be a limit)."""
  n_out=0;
  if skip: logging.debug(f"skip: [1-{skip}]")
  nchunk=50; nskip_this=skip;
  while True:
    if nskip_this>=len(sids): break
    nchunk = min(nchunk, nmax-(nskip_this-skip))
    n_sid_in+=nchunk
    idstr = (','.join(map(lambda x:str(x), sids[nskip_this:nskip_this+nchunk])))
    rval = rest.Utils.PostURL(base_url+'/substance/sid/SDF', data={'sid':idstr})
    if rval:
      fout.write(rval)
      n_out += len(re.findall(r'^\$\$\$\$$', rval, re.M))
    nskip_this+=nchunk
    if nmax and (nskip_this-skip)>=nmax:
      logging.info(f"NMAX limit reached: {nmax}")
      break
  logging.info(f"SIDs: {len(sids)}; SDFs out: {n_out}")

#############################################################################
def GetCID2Smiles(base_url, ids, isomeric, fout=None):
  """Returns Canonical or Isomeric SMILES."""
  nchunk=50; nskip_this=0; tq=None;
  n_in=0; n_out=0; n_err=0; results=[];
  while True:
    if tq is None: tq = tqdm.tqdm(total=len(ids), unit="mols")
    if nskip_this>=len(ids): break
    ids_this = ids[nskip_this:nskip_this+nchunk]
    n_in+=len(ids_this)
    idstr = (','.join(map(lambda x:str(x), ids_this)))
    prop = 'IsomericSMILES' if isomeric else 'CanonicalSMILES'
    txt = rest.Utils.PostURL(base_url+f"/compound/cid/property/{prop}/CSV", data={'cid':idstr})
    lines = txt.splitlines()
    for line in lines:
      cid,smi = re.split(',', line)
      if cid.upper()=='CID': continue #header
      smi = smi.replace('"', '')
      results.append([smi, cid])
      n_out+=1
    nskip_this+=nchunk
    tq.update(n=len(ids_this))
  tq.close()
  df = pd.DataFrame(results, columns=["SMILES", "CID"])
  logging.info(f"CIDs in: {n_in}; SMILES (isomeric={bool(isomeric)}) out: {n_out}; errors: {n_err}")
  if fout is not None:
    df.to_csv(fout, "\t", index=False)
  else:
    return df

#############################################################################
def GetCID2Properties(base_url, ids, fout=None):
  PROPTAGS = ["CanonicalSMILES", "IsomericSMILES", "InChIKey", "InChI", "MolecularFormula", "HeavyAtomCount", "MolecularWeight", "XLogP", "TPSA"]
  url = (base_url+"/compound/cid/property/{}/CSV".format(','.join(PROPTAGS)))
  nchunk=50; nskip_this=0; df=None; tq=None;
  n_in=0; n_out=0; n_err=0; results=[];
  while True:
    if tq is None: tq = tqdm.tqdm(total=len(ids), unit="mols")
    if nskip_this>=len(ids): break
    ids_this = ids[nskip_this:nskip_this+nchunk]
    n_in+=len(ids_this)
    idstr = (','.join(map(lambda x:str(x), ids_this)))
    rval = rest.Utils.PostURL(url, headers={'Accept':'text/CSV', 'Content-type':'application/x-www-form-urlencoded'}, data={'cid':idstr})
    df_this = pandas.read_csv(io.StringIO(rval), sep=',')
    if fout is not None:
      df_this.to_csv(fout, sep='\t', index=False, header=bool(n_out==0))
    else:
      df = pd.concat([df, df_this])
    nskip_this+=nchunk
    n_out+=len(ids_this)
    tq.update(n=len(ids_this))
  tq.close()
  logging.info(f"Input IDs: {len(ids)}; Output records: {n_out}")
  if fout is None:
    return df

#############################################################################
def Inchi2CID(base_url, inchis, fout):
  '''	Must be POST with "Content-Type: application/x-www-form-urlencoded"
	or "Content-Type: multipart/form-data" with the POST body formatted accordingly.
	See: http://pubchem.ncbi.nlm.nih.gov/pug_rest/PUG_REST.html and
	http://pubchem.ncbi.nlm.nih.gov/pug_rest/PUG_REST_Tutorial.html
  '''
  n_out=0;
  fout.write("InChI\tCID\n")
  for inchi in inchis:
    url = "http://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/inchi/cids/TXT"
    logging.info('inchi="%s"'%(inchi))
    body_dict={'inchi':urllib.parse.quote(inchi)}
    rval = rest.Utils.PostURL(url=url, headers={'Content-Type':'application/x-www-form-urlencoded','Accept':'text/plain'}, data=body_dict)
    cids_this = set()
    lines = rval.splitlines()
    for line in lines:
      if re.match(r'[\d]+$', line.strip()):
        cid = line.strip()
        cids_this.add(cid)
        fout.write(f"{inchi}\t{cid}\n")
        n_out+=1
  logging.info(f"n_out: {n_out}")

#############################################################################
def GetAssayName(base_url, aids, fout):
  for aid in aids:
    xmlstr = requests.get(base_url+f"/assay/aid/{aid}/description/XML").text
    name, source = AssayXML2NameAndSource(xmlstr)
    fout.write(f"{aid}\t{name}\t{source}\n")

#############################################################################
def GetAssayDescriptions(base_url, ids, skip, nmax, fout=None):
  """Example AIDs: 527,159014"""
  n_in=0; n_out=0; df=None;
  for aid in ids:
    n_in+=1
    if skip and n_in<skip: continue
    if nmax and n_out==nmax: break
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
      if fout is not None:
        df_this.to_csv(fout, "\t", index=False)
      else:
        df = pd.concat([df, df_this])
      n_out+=1
  logging.info(f"n_out: {n_out}")
  if fout is None: return df

#############################################################################
def OutcomeCode(txt):
  return OUTCOME_CODES[txt.lower()] if txt.lower() in OUTCOME_CODES else OUTCOME_CODES['unspecified']

#############################################################################
def GetAssaySIDs(base_url, aids, skip, nmax, fout=None):
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
  else: return df

#############################################################################
def GetAssaySIDResults(base_url, aids, sids, skip, nmax, fout):
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
  else: return df

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
def GetSID2Synonyms(base_url, sids, fout):
  synonyms=[]
  if fout: fout.write("SID\tSynonym\n")
  for sid in sids:
    rval = requests.get(base_url+f"/substance/sid/{sid}/synonyms/JSON").json()
    infos = rval['InformationList']['Information'] if 'InformationList' in rval and 'Information' in rval['InformationList'] else []
    for info in infos:
      synonyms_this = info['Synonym'] if 'Synonym' in info else []
      for synonym in synonyms_this:
        synonyms.append(synonym)
        if fout: fout.write(f"{sid}\t{synonym}\n")
  return synonyms

#############################################################################
def GetCID2Synonyms(base_url, cids, skip, nmax, nmax_per_cid, fout):
  fout.write('CID\tSynonym\n')
  sids_all = set([])
  i_cid=0; n_out=0;
  for cid in cids:
    i_cid+=1
    if skip and i_cid<=skip: continue
    sids_this = GetCID2SID(base_url, [cid], None)
    sids_all |= set(sids_this)
    synonyms_this_cid = set()
    for sid in sids_this:
      synonyms_this_sid = GetSID2Synonyms(base_url, [sid], None)
      synonyms_this_cid |= set(synonyms_this_sid)
    synonyms_this_cid_nice = SortCompoundNamesByNiceness(list(synonyms_this_cid))
    for j,synonym in enumerate(synonyms_this_cid_nice):
      if nmax_per_cid and j>=nmax_per_cid:
        logging.info(f"{i_cid}. CID={cid}: synonyms out+truncated=all: {nmax_per_cid}+{len(synonyms_this_cid_nice)-nmax_per_cid}={len(synonyms_this_cid_nice)}")
        break
      fout.write(f"{cid}\t{synonym}\n")
      n_out+=1
    logging.info(f"{i_cid}. CID={cid}: SIDs: {len(sids_this)}; synonyms: {len(synonyms_this_cid)} ({min(len(synonyms_this_cid_nice), nmax_per_cid)})")
    if nmax and i_cid>=(skip+nmax): break
  logging.info(f"Totals: CIDs: {len(cids)}; SIDs: {len(sids_all)}; Synonyms: {n_out}")

#############################################################################
def GetName2SID(base_url, names, fout):
  n_sid=0; sids_all = set()
  if fout: fout.write("Name\tSID\n")
  for name in names:
    rval = requests.get(base_url+f"/substance/name/{urllib.parse.quote(name)}/sids/JSON").json()
    sids_this = rval['IdentifierList']['SID']
    for sid in sids_this:
      n_sid+=1
      if fout: fout.write(f"{name}\t{sid}\n")
      sids_all |= set(sids_this)
  logging.info(f"n_name: {len(names)}; n_sid: {n_sid}; n_unique: {len(sids_all)}")
  return list(sids_all)

#############################################################################
def GetName2CID(base_url, names, fout):
  n_cid=0; cids_all = set()
  if fout: fout.write("Name\tCID\n")
  for name in names:
    sids_this = GetName2SID(base_url, [name], None)
    cids_this = list(set(GetSID2CID(base_url, sids_this, None)) )
    for cid in cids_this:
      n_cid+=1
      if fout: fout.write(f"{name}\t{cid}\n")
    cids_all |= set(cids_this)
  logging.info(f"n_name: {len(names)}; n_cid: {n_cid}; n_unique: {len(cids_all)}")
  return list(cids_all)

#############################################################################
def GetName2Synonyms(base_url, names, fout):
  n_synonym=0; sids_all = set(); synonyms_all = set()
  if fout: fout.write("Name\tSID\tSynonym\n")
  for name in names:
    sids_this = GetName2SID(base_url, [name], None)
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
  logging.info(f"n_name: {len(names)}; n_synonym: {n_synonym}; n_unique: {len(synonyms_all)}; n_sids_unique: {len(sids_all)}")

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
def GetCpdAssayStats(base_url, cid, smiles, aidset, fout_mol, fout_act, aidhash):
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
def GetCpdAssayData(base_url, cid_query, aidset, fout):
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
