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
import sys,os,io,re,csv,json,pandas,math,time,logging
import urllib.request,urllib.parse
#
from ..util import rest_utils
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
  rval = rest_utils.GetURL(base_url+'/sources/%s/JSON'%src_type, parse_json=True)
  logging.debug(json.dumps(rval,indent=2))
  sources = rval['InformationList']['SourceName'] if 'InformationList' in rval and 'SourceName' in rval['InformationList'] else []
  n_src=0;
  for source in sorted(sources):
    fout.write('"%s"\n'%source)
    n_src+=1
  logging.info('n_src (%s): %d'%(src_type, n_src))

##############################################################################
def GetSID2SDF(base_url, id_query):
  url=(base_url+'/substance/sid/%d/SDF'%id_query)
  txt=rest_utils.GetURL(url)
  return txt

#############################################################################
def GetSID2CID(base_url, sids, fout):
  cids = set()
  if fout: fout.write("SID\tCID\n")
  for sid in sids:
    rval = rest_utils.GetURL(base_url+'/substance/sid/%s/cids/JSON?cids_type=standardized'%sid, parse_json=True)
    infos = rval['InformationList']['Information'] if 'InformationList' in rval and 'Information' in rval['InformationList'] else []
    for info in infos:
      cids_this = info['CID'] if 'CID' in info else []
      for cid in cids_this:
        cids.add(str(cid))
        if fout: fout.write("%s\t%s\n"%(sid, cid))
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
    rval = rest_utils.GetURL(base_url+'/compound/cid/%s/sids/JSON'%cid, parse_json=True)
    infos = rval['InformationList']['Information'] if 'InformationList' in rval and 'Information' in rval['InformationList'] else []
    for info in infos:
      sids_this = info['SID'] if 'SID' in info else []
      for sid in sids_this:
        sids.add(str(sid))
        if fout: fout.write("%s\t%s\n"%(cid, sid))
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
    rval = rest_utils.GetURL(base_url+'/compound/smiles/%s/cids/JSON'%urllib.parse.quote(smi, ''), parse_json=True)
    if not rval: continue
    cids = rval['IdentifierList']['CID'] if 'IdentifierList' in rval and 'CID' in rval['IdentifierList'] else []
    for cid in cids:
      fout.write("%s\t%s\t%s\n"%(cid, smi, name))
      n_out+=1
  logging.info('SMIs: %d; CIDs out: %d'%(len(smis), n_out))

#############################################################################
def GetCID2AssaySummary(base_url, ids, fout):
  """Example CIDs: 2519 (caffeine), 3034034 (quinine)"""
  n_out=0;
  for i,id_this in enumerate(ids):
    rval = rest_utils.GetURL(base_url+'/compound/cid/%s/assaysummary/CSV'%id_this)
    logging.debug(rval)
    if not rval: continue
    df = pandas.read_csv(io.StringIO(rval), sep=',')
    df.to_csv(fout, sep='\t', index=False, header=bool(i==0))
    n_out += df.shape[0]
  logging.info('CIDs: %d; assay summaries out: %d'%(len(ids), n_out))

#############################################################################
def GetSID2AssaySummary(base_url, ids, fout):
  n_out=0;
  for id_this in ids:
    rval = rest_utils.GetURL(base_url+'/substance/sid/%s/assaysummary/CSV'%id_this)
    if not rval: continue
    df = pandas.read_csv(io.StringIO(rval), sep=',')
    df.to_csv(fout, sep='\t', index=False, header=bool(i==0))
    n_out += df.shape[0]
  logging.info('SIDs: %d; assay summaries out: %d'%(len(ids), n_out))

#############################################################################
def GetCID2Properties(base_url, ids, fout):
  PROPTAGS = [ "CanonicalSMILES", "IsomericSMILES", "InChIKey", "InChI", "MolecularFormula", "HeavyAtomCount", "MolecularWeight", "XLogP", "TPSA"]
  ids_dict = {'cid':(','.join(map(lambda x:str(x), ids)))}
  url = (base_url+'/compound/cid/property/%s/CSV'%(','.join(PROPTAGS)))
  rval = rest_utils.PostURL(url, headers={'Accept':'text/CSV', 'Content-type':'application/x-www-form-urlencoded'}, data=ids_dict)
  df = pandas.read_csv(io.StringIO(rval), sep=',')
  df.to_csv(fout, sep='\t', index=False)
  logging.info("Input IDs: {0}; Output records: {1}".format(len(ids), df.shape[0]))

#############################################################################
def GetCID2Inchi(base_url, ids, fout):
  PROPTAGS = [ "InChIKey", "InChI" ]
  ids_dict = {'cid':(','.join(map(lambda x:str(x), ids)))}
  url = (base_url+'/compound/cid/property/%s/CSV'%(','.join(PROPTAGS)))
  rval = rest_utils.PostURL(url, headers={'Accept':'text/CSV', 'Content-type':'application/x-www-form-urlencoded'}, data=ids_dict)
  df = pandas.read_csv(io.StringIO(rval), sep=',')
  df.to_csv(fout, sep='\t', index=False)
  logging.info("Input IDs: {0}; Output InChIs: {1}".format(len(ids), df.shape[0]))

##############################################################################
#def GetCID2SDF(base_url, ids, fout):
#  n_out=0;
#  for cid in ids:
#    url = (base_url+'/compound/cid/%d/SDF'%cid)
#    rval = rest_utils.GetURL(url)
#    fout.write(rval)
#  logging.info('SDFs out: %d'%n_out)
#
#############################################################################
def GetCID2SDF(base_url, ids, fout):
  """Faster via POST(?). Request in chunks.  Works for 50, and not
  for 200 (seems to be a limit)."""
  nchunk=50; nskip_this=0; n_out=0;
  while True:
    if nskip_this>=len(ids): break
    idstr = (','.join(map(lambda x:str(x), ids[nskip_this:nskip_this+nchunk])))
    rval = rest_utils.PostURL(base_url+'/compound/cid/SDF', data={'cid':idstr})
    fout.write(rval)
    n_out += len(re.findall(r'^\$\$\$\$$', rval, re.M))
    nskip_this+=nchunk
  logging.info('SDFs out: %d'%n_out)

#############################################################################
def GetSID2SDF(base_url, sids, skip, nmax, fout):
  """Faster via POST(?). Request in chunks.  Works for 50, and not
  for 200 (seems to be a limit)."""
  n_out=0;
  if skip: logging.debug('skip: [1-%d]'%skip)
  nchunk=50; nskip_this=skip;
  while True:
    if nskip_this>=len(sids): break
    nchunk = min(nchunk, nmax-(nskip_this-skip))
    n_sid_in+=nchunk
    idstr = (','.join(map(lambda x:str(x), sids[nskip_this:nskip_this+nchunk])))
    rval = rest_utils.PostURL(base_url+'/substance/sid/SDF', data={'sid':idstr})
    if rval:
      fout.write(rval)
      n_out += len(re.findall(r'^\$\$\$\$$', rval, re.M))
    nskip_this+=nchunk
    if nmax and (nskip_this-skip)>=nmax:
      logging.info('NMAX limit reached: %d'%nmax)
      break
  logging.info('SIDs: %d ; SDFs out: %d'%(len(sids), n_out))

#############################################################################
def GetCID2Smiles(base_url, ids, isomeric, fout):
  """Returns Canonical or Isomeric SMILES."""
  t0 = time.time()
  nchunk=50; nskip_this=0;
  n_in=0; n_out=0; n_err=0;
  fout.write('CID\t%s\n'%('IsomericSMILES' if isomeric else 'CanonicalSMILES'))
  while True:
    if nskip_this>=len(ids): break
    ids_this = ids[nskip_this:nskip_this+nchunk]
    n_in+=len(ids_this)
    idstr = (','.join(map(lambda x:str(x), ids_this)))
    prop = 'IsomericSMILES' if isomeric else 'CanonicalSMILES'
    txt = rest_utils.PostURL(base_url+'/compound/cid/property/%s/CSV'%prop, data={'cid':idstr})
    if not txt:
      n_err+=1
      break
    lines = txt.splitlines()
    for line in lines:
      cid,smi = re.split(',', line)
      if cid.upper()=='CID': continue #header
      try:
        cid = int(cid)
      except:
        continue
      smi = smi.replace('"', '')
      fout.write('%s %d\n'%(smi, cid))
      n_out+=1
    nskip_this+=nchunk
    if (n_in%1000)==0:
      logging.info('processed: %6d / %6d (%.1f%%); elapsed time: %s'%(n_in, len(ids), 100.0*n_in/len(ids), time.gmtime(time.time()-t0)))
  logging.info('CIDs in: %d; SMILES (isomeric=%s) out: %d; errors: %d'%(n_in, bool(isomeric), n_out, n_err))

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
    rval = rest_utils.PostURL(url=url, headers={'Content-Type':'application/x-www-form-urlencoded','Accept':'text/plain'}, data=body_dict)
    cids_this = set()
    lines = rval.splitlines()
    for line in lines:
      if re.match(r'[\d]+$', line.strip()):
        cid = line.strip()
        cids_this.add(cid)
        fout.write("%s\t%s\n"%(inchi, cid))
        n_out+=1
  logging.info('n_out: %d'%n_out)

#############################################################################
def GetAssayName(base_url, aids, fout):
  for aid in aids:
    xmlstr = rest_utils.GetURL(base_url+'/assay/aid/%d/description/XML'%id_query)
    name, source = AssayXML2NameAndSource(xmlstr)
    fout.write('%d\t%s\t%s'%(aid, name, source))

#############################################################################
def GetAssayDescriptions(base_url, ids, skip, nmax, fout):
  """Example AIDs: 159014"""
  n_in=0; n_out=0;
  fout.write("aid\tname\tsource\trevision\tassay_group\tproject_category\tactivity_outcome_method\tdescription\tcomment\n")
  for aid in ids:
    n_in+=1
    if skip and n_in<skip: continue
    if nmax and n_out==nmax: break
    url = (base_url+'/assay/aid/%s/description/JSON'%aid)
    rval = rest_utils.GetURL(url, parse_json=True)
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
      assay_group = descr['assay_group'] #list of PMIDs
      description_lines = descr['description'] #list of lines
      comment_lines = descr['comment'] #list of lines
      description = (r'\\n').join(description_lines)
      comment = (r'\\n').join(comment_lines)
      vals = [aid, name, source, revision, (';'.join(assay_group)), project_category, activity_outcome_method, description, comment]
      fout.write('\t'.join(vals)+'\n')
      n_out+=1
  logging.info("n_out: %d"%n_out)

#############################################################################
def OutcomeCode(txt):
  return OUTCOME_CODES[txt.lower()] if txt.lower() in OUTCOME_CODES else OUTCOME_CODES['unspecified']

#############################################################################
def GetAssaySIDResults(base_url, aids, sids, skip, nmax, fout):
  '''One CSV line for each activity.  skip and nmax applied to AIDs.
In this version of the function, use the "concise" mode to download full data
for each AID, then iterate through SIDs and use local hash.
'''
  if skip: logging.info('skip: [1-%d]'%skip)
  if nmax: logging.info('NMAX: %d'%nmax)
  n_aid_in=0; n_aid_done=0; n_out=0;
  nchunk_sid=100;
  #fout.write('aid,sid,outcome,version,rank,year\n')
  tags = None
  for aid in aids:
    n_aid_in+=1
    n_out_this=0;
    if skip and n_aid_in<skip: continue
    if nmax and n_aid_done>=nmax: break
    n_aid_done+=1
    logging.debug('Request: (%d) [AID=%d] SID count: %d'%(n_aid_done,aid,len(sids)))
    try:
      url = base_url+'/assay/aid/%d/concise/JSON'%(aid)
      logging.debug('%s'%(url))
      rval = rest_utils.GetURL(url,parse_json=True)
    except Exception as e:
      logging.info('Error: %s'%(e))
      break

    if not type(rval) is dict:
      #logging.info('Error: %s'%(str(rval)))
      f = open("z.z", "w")
      f.write(str(rval))
      f.close()
      logging.debug('rval not DictType.  See z.z')
      break
    adata = {} # data this assay
    tags_this = rval["Table"]["Columns"]["Column"]
    logging.debug('tags_this = %s'%(str(tags_this)))
    j_sid = None;
    j_res = None;
    if not tags:
      tags = tags_this
      for j,tag in enumerate(tags):
        if tag == 'SID': j_sid = j
        if tag == 'Bioactivity Outcome': j_res = j
      fout.write(','.join(tags)+'\n')

    rows = rval["Table"]["Row"]

    for row in rows:
      cells = row["Cell"]
      if len(cells) != len(tags):
        logging.info('Error: n_cells != n_tags (%d != %d)'%(len(cells), len(tags)))
        continue

      sid = cells[j_sid]
      res = cells[j_res]
      adata[sid] = res

      #break #DEBUG

#############################################################################
def GetAssaySIDResults_OLD(base_url, aids, sids, skip, nmax, fout):
  '''One CSV line for each activity.  skip and nmax applied to AIDs.
Must chunk the SIDs, since requests limited to 10k SIDs.
'''
  if skip: logging.info('skip: [1-%d]'%skip)
  if nmax: logging.info('NMAX: %d'%nmax)
  n_aid_in=0; n_aid_done=0; n_out=0;
  nchunk_sid=100;
  fout.write('aid,sid,outcome,version,rank,year\n')
  for aid in aids:
    n_aid_in+=1
    n_out_this=0;
    if skip and n_aid_in<skip: continue
    if nmax and n_aid_done>=nmax: break
    n_aid_done+=1
    logging.debug('Request: (%d) [AID=%d] SID count: %d'%(n_aid_done,aid,len(sids)))
    nskip_sid=0;
    while True:
      if nskip_sid>=len(sids): break
      logging.debug('(%d) [AID=%s] ; SIDs [%d-%d of %d] ; measures: %d'%(n_aid_done,aid,nskip_sid+1,min(nskip_sid+nchunk_sid,len(sids)),len(sids),n_out_this))
      sidstr=(','.join(map(lambda x:str(x),sids[nskip_sid:nskip_sid+nchunk_sid])))
      try:
        rval = rest_utils.GetURL(base_url+'/assay/aid/%d/JSON?sid=%s'%(aid,sidstr),parse_json=True)
      except Exception as e:
        logging.info('Error: %s'%(e))
        break
      if not type(rval) is dict:
        logging.info('Error: %s'%(str(rval)))
        break
      pcac = rval['PC_AssayContainer'] if 'PC_AssayContainer' in rval else None
      if len(pcac)<1:
        logging.info('Error: [%s] empty PC_AssayContainer.'%aid)
        break
      if len(pcac)>1:
        logging.info('NOTE: [%s] multiple assays in PC_AssayContainer.'%aid)
      for assay in pcac:
        if not assay: continue
        logging.debug(json.dumps(assay,indent=2))
        ameta = assay['assay'] if 'assay' in assay else None
        adata = assay['data'] if 'data' in assay else None
        if not ameta: logging.info('Error: [%s] no metadata.'%aid)
        if not adata: logging.info('Error: [%s] no data.'%aid)
        for datum in adata:
          sid = datum['sid'] if 'sid' in datum else ''
          outcome = datum['outcome'] if 'outcome' in datum else ''
          version = datum['version'] if 'version' in datum else ''
          rank = datum['rank'] if 'rank' in datum else ''
          date = datum['date'] if 'date' in datum else {}
          year = date['std']['year'] if 'std' in date and 'year' in date['std'] else ''
          fout.write('%d,%s,%d,%s,%s,%s\n'%(aid,sid,OutcomeCode(outcome),version,rank,year))
          fout.flush()
          n_out_this+=1
      nskip_sid+=nchunk_sid
    logging.debug('Result: [AID=%d] total measures: %d'%(aid,n_out_this))

  return n_aid_in,n_out

#############################################################################
def AssayXML2NameAndSource(xmlstr):
  '''Required: xpath - XPath Queries For DOM Trees, http://py-dom-xpath.googlecode.com/'''
  tag_name='PC-AssayDescription_name'
  tag_source='PC-DBTracking_name'

  #import xpath #old
  #dom=xml.dom.minidom.parseString(xmlstr)
  #name=xpath.findvalue('//%s'%tag_name,dom)  ##1st
  #source=xpath.findvalue('//%s'%tag_source,dom)  ##1st

  from xml.etree import ElementTree #newer

  root = ElementTree.fromstring(xmlstr)
  name=root.find('//%s'%tag_name).text  ##1st
  source=root.find('//%s'%tag_sourcedom).text  ##1st

  return name,source

#############################################################################
def GetSID2Synonyms(base_url, sids, fout):
  synonyms=[]
  if fout: fout.write("SID\tSynonym\n")
  for sid in sids:
    rval = rest_utils.GetURL(base_url+'/substance/sid/%s/synonyms/JSON'%(sid), parse_json=True)
    infos = rval['InformationList']['Information'] if 'InformationList' in rval and 'Information' in rval['InformationList'] else []
    for info in infos:
      synonyms_this = info['Synonym'] if 'Synonym' in info else []
      for synonym in synonyms_this:
        synonyms.append(synonym)
        if fout: fout.write("%s\t%s\n"%(sid,synonym))
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
        logging.info('%d. CID=%s: synonyms out+truncated=all: %d+%d=%d'%(
            i_cid, cid, nmax_per_cid,
            len(synonyms_this_cid_nice)-nmax_per_cid,
            len(synonyms_this_cid_nice)))
        break
      fout.write('%s\t%s\n'%(cid, synonym))
      n_out+=1
    logging.info('%d. CID=%s: SIDs: %d ; synonyms: %d (%d)'%(i_cid, cid,
        len(sids_this), len(synonyms_this_cid),
        min(len(synonyms_this_cid_nice), nmax_per_cid)))
    if nmax and i_cid>=(skip+nmax): break
  logging.info('Totals: CIDs: %d; SIDs: %d; Synonyms: %d'%(len(cids), len(sids_all), n_out))

#############################################################################
def GetName2SID(base_url, names, fout):
  n_sid=0; sids_all = set()
  if fout: fout.write("Name\tSID\n")
  for name in names:
    rval = rest_utils.GetURL(base_url+'/substance/name/%s/sids/JSON'%urllib.parse.quote(name), parse_json=True)
    sids_this = rval['IdentifierList']['SID']
    for sid in sids_this:
      n_sid+=1
      if fout: fout.write("%s\t%s\n"%(name, sid))
      sids_all |= set(sids_this)
  logging.info("n_name: %d; n_sid: %d; n_unique: %d"%(len(names), n_sid, len(sids_all)))
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
      if fout: fout.write("%s\t%s\n"%(name, cid))
    cids_all |= set(cids_this)
  logging.info("n_name: %d; n_cid: %d; n_unique: %d"%(len(names), n_cid, len(cids_all)))
  return list(cids_all)

#############################################################################
def GetName2Synonyms(base_url, names, fout):
  n_synonym=0; sids_all = set(); synonyms_all = set()
  if fout: fout.write("Name\tSID\tSynonym\n")
  for name in names:
    sids_this = GetName2SID(base_url, [name], None)
    sids_all |= set(sids_this)
    for sid in sids_this:
      rval = rest_utils.GetURL(base_url+'/substance/sid/%s/synonyms/JSON'%(sid), parse_json=True)
      infos = rval['InformationList']['Information'] if 'InformationList' in rval and 'Information' in rval['InformationList'] else []
      synonyms_this_sid = set()
      for info in infos:
        synonyms_this = info['Synonym'] if 'Synonym' in info else []
        synonyms_this_sid |= set(synonyms_this)
        for synonym in synonyms_this:
          n_synonym+=1
          if fout: fout.write("%s\t%s\t%s\n"%(name, sid, synonym))
      synonyms_all |= set(synonyms_this_sid)
  logging.info("n_name: %d; n_synonym: %d; n_unique: %d; n_sids_unique: %d"%(len(names), n_synonym, len(synonyms_all), len(sids_all)))

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
    fcsv=rest_utils.GetURL(base_url+'/compound/cid/%d/assaysummary/CSV'%cid)
  except Exception as e:
    logging.error('[%d] REST request failed; %s'%(cid, e))
    fout_mol.write("%s %d\n"%(smiles, cid))
    return mol_found,mol_active,n_sam,n_sam_active
  mol_found=True

  try:
    csvReader=csv.DictReader(fcsv.splitlines(),fieldnames=None,restkey=None,restval=None,dialect='excel',delimiter=',',quotechar='"')
    csvrow=csvReader.next()    ## must do this to get fieldnames
  except Exception as e:
    logging.error('[CID=%d] CSV problem:%s'%(cid,e))
    fout_mol.write("%s %d\n"%(smiles,cid))
    return mol_found,mol_active,n_sam,n_sam_active

  for field in ('AID','CID','SID','Bioactivity Outcome','Bioassay Type'):
    if field not in csvReader.fieldnames:
      logging.error('[CID=%d] bad CSV header, no "%s" field.'%(cid,field))
      logging.debug('DEBUG: fieldnames: %s'%(','.join(map((lambda
x:'"%s"'%x),csvReader.fieldnames))))
      fout_mol.write("%s %d\n"%(smiles,cid))
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
      logging.error('[CID=%d] bad CSV line; problem parsing: "%s"'%(cid,str(csvrow)))
      continue
    if cid!=csvrow_cid:
      logging.error('Aaack! [CID=%d] CID mismatch: != %d'%(cid,csvrow_cid))
      return mol_found,mol_active,n_sam,n_sam_active

    if aidset:
      if aid not in aidset:
        continue
      #logging.debug('DEBUG: AID [%d] ok (pre-selected).'%(aid))

    ## Assay filtering done; now update statistics (sTested, sActive).
    n_sam+=1
    aidhash[aid]=True
    act_outcome=csvrow['Bioactivity Outcome'].lower()
    if act_outcome in OUTCOME_CODES:
      fout_act.write("%d,%d,%d,%d\n"%(cid,sid,aid,OUTCOME_CODES[act_outcome]))
    else:
      logging.debug('[%d] unrecognized outcome (CID=%d,AID=%d): "%s"'%(n_in,cid,aid,act_outcome))

    aids_tested.add(aid)
    sids_tested.add(sid)
    if act_outcome=='active':
      n_sam_active+=1
      mol_active=True
      aids_active.add(aid)
      sids_active.add(sid)

  logging.debug('[CID=%d] CSV data lines: %d'%(cid,n_in))

  fout_mol.write("%s %d %d %d %d %d %d %d\n"%(
	smiles,
	cid,
	len(sids_tested),
	len(sids_active),
	len(aids_tested),
	len(aids_active),
	n_sam,
	n_sam_active))
  logging.debug((
	"cid=%d,sTested=%d,sActive=%d,aTested=%d,aActive=%d,wTested=%d,wActive=%d"%(
	cid,
	len(sids_tested),
	len(sids_active),
	len(aids_tested),
	len(aids_active),
	n_sam,
	n_sam_active)))

  return mol_found,mol_active,n_sam,n_sam_active

#############################################################################
def GetCpdAssayData(base_url, cid_query, aidset, fout):
  """This function needs fixing."""
  try:
    fcsv=rest_utils.GetURL(base_url+'/compound/cid/%d/assaysummary/CSV'%cid_query)
  except Exception as e:
    logging.error('[%d] REST request failed; %s'%(cid_query,e))
    return False

  if not fcsv:
    return False

  try:
    csvReader=csv.DictReader(fcsv.splitlines(),fieldnames=None,restkey=None,restval=None,dialect='excel',delimiter=',',quotechar='"')
    csvrow=csvReader.next()    ## must do this to get fieldnames
  except Exception as e:
    logging.error('[CID=%d] CSV problem: %s'%(cid_query,e))
    return True

  for field in ('CID','SID','AID','Bioactivity Outcome','Activity Value [uM]'):
    if field not in csvReader.fieldnames:
      logging.error('[CID=%d] bad CSV header, no "%s" field.'%(cid_query,field))
      logging.debug('fieldnames: %s'%(','.join(map((lambda x:'"%s"'%x),csvReader.fieldnames))))
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
      logging.error('[CID=%d] bad CSV line; problem parsing.'%cid)
      logging.debug('csvrow = %s'%str(csvrow))
      continue
    if cid_query!=cid:
      logging.error('Aaack! [CID=%d] CID mismatch: != %d'%(cid,int(csvrow['CID'])))
      return True
    if aid not in aidset:
      continue
      logging.debug('AID [%d] ok (pre-selected).'%(aid))

    if not csvrow['Activity Value [uM]']:
      continue

    try:
      actval=float(csvrow['Activity Value [uM]'])
    except:
      logging.error('[CID=%d] bad CSV line; problem parsing activity: "%s"'%(cid,csvrow['Activity Value [uM]']))
      continue

    n_act+=1
    outcome_code = OUTCOME_CODES[outcome.lower()] if outcome.lower() in OUTCOME_CODES else 0

    fout.write('%d,%d,%d,%d,%.3f\n'%(cid,sid,aid,outcome_code,actval))

  logging.info('[CID=%d] records: %2d ; activities: %2d'%(cid_query,n_in,n_act))
  return True

#############################################################################
