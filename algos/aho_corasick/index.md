---
title: "Aho-Corasick: Fast multi-keyword string search"
...

# Introduction
Many important computational applications rely on efficient string search. Malware detection,
information retrieval, and gene sequencing (among others) require at their core checking for the
presence of a large set of target strings in a large corpus of text. In this article, we will
explain and implement the **Aho-Corasick** algorithm, a fast classical approach for finding keywords
in an input string.

## A naive approach to string search

Searching for a single string (keyword) in a corpus is straightforward: Iterate through the
characters of the keyword and the corpus checking for matches. If you reach the end of the keyword,
you've found the string. If two characters **don't** match, start over at the next start position in
the corpus and the first character of the keyword. String search algorithms that simultaneously
search for multiple keywords in a corpus are more interesting. A straightforward approach is to loop
over the keywords and check if each one is in the text, just like in the single keyword case. Each
individual check requires scanning the entire input text, giving a runtime of $O(KT)$, where $K$
is the number of keywords and $T$ is the length of the text. If we have many keywords and/or a
long text, this search algorithm will perform poorly. We can improve this by constructing a new
approach that can check for many keywords at once.

## Trie-ing harder: More efficient string matching

```{.graphviz name="trie" style="width:100%;height:100%;" caption="A trie for the words \"tars, start, tsar, arts, art\""}
digraph {
  rankdir=LR;
  root [id="root" keyword="True"];
  t [id="t" keyword="True"];
  ta [id="ta" keyword="True"];
  tar [id="tar" keyword="False"];
  tars [id="tars" keyword="False"];
  ts [id="ts" keyword="True"];
  tsa [id="tsa" keyword="False"];
  tsar [id="tsar" keyword="False"];
  s [id="s" keyword="True"];
  st [id="st" keyword="True"];
  sta [id="sta" keyword="True"];
  star [id="star" keyword="False"];
  start [id="start" keyword="False"];
  a [id="a" keyword="True"];
  ar [id="ar" keyword="True"];
  art [id="art" keyword="False"];
  arts [id="arts" keyword="False"];
  root -> a [label="a"];
  root -> s [label="s"];
  root -> t [label="t"];
  t -> ts [label="s"];
  t -> ta [label="a"];
  ta -> tar [label="r"];
  tar -> tars [label="s"];
  ts -> tsa [label="a"];
  tsa -> tsar [label="r"];
  s -> st [label="t"];
  st -> sta [label="a"];
  sta -> star [label="r"];
  star -> start [label="t"];
  a -> ar [label="r"];
  ar -> art [label="t"];
  art -> arts [label="s"];
}
```

As a first effort, we can use a **[trie](https://en.wikipedia.org/wiki/Trie)** to make a single scan
of the text and simultaneously check for every keyword at once. A trie is a tree representing a
collection of keys. Each path from the root to a node represents the prefix of at least one key,
signified by the labels of the edges moving between nodes. Each node stores whether it signifies the
end of a full keyword: that is, if the path from the root to that node spells out a complete
keyword. We’ll call the nodes for which this is true __output nodes__. We can now search for
keywords in the input text by traversing the tree starting from each character of the input text in
sequence.

This version of the search algorithm has a complexity of $O(LT)$, where $L$ is the length of the
longest keyword. This is better than what we had before --- in most practical cases, the number of
keywords will be much larger than the length of the longest keyword (i.e. $K \gg L$). However,
there's still room for improvement. Consider what happens when we reach an input character with no
matches, or reach a leaf node: We have to go back to the root and back to only a single character
further in the input than our last start position. This means that we perform lots of redundant
traversals of the trie, and thus that our algorithm is slower than it has to be. What if we could
remember the progress we've already made and use it to shortcut through the trie, avoiding
backtracking? This is the core insight of the Aho-Corasick algorithm.

# The Aho-Corasick Algorithm

The Aho-Corasick algorithm for string matching (named after its inventors, [Alfred V.
Aho](https://en.wikipedia.org/wiki/Alfred_Aho) and [Margaret J.
Corasick](https://dblp.org/pers/hd/c/Corasick:Margaret_J=)), extends trie-based string matching by
making it easier to re-use work in traversing the trie. We'll need three core components to do this:
the *goto function*, which is similar to the existing graph structure of the trie and handles normal
transitions, the *failure function*, which tells us how to avoid restarting entirely when a match
fails, and the *output function*, which allows us to encode multiple matches from a single trie
traversal.

## The goto function

Constructing the goto function is actually the same as constructing the trie in the preceding
section! **NOTE/TODO: We don't actually say how to do this in the preceding section.**
There is one minor difference pertaining to how we handle output nodes. Instead of labelling a node
terminating the path for a keyword as an output node, we instead add a reference to this node and
the corresponding keyword to the output function (described [below](#the_output_function)). The
reason for this will become clear once we explain the construction of the failure function, which
also contributes elements to the output function. The final difference from the trie construction
above is the addition of a loopback edge on the root node for every character without an outgoing
edge from the root. At this point, we've built the structure shown in **TODO: Fix this ref**\cref{fig:ac:goto}.

## The failure function

```{.graphviz name="failure" caption="The failure function in action" animate="fail"} 
digraph {
  splines=true;
  rankdir=LR;
  root [id="root"];
  a [id="a"];
  ab [id="ab"];
  b [id="b"];
  bc [id="bc"];
  root -> a [xlabel="a"];
  a -> ab [xlabel="b"];
  root -> b [xlabel="b"];
  b -> bc [xlabel="c"];

  ab:n -> a:ne [id="ab2a" constraint=false];
  a:n -> root:n [id="a2root" constraint=false];
  root:s -> b:s [id="root2b" constraint=false];
  ab -> b [id="ab2b" constraint=false];
}
```

The failure function is the meat of Aho-Corasick. It is responsible for letting us avoid redundant
work in the search process by re-routing paths in the search graph when we find a character in the
input with no matching outgoing edge from the current node (i.e. a character mismatch between the
input and a keyword). Rather than returning to the root and starting again, the failure function
tells us how to keep going without a full restart whenever possible.

The failure function is defined recursively based on the goto function. For the first layer of the
graph --- the set of nodes representing having matched a single character --- the failure function
will always map back to the root. The intuition here is simple: If we have reached a failure state
after matching a single character, then we can't possibly be in a prefix state for any other
keywords and need to go back to the root.

For subsequent layers, we compute the failure function inductively in terms of the failure function
for the immediately preceding layer. This process works as follows:

1. Consider all states in the preceding layer. For each state $r$, find every symbol $a$ with a
   valid transition out of $r$ to some state $s$.
2. For each $a$, follow the failure function from $r$ until reaching either the root or a state $t$
   such that $t$ has a valid transition for $a$.
3. Then, set the value of the failure function for $s$ to be the state $s^\prime$ reached by
   transitioning with $a$ from $t$.
4. Set the output function for state $s$ to be its original outputs combined with the outputs for
   $s^\prime$.
5. Continue for all other $r$ and $a$ in the layer, then move to the next layer.

Intuitively, this process finds the next state in the search graph that could possibly be correct if
the current character is actually part of another keyword. Merging the output sets in step (4) means
that we don't miss keywords by taking these transitions, but also don't need to keep restarting the
search for every character of the input. It's interesting to think about why there's only a single
failure state for any given state --- try it! (Hint: think about what would happen if, after
transitioning to the state specified by the failure function, we fail again on the next character.)

## The output function

Surprise! We have actually already constructed the output function through the previous two steps to
construct the goto function and the failure function. The main difference from our output node
labeling in the trie example is that the output function may now return multiple keywords for a
single state. This is to let us maintain the correct output set when following failure transitions.

## Putting it all together

We've now built the structure shown in **TODO: Fix this ref**\cref{fig:ac:full}. How do we use it to
match against an input text?

This procedure is quite simple; we've done all the hard work already. We start at the first
character of the input text and the root node of the search graph. For each character, if there
exists an outgoing transition from the current node in the goto function, we follow that transition.
If there is no such transition, we follow the failure transition for the current node. After every
transition, we advance our position in the input by one. At every state, we merge its (possibly
empty) output set from the output function into our final, overall output, tracking the index in the
input text to report the position of the match. That's it!

This process is very similar to how we searched for keywords using the trie. The difference is that,
thanks to the failure function, we only go back to the root of the search graph when we absolutely
must, and we don't have to keep re-checking characters in the input. This makes our speed even
better than the trie --- we now run in time $O(T)$, since we make one transition for each input
character, once. Though we don't prove it here, it's not hard to show that the constant factor on
this execution time is quite small --- less than two!

# Conclusions and further reading
** TODO: Add wrap-up paragraph**
