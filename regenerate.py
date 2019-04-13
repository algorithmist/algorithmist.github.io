#!/usr/bin/env python3

from typing import List

import argparse
import glob
import itertools
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


def run(*args) -> str:
  logging.debug('Running command: %s', args)
  result = subprocess.run(
    args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
  logging.debug('\nStdout: %s\nStderr: %s', result.stdout, result.stderr)
  return result


def GenerateHtml(pandoc_flags: List[str], html_dir: str, post_paths: List[str]):
  # TODO: Process multiple files concurrently.
  for post_path in post_paths:
    file_name = os.path.splitext(os.path.basename(post_path))[0]
    output_path = os.path.join(html_dir, file_name + '.html')
    logging.info('Reading from %s\nWriting to %s', post_path, output_path)
    args = ['pandoc', '-s', '-H', 'header.html'
           ] + pandoc_flags + [post_path, '-o', output_path]
    run(*args)


def ParseArgs():
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument(
    '--posts',
    type=str,
    default='algos',
    help='directory relative to the repo root')
  parser.add_argument(
    '--html',
    type=str,
    default='html',
    help='directory relative to the repo root')
  parser.add_argument(
    '--pandoc_flags', type=str, default='', help='passed verbatim to pandoc')
  parser.add_argument(
    '--log_level',
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
  post_paths = itertools.chain(
    glob.iglob(os.path.join('docs', '*.md')),
    glob.iglob(os.path.join(args.posts, '*.md')))
  pandoc_flags = [arg for arg in args.pandoc_flags.split(' ') if arg]
  GenerateHtml(pandoc_flags, args.html, post_paths)


if __name__ == '__main__':
  try:
    main()
  except subprocess.CalledProcessError as err:
    print(err.stderr)
