#!/usr/bin/env python3
'''
	XML utility functions.
'''
import sys,os,re,argparse,logging

from xml.etree import ElementTree #newer
from xml.parsers import expat


#############################################################################
def DOM_NodeText(node):
  #logging.info('DEBUG: type(node) = %s'%str(type(node)))
  if type(node) in (ElementTree.Element, ElementTree.ElementTree):
    return DOM_NodeText_ET(node)
  else:
    return DOM_NodeText_minidom(node)

#############################################################################
def DOM_NodeText_ET(node):
  return node.text

#############################################################################
def DOM_NodeText_minidom(node):
  for cnode in node.childNodes:
    #if cnode.nodeName=='#text':
    if cnode.nodeType == cnode.TEXT_NODE:
      return cnode.nodeValue.strip()
  return ''

#############################################################################
def DOM_GetLeafValsByTagName(root, tag):
  if type(root) in (ElementTree.Element, ElementTree.ElementTree):
    return DOM_GetLeafValsByTagName_ET(root, tag)
  else:
    return DOM_GetLeafValsByTagName_minidom(root, tag)

#############################################################################
def DOM_GetLeafValsByTagName_ET(root, tag):
  vals=[]
  for node in root.iter(tag):
    txt=DOM_NodeText(node)
    if txt: vals.append(txt)
  return vals

#############################################################################
def DOM_GetLeafValsByTagName_minidom(root, tag):
  vals=[]
  for node in root.getElementsByTagName(tag):
    txt=DOM_NodeText(node)
    if txt: vals.append(txt)
  return vals

#############################################################################
def DOM_GetAttr(root, tag, attname):
  if type(root) in (ElementTree.Element, ElementTree.ElementTree):
    return DOM_GetAttr_ET(root, tag, attname)
  else:
    return DOM_GetAttr_minidom(root, tag, attname)

#############################################################################
def DOM_GetAttr_ET(root, tag, attname):
  vals=[]
  for node in root.iter(tag):
    if attname in node.attrib:
      vals.append(node.attrib[attname])
  return vals

#############################################################################
def DOM_GetAttr_minidom(root, tag, attname):
  vals=[]
  for node in root.getElementsByTagName(tag):
    if attname in node.attributes:
      vals.append(node.attributes[attname].value)
  return vals

#############################################################################
def DOM_GetNodeAttr(node, attname):
  if type(node) in (ElementTree.Element, ElementTree.ElementTree):
    return DOM_GetNodeAttr_ET(node, attname)
  else:
    return DOM_GetNodeAttr_minidom(node, attname)

#############################################################################
def DOM_GetNodeAttr_ET(node, attname):
  return node.attrib[attname] if attname in node.attrib else None

#############################################################################
def DOM_GetNodeAttr_minidom(node, attname):
  return node.attributes[attname].value if attname in node.attributes else None

#############################################################################
def XpathFind(xp, root):
  if type(root) in (ElementTree.Element, ElementTree.ElementTree):
    return root.findall(xp)
  else:
    import xpath #for minidom
    return xpath.find(xp, root)

#############################################################################
def Describe(fin):
  tags={}
  et_itrabl = ElementTree.iterparse(fin, events=("start", "end")) #iterable
  et_itr = iter(et_itrabl) #iterator
  event, root = et_itr.next() #root element
  n_elem=0; n_term=0;
  while True:
    try:
      ee = et_itr.next()
    except Exception as e:
      break
    event, elem = ee
    n_elem+=1
    if event == 'start':
      if elem.tag not in tags:
        tags[elem.tag] = 0
      tags[elem.tag] += 1
    logging.debug('event:%6s, elem.tag:%6s, elem.text:%6s'%(event, elem.tag, elem.text))
    for k,v in elem.attrib.items():
      logging.debug('\telem.attrib["%s"]: %s'%(k, v))
    n_term+=1
  logging.debug('n_elem: %d'%n_elem)
  logging.debug('n_term: %d'%n_term)
  for tag in sorted(tags.keys()):
    logging.info('%24s: %6d'%(tag, tags[tag]))

#############################################################################
if __name__=='__main__':
  parser = argparse.ArgumentParser(description='XML utility', epilog='clean: UTF-8 encoding compliant')

  ops = ['match_xpath', 'describe', 'clean']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="input XML file")
  parser.add_argument("--xpath", help="xpath pattern")
  parser.add_argument("--force", type=bool, help="ignore UTF-8 encoding errors")
  parser.add_argument("--o", dest="ofile", help="output XML file")
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  codecs_mode = "ignore" if args.force else "replace"

  fin = open(args.ifile, "r") if args.ifile else sys.stdin
  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  if args.op == "describe":
    Describe(fin)

  elif args.op == "clean":
    try:
      root = ElementTree.parse(fin)
    except Exception as e:
      parser.error('ElementTree.parse(): %s'%str(e))
    fin.close()
    root.write(fout, encoding="UTF-8", xml_declaration=True)

  elif args.op == "match_xpath":
    try:
      root = ElementTree.parse(fin)
    except Exception as e:
      parser.error('ElementTree.parse(): %s'%str(e))
    fin.close()
    if not (xp and ifile):
      parser.error('--i and --xpath required.')
    nodes = XpathFind(xp, root)
    fout.write('"xpath","match"\n')
    for i,node in enumerate(nodes):
      fout.write('"%s","%s"\n'%(xp, DOM_NodeText(node)))
    logging.info('matches: %d'%len(nodes))

  else:
    parser.error('Invalid operation. %s'%(args.op))
