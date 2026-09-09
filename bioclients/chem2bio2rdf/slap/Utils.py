#!/usr/bin/env python3
"""
utility functions for SLAP, and utility application.

See: http://slapfordrugtargetprediction.wikispaces.com/API

URL form
http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/slap/5591:PPARG
"""
###
import sys,os,re,argparse,time,logging
import urllib,urllib.parse,json,csv

from xml.etree import ElementTree
from xml.parsers import expat

from ...util import rest
#
#############################################################################
### Scrape HTML for predicted-target table for CSV
### 
### all targets have Chem2Bio2RDF links like:
### http://chem2bio2rdf.org/uniprot/resource/gene/AMPD1
### "approved interaction" targets have Chem2Bio2RDF links like:
### http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/cid_gene/2995:ADRA1D
### all targets have SLAP links like:
### http://cheminfov.informatics.indiana.edu:8080/slap/slap.jsp?cid=2995&gene=NFKB2
#############################################################################
def Drug2Targets(base_url,cids,fout):
  n_cid=0; n_found=0; n_not_found=0; n_none_predicted=0;
  fout.write('"cid","target","p_value","score","type","chemohub"\n')
  for cid in cids:
    n_cid+=1
    logging.info('%9s: '%(cid))
    try:
      rval=rest.Utils.GetURL(base_url+'/cid=%s'%(cid))
    except Exception as e:
      logging.error('Exception: %s'%(e))
      n_not_found+=1
      continue
    htm=rval
    if not htm:
      n_not_found+=1
      logging.info('%9s: CID not found.'%(cid))
      continue
    elif re.search('No target predicted', htm):
      n_none_predicted+=1
      logging.info('%9s: No targets predicted.'%(cid))
      continue
    n_found+=1
    htm = re.sub(r'[\n\r]', '', htm)
    htm = re.sub(r'</table>.*$', '', htm)
    htm = re.sub(r'^.*<table[^>]*>', '', htm)
    rows = re.split('<tr>', htm)
    logging.debug('n_rows = %d'%len(rows))
    logging.info('%9s: Targets predicted: %d'%(cid,len(rows)-1))
    for row in rows:
      if not row: continue
      row = re.sub('</?tr>', '', row, re.I)
      row = re.sub('^<td>(.*)</td>$', '\\1', row, re.I)
      vals_raw = re.split(r'</td><td>', row)
      if not vals_raw: continue
      logging.debug('vals_raw[0] = "%s"'%vals_raw[0])
      if vals_raw[0] == 'target':
        continue #kludge
      vals=[];
      for val in vals_raw:
        val = re.sub('</?t[dr]>', '', val, re.I)
        url = None
        if re.search(r'<a href="([^"]+)">', val):
          url = re.sub(r'^.*<a href="([^"]+)">.*$', '\\1', val, re.I)
          val = re.sub(r'^.*<a href="[^"]+">([^<]*)</a>.*$', '\\1', val, re.I)
          val = '%s [%s]'%(val,url) if vals else val
        vals.append(val)
      vals = [cid]+vals
      vals = [csv_utils.ToStringForCSV(val) for val in vals]
      fout.write(','.join(vals)+'\n')

  logging.info('n_cid = %d'%(n_cid))
  logging.info('n_found = %d'%(n_found))
  logging.info('n_not_found = %d'%(n_not_found))
  logging.info('n_none_predicted = %d'%(n_none_predicted))

#############################################################################
def Drug2BioSimilarDrugs(base_url,cids,fout):
  n_cid=0; n_found=0; n_not_found=0; n_none_predicted=0;
  fout.write('"query_cid","pubchem_cid","drug_name","similarity","related_diseases","atc"\n')
  for cid in cids:
    n_cid+=1
    logging.info('%9s: '%(cid))
    try:
      rval=rest.Utils.GetURL(base_url+'/cid=%s'%(cid))
    except Exception as e:
      logging.error('Exception: %s'%(e))
      n_not_found+=1
      continue
    htm=rval
    if not htm:
      n_not_found+=1
      logging.info('%9s: CID not found.'%(cid))
      continue
    elif re.search('No target predicted', htm): #FIX
      n_none_predicted+=1
      logging.info('%9s: No bio-similar drugs found.'%(cid))
      continue
    n_found+=1
    htm = re.sub(r'[\n\r]', '', htm)
    htm = re.sub(r'^.*Biological Similar Drugs', '', htm)
    htm = re.sub(r'</table>.*$', '', htm)
    htm = re.sub(r'^.*<table[^>]*>', '', htm)
    rows = re.split('<tr>', htm)
    logging.debug('n_rows = %d'%len(rows))
    logging.info('%9s: Bio-similar drugs predicted: %d'%(cid,len(rows)-1))
    for row in rows:
      if not row: continue
      row = re.sub('</?tr>', '', row, re.I)
      row = re.sub('^<td>(.*)</td>$', '\\1', row, re.I)
      vals_raw = re.split(r'</td><td>', row)
      if not vals_raw: continue
      if vals_raw[0] == 'PubChem CID':
        continue #kludge
      vals=[];
      for val in vals_raw:
        val = re.sub('</?t[dr]>', '', val, re.I)
        url = None
        if re.match('<img .*>$', val, re.I): continue #skip imgs
        if re.search(r'<a href="([^"]+)">', val):
          url = re.sub(r'^.*<a href="([^"]+)">.*$', '\\1', val, re.I)
          val = re.sub(r'^.*<a href="[^"]+">([^<]*)</a>.*$', '\\1', val, re.I)
          val = '%s [%s]'%(val,url) if vals else val
        vals.append(val)
      vals = [cid]+vals
      vals = [csv_utils.ToStringForCSV(val) for val in vals]
      fout.write(','.join(vals)+'\n')

  logging.info('n_cid = %d'%(n_cid))
  logging.info('n_found = %d'%(n_found))
  logging.info('n_not_found = %d'%(n_not_found))
  logging.info('n_none_predicted = %d'%(n_none_predicted))


#############################################################################
def Target2Drugs(base_url,tids,fout):
  n_tid=0; n_found=0; n_not_found=0; n_none_assn=0;
  fout.write('"target","cid","sources","paths","smiles"\n')
  for tid in tids:
    n_tid+=1
    logging.info('%9s: '%(tid))
    try:
      rval=rest.Utils.GetURL(base_url+'/target=%s'%(tid))
    except Exception as e:
      logging.error('Exception: %s'%(e))
      n_not_found+=1
      continue
    htm=rval
    logging.debug('htm = "%s"'%(htm))
    if not htm:
      n_not_found+=1
      logging.info('%9s: target not found.'%(tid))
      continue
    elif re.search('No compounds predicted', htm): #FIX
      n_none_assn+=1
      logging.info('%9s: No compounds associated.'%(tid))
      continue

    n_found+=1
    htm = re.sub(r'[\n\r]', '', htm)
    htm = re.sub(r'</table>.*$', '', htm)
    htm = re.sub(r'^.*<table[^>]*>', '', htm)
    rows = re.split('<tr>', htm)
    logging.debug('n_rows = %d'%len(rows))
    logging.info('%9s: Compounds associated: %d'%(tid,len(rows)-1))
    for row in rows:
      if not row: continue
      row = re.sub('</?tr>', '', row, re.I)
      row = re.sub('^<td>(.*)</td>$', '\\1', row, re.I)
      vals_raw = re.split(r'</td><td>', row)
      if not vals_raw: continue
      logging.debug('vals_raw[0] = "%s"'%vals_raw[0])
      if vals_raw[0] == 'cid':
        continue #kludge
      vals=[];
      for j,val in enumerate(vals_raw):
        val = re.sub('</?t[dr]>', '', val, re.I)
        if j==2:
          val = re.sub(' +', '; ', val.strip()) #sources
        if re.match('<img .*>$', val, re.I): continue #skip imgs
        url = None
        if re.search(r'<a href="([^"]+)">', val):
          url = re.sub(r'^.*<a href="([^"]+)">.*$', '\\1', val, re.I)
          val = re.sub(r'^.*<a href="[^"]+">([^<]*)</a>.*$', '\\1', val, re.I)
          val = '%s [%s]'%(val,url) if vals else val
        vals.append(val)
      vals = [tid]+vals
      vals = [csv_utils.ToStringForCSV(val) for val in vals]
      fout.write(','.join(vals)+'\n')

  logging.info('n_tid = %d'%(n_tid))
  logging.info('n_found = %d'%(n_found))
  logging.info('n_not_found = %d'%(n_not_found))
  logging.info('n_none_assn = %d'%(n_none_assn))

#############################################################################
### Given input drug (CID) and target (TID), find paths, subnetwork, and
### SLAP association scores and type.
#############################################################################
###	<b><i>Input: </i></b> Compound: 5591; Target: PPARG
###	<b><i>P value: </i></b>9.06524962196e-06 (very strong)
###	<b><i>Type: </i></b><a
###	href="http://cheminfov.informatics.indiana.edu/rest/Chem2Bio2RDF/cid_gene/5591:PPARG">approved binding</a>
###	*Smaller p value, stronger association
###	<graphml>
###	...
###	<b><i>Input: </i></b> Compound: 176870; Target: TRIP13
###	<b><i>P value: </i></b>0.8795 (undecided)
###	<b><i>Type: </i></b>predicted
###	*Smaller p value, stronger association
#############################################################################
### Output CSV file contains IDs and scores only.
### If odir and path exists, write full graphml file with IDs in name.
#############################################################################
def DrugTargetPaths(base_url, cids, tids, cid_skip, cid_nmax, tid_skip, tid_nmax, odir, fout):
  errs={}; score_types={}; score_notes={};
  fout.write("cid\ttid\tscore\tscore_note\tscore_type\terror\n")
  n=0; n_cid=0; n_dtp=0;
  tids_not_found = set()
  cids_not_found = set()
  for cid in cids:
    n_cid+=1
    if cid_skip and n_cid<=cid_skip: continue
    n_tid=0;
    for tid in tids:
      n_tid+=1
      if tid_skip and n_tid<=tid_skip: continue
      n+=1
      if cid in cids_not_found:
        logging.info("cid not found; skipping %s:%s"%(cid,tid))
        continue
      if tid in tids_not_found:
        logging.info("tid not found; skipping %s:%s"%(cid,tid))
        continue
      logging.info('%d.  [%d/%d][%d/%d]'%(n,n_cid,len(cids),n_tid,len(tids)))

      #######################################################################
      logging.info('%9s: %9s:'%(cid,tid))
      try:
        rval=rest.Utils.GetURL(base_url+'/%s:%s'%(cid,tid))
      except Exception as e:
        logging.error('HTTP Error (%s): %s'%(res,e))
      txt=('%s'%(str(rval)))
      logging.debug('rval="%s"'%txt)

      rob=re.compile(r'^(.*)(<graphml.*</graphml>).*$',re.I|re.DOTALL)
      score=""; score_note=""; score_type=""; errtxt=""; graphml="";
      m=rob.search(txt)
      if m:
        scorehtm=m.group(1)
        logging.debug('[cid=%s,tid=%s]: scorehtm: "%s"'%(cid,tid,scorehtm))
        graphml=m.group(2)
        rob2=re.compile(r'^.*P value: </i></b>([0-9+-e]+)\s*\(([^\)]+)\).*Type: </i></b><a.*>([^>]+)</a>.*$',re.I|re.DOTALL)
        rob3=re.compile(r'^.*P value: </i></b>([0-9+-e]+)\s*\(([^\)]+)\).*Type: </i></b>([^\n\r]+).*$',re.I|re.DOTALL)
        m2=rob2.search(scorehtm)
        m3=rob3.search(scorehtm)
        if m2:
          score=m2.group(1)
          score_note=m2.group(2)
          score_type=m2.group(3)
        elif m3:
          score=m3.group(1)
          score_note=m3.group(2)
          score_type=m3.group(3)
        logging.info('NOTE [cid=%s,tid=%s]: score=%s ; note="%s" ; type="%s"'%(cid,tid,score,score_note,score_type))
      else:
        errtxt=txt
        #if 'not found' in errtxt:
        logging.error('[cid=%s,tid=%s]: "%s"'%(cid,tid,errtxt))
      if odir and graphml.strip():
        ofile_graphml=(odir+"/%s_%s.graphml"%(cid,tid))
        fout_graphml=open(ofile_graphml,"w+")
        if not fout_graphml: logging.error('Failed to open output file: %s'%ofile_graphml)
        logging.info('%s'%ofile_graphml)
        fout_graphml.write(graphml+'\n')
        fout_graphml.flush()

      fout.write('%s,"%s",%s,"%s","%s","%s"\n'%(cid,tid,score,score_note,score_type,re.sub(r'[\n\r]+',r'\\n',errtxt)))
      fout.flush()
      #######################################################################

      if score:
        n_dtp+=1
        if score_type and not score_type in score_types: score_types[score_type]=1
        score_types[score_type]+=1
        if score_note and not score_note in score_notes: score_notes[score_note]=1
        score_notes[score_note]+=1
      if errtxt:
        if not errtxt in errs: errs[errtxt]=1
        errs[errtxt]+=1
        if errtxt == 'target was not found':
          tids_not_found.add(tid)
        elif errtxt == 'compound was not found':
          cids_not_found.add(cid)
      if tid_nmax and n_tid>=tid_skip+tid_nmax: break
    if cid_nmax and n_cid>=cid_skip+cid_nmax: break

  logging.info("drugs: %d targets: %d"%(n_cid-cid_skip,n_tid-tid_skip))
  logging.info("drug-target queries: %d  drug-target predictions: %d"%(n,n_dtp))
  for score_type in score_types.keys():
    logging.info('score_type "%s": %d'%(score_type,score_types[score_type]))
  for score_note in score_notes.keys():
    logging.info('score_note "%s": %d'%(score_note,score_notes[score_note]))
  for errtxt in errs.keys():
    logging.info('ERRORS: "%s": %d'%(errtxt,errs[errtxt]))

#############################################################################
def DDSimilarity(base_url,cid1,cid2,fout):
  '''Drug-drug similarity query'''
  htm = rest.Utils.GetURL(base_url+'/sim_%s:%s'%(cid1,cid2))
  logging.debug('htm = "%s"'%htm)

#############################################################################
#Kludge: workaround since py-dom-xpath does not allow nodes named "node"!
#############################################################################
def ParseDTPathGraphml(fin_xml):
  '''Parse drug-target graphml.'''
  xml_str=fin_xml.read()
  xml_str=re.sub(r'<node','<nnode',xml_str) #kludge
  xml_str=re.sub(r'/node>','/nnode>',xml_str) #kludge
  doc=None
  try:
    doc=ElementTree.fromstring(xml_str)
  except Exception as e:
    logging.error('XML parse error: %s'%e)
    return False
  return doc

#############################################################################
#We want to add a data node for gene name:
#
#<node id="http://chem2bio2rdf.org/uniprot/resource/gene/KCNJ11">
#       <data key="label">KCNJ11</data>
#       <data key="class">gene</data>
#       <data key="nodesize">1</data>
#       <data key="startnode">no</data>
#</node>
#
#       <data key="name">Potassium channel, inwardly rectifying, subfamily J, member 11</data>
#############################################################################
#"tid","protein_accession","chembl_id","tax_id","target_type","organism","db_source","gene_symbol","pref_name"
#"1","O43451","CHEMBL2074","9606","PROTEIN","Homo sapiens","SWISS-PROT","MGAM","Maltase-glucoamylase"
#"2","O60706","CHEMBL1971","9606","PROTEIN","Homo sapiens","SWISS-PROT","ABCC9","Sulfonylurea receptor 2"
#"3","O76074","CHEMBL1827","9606","PROTEIN","Homo sapiens","SWISS-PROT","PDE5A","Phosphodiesterase 5A"
#############################################################################
def AnnotateDTPathGraphmlTargets(doc,fin_csv):
  '''Annotate graphml with additional data from CSV file.'''

  n_in=0; n_out=0; errtxt=None;

  if not doc:
    return None

  ### Read CSV file containing target data:
  csvReader=csv.DictReader(
	fin_csv,
	fieldnames=None,
	restkey=None,
	restval=None,
	dialect='excel',
	delimiter=',',
	quotechar='"')
  try:
    csvrow=csvReader.next()    ## must do this to get fieldnames
    n_in+=1
  except:
    errtxt=('ERROR: bad ifile: %s'%fin_csv.name)
    return doc
  logging.debug('fieldnames=', csvReader.fieldnames)
  tgt_id_tag='protein_accession'
  tgt_gene_tag='gene_symbol'
  tgt_name_tag='pref_name'
  for tag in (tgt_id_tag,tgt_name_tag,tgt_gene_tag):
    if tag not in csvReader.fieldnames:
      logging.error('%s not in fieldnames'%tag)
      return doc

  tgt_id2name={};
  tgt_gene2id={};
  while True:
    try:
      csvrow=csvReader.next()
      n_in+=1
      tgt_id = csvrow[tgt_id_tag]
      tgt_name = csvrow[tgt_name_tag]
      tgt_gene = csvrow[tgt_gene_tag]
      tgt_gene2id[tgt_gene]=tgt_id
      tgt_id2name[tgt_id]=tgt_name
    except:
      break
  logging.debug('protein ids/names read: %d'%len(tgt_id2name))
  for tgt_id in tgt_id2name.keys():
    logging.debug('protein id: %s'%tgt_id)

  #gene_nodes = xpath.find('/graphml/graph/nnode/data[@key="class" and text()="gene"]/parent::node()', doc)
  gene_nodes = doc.findall('/graphml/graph/nnode/data[@key="class" and text()="gene"]/parent::node()')
  logging.debug('gene count: %d'%len(gene_nodes))

  for node in gene_nodes:
    tgt_id=None
    atts=node.attributes
    for cnode in node.childNodes:
      if cnode.attributes:
        for attName,attValue in cnode.attributes.items():
          if attName=='key' and attValue=='label':
            tgt_gene=cnode.text
            if tgt_gene in tgt_gene2id:
              tgt_id=tgt_gene2id[tgt_gene]
            logging.debug(': gene = "%s" ; tgt = "%s"'%(tgt_gene,tgt_id))

    if tgt_id and tgt_id in tgt_id2name:
      namenode=doc.createElement('data')
      namenode.setAttribute('key','name')
      namenode.appendChild(doc.createTextNode(tgt_id2name[tgt_id]))
      node.appendChild(namenode)
      xml_str=node.toprettyxml()
      xml_str=re.sub(r'\s*[\n\r]+',r'\n',xml_str)
      #xml_str=re.sub(r'<nnode (.*?)</nnode>',r'<node \1</node>',xml_str,re.DOTALL)
      xml_str=re.sub(r'<nnode','<node',xml_str)
      xml_str=re.sub(r'/nnode>','/node>',xml_str)
      logging.debug('%s'%xml_str)

  return doc

#############################################################################
# <node id="http://chem2bio2rdf.org/pubchem/resource/pubchem_compound/5472">
# 	<data key="label">5472</data>
# 	<data key="class">pubchem_compound</data>
# 	<data key="nodesize">1</data>
# 	<data key="startnode">no</data>
# </node>
#############################################################################
# cpd csv fields: cid, sids, synonyms
# sids and synonyms are semicolon-delimited
# synonyms only up to top ten "nicest"
#############################################################################
def AnnotateDTPathGraphmlCompounds(doc,fin_csv):
  '''Annotate graphml with additional data from CSV file.'''

  n_in=0; n_out=0; errtxt=None;

  if not doc: return None

  ### Read CSV file containing target data:
  csvReader=csv.DictReader(
	fin_csv,
	fieldnames=None,
	restkey=None,
	restval=None,
	dialect='excel',
	delimiter=',',
	quotechar='"')
  try:
    csvrow=csvReader.next()    ## must do this to get fieldnames
    n_in+=1
  except:
    errtxt=('ERROR: bad ifile: %s'%fin_csv.name)
    return doc
  logging.debug('fieldnames=', csvReader.fieldnames)

  cid_tag='cid'
  synonyms_tag='synonyms'
  for tag in (cid_tag,synonyms_tag):
    if tag not in csvReader.fieldnames:
      logging.error('%s not in fieldnames'%tag)
      return doc
  cid2synonyms={};
  n_synonyms_total=0;
  while True:
    try:
      csvrow=csvReader.next()
      n_in+=1
      cid = int(csvrow[cid_tag])
      synonyms = csvrow[synonyms_tag].split(';')
      cid2synonyms[cid]=synonyms
      n_synonyms_total+=len(synonyms)
    except:
      break
  logging.debug('cpd ids read: %d ; total synonyms: %d'%(len(cid2synonyms),n_synonyms_total))

  #Find cpd nodes in Graphml:
  #cpd_nodes=xpath.find('/graphml/graph/nnode/data[@key="class" and text()="pubchem_compound"]/parent::node()',doc)
  cpd_nodes=doc.findall('/graphml/graph/nnode/data[@key="class" and text()="pubchem_compound"]/parent::node()')
  n_cid=0;
  for node in cpd_nodes:
    cid=None
    atts=node.attributes
    for cnode in node.childNodes:
      if cnode.attributes:
        for attName,attValue in cnode.attributes.items():
          if attName=='key' and attValue=='label':
            try:
              cid = int(re.sub(r'\(.*\)','',cnode.text))
            except Exception as e:
              logging.error('%s'%e)
    if cid==None: continue
    n_cid+=1

    if cid in cid2synonyms:
      namenode=doc.createElement('data')
      namenode.setAttribute('key','synonyms')
      namenode.appendChild(doc.createTextNode('; '.join(cid2synonyms[cid])))
      node.appendChild(namenode)

      #Also revise cpd label:
      #cpd_label_node=xpath.find('data[@key="label"]',node)[0]
      cpd_label_node=node.find('data[@key="label"]')
      ReplaceNodeText(cpd_label_node, cid2synonyms[cid][0])

      xml_str=node.toprettyxml()
      xml_str=re.sub(r'\s*[\n\r]+',r'\n',xml_str)
      xml_str=re.sub(r'<nnode','<node',xml_str)
      xml_str=re.sub(r'/nnode>','/node>',xml_str)
      logging.debug('%s'%xml_str)

    else:
      logging.debug('cid %d not in csv'%cid)

  logging.info('graphml cid count: %d'%len(cid2synonyms))

  return doc

##############################################################################
def ReplaceNodeText(node, txt):
  if node.firstChild.nodeType != node.TEXT_NODE:
    raise Exception("node does not contain text")
  node.firstChild.replaceWholeText(txt)

##############################################################################
def DTPathGraphml2CIDs(doc,fout):
  #cpd_nodes=xpath.find('/graphml/graph/nnode/data[@key="class" and text()="pubchem_compound"]/parent::node()',doc)
  cpd_nodes=doc.findall('/graphml/graph/nnode/data[@key="class" and text()="pubchem_compound"]/parent::node()')
  n_cid=0;
  for node in cpd_nodes:
    cid=None
    atts=node.attributes
    for cnode in node.childNodes:
      if cnode.attributes:
        for attName,attValue in cnode.attributes.items():
          if attName=='key' and attValue=='label':
            try:
              cid = int(re.sub(r'\(.*\)', '', cnode.text))
            except Exception as e:
              logging.error('Error (Exception): %s'%e)
    if cid==None: continue
    fout.write('%d\n'%cid)
    n_cid+=1
  logging.info('cid count: %d'%n_cid)

##############################################################################
def DTPathGraphml2TIDs(doc,fout):
  #tgt_nodes=xpath.find('/graphml/graph/nnode/data[@key="class" and text()="gene"]/parent::node()',doc)
  tgt_nodes=doc.findall('/graphml/graph/nnode/data[@key="class" and text()="gene"]/parent::node()')
  n_tid=0;
  for node in tgt_nodes:
    tid=None
    atts=node.attributes
    for cnode in node.childNodes:
      if cnode.attributes:
        for attName,attValue in cnode.attributes.items():
          if attName=='key' and attValue=='label':
            try:
              tid = re.sub(r'\(.*\)', '', cnode.text)
            except Exception as e:
              logging.error('Error (Exception): %s'%e)
    if tid==None: continue
    fout.write('%s\n'%tid)
    n_tid+=1
  logging.info('tid count: %d'%n_tid)

##############################################################################
def MergeDTPathGraphmlsDir(idir_graphml):
  import glob
  i=0;
  doc_merged=None;
  for fpath in glob.glob(idir_graphml+'/*.graphml'):
    logging.debug('%s'%fpath)
    fin=open(fpath,"r")
    if not fin: logging.error('Failed to open input file: %s'%fpath)
    doc_this = ParseDTPathGraphml(fin)
    fin.close()
    if not doc_this:
      logging.error('Problem parsing: %s'%fpath)
      continue
    root_node = doc_this.documentElement
    child_nodes = []
    child_node = root_node.firstChild
    while child_node:
      child_nodes.append(child_node)
      child_node = child_node.nextSibling
    logging.debug('%s: root: %s  children: %s'%(fpath,root_node.tagName,','.join(map(lambda n:n.tagName,child_nodes))))
    if i==0:
      doc_merged=doc_this
    else:
      try:
        doc_merged = MergeDTPathGraphmlsPair(doc_merged,doc_this)
      except Exception as e:
        logging.error('(MergeDTPathGraphmlsDir): (Exception): %s'%e)
    i+=1
  logging.debug('merged graphmls: %d'%i)

  return doc_merged

##############################################################################
def MergeDTPathGraphmlsPair(docA,docB):
  '''Merge docB into docA and return docA.'''

  #graphA = xpath.find('/graphml/graph[1]', docA)
  graphA = docA.findall('/graphml/graph[1]')
  if not graphA:
    logging.debug('not graphA')
  else:
    graphA = graphA[0]
  #nodesA = xpath.find('/graphml/graph/nnode', docA)
  nodesA = docA.findall('/graphml/graph/nnode')
  #edgesA = xpath.find('/graphml/graph/edge', docA)
  edgesA = docA.findall('/graphml/graph/edge')
  if not edgesA:
    logging.debug('not edgesA')
  #edgeA1 = xpath.find('/graphml/graph/edge[1]', docA)
  edgeA1 = docA.find('/graphml/graph/edge[1]')
  edgeA1 = edgeA1[0]
  if not edgeA1:
    logging.debug('not edgeA1')

  #nodesB = xpath.find('/graphml/graph/nnode', docB)
  nodesB = docB.findall('/graphml/graph/nnode')
  #edgesB = xpath.find('/graphml/graph/edge', docB)
  edgesB = docB.findall('/graphml/graph/edge')

  for nodeB in nodesB:
    graphA.insertBefore(nodeB,edgeA1)
  for edgeB in edgesB:
    graphA.appendChild(edgeB)
  logging.debug('new nodes: %d edges: %d'%(len(nodesB),len(edgesB)))
  logging.debug('merged nodes: %d edges: %d'%(len(nodesA),len(edgesA)))

  return docA

##############################################################################
def ShowNodeClasses(doc):
  #nodes=xpath.find('/graphml/graph/nnode',doc)
  nodes=doc.findall('/graphml/graph/nnode')
  node_classes = {}
  for node in nodes:
    node_id=None
    node_class=None
    if node.attributes:
      for attName,attValue in node.attributes.items():
        if attName=='id':
          node_id = attValue
          node_class_uri = re.sub(r'/[^/]+$','',node_id)

    for cnode in node.childNodes:
      if cnode.nodeName=='data':
        if cnode.attributes:
          for attName,attValue in cnode.attributes.items():
            if attName=='key' and attValue=='class':
              node_classes[cnode.text] = node_class_uri
  logging.info('Node classes (%d):'%len(node_classes))
  for node_class in sorted(node_classes.keys()):
    logging.info('%18s:\t[%s]'%(node_class,node_classes[node_class]))
  return node_classes

##############################################################################
def ShowEdgeClasses(doc):
  #edges=xpath.find('/graphml/graph/edge',doc)
  edges=doc.findall('/graphml/graph/edge')
  edge_classes = {}
  for edge in edges:
    source_id=None
    source_class=None
    target_id=None
    target_class=None
    if edge.attributes:
      for attName,attValue in edge.attributes.items():
        if attName=='source':
          source_id = attValue
          source_class_uri = re.sub(r'/[^/]+$','',source_id)
        if attName=='target':
          target_id = attValue
          target_class_uri = re.sub(r'/[^/]+$','',target_id)

    for cnode in edge.childNodes:
      if cnode.nodeName=='data':
        if cnode.attributes:
          for attName,attValue in cnode.attributes.items():
            if attName=='key' and attValue=='uri':
              edge_class = cnode.text
              if not edge_class in edge_classes:
                edge_classes[edge_class] = set()
              edge_classes[edge_class].add(tuple(sorted([source_class_uri,target_class_uri])))

  logging.info('Edge classes (%d):'%len(edge_classes))
  for edge_class in sorted(edge_classes.keys()):
    edge_class_name = re.sub(r'^.*/','',edge_class)
    logging.info('%18s:\t[%s]'%(edge_class_name,edge_class))
    for source,target in edge_classes[edge_class]:
      source_name = re.sub(r'^.*/','',source)
      target_name = re.sub(r'^.*/','',target)
      logging.info('\t\t%s : %s'%(source_name,target_name))
  return edge_classes

##############################################################################
def DTPathGraphmlSummary(doc):
  #nodes=xpath.find('/graphml/graph/nnode',doc)
  nodes=doc.findall('/graphml/graph/nnode')
  logging.info('Nodes: %d'%len(nodes))
  #edges=xpath.find('/graphml/graph/edge',doc)
  edges=doc.findall('/graphml/graph/edge')
  logging.info('Edges: %d'%len(edges))

##############################################################################
#Kludge: workaround since py-dom-xpath does not allow nodes named "node"!
def GraphmlDocWrite(doc,fout):
  xml_str = doc.toprettyxml()
  xml_str=re.sub(r'\s*[\n\r]+',r'\n',xml_str)
  #xml_str=re.sub(r'<nnode (.*?)</nnode>',r'<node \1</node>',xml_str,re.DOTALL)
  xml_str=re.sub(r'<nnode','<node',xml_str)
  xml_str=re.sub(r'/nnode>','/node>',xml_str)
  fout.write(xml_str)

##############################################################################
if __name__=='__main__':
  epilog='''\
dtp = Drug Target Prediction;
dtp_annotate_tgts: annotate GraphML (tgts required);
dtp_annotate_cpds: annotate GraphML (cpds required);
dtp_annotate: annotate GraphML (tgts and cpds required);
graphml2cids: find, list PubChem CIDs;
graphml2tids: find, list (Uniprot gene) TIDs;
graphmls_merge: merge all GraphMLs in --i_graphml_dir ;
show_node_classes: show all node classes ;
show_edge_classes: show all edge classes;
summary: summary of GraphML contents
'''
  parser = argparse.ArgumentParser(description="SLAP results GraphML post-processing utility", epilog=epilog)
  ops = [ "summary", "dtp_annotate", "dtp_annotate_tgts", "dtp_annotate_cpds", "graphml2cids", "graphml2tids", "graphmls_merge", "show_node_classes", "show_edge_classes" ]
  parser.add_argument("op", choices=ops, help="operation")
  parser.add_argument("--i_graphml", dest="ifile_graphml", help="input file (GRAPHML)")
  parser.add_argument("--i_graphml_dir", dest="idir_graphml", help="input dir (GRAPHML)")
  parser.add_argument("--i_tgts", dest="ifile_tgts", help="input file, target IDs (CSV)")
  parser.add_argument("--i_cpds", dest="ifile_cpds", help="input file, compound IDs (CSV)")
  parser.add_argument("--o", dest="ofile", help="output (TSV or GraphML)")
  parser.add_argument("-v", "--verbose", dest="verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  fout = open(args.ofile, "w+") if args.ofile else sys.stdout

  fin_graphml = open(args.ifile_graphml, "r") if args.ifile_graphml else None
  fin_tgts = open(args.ifile_tgts, "r") if args.ifile_tgts else None
  fin_cpds = open(args.ifile_cpds, "r") if args.ifile_cpds else None

  t0=time.time()

  if args.op=="dtp_annotate":
    doc = ParseDTPathGraphml(fin_graphml)
    doc = AnnotateDTPathGraphmlTargets(doc, fin_tgts)
    doc = AnnotateDTPathGraphmlCompounds(doc, fin_cpds)
    GraphmlDocWrite(doc, fout)

  elif args.op=="dtp_annotate_tgts":
    doc = ParseDTPathGraphml(fin_graphml)
    doc = AnnotateDTPathGraphmlTargets(doc, fin_tgts)
    GraphmlDocWrite(doc, fout)

  elif args.op=="dtp_annotate_cpds":
    doc = ParseDTPathGraphml(fin_graphml)
    doc = AnnotateDTPathGraphmlCompounds(doc, fin_cpds)
    GraphmlDocWrite(doc, fout)

  elif args.op=="graphml2cids":
    doc = ParseDTPathGraphml(fin_graphml)
    DTPathGraphml2CIDs(doc, fout)

  elif args.op=="graphml2tids":
    doc = ParseDTPathGraphml(fin_graphml)
    DTPathGraphml2TIDs(doc, fout)

  elif args.op=="graphmls_merge":
    doc = MergeDTPathGraphmlsDir(idir_graphml)
    GraphmlDocWrite(doc, fout)

  elif args.op=="show_node_classes":
    doc = ParseDTPathGraphml(fin_graphml)
    node_classes=ShowNodeClasses(doc)

  elif args.op=="show_edge_classes":
    doc = ParseDTPathGraphml(fin_graphml)
    edge_classes=ShowEdgeClasses(doc)

  elif args.op=="summary":
    doc = ParseDTPathGraphml(fin_graphml)
    DTPathGraphmlSummary(doc)

  else:
    parser.error("Invalid operation: {0}".format(args.op))

  logging.info('Elapsed time: %s'%(time.strftime('%Hh:%Mm:%Ss', time.gmtime(time.time()-t0))))
