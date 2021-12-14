#!/usr/bin/env python3
"""
http://igraph.org/python/doc/tutorial/tutorial.html

Note that igraph defines its own IDs.  These are integers, not the same
as imported GraphML "id" values.

See also: igraph_plot.py
"""
#############################################################################
import sys,os,argparse,logging,re

from .. import igraph as util_igraph

#############################################################################
if __name__=='__main__':
  DEPTH=1;
  epilog="""\
OPERATIONS:
summary: summary of graph;
degree_distribution: degree distribution;
node_select: select for nodes by criteria;
edge_select: select for edges by criteria;
connectednodes: connected node[s];
disconnectednodes: disconnected node[s];
rootnodes: root node[s] of DAG;
topnodes: root node[s] & children of DAG;
shortest_paths: shortest paths, nodes A ~ B;
show_ancestry: show ancestry, node A;
graph2cyjs: CytoscapeJS JSON;
NOTE: select also deletes non-matching for modified output.
"""
  parser = argparse.ArgumentParser(description="IGraph (python-igraph API) utility, graph processingand display", epilog=epilog)
  ops = ["summary",
	"degree_distribution",
	"rootnodes",
	"topnodes",
  	"graph2cyjs",
	"shortest_path",
	"show_ancestry",
	"connectednodes",
	"disconnectednodes",
	"node_select",
	"edge_select" ]
  parser.add_argument("op", choices=ops, help='OPERATION')
  parser.add_argument("--i", dest="ifile", required=True, help="input file or URL (e.g. GraphML)")
  parser.add_argument("--o", dest="ofile", help="output file")
  parser.add_argument("--selectfield", help="field (attribute) to select")
  parser.add_argument("--selectquery", help="string query")
  parser.add_argument("--selectval", type=float, help="numerical query")
  parser.add_argument("--select_exact", help="exact string match (else substring/regex)")
  parser.add_argument("--select_equal", action="store_true", help="numerical equality select")
  parser.add_argument("--select_lt", action="store_true", help="numerical less-than select")
  parser.add_argument("--select_gt", action="store_true", help="numerical greater-than select")
  parser.add_argument("--select_negate", action="store_true", help="negate select criteria")
  parser.add_argument("--display", action="store_true", help="display graph interactively")
  parser.add_argument("--depth", type=int, default=DEPTH, help="depth for --topnodes")
  parser.add_argument("--nidA", help="nodeA ID")
  parser.add_argument("--nidB", help="nodeB ID")
  parser.add_argument("--quiet", action="store_true")
  parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>0 else logging.ERROR if args.quiet else 15))

  fin = open(args.ifile)

  fout = open(args.ofile,"w+") if args.ofile else sys.stdout

  ###
  #INPUT:
  ###
  g = util_igraph.Load_GraphML(args.ifile)

  vs = []; #vertices for subgraph selection

  if args.op=='summary':
    util_igraph.GraphSummary(g)

  elif args.op=='degree_distribution':
    util_igraph.DegreeDistribution(g)

  elif args.op=='node_select':
    if args.selectquery:
      vs = util_igraph.NodeSelect_String(g, args.selectfield, args.selectquery, args.select_exact, args.select_negate)
    elif args.selectval:
      parser.error('numerical select not implemented yet.')
    else:
      parser.error('select query or value required.')

  elif args.op=='edge_select':
    parser.error('not implemented yet.')

  elif args.op=='connectednodes':
    vs = util_igraph.ConnectedNodes(g)

  elif args.op=='disconnectednodes':
    vs = util_igraph.DisconnectedNodes(g)

  elif args.op=='rootnodes':
    vs = util_igraph.RootNodes(g)

  elif args.op=='topnodes':
    vs = util_igraph.TopNodes(g, args.depth)

  elif args.op=='shortest_path':
    if not (args.nidA and  args.nidB): parser.error('--shortest_path requires nidA and nidB.')
    vs = util_igraph.ShortestPath(g, args.nidA, args.nidB)

  elif args.op=='show_ancestry':
    if not nidA: parser.error('--show_ancestry requires nidA.')
    vA = g.vs.find(id =  args.nidA)
    vidxA = vA.index
    util_igraph.ShowAncestry(g, vidxA, 0)

  elif args.op=='graph2cyjs':
    fout.write(util_igraph.Graph2CyJsElements(g))

  if vs:
    for v in vs:
      logging.debug(f"{v['id']}: {v['name']}")
    logging.info(f"Selected nodes: {len(vs)}")
    g = g.induced_subgraph(vs, implementation="auto")
    logging.info(f"SELECTED SUBGRAPH:  nodes: {g.vcount()}; edges: {g.ecount()}")

  ###
  #OUTPUT:
  ###
  if args.ofile:
    util_igraph.Save_GraphML(g, fout)
    fout.close()

  elif args.display:
    w,h = 700,500
    layout = 'rt'
    util_igraph.DisplayGraph(g, layout, w, h)

