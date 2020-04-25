#!/usr/bin/python
### #!/usr/bin/env python	## on cheminfov, python2.4 has pgdb ; python 2.6 does not, alas.
'''
	Chem2Bio2RDF query utility.

	All relevant tables assumed to have substring "c2b2r_".

	Jeremy Yang
	 4 Nov 2013
'''
import os,sys,getopt,re,time
import pgdb

import c2b2r_utils

PROG=os.path.basename(sys.argv[0])

DBSCHEMA='public'
#DBHOST='localhost'
DBHOST='cheminfov.informatics.indiana.edu'
DBNAME='chord'
DBUSR='cicc3'
DBPW=None

#############################################################################
if __name__=='__main__':

  usage='''
  %(PROG)s - 
operations (one of):
  --schema .................... describe schema, contents
  --schema_with SUBSTR ........ describe tables w/ SUBSTR in name
  --list_targets .............. list all protein targets
  --list_genes ................ list all genes
  --tablecounts ............... table row counts
  --get_target ................ get targets for TID[s]
  --get_compound .............. get compounds for CID[s]

parameters:
  --tidfile TIDFILE ...........
  --tid TID ...................
  --cidfile CIDFILE ...........
  --cid CID ...................

options:
  --o OFILE ................... output file (CSV)
  --v ......................... verbose
  --h ......................... this help

schema: %(DBSCHEMA)s
'''%{'PROG':PROG,'DBSCHEMA':DBSCHEMA}

  def ErrorExit(msg):
    print >>sys.stderr,msg
    sys.exit(1)

  verbose=0;
  schema=False;
  schema_with=False;
  tablecounts=False;
  get_target=False;
  list_targets=False;
  list_genes=False;
  tid=''; tidfile=''; tid_skip=0; tid_nmax=0;
  cid=''; cidfile=''; cid_skip=0; cid_nmax=0;
  ofile=None;
  opts,pargs = getopt.getopt(sys.argv[1:],'',['h','v','vv','o=',
  'tid=', 'tidfile=', 'tid_skip=', 'tid_nmax=',
  'cid=', 'cidfile=', 'cid_skip=', 'cid_nmax=',
  'get_target',
  'get_compound',
  'list_targets',
  'list_genes',
  'schema',
  'schema_with=',
  'tablecounts'])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--h': ErrorExit(usage)
    elif opt=='--tid': tid=int(val)
    elif opt=='--tidfile': tidfile=val
    elif opt=='--tid_skip': tid_skip=int(val)
    elif opt=='--tid_nmax': tid_nmax=int(val)
    elif opt=='--cid': cid=int(val)
    elif opt=='--cidfile': cidfile=val
    elif opt=='--cid_skip': cid_skip=int(val)
    elif opt=='--cid_nmax': cid_nmax=int(val)
    elif opt=='--o': ofile=val
    elif opt=='--get_target': get_target=True
    elif opt=='--get_compound': get_compound=True
    elif opt=='--list_targets': list_targets=True
    elif opt=='--list_genes': list_genes=True
    elif opt=='--tablecounts': tablecounts=True
    elif opt=='--schema': schema=True
    elif opt=='--schema_with': schema_with=val
    elif opt=='--vv': verbose=2
    elif opt=='--v': verbose=1
    else: ErrorExit('Illegal option: %s'%val)

  tids=[]
  if tidfile:
    fin=open(tidfile)
    if not fin: ErrorExit('ERROR: failed to open input file: %s'%tidfile)
    while True:
      line=fin.readline()
      if not line: break
      tids.append(line.strip())
  elif tid:
    tids=[tid]

  cids=[]
  if cidfile:
    fin=open(cidfile)
    if not fin: ErrorExit('ERROR: failed to open input file: %s'%cidfile)
    while True:
      line=fin.readline()
      if not line: break
      cids.append(int(line.strip()))
  elif cid:
    cids=[cid]

  if ofile:
    fout=open(ofile,"w+")
    if not fout: ErrorExit('ERROR: failed to open output file: %s'%ofile)
  else:
    fout=sys.stdout

  t0=time.time()

  db = c2b2r_utils.Connect(dbhost=DBHOST,dbname=DBNAME,dbusr=DBUSR,dbpw=DBPW)[0]

  if verbose:
    if db: print >>sys.stderr, "DB connect ok: %s @ %s : %s"%(DBUSR,DBHOST,DBNAME)

  t0=time.time()

  if schema:
    c2b2r_utils.DescribeSchema(None,DBSCHEMA,db)

  elif schema_with:
    c2b2r_utils.DescribeSchema(schema_with,DBSCHEMA,db)

  elif tablecounts:
    c2b2r_utils.DescribeCounts(DBSCHEMA,db)

  elif get_target:
    c2b2r_utils.GetTarget(tids,fout,DBSCHEMA,db)

  elif list_targets:
    c2b2r_utils.ListTargets(fout,DBSCHEMA,db)

  elif list_genes:
    c2b2r_utils.ListGenes(fout,DBSCHEMA,db)

  elif get_compound:
    fout.write('"cid","synonyms","isosmi"\n')
    n_found=0
    for cid in cids:
      ok=c2b2r_utils.GetCompound(cid,fout,DBSCHEMA,db)
      if ok: n_found+=1
      else: print >>sys.stderr, '%s: CID %d not found'%(PROG,cid)
    fout.close()
    print >>sys.stderr, '%s: %d / %d found'%(PROG,n_found,len(cids))

  else:
    ErrorExit('ERROR: No operation specified.')

  db.close()

  if verbose:
    print >>sys.stderr, "%s: elapsed time: %s"%(PROG,c2b2r_utils.NiceTime(time.time()-t0))
