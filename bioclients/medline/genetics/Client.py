#!/usr/bin/env python3
##############################################################################
### Medline Plus Genetics
### (Formerly Genetics Home Reference)
### https://medlineplus.gov/about/developers/geneticsdatafilesapi/
### https://medlineplus.gov/download/ghr-summaries.xml
##############################################################################
### https://wsearch.nlm.nih.gov/ws/query?db=ghr&term=alzheimer
### https://medlineplus.gov/download/genetics/condition/alzheimer-disease.json
##############################################################################
import sys,os,re,argparse,time,logging
#
from ... import medline
#
##############################################################################
if __name__=="__main__":
  epilog = """
Example conditions:
allergic-asthma,
alzheimer-disease,
parkinson-disease,
rapid-onset-dystonia-parkinsonism,
type-1-diabetes,
type-2-diabetes,

"""
  ops = ["search", "list_conditions", "list_genes", "get_condition_genes"]
  parser = argparse.ArgumentParser(description="MedlinePlus Genetics REST API client", epilog=epilog)
  parser.add_argument("op", choices=ops, help="OPERATION (select one)")
  parser.add_argument("--i", dest="ifile", help="input term file (one per line)")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--ids", help="term list (comma-separated)")
  parser.add_argument("--api_host", default=medline.genetics.API_HOST)
  parser.add_argument("--api_base_path", default=medline.genetics.API_BASE_PATH)
  parser.add_argument("--download_host", default=medline.genetics.DOWNLOAD_HOST)
  parser.add_argument("--download_base_path", default=medline.genetics.DOWNLOAD_BASE_PATH)
  parser.add_argument("--summary_url", default=medline.genetics.SUMMARY_URL)
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format="%(levelname)s:%(message)s", level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  api_base_url="https://"+args.api_host+args.api_base_path
  download_base_url="https://"+args.download_host+args.download_base_path

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  t0=time.time()

  ids=[]
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      ids.append(line.rstrip())
    fin.close()
  elif args.ids:
    ids = re.split('[, ]+', args.ids.strip())
  if len(ids)>0: logging.info(f"Input IDs: {len(ids)}")

  if args.op=="search":
    medline.genetics.Utils.Search(ids, api_base_url, fout)

  elif args.op=="list_conditions":
    medline.genetics.Utils.ListConditions(args.summary_url, fout)

  elif args.op=="list_genes":
    medline.genetics.Utils.ListGenes(args.summary_url, fout)

  elif args.op=="get_condition_genes":
    medline.genetics.Utils.GetConditionGenes(ids, download_base_url, fout)

  else:
    parser.error(f"Operation invalid: {args.op}")

  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}")

