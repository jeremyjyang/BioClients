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
API_HOST='reactome.org'
API_BASE_PATH='/ContentService'
#
#
##############################################################################
if __name__=='__main__':

  parser = argparse.ArgumentParser(
        description='Reactome (www.reactome.org) REST API client utility',
        epilog="""\
Example IDs:
	109581 (Pathway),
	57033 (EntityWithAccessionedSequence);
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
  ops = ['list_diseases', 'list_ToplevelPathways', 'list_proteins', 'list_compounds', 'get_entity', 'get_pathwaysforgenes', 'get_pathwaysforentities', 'get_pathwayparticipants']
  parser.add_argument("op",choices=ops,help='operation')
  parser.add_argument("--ids", dest="ids", help="IDs, comma-separated")
  parser.add_argument("--i", dest="ifile", help="input file, IDs")
  parser.add_argument("--o", dest="ofile", help="output file")
  parser.add_argument("--ctype", default='Pathway', help="class type")
  parser.add_argument("--api_host", default=API_HOST)
  parser.add_argument("--api_base_path", default=API_BASE_PATH)
  parser.add_argument("-v", "--verbose", action="count", default=0)

  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  base_url='https://'+args.api_host+args.api_base_path

  if args.ofile:
    fout = open(args.ofile,"w")
  else:
    fout = sys.stdout

  t0=time.time()

  if args.ifile:
    fin=open(args.ifile)
    if not fin: parser.error('cannot open: %s'%args.ifile)
    ids = [];
    while True:
      line=fin.readline()
      if not line: break
      if line.rstrip(): ids.append(line.rstrip())
    logging.info('input queries: %d'%(len(ids)))
    fin.close()
  elif args.ids:
    ids = re.split('[, ]+', args.ids.strip())

  if args.op == "get_entity":
    reactome.Utils.GetEntity(base_url, ids, ctype, fout)
    #fout.write(json.dumps(rval, sort_keys=True, indent=2)+'\n')

  elif args.op == "list_diseases":
    reactome.Utils.ListDiseases(base_url, fout)

  elif args.op == "list_proteins":
    reactome.Utils.ListProteins(base_url, fout)

  elif args.op == "list_ToplevelPathways":
    reactome.Utils.ListToplevelPathways(base_url, fout)

  elif args.op == "list_compounds":
    reactome.Utils.ListCompounds(base_url, fout)

  elif args.op == "get_pathwaysforgenes":
    reactome.Utils.PathwaysForGenes(base_url, ids, fout)

  elif args.op == "get_pathwaysforentities":
    reactome.Utils.PathwaysForEntities(base_url, ids, fout)

  elif args.op == "get_pathwayparticipants":
    reactome.Utils.PathwayParticipants(base_url, ids, fout)

  else:
    parser.error("No operation specified.")

  logging.info(('elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))
