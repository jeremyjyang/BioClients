#!/usr/bin/env python3
##############################################################################
### Medline Plus Genetics
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
  ops = ["get_disease", "search_disease"]
  parser = argparse.ArgumentParser(description="MedlinePlus Genetics REST API client", epilog="")
  parser.add_argument("op", choices=ops, help="OPERATION (select one)")
  parser.add_argument("--i", dest="ifile", help="input term file (one per line)")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--ids", help="term list (comma-separated)")
  parser.add_argument("--api_host", default=medline.genetics.API_HOST)
  parser.add_argument("--api_base_path", default=medline.genetics.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format="%(levelname)s:%(message)s", level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url="https://"+args.api_host+args.api_base_path

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

  if args.op=="search_disease":
    medline.genetics.Utils.SearchDisease(ids, base_url, fout)

  else:
    parser.error(f"Operation invalid: {args.op}")

  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))}")

