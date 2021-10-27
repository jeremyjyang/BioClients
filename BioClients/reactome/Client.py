#!/usr/bin/env python3
"""
Client for Reactome REST API.
https://reactome.org/ContentService/
https://reactome.org/ContentService/data/pathways/top/9606
"""
import sys,os,re,argparse,time,json,logging
#
from .. import reactome
#
##############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(
        description='Reactome (www.reactome.org) REST API client utility',
        epilog="""\
Example IDs:
	1640170 (dbId for "Cell Cycle")
	R-HSA-1640170 (stId for "Cell Cycle")
	109581 (Pathway),
	57033 (EntityWithAccessionedSequence);
	Q13501 (interactor accession (UniProt))
Classes:
	ExternalOntology:Disease,
	Event:Pathway,
	Event:ReactionlikeEvent,
	Person,
	PhysicalEntity [388758],
	PhysicalEntity:Complex [75208],
	PhysicalEntity:Polymer [1181],
	PhysicalEntity:EntitySet [65039],
	PhysicalEntity:GenomeEncodedEntity [244344],
	PhysicalEntity:GenomeEncodedEntity:EntityWithAccessionedSequence [239613],
	PhysicalEntity:SimpleEntity [2668],
	Publication,
	Taxon:Species
""")
  ops = [
          'dbinfo',
          'list_diseases',
          'list_toplevelpathways',
          'list_compounds',
          'query_entry',
          'get_interactors',
          'get_pathwaysforgenes',
          'get_pathwaysforentities',
          'get_pathwayparticipants']
  parser.add_argument("op",choices=ops, help='OPERATION')
  parser.add_argument("--ids", dest="ids", help="IDs, comma-separated")
  parser.add_argument("--i", dest="ifile", help="input file, IDs")
  parser.add_argument("--o", dest="ofile", help="output file")
  parser.add_argument("--api_host", default=reactome.API_HOST)
  parser.add_argument("--api_base_path", default=reactome.API_BASE_PATH)
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='https://'+args.api_host+args.api_base_path

  fout = open(args.ofile,"w") if args.ofile else sys.stdout

  t0=time.time()

  if args.ifile:
    fin = open(args.ifile)
    ids = [];
    while True:
      line = fin.readline()
      if not line: break
      if line.rstrip(): ids.append(line.rstrip())
    logging.info('Input queries: {}'.format(len(ids)))
    fin.close()
  elif args.ids:
    ids = re.split('[, ]+', args.ids.strip())

  if args.op == "dbinfo":
    reactome.DBInfo(base_url, fout)

  elif args.op == "query_entry":
    reactome.QueryEntry(ids, base_url, fout)

  elif args.op == "list_diseases":
    reactome.ListDiseases(base_url, fout)

  elif args.op == "list_toplevelpathways":
    reactome.ListToplevelPathways(base_url, fout)

  elif args.op == "list_compounds":
    reactome.ListCompounds(base_url, fout)

  elif args.op == "get_interactors":
    reactome.GetInteractors(ids, base_url, fout)

  elif args.op == "get_pathwaysforgenes":
    reactome.GetPathwaysForGenes(ids, base_url, fout)

  elif args.op == "get_pathwayparticipants":
    reactome.GetPathwayParticipants(ids, base_url, fout)

  else:
    parser.error("No operation specified.")

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))
