import unittest

ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class TestAllowedFileFunction(unittest.TestCase):

    def test_filename_with_extension(self):
        self.assertTrue(allowed_file('example.txt'))

    def test_filename_without_extension(self):
        self.assertFalse(allowed_file('example'))

    def test_filename_with_allowed_extension(self):
        self.assertTrue(allowed_file('example.txt'))

    def test_filename_with_disallowed_extension(self):
        self.assertFalse(allowed_file('example.exe'))

    def test_filename_with_multiple_extensions(self):
        self.assertTrue(allowed_file('example.tar.gz'))

    def test_empty_filename(self):
        self.assertFalse(allowed_file(''))

if __name__ == '__main__':
    unittest.main()
