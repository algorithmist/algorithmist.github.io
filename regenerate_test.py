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
    mock_iglob.return_value = ['a/b/c/foo.md', 'a/b/c/bar.md']
    regenerate.CopyFiles(input_dir, site_root, '*.md')
    mock_iglob.assert_called_with(os.path.join(input_dir, '*.md'))
    mock_copy2.assert_has_calls([
      unittest.mock.call('a/b/c/foo.md', 'build/a/b/c'),
      unittest.mock.call('a/b/c/bar.md', 'build/a/b/c'),
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
    pandoc_flags = 'pandoc_flags'
    dir_foo = unittest.mock.MagicMock()
    dir_foo.name = 'foo'
    dir_foo.path = 'algos/foo'
    dir_bar = unittest.mock.MagicMock()
    dir_bar.name = 'bar'
    dir_bar.path = 'algos/bar'
    post_dirs = [dir_foo, dir_bar]
    mocked_files = {
      'algos/foo/*': [
        'algos/foo/a.md',
        'algos/foo/b.md',
      ],
      'algos/bar/*': [
        'algos/bar/c.js',
        'algos/bar/c_test.js',
        'algos/bar/c.test.js',
        'algos/bar/d.md',
      ]
    }
    mock_iglob.side_effect = lambda args: mocked_files[args]
    regenerate.GeneratePosts(site_root, post_dirs, pandoc_flags)
    mock_output.assert_has_calls([
      unittest.mock.call('algos/foo/a.md', 'build/foo/a.html', pandoc_flags),
      unittest.mock.call('algos/foo/b.md', 'build/foo/b.html', pandoc_flags),
      unittest.mock.call('algos/bar/d.md', 'build/bar/d.html', pandoc_flags),
    ])
    mock_copy2.assert_called_once_with('algos/bar/c.js', 'build/bar/c.js')


if __name__ == '__main__':
  unittest.main()
