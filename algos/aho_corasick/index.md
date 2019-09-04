---
title: "Aho-Corasick: Fast multi-keyword string search"
...

# Introduction
Many important computational applications rely on efficient string search. Malware detection,
information retrieval, and gene sequencing (among others) require at their core checking for the
presence of a large set of target strings in a large or unbounded corpus of text. In this article,
we will explain and implement the **Aho-Corasick** algorithm, a fast streaming algorithm for finding
keywords in an input text.

The article assumes some familiarity with tries. Wikipedia's [page][trie] has a good overview.
There are also some additional examples in the [appendix](#appendix).

[trie]: https://en.wikipedia.org/wiki/Trie

Throughout this article, our working example will consist of the keywords `[ab, aba, bab]` and the
input text `abab`. These keywords form this trie:

```{
  .graphviz
  #example_trie
  source="algos/aho_corasick/aba_bab_example.dot"
  fig_style="width: 80%"
}
```

# Trie Limitations

Using the trie, we can find the keywords present in `abab` by starting at each character and
checking whether a substring anchored there matches a keyword. These checks use four passes over
our input:

#. start at index 0 and find `ab`, continue matching, and then find `aba`
#. start at index 1 and find `bab`
#. start at index 2 and find the second `ab`
#. start at index 3 and find no keywords

Working through this ourselves, we can be much more efficient and check all the keywords in a single
pass:

* scan through index 2 and find `ab`
* move to index 3 and find `aba`
* move to index 4, remember we just saw `ba`, and find `bab` as well as the second `ab`

By remembering our previous state, we only need a single scan. Is this always possible? If so, can
we augment our trie to achieve something similar?

(Spoiler: yes and yes, with Aho-Corasick)

# The Aho-Corasick Algorithm

The Aho-Corasick algorithm for string matching (named after its inventors, [Alfred V. Aho][aho] and
[Margaret J. Corasick][corasick]), extends trie-based string matching by making it easier to re-use
work when traversing the trie.

[aho]: https://en.wikipedia.org/wiki/Alfred_Aho
[corasick]: https://dblp.org/pers/hd/c/Corasick:Margaret_J=

The algorithm has three core components:

* the *goto function*, $g(\star, c)$, which says where to go if we're at location $\star$ in the
  trie and see the character $c$. The goto function either returns another location or fails.
* the *failure function*, $f(\star)$, which tells us where to go if $g(\star, c)$ fails.
* the *output function*, $o(\star)$, which says which keywords are matched at location $\star$.

## The goto function

Constructing the goto function is essentially the same as constructing the trie in the preceding
section! In addition, we also add a loop to the root node. At the root, any characters without a
match will go back to the root instead of failing.

```{
  .graphviz
  #example_loop
  source="algos/aho_corasick/aba_bab_loop_example.dot"
  fig_style="width: 80%"
}
```

For now, we can declare victory and move on. However, the goto function will appear again when
discussing the output function.

## The failure function

## The output function

above is the addition of a loopback edge on the root node for every character without an outgoing
edge from the root. At this point, we've built the structure shown in **TODO: Fix this ref**\cref{fig:ac:goto}.

## The failure function

```{
  .graphviz
  #failure
  source="algos/aho_corasick/failure.dot"
  caption="The failure function in action"
  animate="fail"
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

# Appendix

We'll be using Python throughout the appendix.

## Trie construction

```python
def build_trie(keywords):
  root = {}
  for keyword in keywords:
    current = root
    for c in keyword:
      if c not in current:
        current[c] = {}
      current = current[c]
    # Sentinel value. Only present if a
    # keyword ends at this node.
    current[None] = True
  return root
```

## Matching with the trie

```python
def match(trie, input_text):
  current, match, matches = trie, '', []
  for c in input_text:
    if c not in current:
      return None
    match += c
    if None in current:
      matches.append(match)
    current = current[c]
  return matches
```

## Searching an entire text

```python
def search(keywords, input_text):
  trie = build_trie(keywords)
  matches = []
  for i, _ in enumerate(input_text):
    new_matches = match(trie, input_text[i:])
    matches.extend(new_matches)
  return matches 
```
