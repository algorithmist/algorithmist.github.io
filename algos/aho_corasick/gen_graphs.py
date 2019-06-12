import collections


class Graph(object):

  def __init__(self):
    self.nodes = []
    self.edges = []

  def addNode(self, id, attrs):
    self.nodes.append((id, attrs))

  def addEdge(self, lhs, rhs, attrs):
    self.edges.append((lhs, rhs, attrs))

  def build(self):
    text = (
      ['digraph {', '  rankdir=LR;'] +
      ['  %s [%s];' % (id, ' '.join(attrs)) for (id, attrs) in self.nodes] + [
        '  %s -> %s [%s];' % (lhs, rhs, ' '.join(attrs))
        for (lhs, rhs, attrs) in self.edges
      ] + ['}'])
    return '\n'.join(text)


class Trie(collections.abc.MutableMapping):

  def __init__(self, prefix=''):
    self.children = {}
    self._prefix = prefix
    self.is_keyword = False

  def __getitem__(self, k):
    return self.children[k]

  def __setitem__(self, k, v):
    self.children[k] = v

  def __delitem__(self, k, v):
    pass  # unsupported

  def __iter__(self):
    return iter(self.children)

  def __len__(self):
    return len(self.children)

  def __str__(self):
    return 'Trie(%s)' % self.prefix() + ''.join([
      '\n  ' + line
      for (_, child) in self.children.items()
      for line in str(child).split('\n')
    ])

  def prefix(self):
    return self._prefix if self._prefix else 'root'

  def add_word(self, word):
    if not word:
      self.is_keyword = True
      return
    letter, rest = word[0], word[1:]
    if letter not in self.children:
      self.children[letter] = Trie(prefix=self._prefix + letter)
    self.children[letter].add_word(rest)


trie = Trie()
keywords = ['arts', 'star', 'tsar', 'tars', 'start']
for keyword in keywords:
  trie.add_word(keyword)

g = Graph()

stack = [trie]
while stack:
  current = stack.pop()
  g.addNode(current.prefix(), ['id="%s"' % current.prefix()])
  for child in current.values():
    g.addEdge(current.prefix(), child.prefix(),
              ['label="%s"' % child.prefix()[-1]])
    stack.append(child)

print(g.build())
