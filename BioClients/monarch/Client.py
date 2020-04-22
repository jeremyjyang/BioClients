#!/usr/bin/env python
#############################################################################
### monarch_query.py - Monarch REST client 
### 
### https://monarchinitiative.org/page/services
### https://monarchinitiative.org/docs/files/api-js.html
### https://github.com/monarch-initiative/owlsim-v3
### https://github.com/monarch-initiative/monarch-analysis
### 
### /search	searches over ontology terms via OntoQuest
### /autocomplete	proxy for vocbaulary services autocomplete
### /disease	disease info or page
### /phenotype	phenotype info or page
### /simsearch	OwlSim search using search profile of ontology classes
#############################################################################
### https://monarchinitiative.org/disease/OMIM_127750.json
### https://monarchinitiative.org/phenotype/HP_0000003.json
### https://monarchinitiative.org/compare/OMIM:270400/NCBIGene:5156,OMIM:249000,OMIM:194050.json
### 
### We use OwlSim for semantic matching when comparing two entities (such as genes,
### diseases, or genotypes) with sets of attributes (phenotypes). URLs are of the form
### /compare/:x/:y.json
### where x can be either an entity or a list of phenotypes and y can be a list of
### entities and/or sets of phenotypes.
### This wraps a call to getGroupwiseSimilarity(x,y) in OwlSim. This works such that
### given a query id (such as a gene, genotype, disease), and one or more target
### identifiers, it will map each to it's respective phenotypes, and perform an OwlSim
### comparison of the query to each target. You are permitted to mix query and target
### types. For example, your query can be a disease, and the target(s) be a list of
### gene(s), disease(s), phenotype(s), and/or genotype(s). You can indicate to union the
### phenotypes of either the query or the target with a plus "+". Only one entity may be
### supplied for the query, whereas multiple target entities are allowed (delimited by a
### comma).  For details on owlsim, see http://owlsim.org
### 
### Paths:
### /compare/:id1/:id2
### /compare/:id1/:id2,id3,...idN
### /compare/:id1+:id2/:id3,:id4,...idN
### /compare/:id1/:id2+:id3,:id4,:id5+:id6,...,:idN
#############################################################################
### IC = Information Content
### LCS = Least Common Subsumers
### See OwlSim docs and pubs.
### https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3653101/
#############################################################################
### Jeremy Yang
###  2 Mar 2017
#############################################################################
import sys,os,re,getopt,time,types,codecs
import urllib,urllib2,httplib
import json
#
import time_utils
import rest_utils_py2 as rest_utils
import csv_utils
#
API_HOST='monarchinitiative.org'
BASE_PATH=''
API_BASE_URL='http://'+API_HOST+BASE_PATH
#
#
##############################################################################
def GetDisease(ids,base_url,fout,verbose):
  n_out=0;
  fout.write('id,name,definition,child_count,parent_count,meshid\n')
  for id in ids:
    try:
      rval=rest_utils.GetURL(base_url+'/disease/%s.json'%(id),parse_json=True,verbose=verbose)
    except urllib2.HTTPError, e:
      print >>sys.stderr, 'HTTP Error: %s'%(e)
      continue
    if not type(rval)==types.DictType:
      print >>sys.stderr, 'Error: %s'%(str(rval))
      continue

    #name = rval['name'] if rval.has_key('name') else ''
    #fout.write('"%s","%s","%s",%d,%d,"%s"\n'%(id,name,definition,len(children),len(parents),meshid))
    n_out+=1

    if verbose>1: print >>sys.stderr, (json.dumps(rval,indent=2,sort_keys=False))
  print >>sys.stderr, 'DOIDs in: %d ; records out: %d'%(len(ids),n_out)

##############################################################################
def GetPhenotype(ids,base_url,fout,verbose):
  return

##############################################################################
def GetGene(ids,base_url,fout,verbose):
  n_out=0;
  fout.write('gid,gsymb,species_id,species,iri,synonyms\n')
  for gid in ids:
    try:
      rval=rest_utils.GetURL(base_url+'/gene/%s.json'%(gid),parse_json=True,verbose=verbose)
    except urllib2.HTTPError, e:
      print >>sys.stderr, 'HTTP Error: %s'%(e)
      continue
    if not type(rval)==types.DictType:
      print >>sys.stderr, 'Error: %s'%(str(rval))
      continue

    gsymb = rval['label'] if rval.has_key('label') else ''
    iri = rval['iri'] if rval.has_key('iri') else ''
    taxon = rval['taxon'] if rval.has_key('taxon') else {}
    species_id = taxon['id'] if taxon.has_key('id') else ''
    species = taxon['label'] if taxon.has_key('label') else ''
    synonyms = rval['synonyms'] if rval.has_key('synonyms') else []
    fout.write('"%s","%s","%s","%s","%s","%s"\n'%(gid,gsymb,species_id,species,iri,(';'.join(synonyms))))
    n_out+=1

    if verbose>2: print >>sys.stderr, (json.dumps(rval,indent=2,sort_keys=False))
  print >>sys.stderr, 'GENEIDs in: %d ; records out: %d'%(len(ids),n_out)
  return

##############################################################################
### Guess: The matches each consist of a 3-tuple,
###	A = phenotype in profileA,
###	B = phenotype in profileB, and
###	LCS = Least Common Subsumers phenotype in...
### EPO?  (But we see MP, ZP, HP...)
##############################################################################
def Compare(idAs,idsB,base_url,fout,verbose):
  n_match=0;
  n_out=0;
  fout.write('idA,typeA,labelA,taxonA,idB,typeB,labelB,taxonB,url,matchidA,matchlabelA,matchidB,matchlabelB,matchidLCS,matchlabelLCS,matchicA,matchicB,matchicLCS\n')
  for idA in idAs:
    url_this=base_url+'/compare/%s/%s.json'%(idA,','.join(idsB))
    try:
      rval=rest_utils.GetURL(url_this,parse_json=True,verbose=verbose)
    except urllib2.HTTPError, e:
      print >>sys.stderr, 'HTTP Error: %s'%(e)
      continue
    if not type(rval)==types.DictType:
      print >>sys.stderr, 'Error: %s'%(str(rval))
      continue
    if verbose>2: print >>sys.stderr, (json.dumps(rval,indent=2,sort_keys=False))

    A = rval['a'] if rval.has_key('a') else {}
    typeA = A['type'] if A.has_key('type') else ''
    idAx = A['id'] if A.has_key('id') else ''
    labelA = A['label'] if A.has_key('label') else ''
    taxonA = A['taxon']['id'] if (A.has_key('taxon') and A['taxon'].has_key('id')) else {}
    if verbose>1:
      print >>sys.stderr, 'A[type]: "%s" ; A[id]: "%s" ; A[label]: "%s"'%(typeA,idA,labelA)

    resource = rval['resource'] if rval.has_key('resource') else {}
    for key in resource.keys():
      if verbose>1:
        print >>sys.stderr, 'resource[%s]: %s'%(key,resource[key])

    metadata = rval['metadata'] if rval.has_key('metadata') else {}
    for key in metadata.keys():
      if verbose>1:
        print >>sys.stderr, 'metadata[%s]: %s'%(key,str(metadata[key]))

    Bs = rval['b'] if rval.has_key('b') else []
    for B in Bs:
      labelB = B['label'] if B.has_key('label') else ''
      typeB = B['type'] if B.has_key('type') else ''
      idB = B['id'] if B.has_key('id') else ''
      print >>sys.stderr, 'B[type]: "%s" ; B[id]: "%s" ; B[label]: "%s"'%(typeB,idB,labelB)
      bscore = B['score'] if B.has_key('score') else {}
      taxonB = B['taxon']['id'] if (B.has_key('taxon') and B['taxon'].has_key('id')) else {}
      matches = B['matches'] if B.has_key('matches') else []
      vals_ab=[idA,typeA,labelA,taxonA,idB,typeB,labelB,taxonB,url_this]
      for m in matches:
        n_match+=1
        mA = m['a'] if m.has_key('a') else {}
        matchidA = mA['id'] if mA.has_key('id') else ''
        matchlabelA = mA['label'] if mA.has_key('label') else ''

        mB = m['b'] if m.has_key('b') else {}
        matchidB = mB['id'] if mB.has_key('id') else ''
        matchlabelB = mB['label'] if mB.has_key('label') else ''

        mLCS = m['lcs'] if m.has_key('lcs') else {}
        matchidLCS = mLCS['id'] if mLCS.has_key('id') else ''
        matchlabelLCS = mLCS['label'] if mLCS.has_key('label') else ''

        matchicA = mA['IC'] if mA.has_key('IC') else '' #same as LCS?
        matchicB = mB['IC'] if mB.has_key('IC') else '' #same as LCS?
        matchicLCS = mLCS['IC'] if mLCS.has_key('IC') else ''

        vals_this=vals_ab+[matchidA,matchlabelA,matchidB,matchlabelB,matchidLCS,matchlabelLCS,matchicA,matchicB,matchicLCS]
        fout.write(','.join([csv_utils.ToStringForCSV(val) for val in vals_this])+'\n')
        n_out+=1

  print >>sys.stderr, 'n_comparison = %d (%dx%d)'%(len(idAs)*len(idBs),len(idAs),len(idBs))
  print >>sys.stderr, 'n_match = %d'%n_match
  print >>sys.stderr, 'n_out = %d'%n_out


##############################################################################
if __name__=='__main__':
  PROG=os.path.basename(sys.argv[0])
  usage='''\
%(PROG)s - Monarch Initiative REST client

operations:
        --get_disease ............... 
        --get_phenotype ............. 
        --get_gene ............. 
        --compare ................... id vs idBs, OwlSim phenotype-based similarity

options:
        --id ID ..................... query ID
        --idBs IDBS ................. IDs to compare
        --idfile IDFILE ............. query file, IDs
        --o OFILE ................... output file (CSV)
        --api_host HOST ............. [%(API_HOST)s]
        --v[v[v]] ................... verbose [very [very]]
        --h ......................... this help

Entity: gene|disease|genotype

Examples:
OMIM:612528 (human disease)
HP:0005978 (human disease: T2DM)
DOID:1612 (human disease: breast cancer)
NCBIGene:7084 (human gene)
NCBIGene:5156 (human gene)
NCBIGene:3257 (human gene)
NCBIGene:26564 (mouse gene)

'''%{	'PROG':PROG,
	'API_HOST':API_HOST
	}

  def ErrorExit(msg):
    print >>sys.stderr,msg
    sys.exit(1)

  idA=None;
  idBs=[];
  ofile=None;
  idfile=None;
  compare=False; 
  get_disease=False; 
  get_phenotype=False; 
  get_gene=False; 
  list_topclasses=False; 
  verbose=0;
  opts,pargs=getopt.getopt(sys.argv[1:],'',['o=',
	'compare',
	'get_disease',
	'get_phenotype',
	'get_gene',
	'list_topclasses',
	'id=',
	'idBs=',
	'idfile=',
	'api_host=',
	'help','v','vv','vvv'])
  if not opts: ErrorExit(usage)
  for (opt,val) in opts:
    if opt=='--help': ErrorExit(usage)
    elif opt=='--compare': compare=True
    elif opt=='--get_disease': get_disease=True
    elif opt=='--get_phenotype': get_phenotype=True
    elif opt=='--get_gene': get_gene=True
    elif opt=='--list_topclasses': list_topclasses=True
    elif opt=='--o': ofile=val
    elif opt=='--id': idA=val
    elif opt=='--idBs': idBs=re.split(r'[,\s]',val.strip())
    elif opt=='--idfile': idfile=val
    elif opt=='--api_host': API_HOST=val
    elif opt=='--api_key': API_KEY=val
    elif opt=='--v': verbose=1
    elif opt=='--vv': verbose=2
    elif opt=='--vvv': verbose=3
    else: ErrorExit('Illegal option: %s\n%s'%(opt,usage))

  API_BASE_URL='http://'+API_HOST+BASE_PATH

  if ofile:
    fout=codecs.open(ofile,"w","utf8","replace")
    if not fout: ErrorExit('ERROR: cannot open outfile: %s'%ofile)
  else:
    fout=codecs.getwriter('utf8')(sys.stdout,errors="replace")

  t0=time.time()

  idAs=[];
  if idfile:
    fin=open(idfile)
    if not fin: ErrorExit('ERROR: cannot open idfile: %s'%idfile)
    while True:
      line=fin.readline()
      if not line: break
      try:
        idA=line.rstrip()
      except:
        print >>sys.stderr, 'ERROR: invalid DOID: "%s"'%(line.rstrip())
        continue
      if line.rstrip(): idAs.append(idA)
    if verbose:
      print >>sys.stderr, '%s: input queries: %d'%(PROG,len(idAs))
    fin.close()
  elif idA:
    idAs.append(idA)

  if get_disease:
    GetDisease(idAs,API_BASE_URL,fout,verbose)

  elif get_phenotype:
    print >>sys.stderr, 'DEBUG: NOT IMPLEMENTED YET!'
    exit
    GetPhenotype(idAs,API_BASE_URL,fout,verbose)

  elif get_gene:
    GetGene(idAs,API_BASE_URL,fout,verbose)

  elif compare:
    Compare(idAs,idBs,API_BASE_URL,fout,verbose)

  else:
    ErrorExit("No operation specified.")

  if ofile:
    fout.close()

  if verbose:
    print >>sys.stderr, ('%s: elapsed time: %s'%(PROG,time.strftime('%Hh:%Mm:%Ss',time.gmtime(time.time()-t0))))
