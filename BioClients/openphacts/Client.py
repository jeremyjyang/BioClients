#!/usr/bin/env python3
##############################################################################
### OpenPHACTS REST API Client
### https://dev.openphacts.org/docs
### https://dev.openphacts.org/docs/1.5
### https://dev.openphacts.org/docs/2.0
##############################################################################
### From https://dev.openphacts.org/docs/develop
#  ?oidd_assay_uri a ?bao_type ;
#     skos:exactMatch ?pubchem_assay ;
#     void:inDataset <http://rdf.ncats.nih.gov/opddr> .
###
#  /assay?uri=http%3A%2F%2Fopeninnovation.lilly.com%2Fbioassay%2329"
###
##############################################################################
import sys,os,re,time,argparse,logging
#
from .. import openphacts
#
from ..util import yaml as util_yaml
#
#
##############################################################################
if __name__=='__main__':
  epilog='''\
Examples:
http://openinnovation.lilly.com/bioassay#29 (assay)
http://www.conceptwiki.org/concept/38932552-111f-4a4e-a46a-4ed1d7bdf9d5 (compound)
http://www.conceptwiki.org/concept/00059958-a045-4581-9dc5-e5a08bb0c291 (target)
'''
  parser = argparse.ArgumentParser(description='ClinicalTrials.gov API client', epilog=epilog)
  ops = [ "counts", "get_assay", "get_cpd", "get_target", "list_pathways", "list_sources", "list_tgt_types", "list_targets", ]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--qry_uri", help="query URI")
  parser.add_argument("--qry_txt", help="query text")
  parser.add_argument("--o", dest="ofile", help="Output (TSV)")
  parser.add_argument("--api_host", default=openphacts.API_HOST)
  parser.add_argument("--api_base_path", default=openphacts.API_BASE_PATH)
  parser.add_argument("--api_user_id")
  parser.add_argument("--api_user_key")
  parser.add_argument("--param_file", default=os.environ['HOME']+"/.openphacts.yaml")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  params = util_yaml.ReadParamFile(args.param_file) if os.path.isfile(args.param_file) else {}
  api_user_id = args.api_user_id if args.api_user_id else params['ID'] if 'ID' in params else None
  api_user_key = args.api_user_key if args.api_user_key else params['KEY'] if 'KEY' in params else None

  base_url = 'https://'+args.api_host+args.api_base_path

  fout = open(ofile, "w+") if args.ofile else sys.stdout

  if args.op == "list_pathways":
    openphacts.ListPathways(api_user_id, api_user_key, base_url, fout)

  elif args.op == "list_sources":
    openphacts.ListSources(api_user_id, api_user_key, base_url, fout)

  elif args.op == "list_tgt_types":
    openphacts.ListTargetTypes(api_user_id, api_user_key, base_url, fout)

  elif args.op == "list_targets":
    if not qry_uri: parser.error('Query URI required.')
    openphacts.ListTargets(qry_uri, api_user_id, api_user_key, base_url, fout)

  elif args.op == "counts":
    openphacts.ShowCounts(api_user_id, api_user_key, base_url)

  elif args.op == "get_assay":
    if not qry_uri: parser.error('Query URI required.')
    openphacts.GetInstance('assay', qry_uri, api_user_id, api_user_key, base_url, fout)

  elif args.op == "get_cpd":
    if not qry_uri: parser.error('Query URI required.')
    openphacts.GetInstance('compound', qry_uri, api_user_id, api_user_key, base_url, fout)

  elif args.op == "get_target":
    if not qry_uri: parser.error('Query URI required.')
    openphacts.GetInstance('target', qry_uri, api_user_id, api_user_key, base_url, fout)

  else:
    parser.error(f"Operation invalid: {args.op}")
