# `BioClients.jensenlab`

## JensenLab

* <https://api.jensenlab.org/About>

Currently focused on [DISEASES](https://diseases.jensenlab.org/).
Three source channels are defined:

* Experiments
* Knowledge
* Textmining

```
python3 -m BioClients.jensenlab.Client get_disease_genes --ids "DOID:10652" --channel "Knowledge"
```
