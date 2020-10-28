#!/usr/bin/env python3
"""
TIN-X (Target Importance and Novelty Explorer) REST API client
https://www.newdrugtargets.org/
https://api.newdrugtargets.org/docs
https://api.newdrugtargets.org/targets/
"""
###
import sys,os,re,argparse,time,logging
#
from ...idg import tinx
#
##############################################################################
if __name__=='__main__':
  epilog="""\
Example IDs:
5391 (disease); DOID:9297 (DOID);
12203 (target); Q9H4B4 (UniProt);
--disease_ids needed ONLY if BOTH target and disease IDs specified, such
as for get_disease_target_articles.
"""
  parser = argparse.ArgumentParser(description="TIN-X (Target Importance and Novelty Explorer) REST API client)", epilog=epilog)
  ops = [
	"list_diseases", "list_targets", "list_articles", "list_dto",
	"get_disease", "get_disease_by_doid", "get_disease_targets", "get_disease_target_articles", "get_target", "get_target_by_uniprot", "get_target_diseases", "get_dto",
	"search_diseases", "search_targets", "search_articles", "search_dtos"
	]
  parser.add_argument("op", choices=ops, help="operation")
  parser.add_argument("--i", dest="ifile", help="input IDs or search terms")
  parser.add_argument("--ids", help="IDs (comma-separated)")
  parser.add_argument("--disease_ids", help="disease IDs (comma-separated), needed ONLY if BOTH target and disease IDs specified")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--query", help="search query")
  parser.add_argument("--skip", type=int, default=0)
  parser.add_argument("--nmax", type=int, default=None)
  parser.add_argument("--api_host", default=tinx.Utils.API_HOST)
  parser.add_argument("--api_base_path", default=tinx.Utils.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  ids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    fin.close()
  elif args.ids:
    ids = re.split('[,\s]+', args.ids.strip())
  if ids: logging.info('Input IDs: %d'%(len(ids)))
  disease_ids = re.split('[,\s]+', args.disease_ids.strip()) if args.disease_ids else None

  t0=time.time()

  base_url = 'https://'+args.api_host+args.api_base_path

  if args.op=='list_targets':
    tinx.Utils.ListTargets(args.skip, args.nmax, base_url, fout)

  elif args.op=='list_diseases':
    tinx.Utils.ListDiseases(args.skip, args.nmax, base_url, fout)

  elif args.op=='list_articles':
    tinx.Utils.ListArticles(args.skip, args.nmax, base_url, fout)

  elif args.op=='list_dto':
    tinx.Utils.ListDTO(args.skip, args.nmax, base_url, fout)

  elif args.op=='get_disease':
    tinx.Utils.GetDisease(ids, args.skip, args.nmax, base_url, fout)

  elif args.op=='get_disease_by_doid':
    tinx.Utils.GetDiseaseByDOId(ids, args.skip, args.nmax, base_url, fout)

  elif args.op=='get_disease_targets':
    tinx.Utils.GetDiseaseTargets(ids, args.skip, args.nmax, base_url, fout)

  elif args.op=='get_disease_target_articles':
    if not disease_ids: parser.error("--disease_ids required for {}".format(args.op))
    tinx.Utils.GetDiseaseTargetArticles(disease_ids, ids, args.skip,
args.nmax, base_url, fout)

  elif args.op=='get_target':
    tinx.Utils.GetTarget(ids, args.skip, args.nmax, base_url, fout)

  elif args.op=='get_target_by_uniprot':
    tinx.Utils.GetTargetByUniprot(ids, args.skip, args.nmax, base_url, fout)

  elif args.op=='get_target_diseases':
    tinx.Utils.GetTargetDiseases(ids, args.skip, args.nmax, base_url, fout)

  elif args.op=='search_diseases':
    if not args.query: parser.error("--query required for {}".format(args.op))
    tinx.Utils.SearchDiseases(args.query, args.skip, args.nmax,
base_url, fout)

  elif args.op=='search_targets':
    if not args.query: parser.error("--query required for {}".format(args.op))
    tinx.Utils.SearchTargets(args.query, args.skip, args.nmax, base_url, fout)

  elif args.op=='search_articles':
    if not args.query: parser.error("--query required for {}".format(args.op))
    tinx.Utils.SearchArticles(args.query, args.skip, args.nmax, base_url, fout)

  else:
    parser.error('Unknown operation: %s'%args.op)

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))
