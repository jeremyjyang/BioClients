#!/usr/bin/env python3
#############################################################################
### Compute information content (IC) for nodes in a directed acyclic graph
### (DAG).
### For each node, information content (IC) depends on total number of
### descendants ndes, +1 for self.  Then IC is -log10((ndes+1)/n_total).
### Given this we can identify the most informative common ancestor
### (MICA), and the semantic similarity between any two nodes/terms.
### Note that this is a kind of "Platonic" IC; in contrast, a set of
### annotated disease instances could have a sampled IC which depends
### on the frequency of each DO annotation.  In that scenario, an unused
### disease has no effect on the sampled IC.
#############################################################################
### Used for Disease Ontology, as converted to GraphML with obo2csv.py and 
### Go_do_graph_analysis.sh.
#############################################################################
import sys,os,argparse,logging
import igraph,numpy

from .. import igraph as igraph_utils

sys.setrecursionlimit(sys.getrecursionlimit()*2)

#############################################################################
def ComputeInfoContent(g):
  rs = igraph_utils.RootNodes(g)
  if len(rs)>1:
    logging.warning('multiple root nodes (%d) using one only.'%len(rs))
  r = rs[0];
  ridx = r.index
  g.vs["ndes"] = [0 for i in range(len(g.vs))]
  g.vs["ic"] = [0.0 for i in range(len(g.vs))]
  NDescendants(g, ridx, 0)
  for v in g.vs:
    v["ic"] = -numpy.log10(min(float((v["ndes"]+1)/r["ndes"]),1.0))
    v["ic"] = numpy.abs(v["ic"])

#############################################################################
def NDescendants(g, vidx, level):
  '''Recursive by depth first search.  Since DAG may not be a tree, need
to avoid multiple counts via alternate parents.'''
  dvidxs = set() #descendant vidxs
  for vidx_ in g.neighbors(vidx, mode=igraph.OUT):
    dvidxs.add(vidx_)
    dvidxs_this = NDescendants(g, vidx_, level+1)
    dvidxs |= dvidxs_this
    g.vs[vidx_]["ndes"] = len(dvidxs_this)
  ndes=len(dvidxs) #number of descendants of vidx
  logging.debug('%s%d) vs[%d]: %s (%s); ndes = %d'%((level*'>'),level, vidx, g.vs[vidx]['id'], g.vs[vidx]['name'],ndes))
  g.vs[vidx]["ndes"] = ndes
  return dvidxs

#############################################################################
def FindMICA(g, vidxA, vidxB, vidxFrom=None):
  '''Start with root node as default MICA.  Self may be MICA.  If not, test children. 
Accumulate MICA list.  Recurse.'''
  if vidxA==vidxB: return vidxA
  if not vidxFrom:
    r = igraph_utils.RootNodes(g)[0] #should be only one
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
    vidxAAncestors = igraph_utils.GetAncestors(g, vidxA)
    vidxBAncestors = igraph_utils.GetAncestors(g, vidxB)
  except Exception as e:
    logging.error('(aack!): "%s"'%str(e))
    raise
  except:
    logging.error('(aack!): ?')
    raise

  if not (vidxFrom==vidxA or (vidxFrom in vidxAAncestors)):
    logging.error('(aack!): vidxFrom not in vidxAAncestors.')
    logging.debug('vFrom: [%d] %s (%s)'%(vidxFrom,vFrom['doid'], vFrom['name']))
    logging.debug('vidxAAncestors: %s'%(str(vidxAAncestors)))
    return None
  if not (vidxFrom==vidxB or (vidxFrom in vidxBAncestors)):
    logging.error('(aack!): vidxFrom not in vidxBAncestors.')
    logging.debug('vFrom: [%d] %s (%s)'%(vidxFrom,vFrom['doid'], vFrom['name']))
    logging.debug('vidxBAncestors: %s'%(str(vidxBAncestors)))
    return None

  if vidxA==vidxFrom or vidxB==vidxFrom: return vidxFrom

  micas = [] #list of tuples (vidx, ic)
  micas.append((vidxFrom,vFrom['ic']))

  vidxFrom_children = list(g.neighbors(vidxFrom, mode=igraph.OUT))
  for vidxFrom_child in vidxFrom_children:
    if (vidxFrom_child in vidxAAncestors) and (vidxFrom_child in vidxBAncestors):
      vidx_ = FindMICA(g, vidxA, vidxB, vidxFrom_child)
      if vidx_:
        v_ = g.vs[vidx_]
        micas.append((vidx_,v_['ic']))

  if not micas:
    logging.error('(aack!): no MICAs found.')
    return None

  micas = sorted(micas, key=lambda x: -x[1]) #on 2nd field, descending
  return micas[0][0]


#############################################################################
def SimMatrixNodelist(g, fout):
  fout.write("vidx,doid\n")
  vidxs = [v.index for v in g.vs]
  vidxs.sort()
  for vidx in vidxs:
    v=g.vs[vidx]
    doid=v['doid']
    fout.write('%s,%s\n'%(vidx,doid))
  logging.info('n_node: %d'%len(vidxs))


#############################################################################
def SimMatrix(g, vidxA_query, skip, nmax, fout):
  '''For every node-node pair in DAG, find MICA and write IC (similarity).
If vidxA specified, compute one row only.'''
  fout.write("doidA,doidB,doidMICA,sim\n")
  vidxs = [v.index for v in g.vs]
  vidxs.sort()

  n_in=0; n_out=0; n_nonzero=0; n_err=0;
  for i in range(len(vidxs)):
    if skip and i<skip: continue
    if nmax and (i-skip)==nmax: break
    vidxA = vidxs[i]
    if vidxA_query and vidxA_query!=vidxA: continue
    vA=g.vs[vidxA]
    doidA=vA['doid']
    logging.debug('vA: [%d] %s (%s)'%(vidxA,vA['doid'], vA['name']))
    n_nonzero_this=0
    n_in_this=0;
    for j in range(i+1,len(vidxs)):
      n_in+=1
      n_in_this+=1
      vidxB = vidxs[j]
      vB=g.vs[vidxB]
      doidB=vB['doid']
      logging.debug('vB: [%d] %s (%s)'%(vidxB,vB['doid'], vB['name']))
      try:
        vidxMICA = FindMICA(g, vidxA, vidxB, None)
      except Exception as e:
        logging.error('(aack!): "%s"'%str(e))
        vidxMICA = None
        pass
      if vidxMICA is None: #zero possible so use None
        logging.error('vA: [%d] %s (%s)'%(vidxA,vA['doid'], vA['name']))
        logging.error('vB: [%d] %s (%s)'%(vidxB,vB['doid'], vB['name']))
        n_err+=1
        continue
      vMICA=g.vs[vidxMICA]
      doidMICA=vMICA['doid']
      ic=vMICA['ic']
      if ic>0.0:
        n_nonzero_this+=1
        fout.write('%s,%s,%s,%.4f\n'%(
		doidA.replace('DOID:',''),
		doidB.replace('DOID:',''),
		doidMICA.replace('DOID:',''),
		ic))
        fout.flush()
        n_out+=1
      if (n_in%1e5)==0: logging.info('n_in: %d ; n_out: %d ; n_nonzero: %d (%.1f%%)'%(n_in, n_out, n_nonzero, 100.0*n_nonzero/n_in))
    n_nonzero+=n_nonzero_this
    logging.debug('vA: [%d] %s (%s); n_nonzero_this = %d/%d ; total n_nonzero = %d/%d (%.1f%%)'%(vidxA,vA['doid'], vA['name'],n_nonzero_this, n_in_this, n_nonzero, n_in, 100.0*n_nonzero/n_in))
  logging.info('Total n_in: %d ; n_out: %d ; n_nonzero: %d (%.1f%%)'%(n_in, n_out, n_nonzero, 100*n_nonzero/n_in))
  logging.info('Total n_err: %d'%(n_err))

#############################################################################
def test(g, nidA, nidB):
  vA = g.vs.find(id = nidA)
  vB = g.vs.find(id = nidB)
  logging.info('\tvA: [%d] %s (%s)'%(vA.index,vA['doid'], vA['name']))
  logging.info('\tvB: [%d] %s (%s)'%(vB.index,vB['doid'], vB['name']))
  vidx_mica = FindMICA(g, vA.index, vB.index, None)
  v = g.vs[vidx_mica]
  logging.info('MICA: [%d] %s (%s); IC = %f'%(vidx_mica,v['doid'], v['name'],v['ic']))

#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(
	description='''
Info content (IC) and most informative common ancestor (MICA)
for directed acyclic graph (DAG)
''',
	epilog='''
simMatrixNodelist outputs vertex indices with node IDs.
simMatrix with --nidA to compute one row.
''')
  ops = ['computeIC', 'findMICA', 'simMatrix', 'simMatrixNodelist', 'test']
  parser.add_argument("op", choices=ops, help='OPERATION')

  parser.add_argument("--i", dest="ifile", required=True, help="input graph (GraphML)")
  parser.add_argument("--o", dest="ofile", help="output graph (GraphML)")
  parser.add_argument("--nidA", help="nodeA ID")
  parser.add_argument("--nidB", help="nodeB ID")
  parser.add_argument("--nmax", type=int)
  parser.add_argument("--skip", type=int)
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  fout = open(args.ofile,"w") if args.ofile else sys.stdout

  if not fout:
    parser.error('ERROR: cannot open outfile: %s'%args.ofile)
    parser.print_help()

  g = igraph_utils.LoadGraph(args.ifile, 'graphml')

  igraph_utils.GraphSummary(g)

  if not g.is_dag():
    parser.error('Input graph not DAG.')
    parser.print_help()

  if args.op == 'computeIC':
    ComputeInfoContent(g)
    if args.ofile:
      igraph_utils.SaveGraph(g,"graphml",fout)

  elif args.op == 'findMICA':
    if not (args.nidA and args.nidB):
      parser.error('findMICA requires --nidA and --nidB.')
      parser.print_help()
    vA = g.vs.find(id = args.nidA)
    vB = g.vs.find(id = args.nidB)
    logging.debug('\tvA: [%d] %s (%s)'%(vA.index,vA['doid'], vA['name']))
    logging.debug('\tvB: [%d] %s (%s)'%(vB.index,vB['doid'], vB['name']))
    vidx_mica = FindMICA(g, vA.index, vB.index, None)
    v = g.vs[vidx_mica]
    logging.info('MICA: [%d] %s (%s); IC = %f'%(vidx_mica,v['doid'], v['name'],v['ic']))

  elif args.op == 'test':
    #if not (args.nidA and args.nidB):
    #  parser.error('test requires --nidA and --nidB.')
    #  parser.print_help()
    import cProfile
    #cProfile.run('test(g,"%s","%s")'%(args.nidA,args.nidB))
    cProfile.run('SimMatrix(g, 0, 1, fout)')
    #cProfile.runctx('test(g,"%s","%s")'%(args.nidA,args.nidB), globals(), locals())

  elif args.op == 'simMatrix':
    vidxA = g.vs.find(id = args.nidA).index if args.nidA else None
    SimMatrix(g, vidxA, args.skip, args.nmax, fout)

  elif args.op == 'simMatrixNodelist':
    SimMatrixNodelist(g, fout)

  else:
    parser.error('No operation specified.')
    parser.print_help()

  if args.ofile:
    fout.close()


#############################################################################
# def FindMICA_try1(g, vidxAs, vidxB):
#   '''MICA = Max Info Content Ancestor.  From vA (any in list) consider self, then
# search parents till a parent of vB.
# BUGGY!    NOT COMMUTATIVE.
# --nidA DOID:0050624 --nidB DOID:5467
# 	!=
# --nidB DOID:0050624 --nidA DOID:5467
# '''
#   r = igraph_utils.RootNodes(g)[0] #should be only one
#   vB = g.vs[vidxB]
#   logging.debug('\tvB_this: [%d] %s (%s)'%(vidxB,vB['doid'], vB['name']))
#   if not vidxAs:
#     return None
#   micas = [] #list of tuples (vidx, ic)
#   vidxAs_grandparents = []
#   for vidxA in vidxAs:
#     if vidxA==vidxB: return vidxA
#     vA = g.vs[vidxA]
#     logging.debug('\tvA_this: [%d] %s (%s)'%(vidxA,vA['doid'], vA['name']))
#     paths = g.get_shortest_paths(vA, [vB], weights=None, mode=igraph.OUT, output="vpath")
#     if paths and len(paths[0])>0:
#       logging.debug('\tcommon ancestor: [%d] %s (%s); IC = %f'%(vidxA,vA['doid'], vA['name'],vA['ic']))
#       for path in paths:
#         for j,vidx_ in enumerate(path):
#           v_ = g.vs[vidx_]
#           logging.debug('\t %d. [%d] %s (%s)'%(j+1,vidx_,v_['doid'],v_['name']))
#       micas.append((vidxA,vA['ic']))
#     if micas:
#       break
# 
#     vidxA_parents = list(g.neighbors(vidxA, mode=igraph.IN))
#     for vidxA_parent in vidxA_parents:
#       vidxAs_grandparents.extend(list(g.neighbors(vidxA_parent, mode=igraph.IN)))
#       vp = g.vs[vidxA_parent]
#       paths = g.get_shortest_paths(vp, [vB], weights=None, mode=igraph.OUT, output="vpath")
#       if vidxA_parent==vidxB or (paths and len(paths[0])>0):
#         logging.debug('\tcommon ancestor: [%d] %s (%s); IC = %f'%(vidxA_parent,vp['doid'], vp['name'],vp['ic']))
#         for path in paths:
#           for j,vidx_ in enumerate(path):
#             v_ = g.vs[vidx_]
#             logging.debug('\t %d. [%d] %s (%s)'%(j+1,vidx_,v_['doid'],v_['name']))
#         micas.append((vidxA_parent,vp['ic']))
# 
#   #If no parents common ancestors, one generation higher.
#   #If no grandparents, return root node.
#   if not micas:
#     if not vidxAs_grandparents:
#       return r.index
#     else:
#       return FindMICA_try1(g, vidxAs_grandparents, vidxB)
# 
#   micas = sorted(micas, key=lambda x: -x[1]) #on 2nd field, descending
#   #logging.info('DEBUG: \t micas=%s'%str(micas))
#   return (micas[0][0] if micas else None)
