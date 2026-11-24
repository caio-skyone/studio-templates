"""Local `$ref` resolution: memoized, cycle-guarded, depth-capped.

Real specs nest refs several levels deep and some are recursive. The depth cap
counts REF HOPS, never dictionary levels: `paths → path → method → requestBody
→ content → application/json` is already six levels, and a level-counting cap
truncates the spec before it ever reaches a body — returning something empty
that looks right.

The cap alone is not enough. It bounds depth, not work: with a recursive schema
the number of acyclic paths grows exponentially, and a real spec (HubSpot, 73
cycles) took CPU, memory and disk on the user's machine to ~95%. Hence the
cycle stack and the memo below — and `strip_responses`, which removes the part
of the spec where those cycles actually live.
"""

from typing import Any

from studio_iac.openapi.errors import OpenApiSpecInvalid

_MAX_DEPTH = 12
_WHITE, _GREY, _BLACK = 0, 1, 2


def resolve_ref(spec: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise OpenApiSpecInvalid("<spec>", f"external $ref is not supported: {ref!r}")
    node: Any = spec
    for part in ref.removeprefix("#/").split("/"):
        key = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, dict) or key not in node:
            raise OpenApiSpecInvalid("<spec>", f"$ref target not found: {ref!r}")
        node = node[key]
    if not isinstance(node, dict):
        raise OpenApiSpecInvalid("<spec>", f"$ref target is not an object: {ref!r}")
    return node


class _Deref:
    """One resolution pass: holds the memo and the in-progress ref stack.

    The memo is keyed by ref STRING, not by node identity — resolving
    `#/components/schemas/Node` costs the same wherever it appears. An entry is
    memoized only when its resolution was complete: a value cut short by the
    cycle guard or by the depth cap depends on the path that produced it, and
    caching it would poison every later hit.
    """

    def __init__(self, spec: dict[str, Any], max_depth: int) -> None:
        self._spec = spec
        self._max_depth = max_depth
        self._memo: dict[str, Any] = {}
        self._stack: list[str] = []
        self._cut = False

    def run(self, node: Any, depth: int) -> Any:
        if depth > self._max_depth:
            self._cut = True
            return {}
        if isinstance(node, dict):
            ref = node.get("$ref")
            if isinstance(ref, str):
                return self._follow(ref, depth)
            return {key: self.run(value, depth) for key, value in node.items()}
        if isinstance(node, list):
            return [self.run(item, depth) for item in node]
        return node

    def _follow(self, ref: str, depth: int) -> Any:
        if ref in self._stack:
            self._cut = True
            return {}
        memoized = self._memo.get(ref)
        if memoized is not None:
            return memoized
        target = resolve_ref(self._spec, ref)
        outer_cut, self._cut = self._cut, False
        self._stack.append(ref)
        try:
            resolved = self.run(target, depth + 1)
        finally:
            self._stack.pop()
        if not self._cut:
            self._memo[ref] = resolved
        self._cut = self._cut or outer_cut
        return resolved


def deref(
    spec: dict[str, Any],
    node: Any,
    *,
    depth: int = 0,
    max_depth: int = _MAX_DEPTH,
) -> Any:
    """Inline every local `$ref`.

    The result is READ-ONLY: memoized subtrees are shared between call sites,
    so mutating one mutates them all.
    """
    return _Deref(spec, max_depth).run(node, depth)


def resolve_node(spec: dict[str, Any], node: Any) -> Any:
    """Resolve a top-level `$ref` only — one hop at a time, no recursion.

    `components/parameters` and `components/requestBodies` entries are
    referenced this way; they must be readable before the body planner is even
    reached, and inlining them deeply would drag whole schema families along.
    Siblings of the `$ref` win over the target, which is how OpenAPI 3.1 reads.
    """
    seen: set[str] = set()
    current = node
    while isinstance(current, dict):
        ref = current.get("$ref")
        if not isinstance(ref, str) or ref in seen:
            break
        seen.add(ref)
        target = resolve_ref(spec, ref)
        siblings = {key: value for key, value in current.items() if key != "$ref"}
        current = {**target, **siblings}
    return current


def strip_responses(spec: dict[str, Any]) -> dict[str, Any]:
    """A shallow copy of the spec with every `responses` block under `paths` gone.

    The IAC models path, query, header and body — never a response. Response
    schemas are where the recursive `$ref` families live: dropping them took a
    real 1.6 MB spec from 1,881 refs to zero and made analysis instantaneous.
    """
    paths = spec.get("paths")
    if not isinstance(paths, dict):
        return spec
    pruned: dict[str, Any] = {}
    for path, item in paths.items():
        if not isinstance(item, dict):
            pruned[path] = item
            continue
        pruned[path] = {
            key: (
                {inner: value for inner, value in entry.items() if inner != "responses"}
                if isinstance(entry, dict)
                else entry
            )
            for key, entry in item.items()
        }
    return {**spec, "paths": pruned}


def _refs_in(node: Any) -> list[str]:
    found: list[str] = []
    stack: list[Any] = [node]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            ref = current.get("$ref")
            if isinstance(ref, str):
                found.append(ref)
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
    return found


def ref_cycles(spec: dict[str, Any]) -> list[str]:
    """Components that participate in a `$ref` cycle. Cheap pre-check, iterative.

    Iterative on purpose: a big spec has thousands of components and a
    recursive DFS would hit Python's own recursion limit before reporting
    anything useful.
    """
    components = spec.get("components")
    if not isinstance(components, dict):
        return []
    graph: dict[str, list[str]] = {}
    for section, entries in components.items():
        if not isinstance(entries, dict):
            continue
        for name, node in entries.items():
            graph[f"#/components/{section}/{name}"] = _refs_in(node)
    color = dict.fromkeys(graph, _WHITE)
    cycles: set[str] = set()
    for start in sorted(graph):
        if color[start] != _WHITE:
            continue
        color[start] = _GREY
        stack: list[tuple[str, list[str]]] = [(start, list(graph[start]))]
        while stack:
            node_name, pending = stack[-1]
            if not pending:
                color[node_name] = _BLACK
                stack.pop()
                continue
            neighbour = pending.pop()
            if neighbour not in color:
                continue
            if color[neighbour] == _GREY:
                cycles.add(neighbour)
            elif color[neighbour] == _WHITE:
                color[neighbour] = _GREY
                stack.append((neighbour, list(graph[neighbour])))
    return sorted(cycles)
