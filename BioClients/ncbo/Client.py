#!/usr/bin/env python3
"""
http://data.bioontology.org/documentation
The National Center for Biomedical Ontology was founded as one of the
National Centers for Biomedical Computing, supported by the NHGRI, the
NHLBI, and the NIH Common Fund.
"""
###
import sys,os,argparse,re,yaml,logging,time
#
from .. import ncbo
from ..util import yaml as util_yaml
#
#############################################################################
if __name__=='__main__':
  EPILOG="""The National Center for Biomedical Ontology was founded as one of the National Centers for Biomedical Computing, supported by the NHGRI, the NHLBI, and the NIH Common Fund."""
  parser = argparse.ArgumentParser(description='NCBO REST API client utility', epilog=EPILOG)
  OPS = ['recommendOntologies']
  parser.add_argument("op", choices=OPS, help="OPERATION")
  parser.add_argument("--i", dest="ifile", help="input texts")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("--text", help="input text")
  parser.add_argument("--api_host", default=ncbo.API_HOST)
  parser.add_argument("--api_base_path", default=ncbo.API_BASE_PATH)
  parser.add_argument("--param_file", default=os.environ["HOME"]+"/.ncbo.yaml")
  parser.add_argument("--api_key", help="API key")
  parser.add_argument("-v", "--verbose", default=0, action="count")

  args = parser.parse_args()

  logging.basicConfig(format="%(levelname)s:%(message)s", level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url = "https://"+args.api_host+args.api_base_path

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  params = util_yaml.ReadParamFile(args.param_file)
  if args.api_key: params["API_KEY"] = args.api_key
  if not params["API_KEY"]:
    parser.error("Please specify valid API_KEY via --api_key or --param_file") 

  texts=[];
  if args.ifile:
    with open(args.ifile) as fin:
      while True:
        line = fin.readline()
        if not line: break
        texts.append(line.rstrip())
    logging.info(f"input texts: {len(texts)}")
  elif args.text:
    texts = [args.text]

  t0 = time.time()

  if args.op == "recommendOntologies":
    ncbo.RecommendOntologies(base_url, params["API_KEY"], texts, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")

  logging.info(("Elapsed time: %s"%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))
