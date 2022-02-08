#!/usr/bin/env python3
"""
https://igraph.org/python/doc/tutorial/tutorial.html

Note that igraph defines its own IDs.  These are integers, not the same
as imported GraphML "id" values.

"""
#############################################################################
import sys,os,argparse,logging,tqdm
import re,random,tempfile,shutil,json
import numpy as np
import pandas as pd
import igraph

#############################################################################
def Load_GraphML(ifile):
  g = igraph.Graph.Read_GraphML(ifile)
  logging.info(f"nodes: {g.vcount()}; edges: {g.ecount()}")
  return g

#############################################################################
def Save_GraphML(g, fout):
  g.write_graphml(fout) #Works but maybe changes tags?

#############################################################################
def GraphSummary(g):
  #igraph.summary(g,verbosity=0) ## verbosity=1 prints edge list!
  name = g['name'] if 'name' in g.attributes() else None
  logging.info(f"graph name: '{name}'")
  logging.info(f"                 nodes: {g.vcount():3d}")
  logging.info(f"                 edges: {g.ecount():3d}")
  logging.info(f"             connected: {g.is_connected(mode=igraph.WEAK)}")
  logging.info(f"            components: {len(g.components(mode=igraph.WEAK)):3d}")
  logging.info(f"              directed: {g.is_directed()}")
  logging.info(f"DAG (directed-acyclic): {g.is_dag()}")
  logging.info(f"              weighted: {g.is_weighted()}")
  logging.info(f"              diameter: {g.diameter():3d}")
  logging.info(f"                radius: {g.radius():.3f}")
  logging.info(f"             maxdegree: {g.maxdegree():3d}")

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
  """In a directed graph, which are the root nodes?"""
  if not g.is_directed():
    logging.error("Graph not directed; cannot have root nodes.")
    return []
  elif not g.is_dag():
    logging.error("Graph not directed-acyclic; cannot have proper root nodes.")
    return []
  vs=[];
  for v in g.vs:
    #if not g.neighbors(v, igraph.IN):
    #if g.indegree(v)==0:
    if v.indegree()==0:
      vs.append(v)
  return vs

#############################################################################
def AddChildren(vs, r, depth=1):
  if depth<=0: return
  for c in r.neighbors(igraph.OUT):
    vs.append(c)
    AddChildren(vs, c, depth-1)

#############################################################################
def ChildCount(r, depth=1):
  if depth<=0: return 0
  count=0;
  for c in r.neighbors(igraph.OUT):
    count+=(1+ChildCount(c, depth-1))
  return count

#############################################################################
def AllChildCount(r):
  count=0;
  for c in r.neighbors(igraph.OUT):
    count+=(1+AllChildCount(c))
  return count

#############################################################################
def LeafChildCount(r):
  if len(r.neighbors(igraph.OUT))==0:
    count=1
  else:
    count=0;
    for c in r.neighbors(igraph.OUT):
      count+=LeafChildCount(c)
  return count

#############################################################################
def TopNodes(g, depth=1):
  """Return top node[s] of DAG to given depth from root[s]."""
  vs=[];
  rs = RootNodes(g)
  vs.extend(rs)
  for r in rs:
    Hierarchy(r, depth, 0)
    AddChildren(vs, r, depth)
  logging.info(f"Returned {len(rs)} root node[s] and hierarchy to depth {depth}")
  return vs

#############################################################################
def Hierarchy(n, depth, i):
  if i>depth: return
  indent = "".join([f" {ii}> " for ii in range(i+1)])
  n_child = ChildCount(n, 1)
  n_all = AllChildCount(n)
  n_leaf = LeafChildCount(n)
  logging.info(f"{indent}{n['id']:>12}: {n['name']} (child:{n_child}; all:{n_all}; leaf:{n_leaf})")
  for c in n.neighbors(igraph.OUT):
    Hierarchy(c, depth, i+1)

#############################################################################
def DegreeDistribution(g):
  dd = g.degree_distribution(bin_width=1, mode=igraph.ALL, loops=True)
  logging.info(f"{dd}")

#############################################################################
def ShortestPaths(g, nidA, nidB):
  """Must use GraphBase (not Graph) method to get path data."""
  vs=set();
  vA = g.vs.find(id = nidA)
  vB = g.vs.find(id = nidB)
  paths = g.get_shortest_paths(vA, [vB], weights=None, mode=igraph.ALL, output="vpath")
  for path in paths:
    logging.debug(f"path = {str(path)}")
    n_v=len(path)
    for j in range(n_v):
      vid=path[j]
      v = g.vs[vid]
      vs.add(v)
      dr=None
      if j+1<n_v:
        vid_next = path[j+1]
        edge = g.es.find(_between = ([vid], [vid_next]))
        dr = 'FROM' if edge.source==vid else 'TO'
        logging.debug(f"edge: {g.vs[edge.source]['doid']} {dr} {g.vs[edge.target]['doid']}")
      logging.debug(f"{j+1}. {v['doid']} ({v['name']}){dr}")
    vid_pa = PathRoot(g, path)
    logging.debug(f"path ancestor: {g.vs[vid_pa]['doid']}")
  return list(vs)

#############################################################################
def PathRoot(g, path):
  """Given a DAG path (NIDs), return NID for root, i.e. node with no target."""
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
#  rs = RootNodes(g)
#  if len(rs)>1:
#    logging.warning(f"multiple root nodes ({len(rs)}) using one only.")
#  r = rs[0];
#  bfs = g.bfs(r.index, mode=igraph.OUT)
#  vids, start_idxs, prnts = bfs
#  logging.debug(f"len(vids) = {len(vids)}; len(start_idxs) = {len(start_idxs)}; len(prnts) = {len(prnts)}')
#
#  logging.info(f"layers: {len(start_idxs)}")
#  start_idx_prev=0;
#  for layer,start_idx in enumerate(start_idxs):
#    logging.info(f"layer = {layer}")
#    for i in range(start_idx_prev,start_idx):
#      logging.info(f"\t{layer}) vs[{vids[i]}]: {g.vs[vids[i]]['id']} ({g.vs[vids[i]]['name']}); parent = {g.vs[prnts[vids[i]]]['id']} ({g.vs[prnts[vids[i]]]['name']})")
#    start_idx_prev=start_idx

#############################################################################
def InducedSubgraph(g, vs, implementation="auto"):
  for v in vs:
    logging.debug(f"{v['id']}: {v['name']}")
  logging.info(f"Selected nodes: {len(vs)}")
  g = g.induced_subgraph(vs, implementation=implementation)
  logging.info(f"SELECTED SUBGRAPH:  nodes: {g.vcount()}; edges: {g.ecount()}")
  return g

#############################################################################
def DisplayGraph(g,layout,w,h):
  """Layouts:
 "rt"          : reingold tilford tree
 "rt_circular" : reingold tilford circular
 "fr"          : fruchterman reingold
 "lgl"         : large_graph
"""
  visual_style = {}
  #color_dict = {"m": "blue", "f": "pink"}
  #for v in g.vs:
  #  v["gender"] = random.choice(('m', 'f'))
  #for e in g.es:
  #  e["is_formal"] = random.choice(range(0, 3))
  if layout=='kk':
    visual_style["layout"] = g.layout('kk')
  elif layout=='rt':
    visual_style["layout"] = g.layout('rt', 3) #tree depth?
  else:
    visual_style["layout"] = g.layout('large')

  visual_style["bbox"] = (w, h)
  visual_style["vertex_label"] = g.vs["name"]
  visual_style["vertex_size"] = 25
  #visual_style["vertex_size"] = [25+random.choice(range(-10, 10)) for v in g.vs]
  visual_style["vertex_color"] = "lightblue"
  #visual_style["vertex_color"] = [color_dict[gender] for gender in g.vs["gender"]]
  visual_style["vertex_shape"] = [random.choice(('rect', 'circle', 'rhombus')) for v in g.vs]
  #visual_style["edge_width"] = [1 + 2 * int(is_formal) for is_formal in g.es["is_formal"]]
  visual_style["edge_width"] = 2
  visual_style["margin"] = 20
  igraph.plot(g, **visual_style)

#############################################################################
def Graph2CyJsElements(g):
  """Convert igraph object to CytoscapeJS-compatible JSON "elements"."""
  def merge_dicts(x, y):
    return {**x, **y} #Python3
  nodes=[]; edges=[];
  for v in g.vs:
    nodes.append({'data':merge_dicts({'id':v['id']}, v.attributes())})
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
    v["gender"] = random.choice(('m', 'f'))
  for e in g.es:
    e["is_formal"] = random.choice(range(0, 3))
  visual_style = {}
  #visual_style["vertex_size"] = 25
  visual_style["vertex_size"] = [25+random.choice(range(-10, 10)) for v in g.vs]
  color_dict = {"m": "blue", "f": "pink"}
  visual_style["vertex_color"] = [color_dict[gender] for gender in g.vs["gender"]]
  visual_style["vertex_shape"] = [random.choice(('rect', 'circle', 'rhombus')) for v in g.vs]
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
def ComputeInfoContent(g):
  rs = RootNodes(g)
  if len(rs)>1:
    logging.warning(f"Multiple root nodes ({len(rs)}) using one only.")
  r = rs[0];
  ridx = r.index
  g.vs["ndes"] = [0 for i in range(len(g.vs))]
  g.vs["ic"] = [0.0 for i in range(len(g.vs))]
  NDescendants(g, ridx, 0)
  for v in g.vs:
    v["ic"] = -np.log10(min(float((v["ndes"]+1)/r["ndes"]), 1.0))
    v["ic"] = np.abs(v["ic"])

#############################################################################
def NDescendants(g, vidx, level):
  """Recursive by depth first search.  Since DAG may not be a tree, need
to avoid multiple counts via alternate parents."""
  dvidxs = set() #descendant vidxs
  for vidx_ in g.neighbors(vidx, mode=igraph.OUT):
    dvidxs.add(vidx_)
    dvidxs_this = NDescendants(g, vidx_, level+1)
    dvidxs |= dvidxs_this
    g.vs[vidx_]["ndes"] = len(dvidxs_this)
  ndes=len(dvidxs) #number of descendants of vidx
  logging.debug(f"{level*'>'}{level}) vs[{vidx}]: {g.vs[vidx]['id']} ({g.vs[vidx]['name']}); ndes = {ndes}")
  g.vs[vidx]["ndes"] = ndes
  return dvidxs

#############################################################################
def FindMICA(g, vidxA, vidxB, vidxFrom=None):
  """Start with root node as default MICA.  Self may be MICA.  If not, test children. 
Accumulate MICA list.  Recurse."""
  if vidxA==vidxB: return vidxA
  if not vidxFrom:
    r = RootNodes(g)[0] #should be only one
    vidxFrom = r.index
  vFrom = g.vs[vidxFrom] #provisional

  ##Short cut: If sole shared parent, is MICA:
  ##Also a kludge to avoid pathological recursion with DOID:265, DOID:268
  vidxA_parents = set(g.neighbors(vidxA, mode=igraph.IN))
  vidxB_parents = set(g.neighbors(vidxB, mode=igraph.IN))
  coparents = vidxA_parents & vidxB_parents
  if len(coparents)==1:
    vidxCop = list(coparents)[0]
    #logging.debug('returning coparent: %d'%(vidxCop))
    return vidxCop
  try:
    vidxAAncestors = GetAncestors(g, vidxA)
    vidxBAncestors = GetAncestors(g, vidxB)
  except Exception as e:
    logging.error(f"(Aack!): '{str(e)}'")
    raise
  if not (vidxFrom==vidxA or (vidxFrom in vidxAAncestors)):
    logging.error("(Aack!): vidxFrom not in vidxAAncestors.")
    logging.debug(f"vFrom: [{vidxFrom}] {vFrom['doid']} ({vFrom['name']})")
    logging.debug(f"vidxAAncestors: {str(vidxAAncestors)}")
    return None
  if not (vidxFrom==vidxB or (vidxFrom in vidxBAncestors)):
    logging.error("(Aack!): vidxFrom not in vidxBAncestors.")
    logging.debug(f"vFrom: [{vidxFrom}] {vFrom['doid']} ({vFrom['name']})")
    logging.debug(f"vidxBAncestors: {str(vidxBAncestors)}")
    return None
  if vidxA==vidxFrom or vidxB==vidxFrom: return vidxFrom
  micas = [] #list of tuples (vidx, ic)
  micas.append((vidxFrom, vFrom['ic']))
  vidxFrom_children = list(g.neighbors(vidxFrom, mode=igraph.OUT))
  for vidxFrom_child in vidxFrom_children:
    if (vidxFrom_child in vidxAAncestors) and (vidxFrom_child in vidxBAncestors):
      vidx_ = FindMICA(g, vidxA, vidxB, vidxFrom_child)
      if vidx_:
        v_ = g.vs[vidx_]
        micas.append((vidx_, v_['ic']))
  if not micas:
    logging.error('(Aack!): no MICAs found.')
    return None
  micas = sorted(micas, key=lambda x: -x[1]) #on 2nd field, descending
  return micas[0][0]

#############################################################################
def SimMatrixNodelist(g, fout):
  fout.write("vidx\tdoid\n")
  vidxs = [v.index for v in g.vs]
  vidxs.sort()
  for vidx in vidxs:
    v=g.vs[vidx]
    doid=v['doid']
    fout.write(f"{vidx}\t{doid}\n")
  logging.info(f"n_node: {len(vidxs)}")

#############################################################################
def SimMatrix(g, vidxA_query, skip, nmax, fout):
  """For every node-node pair in DAG, find MICA and write IC (similarity).
If vidxA specified, compute one row only."""
  fout.write("doidA\tdoidB\tdoidMICA\tsim\n")
  vidxs = [v.index for v in g.vs]
  vidxs.sort()
  n_in=0; n_out=0; n_nonzero=0; n_err=0;
  for i in range(len(vidxs)):
    if skip and i<skip: continue
    if nmax and (i-skip)==nmax: break
    vidxA = vidxs[i]
    if vidxA_query and vidxA_query!=vidxA: continue
    vA = g.vs[vidxA]
    doidA = vA['doid']
    logging.debug(f"vA: [{vidxA}] {vA['doid']} ({vA['name']})")
    n_nonzero_this=0
    n_in_this=0;
    for j in range(i+1, len(vidxs)):
      n_in+=1
      n_in_this+=1
      vidxB = vidxs[j]
      vB = g.vs[vidxB]
      doidB = vB['doid']
      logging.debug(f"vB: [{vidxB}] {vB['doid']} ({vB['name']})")
      try:
        vidxMICA = FindMICA(g, vidxA, vidxB, None)
      except Exception as e:
        logging.error(f"(Aack!): '{str(e)}'")
        vidxMICA = None
        pass
      if vidxMICA is None: #zero possible so use None
        logging.error(f"vA: [{vidxA}] {vA['doid']} ({vA['name']})")
        logging.error(f"vB: [{vidxB}] {vB['doid']} ({vB['name']})")
        n_err+=1
        continue
      vMICA = g.vs[vidxMICA]
      doidMICA = vMICA['doid']
      ic = vMICA['ic']
      if ic>0.0:
        n_nonzero_this+=1
        fout.write(f"{doidA.replace('DOID:','')}\t{doidB.replace('DOID:','')}\t{doidMICA.replace('DOID:','')}\t{ic:4f}\n")
        fout.flush()
        n_out+=1
      if (n_in%1e5)==0: logging.info(f"n_in: {n_in}; n_out: {n_out}; n_nonzero: {n_nonzero} ({100.0*n_nonzero/n_in:.1f}%%)")
    n_nonzero+=n_nonzero_this
    logging.debug(f"vA: [{vidxA}] {vA['doid']} ({vA['name']}); n_nonzero_this = {n_nonzero_this}/{n_in_this}; total n_nonzero = {n_nonzero}/{n_in} ({100.0*n_nonzero/n_in:.1f}%%)")
  logging.info(f"Total n_in: {n_in}; n_out: {n_out}; n_nonzero: {n_nonzero} ({100*n_nonzero/n_in:.1f}%%)")
  logging.info(f"Total n_err: {n_err}")
