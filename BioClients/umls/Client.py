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
  SRCS_PREFERRED = "ATC,HPO,ICD10,ICD10CM,ICD9CM,MDR,MSH,MTH,NCI,OMIM,RXNORM,SNOMEDCT_US,WHO"
  EPILOG = f"""\
All get* operations require --idsrc CUI, CUIs as inputs; CUI = Concept Unique Identifier.
Example CUIs: C34488, C0018787, C0016644
"""
  parser = argparse.ArgumentParser(description='UMLS REST API client utility', epilog=EPILOG)
  ops = ['getCodes', 'getAtoms', 'getRelations', 'listSources', 'xrefConcept', 'search', 'searchByTUI']
  searchTypes = ['exact', 'words', 'leftTruncation', 'rightTruncation', 'approximate', 'normalizedString']
  inputTypes = ['atom', 'code', 'sourceConcept', 'sourceDescriptor', 'sourceUi', 'tty']
  returnIdTypes = ['aui', 'concept', 'code', 'sourceConcept', 'sourceDescriptor', 'sourceUi']
  parser.add_argument("op", choices=ops, help='OPERATION (select one)')
  parser.add_argument("--ids", help="IDs (comma-separated) (ex:C0018787)")
  parser.add_argument("--idfile", help="input IDs")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--idsrc", default="CUI", help="query ID source (default: CUI)")
  parser.add_argument("--searchType", choices=searchTypes, default='words', help=f" [words]")
  parser.add_argument("--inputType", choices=inputTypes, default='atom', help=f" [atom]")
  parser.add_argument("--returnIdType", choices=returnIdTypes, default='concept', help=f" [concept]")
  parser.add_argument("--srcs", default=SRCS_PREFERRED, help=f"sources to include in response [{SRCS_PREFERRED}]")
  parser.add_argument("--searchQuery", help='string or code')
  parser.add_argument("--skip", default=0, type=int)
  parser.add_argument("--nmax", default=0, type=int)
  parser.add_argument("--api_version", default=f"{umls.API_VERSION}", help=f"API version {umls.API_VERSION}")
  parser.add_argument("--api_host", default=umls.API_HOST)
  parser.add_argument("--api_base_path", default=umls.API_BASE_PATH)
  parser.add_argument("--api_auth_host", default=umls.API_AUTH_HOST)
  parser.add_argument("--api_auth_endpoint", default=umls.API_AUTH_ENDPOINT)
  parser.add_argument("--api_auth_service", default=umls.API_AUTH_SERVICE)
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
  auth = umls.Authentication(params['API_KEY'],
args.api_auth_service, api_auth_url, umls.API_HEADERS)
  auth.setVerbosity(args.verbose)

  ids=[];
  if args.idfile:
    fin = open(args.idfile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    fin.close()
  elif args.ids:
    ids = re.split(r'[,\s]', args.ids)
  if ids: logging.info(f'input IDs: {len(ids)}')

  t0 = time.time()

  srclist = umls.SourceList()
  srclist.initFromApi(base_url, args.api_version, auth)

  if args.srcs:
    for src in re.split(r'[,\s]+', args.srcs.strip()):
      if not srclist.has_src(src):
          parser.error(f'Source unknown: "{src}"')

  if args.op == 'listSources':
    fout.write("abbreviation\tshortName\tpreferredName\n")
    for i,src in enumerate(srclist.sources):
      abbr,name,prefname = src
      fout.write(f'{abbr}\t{name}\t{prefname}\n')
    logging.info(f'n_src: {len(srclist.sources)}')

  elif args.op == 'xrefConcept':
    umls.XrefConcept(args.idsrc, ids, args.skip, args.nmax, auth, args.api_version, base_url, fout)

  elif args.op == 'getRelations':
    umls.GetRelations(ids, args.skip, args.nmax, args.srcs, auth, args.api_version, base_url, fout)

  elif args.op == 'getAtoms':
    umls.GetAtoms(ids, args.skip, args.nmax, args.srcs, auth, args.api_version, base_url, fout)

  elif args.op == 'getCodes':
    umls.GetCodes(ids, args.srcs, auth, args.api_version, base_url, fout)

  elif args.op == 'search':
    if not args.searchQuery:
      parser.error('search requires --searchQuery')
    umls.Search(args.searchQuery, args.searchType, args.inputType, args.returnIdType, args.srcs, auth, args.api_version, base_url, fout)

  elif args.op == 'searchByTUI':
    parser.error(f'{args.op} NOT IMPLEMENTED YET.')

  else:
    parser.error(f'Invalid operation: {args.op}')

  logging.info(f"""Elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}""")
