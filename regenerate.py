#!/usr/bin/env python3

from typing import List

import argparse
import os
import subprocess


def run(*args) -> str:
  return subprocess.run(
    args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')


def GatherPosts(posts_dir: str) -> List[str]:
  post_paths = run('find', posts_dir, '-name',
                   '*.md').stdout.strip().split('\n')
  return post_paths


def GenerateHtml(pandoc_flags: str, post_paths: List[str]):
  for post_path in post_paths:
    output_path = post_path[:-2] + 'html'
    run('pandoc', '-s', pandoc_flags
        if pandoc_flags else '', post_path, '-o', output_path)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument(
    '--posts',
    type=str,
    default='algos',
    help='directory relative to the repo root')
  parser.add_argument(
    '--pandoc_flags', type=str, help='passed verbatim to pandoc')
  args = parser.parse_args()
  root_dir = run('git', 'rev-parse', '--show-toplevel').stdout.strip()
  post_paths = GatherPosts(os.path.join(root_dir, args.posts))
  GenerateHtml(args.pandoc_flags, post_paths)


if __name__ == '__main__':
  try:
    main()
  except subprocess.CalledProcessError as err:
    print(err.stderr)
