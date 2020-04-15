#!/usr/bin/env python
"""BROKEN! TO DO: Port to Python3. Preferrably avoid R and switch to Numpy, Scipy."""
#############################################################################
### Use R via RPy2 to calculate Gini Index using ineq package.
#############################################################################
# rpy2 prerequisites:
#    - Python 2.4+
#    - R v2.7+, built with ./configure --enable-R-shlib
#    - Set R_HOME for Apache
#############################################################################
import os,sys,getopt,math,csv

#import rpy2.robjects

#############################################################################
def GiniRCode(vals):
  xs=[]
  for x in vals:
    if x==None: continue
    xs.append('%.4e'%x)
  if not xs:
    return 'gini<-0.0\n'
  
  r_code='''\
vals<-c(%(SCORES)s)
library(ineq)
gini<-Gini(vals)
'''%{'SCORES':(','.join(xs))}

  return r_code

#############################################################################
def LorentzPlotRCode(vals,ifile):
  r_code='''\
library(ineq)
'''
  xs=[]
  for x in vals:
    if x==None: continue
    xs.append('%.4e'%x)
  r_code+='vals<-c(%s)\n'%(','.join(xs))
  r_code+='''\
gini<-Gini(vals)
Lc.p <- Lc(vals)

#postscript()
pdf('%(FILE)s')
#png()
#jpeg()
#X11()

plot(Lc.p, col=2,
  main=paste('Lorenz Curve\nGini Index:',gini),
  xlab=paste('(N =',%(N)d,')'),
  ylab="score")

dev.off()
#system("acroread \"%(FILE)s\"")
'''%{'FILE':ifile,'N':len(vals)}

  return r_code

#############################################################################
def GiniProcessor(vals):
  r_code=GiniRCode(vals)
  rpy2.robjects.r(r_code)
  try:
    gini=rpy2.robjects.r('gini')[0]
  except:
    gini = 0.0
    print >>sys.stderr, "Error: R failure"
  return gini

#############################################################################
def GiniInteractive(vals,ifile):
  r_code=LorentzPlotRCode(vals,ifile)
  print >>sys.stderr, "DEBUG:\n", r_code
  rpy2.robjects.r(r_code)
  try:
    gini=rpy2.robjects.r('gini')[0]
  except:
    gini = 0.0
    print >>sys.stderr, "Error: R failure"
  return gini

#############################################################################
def Lorenz_img(vals,ofile,title,format='PNG',height=1000,width=1200,
	iconic=False):
  xs=[]
  while None in vals: vals.remove(None)
  if min(vals)==0.0 and max(vals)==0.0:
    return 'gini<-0.0\n'
  for x in vals:
    xs.append('%.4e'%x)
  if not xs:
    return 'gini<-0.0\n'

  r_code='''\
vals<-c(%(SCORES)s)
library(ineq)
gini<-Gini(vals)
Lc.p <- Lc(vals)
'''%{'SCORES':(','.join(xs))}

  if format.upper()=='EPS':
    r_code+='''\
postscript("%(OUTFILE)s",horizontal=FALSE,onefile=FALSE,paper="special",
        height=5,width=7,family="Bookman")
'''%{'OUTFILE':ofile}
  else:
    r_code+='''\
png(filename="%(OUTFILE)s",height=%(H)d,width=%(W)d,units="px")
'''%{'OUTFILE':ofile,'H':height,'W':width}

  if iconic:
    r_code+='''\
#plot(Lc.p,col=2,lwd=4,main="",xlab="",ylab="")
plot(Lc.p,col=2,lwd=4,main="",xlab="",ylab="",
	mar=c(0,0,0,0),
	bty="o",
	tck=0,
	tcl=0,
	pty="m",
	cex=0,
	xaxt="n",
	yaxt="n")
'''
  else:
    r_code+='''\
plot(Lc.p,col=2,lwd=8,main="",xlab="",ylab="")
title(main=paste("%(TITLE)s",'\nLorenz curve'),
        xlab=paste("Lorenz curve","\nN = %(N)d","\ngini = ",gini),ylab="score")
'''%{'TITLE':title,'N':len(vals)}

  r_code+='dev.off()\n'

  rpy2.robjects.r(r_code)

  try:
    gini=rpy2.robjects.r('gini')[0]
  except:
    print >>sys.stderr, "Error: R failure"
    gini = 0.0
  return gini

#############################################################################
def CSVFile2Values(fin,tag,delim=',',verbose=0):
  vals=[]
  n_in=0; n_out=0;
  csvReader=csv.DictReader(fin,fieldnames=None,restkey=None,restval=None,dialect='excel',delimiter=delim,quotechar='"')

  while True:
    try:
      csvrow=csvReader.next()
      n_in+=1
    except Exception, e:
      if str(e)!='':
        print >>sys.stderr, 'Error (Exception): %s'%e
      break

    if n_in==1 and tag not in csvReader.fieldnames:
      print >>sys.stderr, ('ERROR: cannot find field "%s" in ifile.'%tag)
      return vals

    val=csvrow[tag]
    if val=='': continue

    try:
      val=float(val)
      vals.append(val)
      n_out+=1
    except Exception, e:
      print >>sys.stderr, 'Error (Exception): %s'%e

    #if n_out>100000: break

  if verbose:
    print >>sys.stderr, 'n_in: %d ; n_out: %d'%(n_in,len(vals))

  return vals

#############################################################################
def Gini(fin,tag,delim=',',verbose=0):

  vals = CSVFile2Values(fin,tag,delim,verbose)
  g = GiniProcessor(vals)
  print 'DEBUG: gini=%.3f'%g

#############################################################################
def Test():
  valses=[]
  valses.append([0.0,0.5,1.0,0.5,0.0,1.0,1.0,1.0])
  valses.append([0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0])
  valses.append([1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0])

  
  for vals in valses:

    gini=GiniProcessor(vals)
    print 'DEBUG: gini=%.3f'%gini

    #gini=GiniInteractive(vals,"z.pdf")
    #os.system("acroread z.pdf")


#############################################################################
def Help(msg=''):
  if msg: print msg
  print '''\
%(PROG)s
required (one of):
        --gini .................. Gini coefficient for given input file, CSV tag
        --test
options:
        --i IFILE ............... CSV
        --o OFILE ............... 
        --tag TAG ............... CSV tag
        --v ..................... verbose
        --h ..................... this help
'''%{'PROG':PROG}
  sys.exit()

#############################################################################
if __name__=='__main__':
  def ErrorExit(msg): print >>sys.stderr,msg ; sys.exit(1)

  PROG=os.path.basename(sys.argv[0])

  ifile=''; ofile='';
  test=False;
  gini=False;
  tag=''; delim='\t';
  verbose=0;

  opts,pargs=getopt.getopt(sys.argv[1:],'',[
    'i=',
    'o=',
    'test',
    'gini',
    'tag=',
    'delim=',
    'h=','help','v','vv'])
  if not opts: Help()
  for (opt,val) in opts:
    if opt=='--help': Help()
    elif opt=='--i': ifile=val
    elif opt=='--o': ofile=val
    elif opt=='--test': test=True
    elif opt=='--gini': gini=True
    elif opt=='--tag': tag=val
    elif opt=='--delim': delim=val
    elif opt=='--v': verbose=1
    elif opt=='--vv': verbose=2
    else: Help('Illegal option: %s'%(opt))

  if ofile:
    fout=open(ofile,'w+')
    if not fout:
      ErrorExit('Could not open output file: %s'%ofile)
  else:
    fout=sys.stdout

  if ifile:
    fin=open(ifile)
    if not fin:
      ErrorExit('Could not open input file: %s'%ifile)

  if test:
    Test()
  elif gini:
    Gini(fin,tag,delim,verbose)
  else:
    ErrorExit('No action specified.')

  if ofile:
    fout.close()
