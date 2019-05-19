import os
import regenerate
import unittest
import unittest.mock


class TestRegenerate(unittest.TestCase):

  @unittest.mock.patch('os.makedirs')
  @unittest.mock.patch('glob.iglob')
  @unittest.mock.patch('shutil.copy2')
  def test_CopyFiles(self, mock_copy2, mock_iglob, _):
    input_dir = 'a/b/c'
    site_root = 'build'
    mock_iglob.return_value = [
      os.path.join(input_dir, 'foo.md'),
      os.path.join(input_dir, 'bar.md')
    ]
    regenerate.CopyFiles(input_dir, site_root, '*.md')
    mock_iglob.assert_called_with(os.path.join(input_dir, '*.md'))
    mock_copy2.assert_has_calls([
      unittest.mock.call(input_file, os.path.join(site_root, input_dir))
      for input_file in mock_iglob.return_value
    ])

  @unittest.mock.patch('regenerate.OutputHtml')
  def test_GenerateDocs(self, mock_output):
    site_root = 'build'
    doc_paths = ['a/b/c/foo.md', 'd/e/f/bar.md']
    pandoc_flags = 'pandoc flags'
    regenerate.GenerateDocs(site_root, doc_paths, pandoc_flags)
    mock_output.assert_has_calls([
      unittest.mock.call('a/b/c/foo.md', 'build/foo.html', pandoc_flags),
      unittest.mock.call('d/e/f/bar.md', 'build/bar.html', pandoc_flags),
    ])

  @unittest.mock.patch('regenerate.OutputHtml')
  @unittest.mock.patch('os.makedirs')
  @unittest.mock.patch('glob.iglob')
  @unittest.mock.patch('shutil.copy2')
  def test_GeneratePosts(self, mock_copy2, mock_iglob, _, mock_output):
    site_root = 'build'
    post_dirs = []
    pandoc_flags = 'pandoc_flags'
    regenerate.GeneratePosts(site_root, post_dirs, pandoc_flags)


if __name__ == '__main__':
  unittest.main()
