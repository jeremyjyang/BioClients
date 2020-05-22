import os,sys,unittest

from .. import drugcentral

class TestAPI(unittest.TestCase):

  def __init__(self, methodName=""):
    super().__init__(methodName)
    self.params = drugcentral.ReadParamFile(os.environ['HOME']+"/.drugcentral.yaml")
    self.dbcon = drugcentral.Utils.Connect(self.params['DBHOST'], self.params['DBPORT'], self.params['DBNAME'], self.params['DBUSR'], self.params['DBPW'])

  def test_Version(self):
    self.assertTrue(type(drugcentral.Version(self.dbcon)) is not None)

  def test_Version_02(self):
    self.assertEqual(drugcentral.Version(self.dbcon).shape[0], 1)

  def test_Describe(self):
    self.assertTrue(drugcentral.Describe(self.dbcon).shape[0]>10)

  def test_Counts(self):
    self.assertTrue(drugcentral.Counts(self.dbcon).shape[0]>10)

  def test_ListStructures(self):
    df = drugcentral.ListStructures(self.dbcon)
    self.assertTrue(df.shape[0]>4000)

  def test_ListStructures2Smiles(self):
    df = drugcentral.ListStructures2Smiles(self.dbcon)
    self.assertTrue(df.shape[0]>4000)

  def test_ListProducts(self):
    df = drugcentral.ListProducts(self.dbcon)
    self.assertTrue(df.shape[0]>4000)

  def test_ListActiveIngredients(self):
    df = drugcentral.ListActiveIngredients(self.dbcon)
    self.assertTrue(df.shape[0]>4000)

  def test_ListIndications(self):
    self.assertTrue(drugcentral.ListIndications(self.dbcon).shape[0]>100)

  def test_SearchIndications(self):
    self.assertTrue(drugcentral.SearchIndications(self.dbcon, "Alzheimer").shape[0]>0)

  def test_GetStructure(self):
    self.assertTrue(drugcentral.GetStructure(self.dbcon, ["1725"]).shape[0]==1)

  def test_GetStructureBySynonym(self):
    self.assertTrue(drugcentral.GetStructureBySynonym(self.dbcon, ["zantac"]).shape[0]==1)

  def test_GetStructureIds(self):
    self.assertTrue(drugcentral.GetStructureIds(self.dbcon, ["1725"]).shape[0]>5)

  def test_GetStructureProducts(self):
    self.assertTrue(drugcentral.GetStructureProducts(self.dbcon, ["1725"]).shape[0]>10)

#############################################################################
if __name__ == '__main__':
  unittest.main(verbosity=2)
