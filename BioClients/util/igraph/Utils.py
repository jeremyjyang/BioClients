#!/usr/bin/env python3
"""
http://igraph.org/python/doc/tutorial/tutorial.html

Note that igraph defines its own IDs.  These are integers, not the same
as imported GraphML "id" values.

See also: igraph_plot.py
"""
#############################################################################
import sys,os,argparse,logging
import re,random,tempfile,shutil
import json
import igraph

#############################################################################
def Load_GraphML(ifile):
  g = igraph.Graph.Read_GraphML(ifile)
  logging.info(f"\tnodes: {g.vcount()} ; edges: {g.ecount()}")
  return g

#############################################################################
def GraphSummary(g):
  #igraph.summary(g,verbosity=0) ## verbosity=1 prints edge list!

  name = g['name'] if 'name' in g.attributes() else None
  logging.info(f"graph name: '%s'"%(name))
  logging.info(f"\t                 nodes: {g.vcount():3d}")
  logging.info(f"\t                 edges: {g.ecount():3d}")
  logging.info(f"\t             connected: {g.is_connected(mode=igraph.WEAK)}")
  logging.info(f"\t            components: {len(g.components(mode=igraph.WEAK)):3d}")
  logging.info(f"\t              directed: {g.is_directed()}")
  logging.info(f"\tDAG (directed-acyclic): {g.is_dag()}")
  logging.info(f"\t              weighted: {g.is_weighted()}")
  logging.info(f"\t              diameter: {g.diameter():3d}")
  logging.info(f"\t                radius: {g.radius():3d}")
  logging.info(f"\t             maxdegree: {g.maxdegree():3d}")

#############################################################################
def XOR(a,b): return ((a and not b) or (b and not a))

#############################################################################
def NodeSelect_String(g,selectfield,selectquery,exact,negate):
  vs=[]
  if exact:
    vs = eval(f"g.vs.select({selectfield}_{'ne' if negate else 'eq'} = '{selectquery}')")
  else:
    for v in g.vs:
      if XOR(re.search(selectquery, v[selectfield], re.I), negate):
        vs.append(v)
  return vs

#############################################################################
def ConnectedNodes(g):
  vs=[]
  for v in g.vs:
    #if g.neighbors(v, igraph.ALL):
    if v.degree()>0:
      vs.append(v)
  return vs

#############################################################################
def DisconnectedNodes(g):
  vs=[]
  for v in g.vs:
    #if not g.neighbors(v, igraph.ALL):
    if v.degree()==0:
      vs.append(v)
  return vs

#############################################################################
def RootNodes(g):
  '''In a directed graph, which are the root nodes?'''
  if not g.is_directed():
    logging.error('graph not directed; cannot have root nodes.')
  if not g.is_dag():
    logging.error('graph not directed-acyclic; cannot have proper root nodes.')
  vs=[]
  for v in g.vs:
    #if not g.neighbors(v, igraph.IN):
    #if g.indegree(v)==0:
    if v.indegree()==0:
      vs.append(v)
  return vs

#############################################################################
def AddChildren(vs, r, depth, ntype):
  if depth<=0: return
  for c in r.neighbors(ntype):
    vs.append(c)
    AddChildren(vs, c, depth-1, ntype)

#############################################################################
def TopNodes(g, depth):
  vs = []
  rs = RootNodes(g)
  vs.extend(rs)
  for r in rs:
    PrintHierarchy(r, depth, 0)
    AddChildren(vs, r, depth, igraph.OUT)
  return vs

#############################################################################
def PrintHierarchy(n, depth, i):
  if i>depth: return
  logging.info("{}{}: {}".format('\t'*i, n['id'], n['name']))
  for c in n.neighbors(igraph.OUT):
    PrintHierarchy(c, depth, i+1)

#############################################################################
def DegreeDistribution(g):
  dd = g.degree_distribution(bin_width=1, mode=igraph.ALL, loops=True)
  logging.info(f"{dd}")

#############################################################################
def ShortestPath(g, nidA, nidB):
  '''Must use GraphBase (not Graph) method to get path data.'''

  vA = g.vs.find(id = nidA)
  vB = g.vs.find(id = nidB)
  paths = g.get_shortest_paths(vA, [vB], weights=None, mode=igraph.ALL, output="vpath")

  for path in paths:
    logging.debug(f"path = {str(path)}")
    n_v=len(path)
    for j in range(n_v):
      vid=path[j]
      v = g.vs[vid]
      dr=None
      if j+1<n_v:
        vid_next = path[j+1]
        edge = g.es.find(_between = ([vid], [vid_next]))
        dr = 'FROM' if edge.source==vid else 'TO'
        logging.debug(f"edge: {g.vs[edge.source]['doid']} {dr} {g.vs[edge.target]['doid']}")
      logging.debug(f"{j+1}. {v['doid']} ({v['name']}){dr}")
    vid_pa = PathRoot(g,path)
    logging.debug(f"path ancestor: {g.vs[vid_pa]['doid']}")

#############################################################################
def PathRoot(g, path):
  '''Given a DAG path (NIDs), return NID for root, i.e. node with no target.'''
  n_v=len(path)
  for j in range(n_v):
    vid=path[j]
    if j+1<n_v:
      vid_next = path[j+1]
      edge = g.es.find(_between = ([vid], [vid_next]))
      if edge.source==vid:
        return vid
    else:
      return vid
  return None

#############################################################################
def GetAncestors(g,vidxA):
  vA = g.vs[vidxA]
  vidxAncestors = {}
  for p in vA.neighbors(igraph.IN):
    vidxAncestors[p.index] = True
    vidxAncestors.update(GetAncestors(g,p.index))
  return vidxAncestors

#############################################################################
def ShowAncestry(g,vidxA,level):
  vA = g.vs[vidxA]
  logging.info(f"{level if level else '':>2} {'^'*level:>6} [{vA.index:>6}] {vA['id']:-14} ({vA['name']})")
  for p in vA.neighbors(igraph.IN):
    ShowAncestry(g, p.index, level+1)

#############################################################################
### GraphBase.bfs():
### Returns tuple:
###     The vertex IDs visited (in order)
###     The start indices of the layers in the vertex list
###     The parent of every vertex in the BFS
#############################################################################
#def BreadthFirstSearchTest(g):
#  rs = igraph_utils.RootNodes(g)
#  if len(rs)>1:
#    logging.warning('multiple root nodes (%d) using one only.'%len(rs))
#  r = rs[0];
#  bfs = g.bfs(r.index, mode=igraph.OUT)
#  vids, start_idxs, prnts = bfs
#  logging.debug('len(vids) = %d; len(start_idxs) = %d; len(prnts) = %d'%(len(vids),len(start_idxs), len(prnts)))
#
#  logging.info('layers: %d'%(len(start_idxs)))
#  start_idx_prev=0;
#  for layer,start_idx in enumerate(start_idxs):
#    logging.info('layer = %d'%(layer))
#    for i in range(start_idx_prev,start_idx):
#      logging.info('\t%d) vs[%d]: %s (%s); parent = %s (%s)'%(layer, vids[i],
#       g.vs[vids[i]]['id'], g.vs[vids[i]]['name'],
#       g.vs[prnts[vids[i]]]['id'], g.vs[prnts[vids[i]]]['name']))
#    start_idx_prev=start_idx

#############################################################################
def DisplayGraph(g,layout,w,h):
  '''Layouts:
 "rt"          : reingold tilford tree
 "rt_circular" : reingold tilford circular
 "fr"          : fruchterman reingold
 "lgl"         : large_graph
'''
  visual_style = {}
  #color_dict = {"m": "blue", "f": "pink"}
  #for v in g.vs:
  #  v["gender"] = random.choice(('m','f'))
  #for e in g.es:
  #  e["is_formal"] = random.choice(range(0,3))
  if layout=='kk':
    visual_style["layout"] = g.layout('kk')
  elif layout=='rt':
    visual_style["layout"] = g.layout('rt',3) #tree depth?
  else:
    visual_style["layout"] = g.layout('large')

  visual_style["bbox"] = (w, h)
  visual_style["vertex_label"] = g.vs["name"]
  visual_style["vertex_size"] = 25
  #visual_style["vertex_size"] = [25+random.choice(range(-10,10)) for v in g.vs]
  visual_style["vertex_color"] = "lightblue"
  #visual_style["vertex_color"] = [color_dict[gender] for gender in g.vs["gender"]]
  visual_style["vertex_shape"] = [random.choice(('rect','circle','rhombus')) for v in g.vs]
  #visual_style["edge_width"] = [1 + 2 * int(is_formal) for is_formal in g.es["is_formal"]]
  visual_style["edge_width"] = 2
  visual_style["margin"] = 20
  igraph.plot(g, **visual_style)

#############################################################################
def Graph2CyJsElements(g):
  '''Convert igraph object to CytoscapeJS-compatible JSON "elements".'''
  def merge_dicts(x,y):
    #return x.copy().update(y) #Python2
    return {**x, **y} #Python3
  nodes = []
  for v in g.vs:
    nodes.append({'data':merge_dicts({'id':v['id']}, v.attributes())})
  edges = []
  for e in g.es:
    v_source = g.vs[e.source]
    v_target = g.vs[e.target]
    edges.append({'data':merge_dicts({'source':v_source['id'], 'target':v_target['id']}, e.attributes())})
  for node in nodes:
    if 'class' in node['data']:
      node['classes'] = node['data']['class']
  CyGraph = nodes + edges
  CyGraphJS = json.dumps(CyGraph, indent=2, sort_keys=False)
  return CyGraphJS

#############################################################################
def VisualStyle(g):
  for v in g.vs:
    v["gender"] = random.choice(('m','f'))
  for e in g.es:
    e["is_formal"] = random.choice(range(0,3))
  visual_style = {}
  #visual_style["vertex_size"] = 25
  visual_style["vertex_size"] = [25+random.choice(range(-10,10)) for v in g.vs]
  color_dict = {"m": "blue", "f": "pink"}
  visual_style["vertex_color"] = [color_dict[gender] for gender in g.vs["gender"]]
  visual_style["vertex_shape"] = [random.choice(('rect','circle','rhombus')) for v in g.vs]
  visual_style["vertex_label"] = g.vs["name"]
  visual_style["edge_width"] = [1 + 2 * int(is_formal) for is_formal in g.es["is_formal"]]
  visual_style["bbox"] = (700, 500)
  visual_style["margin"] = 20

  return visual_style

#############################################################################
def Plot(g, ofile_plot):
  vstyle = VisualStyle(g)
  if ofile_plot:
    igraph.plot(g, ofile_plot, **vstyle)
  else:
    igraph.plot(g, **vstyle) #interactive

#############################################################################
def Layout(g, method):
  if method=='kamada_kawai':
    visual_style["layout"] = g.layout("kk")
  elif method=='reingold_tilford':
    visual_style["layout"] = g.layout("rt",2)
  elif method=='reingold_tilford_circular':
    visual_style["layout"] = g.layout("rt_circular")
  elif method=='fruchterman_reingold':
    visual_style["layout"] = g.layout("fr")
  elif method=='large_graph':
    visual_style["layout"] = g.layout("lgl")

#############################################################################
if __name__=='__main__':
  PROG=os.path.basename(sys.argv[0])
  DEPTH=1;
  epilog='''\
operations:
        --summary ................... summary of graph
        --degree_distribution ....... degree distribution
        --node_select ............... select for nodes by criteria
        --edge_select ............... select for edges by criteria
	--connectednodes ............ connected node[s]
	--disconnectednodes ......... disconnected node[s]
	--rootnodes ................. root node[s] of DAG
	--topnodes .................. root node[s] & children of DAG
	--shortest_paths ............ shortest paths, nodes A ~ B
	--show_ancestry ............. show ancestry, node A
	--graph2cyjs ................ CytoscapeJS JSON

Note: select also deletes non-matching for modified output.

'''
  parser = argparse.ArgumentParser(description='IGraph (python-igraph API) utility, graph processingand display')
  ops = ['summary',
	'degree_distribution',
	'rootnodes',
	'topnodes',
  	'graph2cyjs',
	'shortest_path',
	'show_ancestry',
	'connectednodes',
	'disconnectednodes',
	'node_select',
	'edge_select' ]
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
  parser.add_argument("--display", help="display graph interactively")
  parser.add_argument("--depth", type=int, default=DEPTH, help="depth for --topnodes")
  parser.add_argument("--nidA", help="nodeA ID")
  parser.add_argument("--nidB", help="nodeB ID")
  parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>0 else logging.ERROR if args.quiet else 15))

  fin = open(args.ifile)

  fout = open(args.ofile,"w+") if args.ofile else sys.stdout

  ###
  #INPUT:
  ###
  g = Load_GraphML(args.ifile)

  vs = []; #vertices for subgraph selection

  if args.op=='summary':
    GraphSummary(g)

  elif args.op=='degree_distribution':
    DegreeDistribution(g)

  elif args.op=='node_select':
    if args.selectquery:
      vs = NodeSelect_String(g, args.selectfield, args.selectquery, args.select_exact, args.select_negate)
    elif args.selectval:
      parser.error('numerical select not implemented yet.')
    else:
      parser.error('select query or value required.')

  elif args.op=='edge_select':
    parser.error('not implemented yet.')

  elif args.op=='connectednodes':
    vs = ConnectedNodes(g)

  elif args.op=='disconnectednodes':
    vs = DisconnectedNodes(g)

  elif args.op=='rootnodes':
    vs = RootNodes(g)

  elif args.op=='topnodes':
    vs = TopNodes(g, args.depth)

  elif args.op=='shortest_path':
    if not ( args.nidA and  args.nidB): parser.error('--shortest_path requires nidA and nidB.')
    vs = ShortestPath(g, args.nidA, args.nidB)

  elif args.op=='show_ancestry':
    if not nidA: parser.error('--show_ancestry requires nidA.')
    vA = g.vs.find(id =  args.nidA)
    vidxA = vA.index
    ShowAncestry(g, vidxA, 0)

  elif args.op=='graph2cyjs':
    print(Graph2CyJsElements(g))

  if vs:
    #for v in vs:
    #  logging.debug(f"{v['id']}: {v['name']}")
    logging.info(f"selected nodes: {len(vs)}")
    g = g.induced_subgraph(vs, implementation="auto")
    logging.info(f"SELECTED SUBGRAPH:  nodes: {g.vcount()} ; edges: {g.ecount()}")

  ###
  #OUTPUT:
  ###
  if args.ofile:
    g.write_graphml(fout) #Works but maybe changes tags?
    fout.close()

  elif display:
    w,h = 700,500
    layout = 'rt'
    DisplayGraph(g, layout, w, h)

