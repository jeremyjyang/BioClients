import os,sys,unittest

from .. import drugcentral

class TestAPI(unittest.TestCase):

  def __init__(self, methodName="test_01"):
    super().__init__(methodName)
    self.params = drugcentral.ReadParamFile(os.environ['HOME']+"/.drugcentral.yaml")
    self.dbcon = drugcentral.Utils.Connect(self.params['DBHOST'], self.params['DBPORT'], self.params['DBNAME'], self.params['DBUSR'], self.params['DBPW'])

  def test_01(self):
    self.assertTrue(type(drugcentral.Version(self.dbcon)) is not None)

  def test_02(self):
    self.assertEqual(drugcentral.Version(self.dbcon).shape[0], 1)

  def test_03(self):
    self.assertTrue(drugcentral.Describe(self.dbcon).shape[0]>10)

  def test_04(self):
    self.assertTrue(drugcentral.Counts(self.dbcon).shape[0]>10)

  def test_05(self):
    df = drugcentral.ListStructures(self.dbcon)
    self.assertTrue(df.shape[0]>4000)

  def test_06(self):
    df = drugcentral.ListStructures2Smiles(self.dbcon)
    self.assertTrue(df.shape[0]>4000)

  def test_07(self):
    df = drugcentral.ListProducts(self.dbcon)
    self.assertTrue(df.shape[0]>4000)

  def test_08(self):
    df = drugcentral.ListActiveIngredients(self.dbcon)
    self.assertTrue(df.shape[0]>4000)

  def test_09(self):
    self.assertTrue(drugcentral.ListIndications(self.dbcon).shape[0]>100)

  def test_10(self):
    self.assertTrue(drugcentral.SearchIndications(self.dbcon, "Alzheimer").shape[0]>0)

  def test_11(self):
    self.assertTrue(drugcentral.GetStructure(self.dbcon, ["1725"]).shape[0]==1)

  def test_12(self):
    self.assertTrue(drugcentral.GetStructureBySynonym(self.dbcon, ["zantac"]).shape[0]==1)

  def test_13(self):
    self.assertTrue(drugcentral.GetStructureIds(self.dbcon, ["1725"]).shape[0]>5)

  def test_14(self):
    self.assertTrue(drugcentral.GetStructureProducts(self.dbcon, ["1725"]).shape[0]>10)

#############################################################################
if __name__ == '__main__':
  unittest.main(verbosity=2)
