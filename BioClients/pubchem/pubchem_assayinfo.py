#!/usr/bin/env python
#############################################################################
### pubchem_assayinfo.py - From PubChem PUG REST API
### 
### Input: AIDs
### Output: AID,Name,Source
###
### ref: http://pubchem.ncbi.nlm.nih.gov/pug_rest/
#############################################################################
import os,sys,re,getopt,time
import csv,urllib2

from .. import pubchem

#############################################################################
def main():
  global PROG
  PROG=os.path.basename(sys.argv[0])

  usage='''
  %(PROG)s - fetch assay info from AIDs (PUG REST client)
  required:
  --i=<infile> ........ input AIDs file
  --o=<outfile> ....... output data file (CSV)

  options:
  --nmax=<N> .......... maximum N IDs
  --skip=<N> .......... skip N IDs
  --v ................. verbose
  --vv ................ very verbose
  --h ................. this help
'''%{'PROG':PROG}


  def ErrorExit(msg):
    print >>sys.stderr,msg
    sys.exit(1)

  ifile=None; ofile=None; verbose=0; nskip=0; nmax=0;
  format=None; gzip=False; 
  opts,pargs = getopt.getopt(sys.argv[1:],'',['h','v','vv','i=',
	'o=','out=','skip=','nmax=','n='])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--h': ErrorExit(usage)
    elif opt=='--i': ifile=val
    elif opt=='--o': ofile=val
    elif opt=='--nmax': nmax=int(val)
    elif opt=='--skip': nskip=int(val)
    elif opt=='--v': verbose=1
    elif opt=='--vv': verbose=2
    else: ErrorExit('Illegal option: %s'%val)

  if not (ifile and ofile):
    ErrorExit('input and output files required\n'+usage)

  fids=file(ifile)
  if not fids:
    ErrorExit('cannot open: %s\n%s'%(ifile,usage))
  fout=file(ofile,'w')
  if not fout:
    ErrorExit('cannot open: %s\n%s'%(ofile,usage))

  print >>sys.stderr, time.asctime()

  t0=time.time()

  ### For each AID, query using URI like:
  ### http://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/1001/description/XML


  n_id=0; 
  n_id_notfound=0
  http_errs={};
  while True:
    line=fids.readline()
    if not line: break
    n_id+=1
    if nskip and n_id<=nskip:
      continue
    if nmax and n>nmax: break
    line=line.rstrip()
    fields=line.split()
    if len(fields)<1:
      print >>sys.stderr, 'Warning: bad line; no ID [%d]: %s'%(n_id,line)
      continue
    aid=int(fields[0])

    name,source = '',''
    try:
      xmlstr = pubchem.Utils.Aid2DescriptionXML(aid,verbose)
      name,source = pubchem.Utils.AssayXML2NameAndSource(xmlstr)
    except urllib2.HTTPError,e:
      if verbose:
        print >>sys.stderr, 'ERROR: [%d] REST request failed; response code = %d'%(aid,e.code)
      if not http_errs.has_key(e.code):
        http_errs[e.code]=1
      else:
        http_errs[e.code]+=1
      n_id_notfound+=1
    except urllib2.URLError,e:
      print >>sys.stderr, 'ERROR: [%d] REST request failed; %s'%(aid,e)
      n_id_notfound+=1
    except Exception,e:
      print >>sys.stderr, 'ERROR: [%d] REST request failed; %s'%(aid,e)
      n_id_notfound+=1

    fout.write('%d,"%s","%s"\n'%(aid,name,source))

    if 0==(n_id%100):
      print >>sys.stderr, ("n_id = %d ; elapsed time: %s\t[%s]"%(n_id, (time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))), time.asctime()))
    if n_id==nmax:
      break

  fout.close()

  print >>sys.stderr, 'ids read: %d'%(n_id)
  print >>sys.stderr, 'ids found: %d'%(n_id-n_id_notfound)
  print >>sys.stderr, 'ids not found: %d'%(n_id_notfound)
  errcodes=http_errs.keys()
  errcodes.sort()
  for code in errcodes:
    print >>sys.stderr, 'count, http error code %d: %3d'%(code,http_errs[code])
  print >>sys.stderr, ("total elapsed time: %s"%( (time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0)))))
  print >>sys.stderr, time.asctime()

#############################################################################
if __name__=='__main__':
  #import cProfile
  #cProfile.run('main()')
  main()

