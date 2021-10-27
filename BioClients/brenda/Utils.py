#!/usr/bin/env python3
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
'''
#############################################################################
import sys,os,time,string,re,json,logging,zeep,yaml

#############################################################################
def ReadParamFile(fparam):
  params={};
  with open(fparam, 'r') as fh:
    for param in yaml.load_all(fh, Loader=yaml.BaseLoader):
      for k,v in param.items():
        params[k] = v
  return params

#############################################################################
def SoapAPIClient(wsdl_url):
  client = zeep.Client(wsdl_url)
  return client

#############################################################################
def Test(client, api_params):
  params = tuple(api_params+["ecNumber*1.1.1.1", "organism*Homo sapiens", "kmValue*", "kmValueMaximum*", "substrate*", "commentary*", "ligandStructureId*", "literature*"])
  resultString = client.service.getKmValue(*params)
  print(resultString)

#############################################################################
def GetECN(client, api_params, ecns, fout):
  for ecn in ecns:
    params = tuple(api_params+["ecNumber*%s"%ecn])
    #results = client.service.getEcNumber(*params)
    results = client.service.getEcNumbersFromEcNumber(*params)
    logging.debug("type(results) = %s"%type(results))
    print(str(results))

#############################################################################
def ListECNumbers(client, api_params, fout):
  '''We think this gets all EC numbers.  But maybe not. 6549 on Jan 7 2015.'''
  rstr = client.getEcNumbersFromEcNumber(api_params)
  results = brenda.ParseResultListString(rstr)
  OutputResultsList(results, fout)

#############################################################################
### List all enzymes linked to synonyms.  (5000+ hits but not all.)
def ListECNumbersFromSynonyms(client, api_params, fout):
  rstr = client.getEcNumbersFromSynonyms(api_params)
  results = brenda.ParseResultListString(rstr)
  OutputResultsList(results, fout)

#############################################################################
### List all enzymes linked to inhibitors.
def ListECNumbersFromInhibitors(client, api_params, fout):
  rstr = client.getEcNumbersFromInhibitors(api_params)
  results = brenda.ParseResultListString(rstr)
  OutputResultsList(results, fout)

#############################################################################
### List all enzymes linked to activators.
def ListECNumbersFromActivators(client, api_params, fout):
  rstr = client.getEcNumbersFromActivatingCompound(api_params)
  results = brenda.ParseResultListString(rstr)
  OutputResultsList(results, fout)

#############################################################################
### List all enzymes linked to Ki value.
def ListECNumbersFromKiValue(client, api_params, fout):
  rstr = client.getEcNumbersFromKiValue(api_params)
  results = brenda.ParseResultListString(rstr)
  OutputResultsList(results, fout)

#############################################################################
### List all enzymes linked to Km value.
def ListECNumbersFromKmValue(client, api_params, fout):
  rstr = client.getEcNumbersFromKmValue(api_params)
  results = brenda.ParseResultListString(rstr)
  OutputResultsList(results, fout)

#############################################################################
def ListOrganisms(client, api_params, fout):
  rstr = client.getOrganismsFromOrganism(api_params)
  results = brenda.ParseResultListString(rstr)
  OutputResultsList(results, fout)

#############################################################################
def GetInhibitorData(client, api_params, ecns, organism, fout):
  '''Get data for input ECNs, CSV output.  Focus on inhibitors and Kis.
Per Sandra Placzek, the "literature" field same as "reference" ID.
'''
  tags = ['ecNumber','systematicName','organism']
  ki_tags = ["commentary", "inhibitor", "kiValue", "kiValueMaximum", "ligandStructureId", "literature"]
  fout.write((','.join(tags+ki_tags))+'\n')
  n_in=0; n_out=0;
  for ecn in ecns:
    n_in+=1
    row={tag:'' for tag in tags}
    row['ecNumber'] = ecn
    row['organism'] = organism
    try:
      rstr = GetSystematicName(client, api_params, ecn)
      #logging.debug('rstr="%s"'%rstr)
      results = ParseResultDictString(rstr)
      val = results[0]['systematicName'] if (results and results[0].has_key('systematicName')) else ''
      row['systematicName'] = val
    except Exception as e:
      logging.error('%s'%str(e))

    ki_rows=[]
    try:
      rstr = GetKiValues(client, api_params, ecn, organism)
      results = ParseResultDictString(rstr)
      for result in results:
        ki_row = {}
        for tag in ki_tags:
          val = result[tag] if result.has_key(tag) else ''
          ki_row[tag] = val
        ki_rows.append(ki_row)
    except Exception as e:
      logging.error('%s'%str(e))

    ###Ignore Ki-less records.###if not ki_rows: ki_rows=[{tag:'' for tag in ki_tags}]
    for ki_row in ki_rows:
      for j,tag in enumerate(tags):
        fout.write('%s"%s"'%((',' if j>0 else ''), row[tag]))
      for tag in ki_tags:
        fout.write(',"%s"'%(ki_row[tag]))
      fout.write('\n')
      n_out+=1
  logging.info('input ECNs: %d ; output rows: %d'%(n_in,n_out))

#############################################################################
def GetSequenceData(client, api_params, ecns, organism, fout):
  '''Get data for input ECNs, CSV output.  Focus on sequences/proteins.
Note "firstAccessionCode" is UniProt ID.  What is "id"?
'''
  tags = ['ecNumber','systematicName','organism']
  seq_tags = ["firstAccessionCode","id","noOfAminoAcids","sequence","source"]
  fout.write((','.join(tags+seq_tags))+'\n')
  n_in=0; n_out=0;
  for ecn in ecns:
    n_in+=1
    row = {tag:'' for tag in tags}
    row['ecNumber'] = ecn
    row['organism'] = organism
    try:
      rstr = GetSystematicName(client, api_params, ecn)
      #logging.debug('rstr="%s"'%rstr)
      results = ParseResultDictString(rstr)
      val = results[0]['systematicName'] if (results and results[0].has_key('systematicName')) else ''
      row['systematicName'] = val
    except Exception as e:
      logging.error('%s'%str(e))

    seq_rows=[]
    try:
      rstr = GetSequence(client, api_params, ecn, organism)
      results = ParseResultDictString(rstr)
      for result in results:
        seq_row={}
        for tag in seq_tags:
          val = result[tag] if result.has_key(tag) else ''
          seq_row[tag] = val
        seq_rows.append(seq_row)
    except Exception as e:
      logging.error('%s'%str(e))

    ###Ignore sequence-less records.###if not seq_rows: seq_rows=[{tag:'' for tag in seq_tags}]
    for seq_row in seq_rows:
      for j,tag in enumerate(tags):
        fout.write('%s"%s"'%((',' if j>0 else ''),row[tag]))
      for tag in seq_tags:
        fout.write(',"%s"'%(seq_row[tag]))
      fout.write('\n')
      n_out+=1
  logging.info('input ECNs: %d ; output rows: %d'%(n_in,n_out))

#############################################################################
def GetLigandData(client, api_params, ecns, organism, fout):
  '''Get data for input ECNs, CSV output.  Focus on ligands, which includes substrates,
inhibitors and activators.
'''
  tags = ['ecNumber','systematicName','organism']
  lig_tags = ["ligand","ligandStructureId","role"]
  fout.write((','.join(tags+lig_tags))+'\n')
  n_in=0; n_out=0;
  for ecn in ecns:
    n_in+=1
    row = {tag:'' for tag in tags}
    row['ecNumber'] = ecn
    row['organism'] = organism
    try:
      rstr = GetSystematicName(client, api_params, ecn)
      #logging.debug('rstr="%s"'%rstr)
      results = ParseResultDictString(rstr)
      val = results[0]['systematicName'] if (results and results[0].has_key('systematicName')) else ''
      row['systematicName'] = val
    except Exception as e:
      logging.error('%s'%str(e))

    lig_rows=[]
    try:
      rstr = GetLigands(client, api_params, ecn, organism)
      results = ParseResultDictString(rstr)
      for result in results:
        lig_row={}
        for tag in lig_tags:
          val = result[tag] if result.has_key(tag) else ''
          lig_row[tag] = val
        lig_rows.append(lig_row)
    except Exception as e:
      logging.error('%s'%str(e))

    ###Ignore ligand-less records.###if not lig_rows: lig_rows=[{tag:'' for tag in lig_tags}]
    for lig_row in lig_rows:
      for j,tag in enumerate(tags):
        fout.write('%s"%s"'%((',' if j>0 else ''), row[tag]))
      for tag in lig_tags:
        fout.write(',"%s"'%(lig_row[tag]))
      fout.write('\n')
      n_out+=1
  logging.info('input ECNs: %d ; output rows: %d'%(n_in, n_out))

#############################################################################
def GetReferenceData(client, api_params, ecns, organism, fout):
  '''Get data for input ECNs, CSV output.  Focus on references.'''
  tags = ['ecNumber','systematicName','organism']
  ref_tags = ['ecNumber','journal','authors','pubmedId','reference','title','volume','year','pages','commentary']
  fout.write((','.join(tags+ref_tags))+'\n')
  n_in=0; n_out=0;
  for ecn in ecns:
    n_in+=1
    row = {tag:'' for tag in tags}
    row['ecNumber'] = ecn
    row['organism'] = organism
    try:
      rstr = GetSystematicName(client, api_params, ecn)
      #logging.debug('rstr="%s"'%rstr)
      results = ParseResultDictString(rstr)
      val = results[0]['systematicName'] if (results and results[0].has_key('systematicName')) else ''
      row['systematicName'] = val
    except Exception as e:
      logging.error('%s'%str(e))

    ref_rows=[]
    try:
      rstr = GetReferences(client, api_params, ecn, organism)
      results = ParseResultDictString(rstr)
      for result in results:
        ref_row = {}
        for tag in ref_tags:
          val = result[tag] if result.has_key(tag) else ''
          ref_row[tag] = val
        ref_rows.append(ref_row)
    except Exception as e:
      logging.error('%s'%str(e))

    ###Ignore reference-less records.###if not ref_rows: ref_rows=[{tag:'' for tag in ref_tags}]
    for ref_row in ref_rows:
      for j,tag in enumerate(tags):
        fout.write('%s"%s"'%((',' if j>0 else ''), row[tag]))
      for tag in ref_tags:
        fout.write(',"%s"'%(ref_row[tag]))
      fout.write('\n')
      n_out+=1
  logging.info('input ECNs: %d ; output rows: %d'%(n_in, n_out))

#############################################################################
def QueryString(ecn, organism):
  qstr = ('ecNumber*%s%s'%(ecn, ('#organism*%s'%organism) if organism else ''))
  logging.debug(qstr)
  return qstr

#############################################################################
def GetNames(client, api_params, ecns, organism, fout):
  for ecn in ecns:
    rstr = client.getEnzymeNames(api_params+','+QueryString(ecn, organism))
    results = ParseResultDictString(rstr)
    OutputResultsDict(results, fout)

#############################################################################
def GetSystematicName(client, api_params, ecns, fout):
  '''Organism param not allowed.'''
  for ecn in ecns:
    qstr = ('ecNumber*%s'%(ecn))
    logging.debug(qstr)
    rstr = client.getSystematicName(api_params+','+qstr)
    results = ParseResultDictString(rstr)
    OutputResultsDict(results, fout)

#############################################################################
def GetOrganism(client, api_params, ecns, organism, fout):
  for ecn in ecns:
    rstr = client.getOrganism(api_params+','+QueryString(ecn, organism))
    results = ParseResultDictString(rstr)
    OutputResultsDict(results, fout)

#############################################################################
def GetSequence(client, api_params, ecns, organism, fout):
  '''Supposedly also accepts uniprot param.  How?'''
  for ecn in ecns:
    rstr = client.getSequence(api_params+','+QueryString(ecn, organism))
    results = ParseResultDictString(rstr)
    OutputResultsDict(results, fout)

#############################################################################
def GetPdb(client, api_params, ecns, organism, fout):
  for ecn in ecns:
    rstr = client.getPdb(api_params+','+QueryString(ecn, organism))
    results = ParseResultDictString(rstr)
    OutputResultsDict(results, fout)

#############################################################################
def GetKiValues(client, api_params, ecns, organism, fout):
  for ecn in ecns:
    rstr = client.getKiValue(api_params+','+QueryString(ecn, organism))
    results = ParseResultDictString(rstr)
    OutputResultsDict(results, fout)

#############################################################################
def GetKmValues(client, api_params, ecns, organism, fout):
  for ecn in ecns:
    rstr = client.getKmValue(api_params+','+QueryString(ecn, organism))
    results = ParseResultDictString(rstr)
    OutputResultsDict(results, fout)

#############################################################################
def GetInhibitors(client, api_params, ecns, organism, fout):
  for ecn in ecns:
    rstr = client.getInhibitors(api_params+','+QueryString(ecn, organism))
    results = ParseResultDictString(rstr)
    OutputResultsDict(results, fout)

#############################################################################
def GetActivators(client, api_params, ecns, organism, fout):
  for ecn in ecns:
    rstr = client.getActivatingCompound(api_params+','+QueryString(ecn, organism))
    results = ParseResultDictString(rstr)
    OutputResultsDict(results, fout)

#############################################################################
def GetLigands(client, api_params, ecns, organism, fout):
  for ecn in ecns:
    rstr = client.getLigands(api_params+','+QueryString(ecn, organism))
    results = ParseResultDictString(rstr)
    OutputResultsDict(results, fout)

#############################################################################
def GetReferences(client, api_params, ecns, organism, fout):
  for ecn in ecns:
    qstr = ('ecNumber*%s%s'%(ecn, ('#organism*%s'%organism) if organism else ''))
    qstr+=('#textmining*0') #manually-annotated entries only
    logging.debug(qstr)
    rstr = client.getReference(api_params+','+qstr)
    results = ParseResultDictString(rstr)
    OutputResultsDict(results, fout)

#############################################################################
def ParseResultDictString(rstr):
  results=[]
  if not rstr.strip(): return results
  ecns = re.split(r'!', rstr.strip())
  for ecn in ecns:
    result = {}
    lines = re.split(r'\#', ecn)
    for line in lines:
      if not line.strip(): continue
      #logging.debug('line = "%s"'%line)
      key = re.sub(r'\*.*$','', line)
      val = re.sub(r'^[^\*]*\*','', line)
      result[key]=val
    results.append(result)
  return results

#############################################################################
def ParseResultListString(rstr):
  results =  re.split(r'!', rstr)
  return results

#############################################################################
#def OutputResultsDict(results, fout):
#  n_out=0;
#  for result in results:
#    n_out+=1
#    for key in sorted(result.keys()):
#      fout.write('\t%28s: %s\n'%(key, result[key]))
#  logging.info('results: %d'%n_out)
#
#############################################################################
def OutputResultsDict(results, fout):
  '''Output JSON list of dicts.'''
  fout.write(json.dumps(results, indent=2, sort_keys=True))
  logging.info('results: %d'%len(results))

#############################################################################
def OutputResultsList(results, fout):
  '''Output simple list of values.'''
  n_out=0;
  for result in results:
    n_out+=1
    fout.write('%s\n'%(result))
  logging.info('results: %d'%n_out)

#############################################################################
