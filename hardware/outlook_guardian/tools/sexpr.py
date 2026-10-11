"""Minimal S-expression reader/writer for KiCad files."""


class Sym(str):
    """An unquoted atom."""


def parse(text):
    pos = 0
    n = len(text)
    stack = [[]]
    while pos < n:
        c = text[pos]
        if c in " \t\r\n":
            pos += 1
        elif c == "(":
            stack.append([])
            pos += 1
        elif c == ")":
            done = stack.pop()
            stack[-1].append(done)
            pos += 1
        elif c == '"':
            pos += 1
            out = []
            while text[pos] != '"':
                if text[pos] == "\\":
                    pos += 1
                    out.append({"n": "\n", "t": "\t"}.get(text[pos], text[pos]))
                else:
                    out.append(text[pos])
                pos += 1
            pos += 1
            stack[-1].append("".join(out))
        else:
            start = pos
            while pos < n and text[pos] not in ' \t\r\n()"':
                pos += 1
            stack[-1].append(Sym(text[start:pos]))
    return stack[0][0]


def _atom(a):
    if isinstance(a, Sym):
        return str(a)
    if isinstance(a, str):
        return '"' + a.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    if isinstance(a, float):
        return ("%.4f" % a).rstrip("0").rstrip(".")
    return str(a)


def dump(node, indent=0):
    if not isinstance(node, list):
        return _atom(node)
    flat = "(" + " ".join(dump(x) for x in node) + ")"
    if len(flat) <= 100 and "\n" not in flat:
        return flat
    pad = "\t" * (indent + 1)
    head = [dump(x) for x in node if not isinstance(x, list)]
    tail = [dump(x, indent + 1) for x in node if isinstance(x, list)]
    return "(" + " ".join(head) + "\n" + "\n".join(pad + t for t in tail) + "\n" + "\t" * indent + ")"


def S(*items):
    """Build a list node, turning the head into a symbol."""
    return [Sym(items[0])] + list(items[1:])


def find(node, key):
    return [x for x in node if isinstance(x, list) and x and x[0] == key]


def first(node, key):
    found = find(node, key)
    return found[0] if found else None
