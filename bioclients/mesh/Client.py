#!/usr/bin/env python3
"""
MeSH XML utility functions.

 MeSH XML
 Download: https://www.nlm.nih.gov/mesh/download_mesh.html
 Doc: https://www.nlm.nih.gov/mesh/xml_data_elements.html
  
 <DescriptorRecord DescriptorClass="1">
 1 = Topical Descriptor.
 2 = Publication Types, for example, 'Review'.
 3 = Check Tag, e.g., 'Male' (no tree number)
 4 = Geographic Descriptor (Z category of tree number).
  
 Category "C" : Diseases
 Category "F" : Psychiatry and Psychology
 Category "F03" : Mental Disorders
 Thus, include "C*" and "F03*" only.
 Terms can have multiple TreeNumbers; diseases can be in non-disease cateories, in addition to a disease category.
"""
###
import sys,os,re,argparse,logging

from .. import mesh

BRANCHES={
	'A':'Anatomy',
	'B':'Organisms',
	'C':'Diseases',
	'D':'Chemicals and Drugs',
	'E':'Analytical, Diagnostic and Therapeutic Techniques, and Equipment',
	'F':'Psychiatry and Psychology',
	'G':'Phenomena and Processes',
	'H':'Disciplines and Occupations',
	'I':'Anthropology, Education, Sociology, and Social Phenomena',
	'J':'Technology, Industry, and Agriculture',
	'K':'Humanities',
	'L':'Information Science',
	'M':'Named Groups',
	'N':'Health Care',
	'V':'Publication Characteristics',
	'Z':'Geographicals'}

#############################################################################
if __name__=='__main__':
  BRANCH='C'
  EPILOG = f"""
operations:
desc2csv: descriptors XML input;
supp2csv: supplementary records XML input;
Branches:
	{"; ".join([f"{k}: {BRANCHES[k]}" for k in sorted(BRANCHES.keys())])}
"""
  parser = argparse.ArgumentParser(description='MeSH XML utility', epilog=EPILOG)
  ops=['desc2csv', 'supp2csv']
  parser.add_argument("op", choices=ops, help='operation')
  parser.add_argument("--i", dest="ifile", help="input MeSH XML file [stdin]")
  parser.add_argument("--o", dest="ofile", help="output file (TSV)")
  parser.add_argument("--branch", choices=BRANCHES, default=BRANCH, help="top-level branch of MeSH tree")
  parser.add_argument("--force", action="store_true", help="ignore UTF-8 encoding errors")
  parser.add_argument("-v", "--verbose", default=0, action="count")
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s:%(message)s', level=(logging.DEBUG if args.verbose>1 else logging.INFO))

  fin = open(args.ifile, "r") if args.ifile else sys.stdin

  fout = open(args.ofile, "w") if args.ofile else sys.stdout

  if args.op == "desc2csv":
    mesh.Desc2Csv(args.branch, fin, fout)

  elif args.op == "supp2csv":
    mesh.Supp2Csv(args.branch, fin, fout)

  else:
    parser.error(f"Invalid operation: {args.op}")
