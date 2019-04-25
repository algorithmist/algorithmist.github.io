#!/usr/bin/env python3

from typing import List

import argparse
import glob
import logging
import os
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
]


def run(*args) -> str:
  logging.debug('Running command: %s', args)
  result = subprocess.run(args,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          encoding='utf-8')
  logging.debug('\nStdout: %s\nStderr: %s', result.stdout, result.stderr)
  return result


def GenerateHtml(pandoc_flags: List[str], doc_paths: List[str],
                 post_paths: List[str], site_root: str):
  # TODO: Process multiple files concurrently.
  def output(input_path, output_path):
    logging.info('Reading from %s\nWriting to %s', input_path, output_path)
    args = (['pandoc'] + DEFAULT_PANDOC_FLAGS + pandoc_flags +
            [input_path, '-o', output_path])
    run(*args)

  for post_path in post_paths:
    output_dir = os.path.join(site_root, os.path.splitext(post_path)[0])
    if not os.path.exists(output_dir):
      os.makedirs(output_dir)
    output_path = os.path.join(output_dir, 'index.html')
    output(post_path, output_path)
  for doc_path in doc_paths:
    output_path = os.path.join(site_root,
                               os.path.basename(doc_path)[:-2] + 'html')
    output(doc_path, output_path)


def ParseArgs():
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


def IsRootDir():
  root_dir = run('git', 'rev-parse', '--show-toplevel').stdout.strip()
  return root_dir == os.getcwd()


def main():
  args = ParseArgs()
  logger.root.setLevel(LOGGING_LEVELS[args.log_level])
  if not IsRootDir():
    logging.error('Must be run from the root git directory')
    return
  doc_paths = glob.iglob(os.path.join(args.docs, '*.md'))
  post_paths = glob.iglob(os.path.join(args.posts, '*.md'))
  pandoc_flags = [arg for arg in args.pandoc_flags.split(' ') if arg]
  GenerateHtml(pandoc_flags, doc_paths, post_paths, args.build_dir)


if __name__ == '__main__':
  try:
    main()
  except subprocess.CalledProcessError as err:
    print(err.stderr)
