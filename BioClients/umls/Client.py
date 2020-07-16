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
  SRCS_PREFERRED= "ATC,HPO,ICD10,ICD10CM,ICD9CM,MDR,MSH,MTH,NCI,OMIM,RXNORM,SNOMEDCT_US,WHO"
  EPILOG="""\
All get* operations require --idsrc CUI, CUIs as inputs.
CUI = Concept Unique Identifier;
Preferred/default sources: {srcs_preferred}
""".format(srcs_preferred=SRCS_PREFERRED)
  parser = argparse.ArgumentParser(description='UMLS REST API client utility', epilog=EPILOG)
  ops = ['getCodes', 'getAtoms', 'getRelations', 'listSources', 'xrefConcept', 'search', 'searchByTUI']
  searchTypes = ['exact', 'words', 'leftTruncation', 'rightTruncation', 'approximate',
	'normalizedString']
  inputTypes = ['atom', 'code', 'sourceConcept', 'sourceDescriptor', 'sourceUi', 'tty']
  returnIdTypes = ['aui', 'concept', 'code', 'sourceConcept', 'sourceDescriptor', 'sourceUi']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--id", help="ID (ex:C0018787)")
  parser.add_argument("--idfile", help="input IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--idsrc", default="CUI", help="query ID source (default: CUI)")
  parser.add_argument("--searchType", choices=searchTypes, default='words')
  parser.add_argument("--inputType", choices=inputTypes, default='atom')
  parser.add_argument("--returnIdType", choices=returnIdTypes, default='concept')
  parser.add_argument("--srcs", default=SRCS_PREFERRED, help='sources to include in response')
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

  if args.op[:3] == 'get' and args.idsrc!='CUI':
    parser.error('Operation "{}" requires --idsrc CUI.'.format(args.op))

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='https://'+args.api_host+args.api_base_path

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  params = umls.ReadParamFile(args.param_file)
  if args.api_key: params['API_KEY'] = args.api_key
  if not params['API_KEY']:
    parser.error('Please specify valid API_KEY via --api_key or --param_file') 

  api_auth_url = 'https://'+args.api_auth_host+args.api_auth_endpoint
  auth = umls.Utils.Authentication(params['API_KEY'], args.api_auth_service, api_auth_url, API_HEADERS)
  auth.setVerbosity(args.verbose)

  ids=[];
  if args.idfile:
    fin = open(args.idfile)
    while True:
      line=fin.readline()
      if not line: break
      ids.append(line.rstrip())
    logging.info('input IDs: %d'%(len(ids)))
    fin.close()
  elif args.id:
    ids.append(args.id)

  t0 = time.time()

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

  elif args.op == 'xrefConcept':
    umls.Utils.XrefConcept(base_url, args.version, args.idsrc, auth, ids, args.skip, args.nmax, fout)

  elif args.op == 'getRelations':
    umls.Utils.GetRelations(base_url, args.version, auth, ids, args.skip, args.nmax, args.srcs, fout)

  elif args.op == 'getAtoms':
    umls.Utils.GetAtoms(base_url, args.version, auth, ids, args.skip, args.nmax, args.srcs, fout)

  elif args.op == 'getCodes':
    umls.Utils.GetCodes(base_url, args.version, auth, ids, args.srcs, fout)

  elif args.op == 'search':
    if not args.searchQuery:
      parser.error('search requires --searchQuery')
    umls.Utils.Search(base_url, args.version, auth, args.searchQuery, args.searchType, args.inputType, args.returnIdType, args.srcs, fout)

  elif args.op == 'searchByTUI':
    parser.error('{} NOT IMPLEMENTED YET.'.format(args.op))

  else:
    parser.error('Invalid operation: %s'%args.op)

  logging.info(('Elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))
