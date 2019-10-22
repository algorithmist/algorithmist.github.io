var noop = function(color, forward) {};
var path = ["ab", "a", "a2ab", "root", "root2b", "b", "ab2b"];
var hidden = ["ab2b"];
var elems = [noop];

var explanations = [
  "What should the failure transition be for node ab?",
  "We start by looking at ab's parent node, a.",
  "Node a transitions to ab on character 'b'.",
  "Node a's failure transition is to the root.",
  "We look at the root's transition on 'b'.",
  "We move to b and are done.",
  "Node ab's failure transition is to node b."
];

var fail;
var caption;
var original_caption;

function fail() {
  let prev = document.getElementById("fail_prev");
  prev.disabled = false;
  prev.style.visibility = "visible";
  let next = document.getElementById("fail_next");
  next.disabled = false;
  next.style.visibility = "visible";

  fail = document.getElementById("fig:failure");
  caption = fail.getElementsByTagName("figcaption")[0];
  original_caption = caption.innerText;

  for (let i in path) {
    let name = path[i];
    let g = fail.querySelector("#" + name);
    let f = null;
    if (g.getAttribute("class") === "node") {
      let ellipse = g.getElementsByTagName("ellipse")[0];
      f = function(color, unused) {
        if (color === "black") {
          ellipse.style.fill = "none";
        } else {
          ellipse.style.fill = color;
        }
        caption.innerText = explanations[i];
      };
    } else {
      // Edge
      let should_hide = hidden.includes(name);
      if (should_hide) {
        g.style.visibility = "hidden";
      }

      let path = g.getElementsByTagName("path")[0];
      let polygon = g.getElementsByTagName("polygon")[0];
      f = function(color, forward) {
        if (should_hide) {
          g.style.visibility = forward ? "visible" : "hidden";
        }
        path.style.stroke = color;
        polygon.style.fill = color;
        polygon.style.stroke = color;
        caption.innerText = explanations[i];
      };
    }
    elems.push(f);
  }

  // End by adding the dummy item to the list.
  elems.push(noop);
}
var curr = 0;

function fail_forward() {
  if (fail == null) {
    return;
  }

  elems[curr]("black", true);

  curr += 1;
  if (curr == elems.length) {
    curr = elems.length - 1;
  }

  elems[curr]("red", true);
}

function fail_backward() {
  if (fail == null) {
    return;
  }

  elems[curr]("black", false);

  curr -= 1;
  if (curr == -1) {
    caption.innerText = original_caption;
    curr = 0;
  }

  elems[curr]("red", true);
}
