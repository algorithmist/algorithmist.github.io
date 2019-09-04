---
title: 'Aho-Corasick'
subtitle: 'Fast multi-keyword string search'
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

Throughout this article, our working example will consist of the keywords `[ab, abb, ba]`. These
keywords form this trie:

```{
  .graphviz
  #example_trie
  source="algos/aho_corasick/abb_ba_example.dot"
  fig_style="width: 80%"
}
```

# Trie Limitations

Using the trie, we can find the keywords present in an input of `abba` by starting at each character
and checking whether a substring anchored there matches a keyword. These checks use four passes over
our input:

#. start at index 0 and find `ab`, continue matching, find `abb`
#. start at index 1 and find no keywords
#. start at index 2 and find `ba`
#. start at index 3 and find no keywords

Working through this ourselves, we can be much more efficient and check all the keywords in a single
pass:

* scan through index 2 and find `ab`
* move to index 3 and find `abb`
* move to index 4, remember we just saw `b`, and find `ba`

By remembering our previous state, we avoid backtracking and only need a single scan. Is this
always possible? If so, can we augment our trie to achieve something similar?

(Spoiler: yes and yes, with Aho-Corasick)

# The Aho-Corasick Algorithm

The Aho-Corasick algorithm for string matching (named after its inventors, [Alfred V. Aho][aho] and
[Margaret J. Corasick][corasick]), extends trie-based string matching by making it easier to re-use
work when traversing the trie.

The first question we need to answer is: How can we avoid backtracking?

[aho]: https://en.wikipedia.org/wiki/Alfred_Aho
[corasick]: https://dblp.org/pers/hd/c/Corasick:Margaret_J=

## The failure function

Our keywords are still `[ab, abb, ba]`. Let's pretend we're at the very beginning of the input
text and we see a `c`. The only thing we can do is stay at the root node and wait for more input,
so we'll add a loop for that.

```{
  .graphviz
  #example_fail0
  source="algos/aho_corasick/abb_ba_loop_example.dot"
  fig_style="width: 80%"
}
```

Now, let's pretend we've seen `ab`, and the next character is `a`, a mismatch. We want to end up
at node $ba$. We could precompute all the suffixes for node $ab$ (`[b, ab]`) in order to find out
that going to node $ab$ also includes going to node $b$, but there's a more efficient way.

We got from node $a$ to node $ab$ when we saw a `b`. What if we went to wherever node $a$ would go
for a mismatch and tried to match `b` there? This approach poses two questions:

#. What do we do if trying to match `b` fails?

The algorithm has three core components:

* the *goto function*, $g(\star, c)$, which says where to go if we're at location $\star$ in the
  trie and see the character $c$. The goto function either returns another location or fails.
* the *failure function*, $f(\star)$, which tells us where to go if $g(\star, c)$ fails.
* the *output function*, $o(\star)$, which says which keywords are matched at location $\star$.

## The goto function

Constructing the goto function is essentially the same as constructing the trie in the preceding
section! In addition, we also add a loop to the root node. At the root, any characters without a
match will go back to the root instead of failing.

For now, we can declare victory and move on. However, the goto function will appear again when
discussing the output function.

## The failure function

The failure function is the meat of Aho-Corasick. It is responsible for letting us avoid redundant
work while searching. Normally, with a trie, when we find a mismatched character, we have to go back
to the root. The failure function works by re-routing mismatches to possibly matching nodes instead
of having to completely restart.

Here's an example. Consider the following search graph for the keywords "ab" and "bc". Step through
to see how the failure function lets us skip jumping back to the root on a character mismatch at
node $ab$.

## Putting it all together

**TODO: Are we going to have a figure here, showing the full search graph? I think it would be
good**
We've now built the structure shown in **TODO: Fix this ref**\cref{fig:ac:full}. How do we use it to
match against an input text?

This procedure is straightforward; we've done all the hard work already. We start at the first
character of the input text and the root node of the search graph. For each character, if there
exists an outgoing transition from the current node in the goto function, we follow that transition.
If there is no such transition, we follow the failure transition for the current node. After every
transition, we advance our position in the input by one. At every state, we merge its (possibly
empty) output set from the output function into our final output, tracking the index in the input
text to report the position of the match. That's it!

This process is similar to how we searched for keywords using the trie. The difference is that,
thanks to the failure function, we only go back to the root of the search graph when we absolutely
must, and we don't have to keep re-checking characters in the input. This makes our speed even
better than the trie --- we now run in time $O(T)$, since we make one transition for each input
character, once. Though we don't prove it here, it's not hard to show that the constant factor on
this execution time is quite small --- less than two!

# Conclusions and further reading

There are still some parts of Aho-Corasick to explore, if you're interested. For one thing, though
we reduced the search time complexity, what did we do to the time complexity for constructing the
search graph? 

You may also have a sense that we could do even better than the failure
function --- why do we potentially have to make *multiple* failure transitions to find the right
node on a mismatch? Why don't we just encode the correct transition for every possible mismatched
character, making only a single jump on a mismatch? Good thinking! We can in fact do exactly this,
constructing a **deterministic finite automaton** instead of a trie, and gaining further performance
improvements.

It may also be interesting to read about other string search algorithms, with other properties. A
few to check out include
[Knuth-Morris-Pratt](https://en.wikipedia.org/wiki/Knuth%E2%80%93Morris%E2%80%93Pratt_algorithm)
and [Boyer-Moore](https://en.wikipedia.org/wiki/Boyer%E2%80%93Moore_string-search_algorithm) for
single-pattern search, as well as
[Commentz-Walter](https://en.wikipedia.org/wiki/Commentz-Walter_algorithm), which extends
Boyer-Moore to the multiple-pattern case (like Aho-Corasick) and can out-perform Aho-Corasick.
Beyond this, there's a host of interesting algorithms for fuzzy string search --- finding partial
keyword matches in strings.

If you want to read more about Aho-Corasick itself, check out the [original
paper](https://cr.yp.to/bib/1975/aho.pdf).

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
