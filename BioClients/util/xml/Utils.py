#!/usr/bin/env python3
"""
	XML utility functions.
"""
import sys,os,re,gzip,argparse,logging

from xml.etree import ElementTree
from xml.parsers import expat

#############################################################################
def GetLeafValsByTagName(root, tag):
  vals=[]
  for node in root.iter(tag):
    txt=node.text
    if txt: vals.append(txt)
  return vals

#############################################################################
def GetAttr(root, tag, attname):
  vals=[]
  for node in root.iter(tag):
    if attname in node.attrib:
      vals.append(node.attrib[attname])
  return vals

#############################################################################
def GetNodeAttr(node, attname):
  return node.attrib[attname] if attname in node.attrib else None

#############################################################################
def Describe(fin):
  n_elem=0; n_term=0; tags={};
  et_itrabl = ElementTree.iterparse(fin, events=("start", "end"))
  for event,elem in et_itrabl:
    n_elem+=1
    if event=='start':
      if elem.tag not in tags:
        tags[elem.tag]=0
      tags[elem.tag]+=1
    logging.debug('event:{}, elem.tag:{}, elem.text:{}'.format(event, elem.tag, elem.text))
    for k,v in elem.attrib.items():
      logging.debug('elem.attrib["{}"]: {}'.format(k, v))
    n_term+=1
  logging.debug('n_elem: {}; n_term: {}'.format(n_elem, n_term))
  for tag in sorted(tags.keys()):
    logging.info('{}: {}'.format(tag, tags[tag]))

#############################################################################
def XML2TSV(xp, ns, fin, fout):
  n_entity=0; tags=[];
  tree = ElementTree.parse(fin)
  logging.debug('root.tag <{}>'.format(tree.getroot().tag))
  itr = tree.iterfind(xp)
  for elem in itr:
    logging.debug('elem.tag <{}>'.format(elem.tag))
    n_entity+=1
    vals={};
    if not tags:
      tags = [re.sub(r'^{.*}', '', se.tag) for se in list(elem)]
      tags = sorted(tags)
      fout.write("\t".join(tags)+"\n")
    for subelem in list(elem):
      val = subelem.text.strip() if subelem.text else ""
      logging.debug('subelem.tag <{}>; text=\"{}\"'.format(subelem.tag, val))
      vals[re.sub(r'^{.*}', '', subelem.tag)] = val
    fout.write("\t".join([vals[tag] if tag in vals else "" for tag in tags])+"\n")
  logging.info('n_entity <{}>: {}'.format(xp, n_entity))

#############################################################################
def MatchXPath(xp, ns, fin):
  n_node=0;
  fout.write("xpath\tmatch\n")
  tree = ElementTree.parse(fin)
  itr = tree.iterfind(xp)
  for node in itr:
    n_node+=1;
    txt = node.text if node.text else ''
    fout.write("{}\t{}\n".format(xp, txt))
  logging.info("matches: {}".format(n_node))

#############################################################################
if __name__=="__main__":
  parser = argparse.ArgumentParser(description="XML utility", epilog="clean: UTF-8 encoding compliant")
  ops = ["match_xpath", "describe", "clean", "xml2tsv"]
  parser.add_argument("op", choices=ops, help="operation")
  parser.add_argument("--i", dest="ifile", help="input XML file")
  parser.add_argument("--xpath", help="xpath pattern")
  parser.add_argument("--namespace", help="XML namespace")
  parser.add_argument("--force", type=bool, help="ignore UTF-8 encoding errors")
  parser.add_argument("--o", dest="ofile", help="output XML file")
  parser.add_argument("-v", "--verbose", action="count", default=0)
  args = parser.parse_args()

  logging.basicConfig(format="%(levelname)s:%(message)s", level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  codecs_mode = "ignore" if args.force else "replace"

  if args.ifile:
    if re.match(r'^.*\.gz$', args.ifile):
      fin = gzip.open(args.ifile)
    else:
      fin = open(args.ifile, "r")
  else:
    fin = sys.stdin

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  if args.op == "describe":
    Describe(fin)

  elif args.op == "clean":
    root = ElementTree.parse(fin)
    fin.close()
    root.write(fout, encoding="UTF-8", xml_declaration=True)

  elif args.op == "match_xpath":
    if not (args.xpath and args.ifile):
      parser.error("--xpath required.")
    MatchXPath(args.xpath, args.namespace, fin) 

  elif args.op == "xml2tsv":
    if not args.xpath:
      parser.error("--xpath required.")
    XML2TSV(args.xpath, args.namespace, fin, fout)

  else:
    parser.error("Invalid operation. %s"%(args.op))
