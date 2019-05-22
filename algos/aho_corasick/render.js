let d3 = window.d3;
let dagre = window.dagreD3;

class Trie {
  constructor() {
    this.children = new Map();
    this.isFullKeyword = false;
    this.parent = null;
    this.index = null;
    this.value = null;
  }

  addWord(word) {
    var currentNode = this;
    for (let currentChar of word) {
      if (!currentNode.children.has(currentChar)) {
        var childTrie = new Trie();
        childTrie.parent = currentNode;
        childTrie.value = currentChar;
        currentNode.children.set(currentChar, childTrie);
      }
      currentNode = currentNode.children.get(currentChar);
    }
    currentNode.isFullKeyword = true;
    return this;
  }

  getValue() {
    return this.isRoot() ? "root" : this.value;
  }

  isRoot() {
    return this.parent == null;
  }

  isLeaf() {
    return this.children.size == 0;
  }

  isKeyword() {
    return this.isFullKeyword;
  }
}

function createDagreGraph(trie) {
  var g = new dagre.graphlib.Graph()
    .setGraph({})
    .setDefaultEdgeLabel(function() {
      return {};
    });
  // We'll use separate CSS classes for the root, leaves, keywords, and interior
  // nodes in case we eventually want to style them differently.
  //
  // How we actually assign numbers to nodes doesn't matter. We just need a
  // numbering scheme that is internally consistent.
  var nodeIndex = 0;
  var stack = [trie];
  while (stack.length > 0) {
    var currentNode = stack.pop();
    currentNode.index = nodeIndex++;
    var classText = ["node"];
    if (currentNode.isRoot()) {
      classText.push("node-root");
    } else if (currentNode.isLeaf()) {
      classText.push("node-leaf");
    } else {
      classText.push("node-interior");
    }
    if (currentNode.isKeyword()) {
      classText.push("node-keyword");
    }
    g.setNode(currentNode.index, {
      label: currentNode.getValue(),
      class: classText.join(" "),
      shape: "rect"
    });
    var parent = currentNode.parent;
    if (parent != null) {
      g.setEdge(parent.index, currentNode.index);
    }
    // JavaScript Maps iterate based on their insertion order, which is useful
    // but not needed right now.
    var sortedEntries = Array.from(currentNode.children.entries()).sort(
      (left, right) => left[0] < right[0]
    );
    for (let entry of sortedEntries) {
      stack.push(entry[1]);
    }
  }
  g.nodes().forEach(function(v) {
    var node = g.node(v);
    // Round the corners of each node.
    node.rx = node.ry = 5;
  });
  return g;
}

function renderTrie(trie, divId) {
  var g = createDagreGraph(trie);
  g.graph().rankDir = "LR";
  var renderer = new dagre.render();
  var svg = d3.select(divId);
  var svgGroup = svg.append("g");
  renderer(d3.select("svg g"), g);
}
