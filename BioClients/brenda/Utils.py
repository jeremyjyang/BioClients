#!/usr/bin/env python3
#############################################################################
### TO DO: Port to Py3.
#############################################################################
'''
Functions for BRENDA API (SOAP) access.

"EC" refers to Enzyme Commission.  EC Numbers are assigned based on functionality,
the catalyzed reaction, not the protein itself.  Hence multiple proteins can 
exist for a given ECN or ECN+organism.

Default is human enzymes, organism="Homo sapiens".

Ref: http://www.brenda-enzymes.org/soap.php

Ref:	BRENDA: a resource for enzyme data and metabolic information.
	Schomburg I, Chang A, Hofmann O, Ebeling C, Ehrentreich F, Schomburg D.
	Trends Biochem Sci. 2002 Jan;27(1):54-6.
	http://www.ncbi.nlm.nih.gov/pubmed/11796225

Ref:	BRENDA in 2015: exciting developments in its 25th year of existence.
	Nucleic Acids Res. 2014 Nov 5. pii: gku1068. [Epub ahead of print]
	Chang A, Schomburg I, Placzek S, Jeske L, Ulbrich M, Xiao M, Sensen CW, Schomburg D.
	http://www.ncbi.nlm.nih.gov/pubmed/25378310.

Ref: http://en.wikipedia.org/wiki/Enzyme_inhibitor

Author: Jeremy Yang
'''
#############################################################################
import sys,os,time,getopt,codecs,hashlib
import string,re,json

from ..util import rest_utils


from SOAPpy import WSDL ## for extracting URL of endpoint from WSDL file
from SOAPpy import SOAPProxy

API_HOST = "www.brenda-enzymes.org"
API_BASE_PATH = "/soap"

#############################################################################
def ListECNumbers(client,api_params,verbose=0):
  '''We think this gets all EC numbers.  But maybe not. 6549 on Jan 7 2015.'''
  return client.getEcNumbersFromEcNumber(api_params)

#############################################################################
### List all enzymes linked to synonyms.  (5000+ hits but not all.)
def ListECNumbersFromSynonyms(client,api_params,verbose=0):
  return client.getEcNumbersFromSynonyms(api_params)

#############################################################################
### List all enzymes linked to inhibitors.
def ListECNumbersFromInhibitors(client,api_params,verbose=0):
  return client.getEcNumbersFromInhibitors(api_params)

#############################################################################
### List all enzymes linked to activators.
def ListECNumbersFromActivators(client,api_params,verbose=0):
  return client.getEcNumbersFromActivatingCompound(api_params)

#############################################################################
### List all enzymes linked to Ki value.
def ListECNumbersFromKiValue(client,api_params,verbose=0):
  return client.getEcNumbersFromKiValue(api_params)

#############################################################################
### List all enzymes linked to Km value.
def ListECNumbersFromKmValue(client,api_params,verbose=0):
  return client.getEcNumbersFromKmValue(api_params)

#############################################################################
def ListOrganisms(client,api_params,verbose=0):
  return client.getOrganismsFromOrganism(api_params)

#############################################################################
def GetInhibitorData(client,api_params,ecns,organism,fout,verbose=0):
  '''Get data for input ECNs, CSV output.  Focus on inhibitors and Kis.
Per Sandra Placzek, the "literature" field same as "reference" ID.
'''
  tags=['ecNumber','systematicName','organism']
  ki_tags=["commentary", "inhibitor", "kiValue", "kiValueMaximum", "ligandStructureId", "literature"]
  fout.write((','.join(tags+ki_tags))+'\n')
  n_in=0; n_out=0;
  for ecn in ecns:
    n_in+=1
    row={tag:'' for tag in tags}
    row['ecNumber']=ecn
    row['organism']=organism
    try:
      rstr=GetSystematicName(client,api_params,ecn,verbose)
      #print >>sys.stderr, 'DEBUG: rstr="%s"'%rstr  #DEBUG
      results=ParseResultDictString(rstr)
      val = results[0]['systematicName'] if (results and results[0].has_key('systematicName')) else ''
      row['systematicName']=val
    except Exception,e:
      print >>sys.stderr, '%s'%str(e)

    ki_rows=[]
    try:
      rstr=GetKiValues(client,api_params,ecn,organism,verbose)
      results=ParseResultDictString(rstr)
      for result in results:
        ki_row={}
        for tag in ki_tags:
          val = result[tag] if result.has_key(tag) else ''
          ki_row[tag]=val
        ki_rows.append(ki_row)
    except Exception,e:
      print >>sys.stderr, '%s'%str(e)

    ###Ignore Ki-less records.###if not ki_rows: ki_rows=[{tag:'' for tag in ki_tags}]
    for ki_row in ki_rows:
      for j,tag in enumerate(tags):
        fout.write('%s"%s"'%((',' if j>0 else ''),row[tag]))
      for tag in ki_tags:
        fout.write(',"%s"'%(ki_row[tag]))
      fout.write('\n')
      n_out+=1
  print >>sys.stderr, 'input ECNs: %d ; output rows: %d'%(n_in,n_out)

#############################################################################
def GetSequenceData(client,api_params,ecns,organism,fout,verbose=0):
  '''Get data for input ECNs, CSV output.  Focus on sequences/proteins.
Note "firstAccessionCode" is UniProt ID.  What is "id"?
'''
  tags=['ecNumber','systematicName','organism']
  seq_tags=["firstAccessionCode","id","noOfAminoAcids","sequence","source"]
  fout.write((','.join(tags+seq_tags))+'\n')
  n_in=0; n_out=0;
  for ecn in ecns:
    n_in+=1
    row={tag:'' for tag in tags}
    row['ecNumber']=ecn
    row['organism']=organism
    try:
      rstr=GetSystematicName(client,api_params,ecn,verbose)
      #print >>sys.stderr, 'DEBUG: rstr="%s"'%rstr  #DEBUG
      results=ParseResultDictString(rstr)
      val = results[0]['systematicName'] if (results and results[0].has_key('systematicName')) else ''
      row['systematicName']=val
    except Exception,e:
      print >>sys.stderr, '%s'%str(e)

    seq_rows=[]
    try:
      rstr=GetSequence(client,api_params,ecn,organism,verbose)
      results=ParseResultDictString(rstr)
      for result in results:
        seq_row={}
        for tag in seq_tags:
          val = result[tag] if result.has_key(tag) else ''
          seq_row[tag]=val
        seq_rows.append(seq_row)
    except Exception,e:
      print >>sys.stderr, '%s'%str(e)

    ###Ignore sequence-less records.###if not seq_rows: seq_rows=[{tag:'' for tag in seq_tags}]
    for seq_row in seq_rows:
      for j,tag in enumerate(tags):
        fout.write('%s"%s"'%((',' if j>0 else ''),row[tag]))
      for tag in seq_tags:
        fout.write(',"%s"'%(seq_row[tag]))
      fout.write('\n')
      n_out+=1
  print >>sys.stderr, 'input ECNs: %d ; output rows: %d'%(n_in,n_out)

#############################################################################
def GetLigandData(client,api_params,ecns,organism,fout,verbose=0):
  '''Get data for input ECNs, CSV output.  Focus on ligands, which includes substrates,
inhibitors and activators.
'''
  tags=['ecNumber','systematicName','organism']
  lig_tags=["ligand","ligandStructureId","role"]
  fout.write((','.join(tags+lig_tags))+'\n')
  n_in=0; n_out=0;
  for ecn in ecns:
    n_in+=1
    row={tag:'' for tag in tags}
    row['ecNumber']=ecn
    row['organism']=organism
    try:
      rstr=GetSystematicName(client,api_params,ecn,verbose)
      #print >>sys.stderr, 'DEBUG: rstr="%s"'%rstr  #DEBUG
      results=ParseResultDictString(rstr)
      val = results[0]['systematicName'] if (results and results[0].has_key('systematicName')) else ''
      row['systematicName']=val
    except Exception,e:
      print >>sys.stderr, '%s'%str(e)

    lig_rows=[]
    try:
      rstr=GetLigands(client,api_params,ecn,organism,verbose)
      results=ParseResultDictString(rstr)
      for result in results:
        lig_row={}
        for tag in lig_tags:
          val = result[tag] if result.has_key(tag) else ''
          lig_row[tag]=val
        lig_rows.append(lig_row)
    except Exception,e:
      print >>sys.stderr, '%s'%str(e)

    ###Ignore ligand-less records.###if not lig_rows: lig_rows=[{tag:'' for tag in lig_tags}]
    for lig_row in lig_rows:
      for j,tag in enumerate(tags):
        fout.write('%s"%s"'%((',' if j>0 else ''),row[tag]))
      for tag in lig_tags:
        fout.write(',"%s"'%(lig_row[tag]))
      fout.write('\n')
      n_out+=1
  print >>sys.stderr, 'input ECNs: %d ; output rows: %d'%(n_in,n_out)

#############################################################################
def GetReferenceData(client,api_params,ecns,organism,fout,verbose=0):
  '''Get data for input ECNs, CSV output.  Focus on references. 
'''
  tags=['ecNumber','systematicName','organism']
  ref_tags=['ecNumber','journal','authors','pubmedId','reference','title','volume','year','pages','commentary']
  fout.write((','.join(tags+ref_tags))+'\n')
  n_in=0; n_out=0;
  for ecn in ecns:
    n_in+=1
    row={tag:'' for tag in tags}
    row['ecNumber']=ecn
    row['organism']=organism
    try:
      rstr=GetSystematicName(client,api_params,ecn,verbose)
      #print >>sys.stderr, 'DEBUG: rstr="%s"'%rstr  #DEBUG
      results=ParseResultDictString(rstr)
      val = results[0]['systematicName'] if (results and results[0].has_key('systematicName')) else ''
      row['systematicName']=val
    except Exception,e:
      print >>sys.stderr, '%s'%str(e)

    ref_rows=[]
    try:
      rstr=GetReferences(client,api_params,ecn,organism,verbose)
      results=ParseResultDictString(rstr)
      for result in results:
        ref_row={}
        for tag in ref_tags:
          val = result[tag] if result.has_key(tag) else ''
          ref_row[tag]=val
        ref_rows.append(ref_row)
    except Exception,e:
      print >>sys.stderr, '%s'%str(e)

    ###Ignore reference-less records.###if not ref_rows: ref_rows=[{tag:'' for tag in ref_tags}]
    for ref_row in ref_rows:
      for j,tag in enumerate(tags):
        fout.write('%s"%s"'%((',' if j>0 else ''),row[tag]))
      for tag in ref_tags:
        fout.write(',"%s"'%(ref_row[tag]))
      fout.write('\n')
      n_out+=1
  print >>sys.stderr, 'input ECNs: %d ; output rows: %d'%(n_in,n_out)

#############################################################################
def GetECN(client,api_params,ecn,verbose=0):
  return client.getEcNumber(api_params+',ecNumber*%s'%ecn)

#############################################################################
def QueryString(ecn,organism,verbose):
  qstr=('ecNumber*%s%s'%(ecn,('#organism*%s'%organism) if organism else ''))
  if verbose>1: print >>sys.stderr, qstr
  return qstr

#############################################################################
def GetNames(client,api_params,ecn,organism,verbose=0):
  return client.getEnzymeNames(api_params+','+QueryString(ecn,organism,verbose))

#############################################################################
def GetSystematicName(client,api_params,ecn,verbose=0):
  '''Organism param not allowed.'''
  qstr=('ecNumber*%s'%(ecn))
  if verbose>1: print >>sys.stderr, qstr
  return client.getSystematicName(api_params+','+qstr)

#############################################################################
def GetOrganism(client,api_params,ecn,organism,verbose=0):
  return client.getOrganism(api_params+','+QueryString(ecn,organism,verbose))

#############################################################################
def GetSequence(client,api_params,ecn,organism,verbose=0):
  '''Supposedly also accepts uniprot param.  How?'''
  return client.getSequence(api_params+','+QueryString(ecn,organism,verbose))

#############################################################################
def GetPdb(client,api_params,ecn,organism,verbose=0):
  return client.getPdb(api_params+','+QueryString(ecn,organism,verbose))

#############################################################################
def GetKiValues(client,api_params,ecn,organism,verbose=0):
  return client.getKiValue(api_params+','+QueryString(ecn,organism,verbose))

#############################################################################
def GetKmValues(client,api_params,ecn,organism,verbose=0):
  return client.getKmValue(api_params+','+QueryString(ecn,organism,verbose))

#############################################################################
def GetInhibitors(client,api_params,ecn,organism,verbose=0):
  return client.getInhibitors(api_params+','+QueryString(ecn,organism,verbose))

#############################################################################
def GetActivators(client,api_params,ecn,organism,verbose=0):
  return client.getActivatingCompound(api_params+','+QueryString(ecn,organism,verbose))

#############################################################################
def GetLigands(client,api_params,ecn,organism,verbose=0):
  return client.getLigands(api_params+','+QueryString(ecn,organism,verbose))

#############################################################################
def GetReferences(client,api_params,ecn,organism,verbose=0):
  qstr=('ecNumber*%s%s'%(ecn,('#organism*%s'%organism) if organism else ''))
  qstr+=('#textmining*0') #manually-annotated entries only
  if verbose>1: print >>sys.stderr, qstr
  return client.getReference(api_params+','+qstr)

#############################################################################
def ParseResultDictString(rstr):
  results=[]
  if not rstr.strip(): return results
  ecns = re.split(r'!',rstr.strip())
  for ecn in ecns:
    result={}
    lines = re.split(r'\#',ecn)
    for line in lines:
      if not line.strip(): continue
      #print >>sys.stderr, 'DEBUG: line = "%s"'%line
      key = re.sub(r'\*.*$','',line)
      val = re.sub(r'^[^\*]*\*','',line)
      result[key]=val
    results.append(result)
  return results

#############################################################################
def ParseResultListString(rstr):
  results= re.split(r'!',rstr)
  return results

#############################################################################
def Test1(base_url):
  print >>sys.stderr, '1) Usage with WSDL (for extracting the URL of the endpoint)'
  wsdl = base_url+"/brenda.wsdl"
  client = WSDL.Proxy(wsdl)
  resultString = client.getKmValue(api_params+','+"ecNumber*1.1.1.1#organism*Homo sapiens")
  print resultString

#############################################################################
#def OutputResultsDict(results,fout):
#  n_out=0;
#  for result in results:
#    n_out+=1
#    for key in sorted(result.keys()):
#      fout.write('\t%28s: %s\n'%(key,result[key]))
#  print >>sys.stderr, 'results: %d'%n_out
#
#############################################################################
def OutputResultsDict(results,fout):
  '''Output JSON list of dicts.'''
  fout.write(json.dumps(results,indent=2,sort_keys=True))
  print >>sys.stderr, 'results: %d'%len(results)

#############################################################################
def OutputResultsList(results,fout):
  '''Output simple list of values.'''
  n_out=0;
  for result in results:
    n_out+=1
    fout.write('%s\n'%(result))
  print >>sys.stderr, 'results: %d'%n_out

#############################################################################
