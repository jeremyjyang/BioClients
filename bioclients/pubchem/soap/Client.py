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
import sys,os,re,time,argparse,logging

from ... import pubchem

#############################################################################
if __name__=='__main__':
  SEARCH_NMAX=100;
  OPS = ["search_exact", "search_substructure", "search_similarity", "standardize", "idexchange"]
  OPERATORS = ["same", "parent", "samepar"]
  FORMATS = ["smiles", "smarts", "inchi", "inchikey", "cid", "sid", "sdf"]
  CHEMFORMATS = ["smiles", "inchi", "sdf"]
  SEARCHFORMATS = ["smiles", "smarts", "inchi", "cid"]
  epilog = """Search operations accept one query CID, SMILES, SMARTS, or InChI;
standardize and idexchange accept batch input files. Standardize accepts and returns
SMILES, SDF, or InChI. IDExchange accepts CID, SID, SMILES, InChI, InChIKey,
Synonym, and Registry ID (for specified Source)"""
  parser = argparse.ArgumentParser(description="PubChem PUG SOAP client: idexchange, standardize, sub|sim|exact search", epilog=epilog)
  parser.add_argument("op", choices=OPS, default="exact", help="OPERATION")
  parser.add_argument("--i", dest="ifile", help="Input file for batch IDs")
  parser.add_argument("--o", dest="ofile", help="Output SMILES|SDF|TSV file")
  parser.add_argument("--operator", choices=OPERATORS, default="same", help="Request logic operator")
  parser.add_argument("--ids", help="Input ID[s] (comma-separated)")
  parser.add_argument("--query_id", help="Input ID (use for search operations)")
  parser.add_argument("--ifmt", choices=FORMATS, default="smiles", help="Input format")
  parser.add_argument("--ofmt", choices=FORMATS, default="cid", help="Output format")
  parser.add_argument("--gz", action="store_true", help="Output gzipped [default via filename]")
  parser.add_argument("--sim_cutoff", type=float, default=pubchem.soap.SIM_CUTOFF, help="Similarity cutoff, Tanimoto")
  parser.add_argument("--active", help="Active mols only (in any assay)")
  parser.add_argument("--search_nmax", type=int, default=SEARCH_NMAX, help="Max search hits returned")
  parser.add_argument("--max_wait", type=int, default=pubchem.soap.MAX_WAIT, help="Max wait for query")
  parser.add_argument("--poll_wait", type=int, default=pubchem.soap.POLL_WAIT, help="Polling wait interval")
  parser.add_argument("--api_host", default=pubchem.soap.API_HOST)
  parser.add_argument("--api_base_path", default=pubchem.soap.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  api_base_url = f"https://{args.api_host}{args.api_base_path}"

  do_gz = args.gz if args.gz else bool(args.ofile and args.ofile[-3:]=='.gz')
  fout = open(args.ofile, 'wb') if args.ofile and do_gz else open(args.ofile, 'w+') if args.ofile else sys.stdout
  ofmt = args.ofmt if args.ofmt else None

  if args.ofile and not args.ofmt:
    ofmt = re.sub('^.*\.', '', args.ofile[:-3]) if (args.ofile[-3:]=='.gz') else re.sub('^.*\.', '', args.ofile)

  ids=[];
  if args.query_id:
    ids = [args.query_id]
  elif args.ids:
    ids = re.split(r'[,\s]+', args.ids)
  elif args.ifile:
    with open(args.ifile) as fin:
      while True:
        line = fin.readline()
        if not line: break
        ids.append(line.rstrip())
  if len(ids)>0: logging.info(f"Input IDs: {len(ids)}")

  t0=time.time()	## start timer

  # Submit request (pubchem.soap.PugSoapRequest class):
  if args.op == "standardize":
    if args.ofmt not in CHEMFORMATS:
      parser.error(f"Output format must be in {str(CHEMFORMATS)} for operation {args.op}.")
    # TO DO: Loop for batch...
    pugreq = pubchem.soap.SubmitRequest_Standardize(ids[0], args.ifmt, args.ofmt, do_gz, api_base_url)
  elif args.op == "idexchange":
    pugreq = pubchem.soap.SubmitRequest_IDExchange(ids, args.ifmt, args.ofmt, args.operator, do_gz, api_base_url)
  elif args.op in ["search_exact", "search_substructure", "search_similarity"]:
    if args.ifmt not in SEARCHFORMATS:
      parser.error(f"Input format must be in {str(SEARCHFORMATS)} for operation {args.op}.")
    pugreq = pubchem.soap.SubmitRequest_StructuralSearch(ids[0], args.op, args.sim_cutoff, args.active, args.search_nmax, api_base_url)
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

  if pugreq.url is not None: # May have url for download.
    logging.info(f"url: {pugreq.url}")
    pubchem.soap.DownloadResults(pugreq.url, ofmt, do_gz, fout) # Output: download via url.
  elif pugreq.qkey is not None: # May have qkey for 2nd request.
    logging.info(f"qkey: {pugreq.qkey}")
    pugreq2 = pubchem.soap.MonitorQuery(pugreq.qkey, pugreq.wenv, ofmt, do_gz, api_base_url)
    pugreq2.waitForResult(args.poll_wait, args.max_wait)
    pubchem.soap.DownloadResults(pugreq2.url, ofmt, do_gz, fout) # Output: download via url.
  elif pugreq.out_struct is not None: # May have standardized structure.
    logging.info(f"out_struct: {pugreq.out_struct}")
    fout.write(f"{pugreq.out_struct}\n")
  else:
    logging.error(f"No url, qkey nor out_struct.")
  fout.close()

  logging.info(f"Output format: {ofmt}{(' (gzipped)' if do_gz else '')}")
  if args.ofile is not None: logging.info(f"Output file {args.ofile} ({os.stat(args.ofile).st_size/1e6:.2f}MB)")
  logging.info(f"Elapsed time: {time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))}")

