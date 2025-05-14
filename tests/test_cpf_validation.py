import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import validate_cpf

class TestCPFValidation(unittest.TestCase):
    def test_valid_cpf(self):
        self.assertTrue(validate_cpf('529.982.247-25'))
        self.assertTrue(validate_cpf('52998224725'))
    
    def test_invalid_cpf(self):
        self.assertFalse(validate_cpf('111.111.111-11'))
        self.assertFalse(validate_cpf('123.456.789-10'))
        
    def test_malformed_cpf(self):
        self.assertFalse(validate_cpf('1234567'))
        self.assertFalse(validate_cpf('abc.def.ghi-jk'))
        self.assertFalse(validate_cpf(''))
        self.assertFalse(validate_cpf(None))

if __name__ == '__main__':
    unittest.main()
