# PDF Hierarchy Coordinator Patterns

from core.domain_models import BookmarkNode, BookmarkTree


def count_total_bookmarks(tree: BookmarkTree) -> int:
    """Recursively count all bookmark nodes in a tree."""

    def _count_nodes(nodes: tuple[BookmarkNode, ...]) -> int:
        return sum(1 + _count_nodes(node.children) for node in nodes)

    return _count_nodes(tree.roots)
