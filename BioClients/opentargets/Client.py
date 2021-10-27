#!/usr/bin/env python3
"""
OpenTargets REST API client, using the Python client package.
http://opentargets.readthedocs.io/
"""
import sys,os,re,time,argparse,json,csv,logging

from opentargets import OpenTargetsClient

from .. import opentargets #BioClients module.

#############################################################################
if __name__=='__main__':
  IDTYPES = ["gene", "disease"]
  #SOURCES = ["cancer_gene_census", "chembl", "crispr", "europepmc", "eva", "eva_somatic", "expression_atlas", "gene2phenotype", "genomics_england", "gwas_catalog", "intogen", "ot_genetics_portal", "phenodigm", "phewas_catalog", "postgap", "progeny", "reactome", "slapenrich", "sysbio", "uniprot", "uniprot_literature", "uniprot_somatic"]
  epilog = """Examples:
Gene IDs: ENSG00000163914, ENSG00000072110;
Disease IDs: EFO_0002630, EFO_1001473, HP_0011446, HP_0100543, EFO_0002508 ;
Search terms: prostate, alzheimer, lymphoma
"""
  parser = argparse.ArgumentParser(description='OpenTargets REST API client utility', epilog=epilog)
  ops = ['searchAssociations', 'getEvidence']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="input file, gene or disease IDs")
  parser.add_argument("--ids", help="(1) target ID, gene symbol or ENSEMBL; (2) disease ID, EFO_ID; or (3) search term (comma-separated)")
  parser.add_argument("--idtype", choices=IDTYPES, default="disease")
  #parser.add_argument("--source", choices=SOURCES)
  parser.add_argument("--minscore", type=float, help="minimum overall association score")
  parser.add_argument("--nmax", type=int, default=0, help="max results")
  parser.add_argument("--skip", type=int, default=0, help="skip results")
  parser.add_argument("--o", dest="ofile", help="output (TSV)")
  parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  t0 = time.time()

  fout = open(args.ofile,"w+") if args.ofile else sys.stdout

  ids=[];
  if args.ifile:
    fin = open(args.ifile)
    while True:
      line = fin.readline()
      if not line: break
      if line.rstrip(): ids.append(line.rstrip())
    fin.close()
  elif args.ids:
    ids = re.split(r'[,\s]+', args.ids)
  if ids: logging.info('Input IDs: {}'.format(len(ids)))

  otclient = OpenTargetsClient()

  logging.debug(otclient.get_stats().info)

  if args.op=='searchAssociations':
    if not ids: parser.error('--i or --ids required.')
    opentargets.SearchAssociations(otclient, ids, args.idtype, args.minscore, args.skip, args.nmax, fout)

  elif args.op=='getEvidence':
    parser.error('Unimplemented operation: {}'.format(args.op))
    if not ids: parser.error('--i or --ids required.')
    #opentargets.Target2Disease_Evidence(otclient, tid, args.did, fout)

  else:
    parser.error('Invalid operation: {}'.format(args.op))

  logging.info("Elapsed: {}".format(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))))

