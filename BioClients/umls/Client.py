#!/usr/bin/env python3
"""
UMLS REST API client
UTS = UMLS Technology Services

 https://utslogin.nlm.nih.gov
 https://github.com/HHS/uts-rest-api
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
 CHEM|Chemicals & Drugs|T103|Chemical
 CHEM|Chemicals & Drugs|T200|Clinical Drug
 CHEM|Chemicals & Drugs|T126|Enzyme
 CHEM|Chemicals & Drugs|T125|Hormone
 CHEM|Chemicals & Drugs|T129|Immunologic Factor
 CHEM|Chemicals & Drugs|T127|Vitamin
 DISO|Disorders|T020|Acquired Abnormality
 DISO|Disorders|T190|Anatomical Abnormality
 DISO|Disorders|T049|Cell or Molecular Dysfunction
 DISO|Disorders|T047|Disease or Syndrome
 DISO|Disorders|T048|Mental or Behavioral Dysfunction
 DISO|Disorders|T046|Pathologic Function
 DISO|Disorders|T184|Sign or Symptom
 GENE|Genes & Molecular Sequences|T087|Amino Acid Sequence
 GENE|Genes & Molecular Sequences|T088|Carbohydrate Sequence
 GENE|Genes & Molecular Sequences|T028|Gene or Genome
 GENE|Genes & Molecular Sequences|T085|Molecular Sequence
 GENE|Genes & Molecular Sequences|T086|Nucleotide Sequence
"""
###
import sys,os,argparse,re,yaml,json,csv,logging,requests,time
#
from .. import umls
#
#############################################################################
if __name__=='__main__':
  API_HOST='uts-ws.nlm.nih.gov'
  API_BASE_PATH="/rest"
  API_AUTH_SERVICE="http://umlsks.nlm.nih.gov"
  API_AUTH_HOST="utslogin.nlm.nih.gov"
  API_AUTH_ENDPOINT='/cas/v1/api-key'
  API_HEADERS={"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "User-Agent":"python" }
  SRCS_FILE='/home/data/UMLS/data/umls_sources.csv'

  parser = argparse.ArgumentParser(description='UMLS REST API client utility', epilog='CUI = Concept Unique Identifier')
  ops = ['getConcept', 'getAtoms', 'getRelations', 'search', 'searchByTUI', 
	'listSources',  'cui2Code']
  searchTypes = ['exact', 'words', 'leftTruncation', 'rightTruncation', 'approximate',
	'normalizedString']
  inputTypes = ['atom', 'code', 'sourceConcept', 'sourceDescriptor', 'sourceUi', 'tty']
  returnIdTypes = ['aui', 'concept', 'code', 'sourceConcept', 'sourceDescriptor', 'sourceUi']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--id", help="ID (ex:C0018787)")
  parser.add_argument("--idfile", help="input IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--idsrc", help="query ID source (default: CUI)")
  parser.add_argument("--searchType", choices=searchTypes, default='words')
  parser.add_argument("--inputType", choices=inputTypes, default='atom')
  parser.add_argument("--returnIdType", choices=returnIdTypes, default='concept')
  parser.add_argument("--srcs", help='list of sources to include in response')
  #parser.add_argument("--umls_srcs_file", help="list of all UMLS sources")
  parser.add_argument("--searchQuery", help='string or code')
  parser.add_argument("--skip", default=0, type=int)
  parser.add_argument("--nmax", default=0, type=int)
  parser.add_argument("--version", default="current", help="API version")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("--api_auth_host", default=API_AUTH_HOST)
  parser.add_argument("--api_auth_endpoint", default=API_AUTH_ENDPOINT)
  parser.add_argument("--api_auth_service", default=API_AUTH_SERVICE)
  parser.add_argument("--param_file", default=os.environ['HOME']+"/.umls.yaml")
  parser.add_argument("--api_key", help="API key")
  parser.add_argument("-v", "--verbose", default=0, action="count")

  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='https://'+args.api_host+args.api_base_path

  if args.ofile:
    fout = open(args.ofile, "w+")
    if not fout: parser.error('Cannot open: %s'%args.ofile)
  else:
    fout = sys.stdout

  params={};
  if os.path.exists(args.param_file):
    with open(args.param_file, 'r') as fh:
      for param in yaml.load_all(fh, Loader=yaml.BaseLoader):
        for k,v in param.items():
          params[k] = v
  api_key = args.api_key if args.api_key else params['API_KEY'] if 'API_KEY' in params else ''
  if not api_key:
    parser.error('Please specify valid API_KEY via --api_key or --param_file') 

  api_auth_url = 'https://'+args.api_auth_host+args.api_auth_endpoint
  auth = umls.Utils.Authentication(api_key, args.api_auth_service, api_auth_url, API_HEADERS)
  auth.setVerbosity(args.verbose)

  ids=[];
  if args.idfile:
    fin = open(args.idfile)
    if not fin:
      parser.error('Cannot open: %s'%args.idfile)
    while True:
      line=fin.readline()
      if not line: break
      ids.append(line.rstrip())
    logging.info('input IDs: %d'%(len(ids)))
    fin.close()
  elif args.id:
    ids.append(args.id)

  srclist = umls.Utils.SourceList()
  srclist.initFromApi(base_url, args.version, auth)

  if args.srcs:
    for src in re.split(r'[,\s]+', args.srcs.strip()):
      if not srclist.has_src(src):
          parser.error('Source unknown: "%s"'%src)

  if args.op == 'listSources':
    fout.write("abbreviation\tshortName\tpreferredName\n")
    for i,src in enumerate(srclist.sources):
      abbr,name,prefname = src
      fout.write('%s\t%s\t%s\n'%(abbr, name, prefname))
    logging.info('n_src: %d'%len(srclist.sources))

  elif args.op == 'getConcept':
    umls.Utils.GetConcept(base_url, args.version, args.idsrc, auth, ids, args.skip, args.nmax, fout)

  elif args.op == 'getRelations':
    if args.idsrc and args.idsrc!='CUI':
      parser.error('getRelations requires --idsrc CUI.')
    umls.Utils.GetRelations(base_url, args.version, auth, ids, args.skip, args.nmax, args.srcs, fout)

  elif args.op == 'getAtoms':
    if args.idsrc and args.idsrc!='CUI':
      parser.error('getAtoms requires --idsrc CUI.')
    umls.Utils.GetAtoms(base_url, args.version, auth, ids, args.skip, args.nmax, args.srcs, fout)

  elif args.op == 'cui2Code':
    if args.idsrc and args.idsrc!='CUI':
      parser.error('cui2Code requires --idsrc CUI.')
    i_cui=0; n_code=0;
    for cui in ids:
      i_cui+=1
      fout.write('%d.\t%s:'%(i_cui,cui))
      codes = umls.Utils.Cui2Code(base_url, args.version, auth, cui, args.srcs, fout)
      n_code_this=0;
      for src in sorted(codes.keys()):
        for i,atom in enumerate(sorted(list(codes[src]))):
          fout.write('%s:\t%d.\t%s\t%s'%(src, i+1, atom.code, atom.name))
          n_code_this+=1
      n_code+=n_code_this
    logging.info('n_cui: %d'%i_cui)
    logging.info('n_code: %d'%n_code)

  elif args.op == 'search':
    if not args.searchQuery:
      parser.error('search requires --searchQuery')
    umls.Utils.Search(base_url, args.version, auth, args.searchQuery, args.searchType, args.inputType, args.returnIdType, args.srcs, fout)

  elif args.op == 'searchByTUI':
    parser.error('ERROR: searchByTUI NOT IMPLEMENTED YET.')

  else:
    parser.error('Invalid operation: %s'%args.op)

