#!/usr/bin/env python3

from typing import List, Iterator

import argparse
import glob
import logging
import os
import shutil
import subprocess

logger = logging.getLogger(__name__)

LOGGING_LEVELS = {
  'NOTSET': logging.NOTSET,
  'DEBUG': logging.DEBUG,
  'INFO': logging.INFO,
  'WARNING': logging.WARNING,
  'ERROR': logging.ERROR,
  'CRITICAL': logging.CRITICAL,
}

DEFAULT_PANDOC_FLAGS = [
  '-s',
  '--template=template.html',
  '--base-header-level=2',
  '--katex',
  '--lua-filter=diagram-generator.lua',
]


def run(*args) -> str:
  '''Helper function to run external commands, i.e. pandoc'''
  logging.debug('Running command: %s', args)
  result = subprocess.run(args,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          encoding='utf-8')
  logging.debug('\nStdout: %s\nStderr: %s', result.stdout, result.stderr)
  return result


def output_html(input_path, output_path, pandoc_flags):
  '''Run pandoc to process a single Markdown file into HTML'''
  # TODO: Process multiple files concurrently.
  logging.info('Reading from %s\nWriting to %s', input_path, output_path)
  args = (['pandoc'] + DEFAULT_PANDOC_FLAGS + pandoc_flags +
          [input_path, '-o', output_path, '-f', 'markdown', '-t', 'html'])
  run(*args)


def generate_docs(site_root: str, doc_paths: Iterator[str],
                  pandoc_flags: List[str]):
  '''Generate documentation files: Contributing and About pages'''
  for doc_path in doc_paths:
    output_path = os.path.join(site_root,
                               os.path.basename(doc_path)[:-2] + 'html')
    output_html(doc_path, output_path, pandoc_flags)


def generate_posts(site_root: str, post_dirs: Iterator[os.DirEntry],
                   pandoc_flags: List[str]):
  '''Generate all algorithm post pages'''
  for post_dir in post_dirs:
    output_dir = os.path.join(site_root, post_dir.name)
    os.makedirs(output_dir, exist_ok=True)
    # Compile all the markdown to html. Copy everything else.
    post_files = glob.iglob(os.path.join(post_dir.path, '*'))
    for input_path in post_files:
      logging.info('Processing %s', input_path)
      (name, ext) = os.path.splitext(os.path.basename(input_path))
      if name.endswith('test'):
        continue
      output_path = os.path.join(output_dir, name)
      if ext == '.md':
        output_html(
          input_path, output_path + '.html', pandoc_flags + [
            '--toc',
            '--extract-media=%s' % output_path, '--variable=is_article:true'
          ])
      else:
        shutil.copy2(input_path, output_path + ext)


def copy_files(input_dir: str, site_root: str, glob_expr: str):
  '''Copy static files to the output directory'''
  output_dir = os.path.join(site_root, input_dir)
  os.makedirs(output_dir, exist_ok=True)
  input_files = glob.iglob(os.path.join(input_dir, glob_expr))
  for input_file in input_files:
    shutil.copy2(input_file, output_dir)


def parse_args():
  '''Parse command-line arguments'''
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument('--posts',
                      type=str,
                      default='algos',
                      help='directory relative to the repo root')
  parser.add_argument('--docs',
                      type=str,
                      default='docs',
                      help='directory relative to the repo root')
  parser.add_argument('--css',
                      type=str,
                      default='css',
                      help='directory relative to the repo root')
  parser.add_argument('--site_root',
                      type=str,
                      default='build',
                      help='output dir, relative to the repo root')
  parser.add_argument('--pandoc_flags',
                      type=str,
                      default='',
                      help='passed verbatim to pandoc')
  parser.add_argument('--log_level',
                      type=str,
                      help='controls the script\'s logging level',
                      default='ERROR')
  return parser.parse_args()


def is_root_dir():
  '''Helper function to test if we're in the root directory'''
  root_dir = run('git', 'rev-parse', '--show-toplevel').stdout.strip()
  return root_dir == os.getcwd()


def main():
  '''Main point of entry'''
  args = parse_args()
  logger.root.setLevel(LOGGING_LEVELS[args.log_level])
  if not is_root_dir():
    logging.error('Must be run from the root git directory')
    return
  pandoc_flags = [arg for arg in args.pandoc_flags.split(' ') if arg]
  # Output algos/algo_name/*.md as site_root/algo_name/*.html
  post_dirs = [path for path in os.scandir(args.posts) if path.is_dir()]
  generate_posts(args.site_root, post_dirs, pandoc_flags)
  # Output docs/*.md as site_root/*.html
  doc_paths = glob.iglob(os.path.join(args.docs, '*.md'))
  generate_docs(args.site_root, doc_paths, pandoc_flags)
  # Copy css into site_root/css
  copy_files(args.css, args.site_root, '*.css')


if __name__ == '__main__':
  try:
    main()
  except subprocess.CalledProcessError as err:
    print(err.stderr)
