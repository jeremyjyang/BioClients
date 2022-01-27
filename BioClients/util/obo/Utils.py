#! /usr/bin/env python3
"""
Developed and tested with doid.obo (Disease Ontology)
"""
import sys,os,argparse,re,logging

#############################################################################
def OBO2CSV(fin, fout):
  n_in=0; n_rec=0; n_out=0;
  tags = ['id', 'name', 'namespace', 'alt_id', 'def', 'subset', 'synonym', 'xref', 'is_a', 'is_obsolete']
  fout.write('\t'.join(tags)+'\n')
  reclines=[];
  while True:
    line=fin.readline()
    if not line: break
    n_in+=1
    line=line.strip()
    if reclines:
      if line == '':
        row = OBO2CSV_Record(reclines)
        n_rec+=1
        vals=[]
        is_obsolete=False
        for tag in tags:
          if tag in row:
            val=row[tag]
            if tag in ('def', 'synonym'):
              val=re.sub(r'^"([^"]*)".*$', r'\1', val)
            else:
              val=re.sub(r'^"(.*)"$', r'\1', val)
          else:
            val=''
          if tag=='is_obsolete': is_obsolete = bool(val.lower() == "true")
          vals.append(val)
        if not is_obsolete:
          fout.write('\t'.join(vals)+'\n')
          n_out+=1
        reclines=[];
      else:
        reclines.append(line)
    else:
      if line == '[Term]':
        reclines.append(line)
      else: continue

  logging.info("input lines: %d; input records: %d ; output lines: %d"%(n_in, n_rec, n_out))

#############################################################################
def OBO2CSV_Record(reclines):
  vals={};
  if reclines[0] != '[Term]':
    logging.error('reclines[0] = "%s"'%reclines[0])
    return
  for line in reclines[1:]:
    line = re.sub(r'\s*!.*$','',line)
    k,v = re.split(r':\s*', line, maxsplit=1)
    if k=='xref' and not re.match(r'\S+:\S+$',v): continue
    if k not in vals: vals[k]=''
    vals[k] = '%s%s%s'%(vals[k],(';' if vals[k] else ''),v)
  return vals

#############################################################################
