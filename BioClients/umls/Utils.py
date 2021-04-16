#!/usr/bin/env python3
"""
UMLS REST API client
UTS = UMLS Technology Services

https://documentation.uts.nlm.nih.gov/rest/home.html
https://documentation.uts.nlm.nih.gov/rest/authentication.html
https://documentation.uts.nlm.nih.gov/rest/concept/
https://documentation.uts.nlm.nih.gov/rest/source-asserted-identifiers/
https://documentation.uts.nlm.nih.gov/rest/search/
https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release/abbreviations.html

TGT = Ticket Granting Ticket
(API requires one ticket per request.)
CUI = Concept Unique Identifier
Atom is a term in a source.
Term-to-concept is many to one.

Retrieves information for a known Semantic Type identifier (TUI)
/semantic-network/{version}/TUI/{id}
(DOES NOT SEARCH FOR INSTANCES OF THIS TYPE -- RETURNS METADATA ONLY.)
Example TUIs:
CHEM|Chemicals & Drugs|T116|Amino Acid, Peptide, or Protein
CHEM|Chemicals & Drugs|T195|Antibiotic
CHEM|Chemicals & Drugs|T123|Biologically Active Substance
CHEM|Chemicals & Drugs|T122|Biomedical or Dental Material
CHEM|Chemicals & Drugs|T103|Chemical
CHEM|Chemicals & Drugs|T120|Chemical Viewed Functionally
CHEM|Chemicals & Drugs|T104|Chemical Viewed Structurally
CHEM|Chemicals & Drugs|T200|Clinical Drug
CHEM|Chemicals & Drugs|T126|Enzyme
CHEM|Chemicals & Drugs|T125|Hormone
CHEM|Chemicals & Drugs|T129|Immunologic Factor
CHEM|Chemicals & Drugs|T130|Indicator, Reagent, or Diagnostic Aid
CHEM|Chemicals & Drugs|T114|Nucleic Acid, Nucleoside, or Nucleotide
CHEM|Chemicals & Drugs|T109|Organic Chemical
CHEM|Chemicals & Drugs|T121|Pharmacologic Substance
CHEM|Chemicals & Drugs|T192|Receptor
CHEM|Chemicals & Drugs|T127|Vitamin
DISO|Disorders|T020|Acquired Abnormality
DISO|Disorders|T190|Anatomical Abnormality
DISO|Disorders|T049|Cell or Molecular Dysfunction
DISO|Disorders|T019|Congenital Abnormality
DISO|Disorders|T047|Disease or Syndrome
DISO|Disorders|T050|Experimental Model of Disease
DISO|Disorders|T033|Finding
DISO|Disorders|T037|Injury or Poisoning
DISO|Disorders|T048|Mental or Behavioral Dysfunction
DISO|Disorders|T191|Neoplastic Process
DISO|Disorders|T046|Pathologic Function
DISO|Disorders|T184|Sign or Symptom
GENE|Genes & Molecular Sequences|T087|Amino Acid Sequence
GENE|Genes & Molecular Sequences|T088|Carbohydrate Sequence
GENE|Genes & Molecular Sequences|T028|Gene or Genome
GENE|Genes & Molecular Sequences|T085|Molecular Sequence
GENE|Genes & Molecular Sequences|T086|Nucleotide Sequence

https://github.com/HHS/uts-rest-api
https://utslogin.nlm.nih.gov

https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release/abbreviations.html
Some term types:

 CE : Entry term for a Supplementary Concept
 ET : Entry term
 FN : Full form of descriptor
 HG : High Level Group Term
 HT : Hierarchical term
 LLT : Lower Level Term
 MH : Main heading
 MTH_FN : MTH Full form of descriptor
 MTH_HG : MTH High Level Group Term
 MTH_HT : MTH Hierarchical term
 MTH_LLT : MTH Lower Level Term
 MTH_OS : MTH System-organ class
 MTH_PT : Metathesaurus preferred term
 MTH_SY : MTH Designated synonym
 NM : Name of Supplementary Concept
 OS : System-organ class
 PCE : Preferred entry term for Supplementary Concept
 PEP : Preferred entry term
 PM : Machine permutation
 PT : Designated preferred name
 PTGB : British preferred term
 SY : Designated synonym
 SYGB : British synonym
 
Some relationships:

 RB : has a broader relationship
 RL : the relationship is similar or "alike". 
 RN : has a narrower relationship
 RO : has relationship other than synonymous, narrower, or broader
 RQ : related and possibly synonymous.
 RU : Related, unspecified
 SY : source asserted synonymy.
"""
###
import sys,os,re,yaml,json,urllib.parse,csv,logging,requests,time
import pandas as pd
from functools import total_ordering
#
from lxml import etree
from pyquery import PyQuery
#
from ..util import rest
#
###
API_HOST='uts-ws.nlm.nih.gov'
API_BASE_PATH="/rest"
API_BASE_URL=f"https://{API_HOST}{API_BASE_PATH}"
API_AUTH_SERVICE="http://umlsks.nlm.nih.gov"
API_AUTH_HOST="utslogin.nlm.nih.gov"
API_AUTH_ENDPOINT='/cas/v1/api-key'
API_VERSION="current"
API_HEADERS={"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "User-Agent":"python" }
#
## elements common to 'Concept' and 'SourceAtomCluster' class
UMLS_COMMON_FIELDS=['classType','name','ui','atomCount','definitions','atoms','defaultPreferredAtom']
UMLS_OPTIONAL_FIELDS=['parents','children','relations','descendants']
#
#############################################################################
@total_ordering
class Atom:
  def __init__(self, cui, src, code, name):
    self.cui = cui
    self.src = src
    self.code = code
    self.name = name

  def __eq__(self, other):
    return ((self.cui, self.src, self.code) == (other.cui, other.src, other.code))

  def __ne__(self, other):
    return not (self == other)

  def __lt__(self, other):
    return ((self.cui, self.src, self.code) < (other.cui, other.src, other.code))
  def __hash__(self):
    return id(self)

#############################################################################
class SourceList:
  def __init__(self):
    self.sources=[];

  def initFromFile(self, sfile):
    fin = open(sfile)
    if not fin:
      logging.error(f'Could not open {sfile}')
      return
    csvReader = csv.reader(fin, delimiter='\t', quotechar='"')
    row = csvReader.next() #ignore header
    while True:
      try:
        row = csvReader.next()
      except:
        break
      self.sources.append(tuple(row))
    self.sources.sort()
    fin.close()

  def initFromApi(self, base_url, ver, auth):
    url = (f'{base_url}/metadata/{ver}/sources')
    tgt = auth.gettgt()
    response = UmlsApiGet(url, auth, tgt)
    response.encoding = 'utf-8'
    items = json.loads(response.text)
    logging.debug(json.dumps(items, indent=4))
    sources = items["result"]
    tags = ["abbreviation", "shortName", "preferredName"]
    for source in sources:
      row=[]
      for tag in tags:
        row.append(source[tag] if tag in source else '')
      self.sources.append(tuple(row))
    self.sources.sort()

  def has_src(self,_src):
    for abbr,name,ver in self.sources:
      if _src == abbr:
        return True
    return False

#############################################################################
class Authentication:
  def __init__(self, apikey, service, url, headers):
    self.apikey=apikey
    self.service=service
    self.url=url
    self.headers=headers
    self.verbosity=0

  def gettgt(self):
    response = requests.post(self.url, data={'apikey':self.apikey}, headers=self.headers)
    logging.debug(f'response = {response}')
    d = PyQuery(response.text)

    if response.status_code not in (200, 201):
      logging.error(f'HTTP RESPONSE CODE: {response.status_code} ({d})')
      return None
      
    ## Extract the entire URL needed (action attribute),
    ## to make a POST call to this URL in the getst method.
    tgt = d.find('form').attr('action')
    logging.debug(f'tgt = {tgt}')
    return tgt

  def getst(self, tgt):
    r = requests.post(tgt, data={'service':self.service}, headers=self.headers)
    st = r.text
    return st

  def setVerbosity(self, v):
    self.verbosity=v

#############################################################################
def UmlsAuthGetTicket(auth, tgt, tries=10, sleep=1):
  for i in range(1, tries+1):
    try:
      tkt = auth.getst(tgt)
      return tkt
    except Exception as e:
      logging.error(f'{i}. {e}')
      time.sleep(sleep)
      continue
  return None

#############################################################################
def UmlsApiGet(url, auth, tgt, params={}, tries=10, sleep=1):
  for i in range(1,tries+1):
    try:
      params['ticket'] = UmlsAuthGetTicket(auth, tgt)
      response = requests.get(url, params=params)
      return response
    except Exception as e:
      logging.error(f'{i}. {e}')
      time.sleep(sleep)
      continue
  return None

#############################################################################
def ReadParamFile(fparam):
  params={};
  with open(fparam, 'r') as fh:
    for param in yaml.load_all(fh, Loader=yaml.BaseLoader):
      for k,v in param.items():
        params[k] = v
  return params

#############################################################################
def XrefConcept(src, ids, skip, nmax, auth, ver=API_VERSION, base_url=API_BASE_URL, fout=None):
  """Find UMLS concept/CUI from external source cross-reference."""
  n_in=0; n_concept=0; n_out=0;
  result_tags=None;
  tgt = auth.gettgt()
  for id_query in ids:
    n_in+=1
    if nmax and n_in>nmax: break
    if skip and n_in<=skip:
      logging.debug(f'[{id_query}] skipping...')
      continue
    url = (f"{base_url}/content/{ver}/source/{src}/{id_query}" if src else f"/CUI/{id_query}")
    logging.debug(f'{n_in}. url="{url}"')
    response = UmlsApiGet(url, auth, tgt)
    response.encoding = 'utf-8'
    try:
      items = json.loads(response.text)
    except Exception as e:
      logging.info(f'{n_in}. [{id_query}] {e}')
      logging.debug(f'response.text="{response.text}"')
      continue
    logging.debug(json.dumps(items, indent=4))
    result = items["result"]
    for key in UMLS_COMMON_FIELDS+UMLS_OPTIONAL_FIELDS:
      logging.info(f"""{key:14s}: {(result[key] if key in result else '')}""") 
    if 'semanticTypes' in result:
      for i,styp in enumerate(result["semanticTypes"]):
        for key in styp.keys():
          logging.info(f'Semantic type {i+1}. {key}: {styp[key]}')
    if n_out==0 or not result_tags:
      result_tags = result.keys()
      id_tag = (f'{src}_id' if src else 'CUI')
      fout.write('\t'.join([id_tag]+result_tags)+'\n')
    vals = [id_query]
    for tag in result_tags:
      val = (result[tag] if tag in result else '')
      if tag == 'concepts':
        url2 = result['concepts']
        response2 = UmlsApiGet(url2, auth, tgt)
        response2.encoding = 'utf-8'
        items2  = json.loads(response2.text)
        logging.debug(json.dumps(items2, indent=4))
        result2 = items2['result']
        concepts = result2['results'] if 'results' in result2 else []
        cuis=[]
        for concept in concepts:
          cui = concept['ui'] if 'ui' in concept else None
          if cui: n_concept+=1
          cuis.append(cui)
        val=';'.join(cuis)
      elif tag=='semanticTypes':
        if type(val) is list:
          sts=[]
          for st in val:
            if type(st) is dict and 'name' in st: sts.append(st['name'])
          val = ';'.join(sts)
      elif tag in ('relations', 'parents', 'children','descendants','ancestors',
	'attributes', 'contentViewMemberships', 'atoms', 'defaultPreferredAtom',
	'definitions'):
        if val != 'NONE': val = ''
      else:
        if type(val) is str:
          val = val.replace(base_url, '')
      vals.append(str(val))
    fout.write('\t'.join(vals)+'\n')
    n_out+=1
  logging.info(f'n_concept: {n_concept}')
  logging.info(f'n_out: {n_out}')

#############################################################################
def GetCodes(cuis, srcs, auth, ver=API_VERSION, base_url=API_BASE_URL, fout=None):
  n_out=0; df=None;
  for cui in cuis:
    codes = Cui2Code(cui, srcs, auth, ver, base_url)
    for src in sorted(codes.keys()):
      atoms = sorted(list(codes[src]))
      for atom in atoms:
        df_this = pd.DataFrame({'CUI':[cui], 'src':[src], 'atom_code':atom.code, 'atom_name':atom.name})
        if fout is None: df = pd.concat([df, df_this])
        else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
        n_out+=1
  logging.info(f'n_cui: {len(cuis)}')
  logging.info(f'n_out: {n_out}')
  if fout is None: return df

#############################################################################
def Cui2Code(cui, srcs, auth, ver=API_VERSION, base_url=API_BASE_URL):
  n_atom=0; pNum=1; params={}; codes={};
  if srcs: params['sabs']=srcs
  url = (f'{base_url}/content/{ver}/CUI/{cui}/atoms')
  tgt = auth.gettgt()
  while True:
    params['pageNumber'] = pNum
    response = UmlsApiGet(url, auth, tgt, params=params)
    response.encoding = 'utf-8'
    try:
      items = json.loads(response.text)
    except Exception as e:
      logging.error(str(e))
      break
    logging.debug (json.dumps(items, indent=4))
    atoms = items["result"] if "result" in items else []
    for atom in atoms:
      n_atom+=1
      src = atom['rootSource'] if 'rootSource' in atom else None
      code = atom['code'] if 'code' in atom else None
      if code: code = re.sub(r'^.*/', '', code)
      name = atom['name'] if 'name' in atom else None
      cui = atom['concept'] if 'concept' in atom else None
      if cui: cui = re.sub(r'^.*/', '', cui)
      a = Atom(cui, src, code, name)
      if not src in codes: codes[src] = set()
      codes[src].add(a)
    pageSize = items["pageSize"] if "pageSize" in items else None
    pageNumber = items["pageNumber"] if "pageNumber" in items else None
    pageCount = items["pageCount"] if "pageCount" in items else None
    if pageNumber!=pNum:
      logging.error(f'pageNumber!=pNum ({pageNumber}!={pNum})')
      break
    elif pNum==pageCount:
      logging.debug(f'(done) pageNumber==pageCount ({pageNumber})')
      break
    else:
      pNum+=1
  return codes

#############################################################################
def GetAtoms(cuis, skip, nmax, srcs, auth, ver=API_VERSION, base_url=API_BASE_URL, fout=None):
  '''Expected fields: sourceDescriptor,suppressible,code,name,language,descendants,classType,sourceConcept,obsolete,relations,parents,children,concept,ui,rootSource,definitions,attributes,ancestors,termType'''
  n_in=0; n_atom=0; n_out=0; df=None; tags=None;
  tgt = auth.gettgt()
  for cui in cuis:
    n_in+=1
    if skip and n_in<=skip:
      logging.debug(f'[{cui}] skipping...')
      continue
    pNum=1;
    url = (f'{base_url}/content/{ver}/CUI/{cui}/atoms')
    params={}
    if srcs: params['sabs']=srcs
    while True:
      params['pageNumber']=pNum
      response = UmlsApiGet(url, auth, tgt, params=params)
      if not response:
        break
      if response.status_code != 200:
        logging.error(f'response.status_code = "{response.status_code}"')
        break
      response.encoding = 'utf-8'
      logging.debug(f'params = {str(params)}')
      logging.debug(response.text)
      items = json.loads(response.text)
      logging.debug(json.dumps(items, indent=4))
      result = items["result"]
      for atom in result:
        n_atom+=1
        if not tags: tags = list(atom.keys())
        for tag in ('relations', 'parents', 'children','descendants','ancestors', 'attributes', 'contentViewMemberships'):
            if tag in atom and atom[tag]!='NONE': atom[tag] = '*'
        df_this = pd.DataFrame({tag:[atom[tag] if tag in atom else ''] for tag in tags})
        if fout is None: df = pd.concat([df, df_this])
        else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
        n_out+=1
      pageSize = items["pageSize"]
      pageNumber = items["pageNumber"]
      pageCount = items["pageCount"]
      if pageNumber!=pNum:
        logging.error(f'pageNumber!=pNum ({pageNumber}!={pNum})')
        break
      elif pNum==pageCount:
        logging.debug(f'(done) pageNumber==pageCount ({pageNumber})')
        break
      else:
        pNum+=1
    if nmax and n_in==nmax: break
  logging.info(f'n_atom: {n_atom}')
  logging.info(f'n_out: {n_out}')
  if fout is None: return df

#############################################################################
def GetRelations(cuis, skip, nmax, srcs, auth, ver=API_VERSION, base_url=API_BASE_URL, fout=None):
  n_in=0; n_rel=0; n_out=0; tags=None; df=None;
  tgt = auth.gettgt()
  for cui in cuis:
    n_in+=1
    if skip and n_in<=skip:
      logging.debug(f'[{cui}] skipping...')
      continue
    pNum=1;
    url = (f'{base_url}/content/{ver}/CUI/{cui}/relations')
    params={}
    if srcs: params['sabs']=srcs
    while True:
      params['pageNumber']=pNum
      response = UmlsApiGet(url, auth, tgt, params=params)
      if not response:
        break
      if response.status_code != 200:
        logging.error(f'response.status_code = "{response.status_code}"')
        break
      response.encoding = 'utf-8'
      logging.debug(f'params = {str(params)}')
      logging.debug(f'{response.text}')
      items = json.loads(response.text)
      logging.debug(json.dumps(items, indent=4))
      result = items["result"]
      for rel in result:
        n_rel+=1
        if not tags: tags = list(rel.keys())
        df_this = pd.DataFrame({tag:[rel[tag] if tag in rel else ''] for tag in tags})
        df_this["cui"] = [cui]
        if fout is None: df = pd.concat([df, df_this])
        else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
        n_out+=1
      pageSize = items["pageSize"]
      pageNumber = items["pageNumber"]
      pageCount = items["pageCount"]
      if pageNumber!=pNum:
        logging.error(f': pageNumber!=pNum ({pageNumber}!={pNum})')
        break
      elif pNum==pageCount:
        break
      else:
        pNum+=1
    if nmax and n_in==nmax: break
  logging.info(f'n_rel: {n_rel}')
  logging.info(f'n_out: {n_out}')
  if fout is None: return df

#############################################################################
def Search(query, searchType, inputType, returnIdType, srcs, auth, ver=API_VERSION, base_url=API_BASE_URL, fout=None):
  """Retrieves CUIs for a search term.
Expected fields: ui, rootSource, name, uri.
See https://documentation.uts.nlm.nih.gov/rest/search/
"""
  src_counts={}; n_item=0; n_out=0; pNum=1; tags=None; df=None;
  url = (f'{base_url}/search/{ver}')
  params = {'string':query, 'searchType':searchType, 'inputType':inputType, 'returnIdType':returnIdType}
  if srcs: params['sabs'] = srcs
  tgt = auth.gettgt()
  while True:
    params['pageNumber']=pNum
    logging.debug(f'params = {str(params)}')
    response = UmlsApiGet(url, auth, tgt, params=params)
    response.encoding = 'utf-8'
    items = json.loads(response.text)
    logging.debug (json.dumps(items, indent=4))
    result = items['result']
    classType = result['classType']
    pageSize = items["pageSize"]
    pageNumber = items["pageNumber"]
    ##No pageCount in search response.
    items = result['results']
    if not items:
      break
    elif len(items)==1 and items[0]['name']=='NO RESULTS':
      break
    elif pageNumber!=pNum:
      logging.debug(f'pageNumber!=pNum ({pageNumber}!={pNum})')
      break
    for item in items:
      n_item+=1
      if not tags: tags = list(item.keys())
      vals = []
      cui = item['ui'] if 'ui' in item else None
      if 'rootSource' in item:
        if not item['rootSource'] in src_counts:
          src_counts[item['rootSource']]=0
        src_counts[item['rootSource']]+=1
      df_this = pd.DataFrame({tag:[item[tag] if tag in item else ''] for tag in tags})
      if fout is None: df = pd.concat([df, df_this])
      else: df_this.to_csv(fout, "\t", index=False, header=bool(n_out==0))
      n_out+=1
    pNum+=1
  logging.info(f'n_item: {n_item}')
  logging.info(f'n_out: {n_out}')
  for src in sorted(src_counts.keys()):
    logging.info(f'{src:16s}: {src_counts[src]:3d} items')
  if fout is None: return df

#############################################################################
