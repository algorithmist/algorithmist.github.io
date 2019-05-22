let d3 = window.d3;
let dagre = window.dagreD3;

class Trie {
  constructor() {
    // Mapping to other tries. The key is a character transition.
    this.children = new Map();
    // True if this trie represents the end of a full keyword. False if it
    // represents an intermediate node.
    this.isFullKeyword = false;
    // Pointer to this trie's parent. null for root nodes. Set while adding
    // keywords to the trie.
    this.parent = null;
    // This trie's index in a dagre graph. Set while constructing the graph.
    this.index = null;
    // This trie's character value. This is the same as its associated key in
    // this.parent.children.
    this.value = null;
    // A count of how many keywords pass through the trie. Updating when adding
    // new keywords.
    this.count = 0;
  }

  completeWord() {
    this.isFullKeyword = true;
  }

  addCharacter(c) {
    if (!this.children.has(c)) {
      var child = new Trie();
      child.parent = this;
      child.value = c;
      this.children.set(c, child);
    }
    this.children.get(c).count += 1;
    return this.children.get(c);
  }

  pop() {
    if (this.isRoot()) {
      return this;
    }
    this.count -= 1;
    if (this.count == 0) {
      this.parent.children.delete(this.value);
    }
    return this.parent;
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

  _createDagreGraph(cursor) {
    var g = new dagre.graphlib.Graph()
      .setGraph({})
      .setDefaultEdgeLabel(function() {
        return {};
      });
    // We'll use separate CSS classes for the root, leaves, keywords, and
    // interior nodes in case we eventually want to style them differently.
    //
    // How we actually assign numbers to nodes doesn't matter. We just need a
    // numbering scheme that is internally consistent.
    var nodeIndex = 0;
    var stack = [this];
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
      if (currentNode == cursor) {
        classText.push("node-cursor");
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

  renderTo(divId, cursor) {
    var g = this._createDagreGraph(cursor);
    g.graph().rankDir = "LR";
    var renderer = new dagre.render();
    var svg = d3.select(divId).selectAll("svg");
    var svgGroup = svg.selectAll("g");
    renderer(svgGroup, g);
  }
}
