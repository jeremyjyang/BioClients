#!/usr/bin/env python3
"""
PubChem PUG SOAP services, including:
  - PubChem Identifier Exchange Service (PIES), https://pubchem.ncbi.nlm.nih.gov/idexchange/idexchange.cgi
  - PubChem Standardization Service, https://pubchem.ncbi.nlm.nih.gov/standardize/standardize.cgi
  - PubChem Structure Search, https://pubchem.ncbi.nlm.nih.gov/search/search.cgi
See Save Query button for template XML.
https://pubchemdocs.ncbi.nlm.nih.gov/pug-soap
https://pubchemdocs.ncbi.nlm.nih.gov/pug-soap-reference
https://pubchem.ncbi.nlm.nih.gov/pug_soap/pug_soap.cgi?wsdl
"""
import sys,os,re,urllib,time,argparse,tempfile,logging

from ... import pubchem
from ...pubchem.soap import Utils

#############################################################################
if __name__=='__main__':
  SEARCH_NMAX=100;
  OPS = ["exact", "substructure", "similarity", "standardize", "idexchange"]
  OPERATORS = ["same", "parent", "samepar"]
  FORMATS = ["smiles", "inchi", "inchikey", "cid", "sid", "sdf"]
  epilog = """Search operations accept one query smiles or smarts; standardize
and idexchange accept batch input files. Standardize accepts and returns
SMILES, SDF, or InChI. IDExchange accepts CID, SID, SMILES, InChI, InChIKey,
Synonym, and Registry ID (for specified Source)"""
  parser = argparse.ArgumentParser(description="PubChem PUG SOAP client: sub|sim|exact search, fetch smiles|sdfs", epilog=epilog)
  parser.add_argument("op", choices=OPS, default="exact", help="OPERATION")
  parser.add_argument("--i", dest="ifile", help="Input file for batch IDs")
  parser.add_argument("--o", dest="ofile", help="Output SMILES|SDF|TSV file")
  parser.add_argument("--operator", choices=OPERATORS, default="same", help="Request logic operator")
  parser.add_argument("--qsmi", help="Input search query smiles (or smarts)")
  parser.add_argument("--ids", help="input IDs (comma-separated)")
  parser.add_argument("--ifmt", choices=FORMATS, default="smiles", help="Input format")
  parser.add_argument("--ofmt", choices=FORMATS, default="cid", help="Output format")
  parser.add_argument("--gz", action="store_true", help="Output gzipped [default via filename]")
  parser.add_argument("--sim_cutoff", type=float, default=Utils.SIM_CUTOFF, help="Similarity cutoff, Tanimoto")
  parser.add_argument("--active", help="Active mols only (in any assay)")
  parser.add_argument("--search_nmax", type=int, default=SEARCH_NMAX, help="Max search hits returned")
  parser.add_argument("--max_wait", type=int, default=Utils.MAX_WAIT, help="Max wait for query")
  parser.add_argument("--poll_wait", type=int, default=Utils.POLL_WAIT, help="Polling wait interval")
  parser.add_argument("--api_host", default=Utils.API_HOST)
  parser.add_argument("--api_base_path", default=Utils.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  api_base_url = f"https://{args.api_host}{args.api_base_path}"

  fout = open(args.ofile, 'wb') if args.ofile else sys.stdout
  ofmt = args.ofmt if args.ofmt else None
  do_gz = args.gz if args.gz else bool(args.ofile and args.ofile[-3:]=='.gz')

  if args.ofile and not args.ofmt:
    ofmt = re.sub('^.*\.', '', args.ofile[:-3]) if (args.ofile[-3:]=='.gz') else re.sub('^.*\.', '', args.ofile)

  ids=[]
  if args.ifile:
    with open(args.ifile) as fin:
      while True:
        line = fin.readline()
        if not line: break
        ids.append(line.rstrip())
  elif args.ids:
    ids = re.split(r'[,\s]+', args.ids)
  if len(ids)>0: logging.info(f"Input IDs: {len(ids)}")

  t0=time.time()	## start timer

  # Submit request (Utils.PugSoapRequest class):
  if args.op == "standardize":
    # TO DO: Loop for batch...
    pugreq = pubchem.soap.Utils.SubmitRequest_Standardize(ids[0], args.ifmt, args.ofmt, do_gz, api_base_url)
  elif args.op == "idexchange":
    pugreq = pubchem.soap.Utils.SubmitRequest_IDExchange(ids, args.ifmt, args.ofmt, args.operator, do_gz, api_base_url)
  elif args.op in ["exact", "substructure", "similarity"]:
    pugreq = pubchem.soap.Utils.SubmitRequest_Structural(args.qsmi, args.op, args.sim_cutoff, args.active, args.nmax, api_base_url)
  else:
    parser.error(f"Operation not suported: {args.op}")
    sys.exit(1)

  # Check request status.
  # Error status values include: "input-error", "server-error"
  if pugreq.status not in ("success", "queued", "running"):
    logging.error(f"Query failed; quitting (status={pugreq.status}, error={pugreq.error})")
    sys.exit()
  logging.info(f"Query [{pugreq.reqid}] status: {pugreq.status}")

  # Wait for result, success or failure.
  pugreq.waitForResult(args.poll_wait, args.max_wait)

  # May have url for download, or qkey for 2nd request.
  logging.info(f"qkey: {pugreq.qkey}; url: {pugreq.url}")
  download_url=None;
  if pugreq.url is not None:
    logging.info(f"url: {pugreq.url}")
    download_url=pugreq.url
    pubchem.soap.Utils.DownloadResults(download_url, fout) # Output: download via url.
  elif pugreq.qkey is not None:
    logging.info(f"qkey: {pugreq.qkey}")
    # Submit 2nd request using query key from initial query.
    pugreq2 = pubchem.soap.Utils.MonitorQuery(pugreq.qkey, pugreq.wenv, ofmt, do_gz, api_base_url)
    pugreq2.waitForResult(args.poll_wait, args.max_wait)
    download_url=pugreq2.url
    pubchem.soap.Utils.DownloadResults(download_url, fout) # Output: download via url.
  elif pugreq.out_struct is not None:
    logging.info(f"out_struct: {pugreq.out_struct}")
    fout.write(f"{pugreq.out_struct}\n")
  else:
    logging.error(f"No url, qkey nor out_struct.")

  fout.close()

  logging.info(f"Output format: {ofmt}{(' (gzipped)' if do_gz else '')}")
  if args.ofile is not None: logging.info(f"Output file {args.ofile} ({os.stat(args.ofile).st_size/1e6:.2f}MB)")
  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))}")

