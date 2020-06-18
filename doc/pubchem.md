# `BioClients.pubchem`

## PubChem

Tools for obtaining and processing PubChem data (REST, SOAP, FTP).

* <https://pubchem.ncbi.nlm.nih.gov>

### PUG-REST

* <https://pubchemdocs.ncbi.nlm.nih.gov/pug-rest>
* <https://pubchem.ncbi.nlm.nih.gov/rest/pug>

```
python3 -m BioClients.pubchem.Client --name remdesivir name2sid
python3 -m BioClients.pubchem.Client --name remdesivir name2cid
```

### PUG-SOAP

The SOAP API was developed first, and includes functionality not available
via PUG-REST (e.g. Standardize).

* <https://pubchemdocs.ncbi.nlm.nih.gov/pug-soap>
* <https://pubchem.ncbi.nlm.nih.gov/pug_soap/pug_soap.cgi?wsdl>

```
python3 -m BioClients.pubchem.soap.Search -h
python3 -m BioClients.pubchem.soap.Search --qsmi "CCN(=O)=O" --searchtype standardize
```
