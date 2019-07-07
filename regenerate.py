#!/usr/bin/env python3

from typing import List, Iterator
from csv import reader

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

ARTICLE_TEMPLATE_FILE_PATH = 'template.html'

DEFAULT_PANDOC_FLAGS = [
  '-s',
  f'--template={ARTICLE_TEMPLATE_FILE_PATH}',
  '--base-header-level=2',
  '--katex',
]

TITLE_LIST_PATH = '/tmp/algorithmist-titles.csv'

FILTER_FLAGS = [
  '--lua-filter=diagram-generator.lua',
  # Set the output filepath in metadata for the metadata extraction filter
  f'--metadata=posts_list_filename:{TITLE_LIST_PATH}',
  '--lua-filter=extract-metadata.lua',
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
          ] + FILTER_FLAGS)
      else:
        shutil.copy2(input_path, output_path + ext)


def generate_root(site_root: str, base_template_path: str,
                  root_template_path: str):
  '''Generate the site root (index.html)'''
  with open(base_template_path, 'r') as base_template_file:
    base_template = base_template_file.read()

  with open(root_template_path, 'r') as root_template_file:
    root_template = root_template_file.read()

  def make_card(row):
    '''Utility function to make a single "card" for an article on the site root'''
    article_path, title, subtitle = row
    card = root_template.replace('{{FILENAME}}', article_path)
    card = card.replace('{{TITLE}}', title)
    card = card.replace('{{SUBTITLE}}', subtitle)
    return card

  # TODO: Right now, this generates cards in the order they were added to TITLE_LIST_PATH. We
  # probably want these to be sorted by creation date or something?
  with open(TITLE_LIST_PATH, 'r') as title_list_file:
    title_reader = reader(title_list_file)
    article_cards = [make_card(row) for row in title_reader]

  with open(os.path.join(site_root, 'index.html'), 'w') as root_index_file:
    root_index = base_template.replace('{{MAIN}}', '\n'.join(article_cards))
    root_index_file.write(root_index)


def generate_templates(base_template_path: str, article_template_path: str):
  '''Update the article template file'''
  with open(base_template_path, 'r') as base_template_file:
    base_template = base_template_file.read()

  with open(article_template_path, 'r') as article_template_file:
    article_template = article_template_file.read()

  with open(ARTICLE_TEMPLATE_FILE_PATH, 'w') as full_template_file:
    full_template = base_template.replace('{{MAIN}}', article_template)
    full_template_file.write(full_template)


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
  parser.add_argument('--base_template',
                      type=str,
                      default='templates/skeleton.html',
                      help='base template HTML file for articles and site root')
  parser.add_argument('--article_template',
                      type=str,
                      default='templates/article.html',
                      help='template HTML file for articles')
  parser.add_argument('--root_template',
                      type=str,
                      default='templates/root.html',
                      help='template HTML file for entries on site root index')
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
  # Update the article template
  # generate_templates(args.base_template, args.article_template)
  # Clear the posts list
  if os.path.exists(TITLE_LIST_PATH):
    os.remove(TITLE_LIST_PATH)
  # Output algos/algo_name/*.md as site_root/algo_name/*.html
  post_dirs = [path for path in os.scandir(args.posts) if path.is_dir()]
  generate_posts(args.site_root, post_dirs, pandoc_flags)
  # Output index.html
  generate_root(args.site_root, args.base_template, args.root_template)
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
