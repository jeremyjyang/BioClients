#!/usr/bin/env python3
"""
http://igraph.org/python/doc/tutorial/tutorial.html

Note that igraph defines its own IDs.  These are integers, not the same
as imported GraphML "id" values.

Compute information content (IC) for nodes in a directed acyclic graph
(DAG).
For each node, information content (IC) depends on total number of
descendants ndes, +1 for self.  Then IC is -log10((ndes+1)/n_total).
Given this we can identify the most informative common ancestor
(MICA), and the semantic similarity between any two nodes/terms.
Note that this is a kind of "Platonic" IC; in contrast, a set of
annotated disease instances could have a sampled IC which depends
on the frequency of each DO annotation.  In that scenario, an unused
disease has no effect on the sampled IC.

Used for Disease Ontology, as converted to GraphML with
BioClients.util.obo.App and Go_do_graph_IC.sh.
"""
#############################################################################
import sys,os,argparse,logging,re

from .. import igraph as util_igraph

#############################################################################
def TestMICA(g, nidA, nidB):
  vA = g.vs.find(id = nidA)
  vB = g.vs.find(id = nidB)
  logging.info(f"\tvA: [{vA.index}] {vA['doid']} ({vA['name']})")
  logging.info(f"\tvB: [{vB.index}] {vB['doid']} ({vB['name']})")
  vidx_mica = util_igraph.FindMICA(g, vA.index, vB.index, None)
  v = g.vs[vidx_mica]
  logging.info(f"MICA: [{vidx_mica}] {v['doid']} ({v['name']}); IC = {v['ic']:.3f}")

#############################################################################
if __name__=='__main__':
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
Info content (IC) and most informative common ancestor (MICA) for directed
acyclic graph (DAG).
simMatrixNodelist outputs vertex indices with node IDs.  simMatrix with --nidA to compute one row.
"""
  parser = argparse.ArgumentParser(description="IGraph (python-igraph API) utility, graph processingand display", epilog=epilog)
  ops = ["summary",
	"degree_distribution",
	"rootnodes",
	"topnodes",
  	"graph2cyjs",
	"shortest_paths",
	"show_ancestry",
	"connectednodes",
	"disconnectednodes",
	"node_select",
	"edge_select",
	"ic_computeIC", "ic_findMICA", "ic_simMatrix", "ic_simMatrixNodelist", "ic_test" ]
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
  parser.add_argument("--display_width", type=int, default=700)
  parser.add_argument("--display_height", type=int, default=500)
  parser.add_argument("--display_layout", default="rt")
  parser.add_argument("--depth", type=int, default=1, help="depth for --topnodes")
  parser.add_argument("--nidA", help="nodeA ID")
  parser.add_argument("--nidB", help="nodeB ID")
  parser.add_argument("--nmax", type=int)
  parser.add_argument("--skip", type=int)
  parser.add_argument("--recursionlimit", type=int, default=sys.getrecursionlimit())
  parser.add_argument("--quiet", action="store_true")
  parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>0 else logging.ERROR if args.quiet else 15))

  fin = open(args.ifile)
  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  sys.setrecursionlimit(args.recursionlimit)

  ###
  #Load graph:
  g = util_igraph.Load_GraphML(args.ifile)
  vs=[]; #vertices for subgraph selection

  if args.op=='summary':
    util_igraph.GraphSummary(g)

  elif args.op=='degree_distribution':
    util_igraph.DegreeDistribution(g)

  elif args.op=='node_select':
    if args.selectquery:
      vs = util_igraph.NodeSelect_String(g, args.selectfield, args.selectquery, args.select_exact, args.select_negate)
    elif args.selectval:
      parser.error('Numerical select not implemented yet.')
    else:
      parser.error('Select query or value required.')
    g = util_igraph.InducedSubgraph(g, vs, implementation="auto")
    util_igraph.Save_GraphML(g, fout)

  elif args.op=='edge_select':
    parser.error(f"Operation not implemented yet: {args.op}")

  elif args.op=='connectednodes':
    vs = util_igraph.ConnectedNodes(g)
    g = util_igraph.InducedSubgraph(g, vs, implementation="auto")
    util_igraph.Save_GraphML(g, fout)

  elif args.op=='disconnectednodes':
    vs = util_igraph.DisconnectedNodes(g)
    g = util_igraph.InducedSubgraph(g, vs, implementation="auto")
    util_igraph.Save_GraphML(g, fout)

  elif args.op=='rootnodes':
    vs = util_igraph.RootNodes(g)
    g = util_igraph.InducedSubgraph(g, vs, implementation="auto")
    util_igraph.Save_GraphML(g, fout)

  elif args.op=='topnodes':
    vs = util_igraph.TopNodes(g, args.depth)
    g = util_igraph.InducedSubgraph(g, vs, implementation="auto")
    util_igraph.Save_GraphML(g, fout)

  elif args.op=='shortest_paths':
    if not (args.nidA and  args.nidB): parser.error('--shortest_path requires nidA and nidB.')
    vs = util_igraph.ShortestPaths(g, args.nidA, args.nidB)
    g = util_igraph.InducedSubgraph(g, vs, implementation="auto")
    util_igraph.Save_GraphML(g, fout)

  elif args.op=='show_ancestry':
    if not nidA: parser.error('--show_ancestry requires nidA.')
    vA = g.vs.find(id=args.nidA)
    vidxA = vA.index
    util_igraph.ShowAncestry(g, vidxA, 0)

  elif args.op=='graph2cyjs':
    fout.write(util_igraph.Graph2CyJsElements(g))

  elif args.op == 'ic_computeIC':
    if not g.is_dag(): parser.error(f"Graph not DAG; required for operation: {args.op}")
    util_igraph.ComputeInfoContent(g)
    util_igraph.Save_GraphML(g, fout)

  elif args.op == 'ic_findMICA':
    if not g.is_dag(): parser.error(f"Graph not DAG; required for operation: {args.op}")
    if not (args.nidA and args.nidB):
      parser.error('findMICA requires --nidA and --nidB.')
      parser.print_help()
    vA = g.vs.find(id = args.nidA)
    vB = g.vs.find(id = args.nidB)
    logging.debug(f"\tvA: [{vA.index}] {vA['doid']} ({vA['name']})")
    logging.debug(f"\tvB: [{vB.index}] {vB['doid']} ({vB['name']})")
    vidx_mica = util_igraph.FindMICA(g, vA.index, vB.index, None)
    v = g.vs[vidx_mica]
    logging.info(f"MICA: [{vidx_mica}] {v['doid']} ({v['name']}); IC = {v['ic']:.3f}")

  elif args.op == 'ic_simMatrix':
    vidxA = g.vs.find(id=args.nidA).index if args.nidA else None
    util_igraph.SimMatrix(g, vidxA, args.skip, args.nmax, fout)

  elif args.op == 'ic_simMatrixNodelist':
    util_igraph.SimMatrixNodelist(g, fout)

  elif args.op == 'test':
    #if not (args.nidA and args.nidB):
    #  parser.error('test requires --nidA and --nidB.')
    #  parser.print_help()
    import cProfile
    #cProfile.run('TestMICA(g,"%s","%s")'%(args.nidA,args.nidB))
    cProfile.run('SimMatrix(g, 0, 1, fout)')
    #cProfile.runctx('TestMICA(g,"%s","%s")'%(args.nidA,args.nidB), globals(), locals())

  else:
    parser.error('No operation specified.')
    parser.print_help()

  fout.close()

  if args.display:
    util_igraph.DisplayGraph(g, args.display_layout, args.display_width, args.display_height)

