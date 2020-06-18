# `BioClients.mesh`

##  MeSH

From the NIH National Library of Medicine (NLM).
Currently XML processing tools only.

* <https://meshb.nlm.nih.gov/>

MeSH XML utility functions.

 MeSH XML
 Download: <https://www.nlm.nih.gov/mesh/download_mesh.html>
 Doc: <https://www.nlm.nih.gov/mesh/xml_data_elements.html>
  
 &lt;DescriptorRecord DescriptorClass="1"&gt;
 1 = Topical Descriptor.
 2 = Publication Types, for example, 'Review'.
 3 = Check Tag, e.g., 'Male' (no tree number)
 4 = Geographic Descriptor (Z category of tree number).
  
 Category "C" : Diseases
 Category "F" : Psychiatry and Psychology
 Category "F03" : Mental Disorders
 Thus, include "C\*" and "F03\*" only.
 Terms can have multiple TreeNumbers; diseases can be in non-disease cateories, in addition to a disease category.
