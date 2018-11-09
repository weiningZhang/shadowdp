import copy
from collections import OrderedDict
from pycparser.c_parser import CParser
from pycparser.c_generator import CGenerator
from pycparser.c_ast import NodeVisitor
from pycparser import c_ast


_parser = CParser()
_generator = CGenerator()


def convert_to_ast(expression):
    # this is a trick since pycparser cannot parse expression directly
    ast = _parser.parse('int placeholder(){{{};}}'.format(expression)).ext[0].body.block_items[0]
    return ast


def is_node_equal(node_1, node_2):
    """ check if two expression AST nodes are equal since pycparser doesn't provide such property
    :param node_1: First expression node
    :param node_2: Second expression node
    :return: Boolean
    """
    # naive comparison, can be optimized
    return node_1.__repr__() == node_2.__repr__()


class _Simplifier(NodeVisitor):
    def __init__(self, conditions):
        self._conditions = conditions

    def _simplify(self, ternary_node):
        assert isinstance(ternary_node, c_ast.TernaryOp)
        for condition, is_true in self._conditions:
            if is_node_equal(ternary_node.cond, condition):
                return ternary_node.iftrue if is_true else ternary_node.iffalse
        return ternary_node

    def visit_BinaryOp(self, node):
        node.left = self._simplify(node.left) if isinstance(node.left, c_ast.TernaryOp) else node.left
        node.right = self._simplify(node.right) if isinstance(node.right, c_ast.TernaryOp) else node.right
        for c in node:
            self.visit(c)

    def visit_UnaryOp(self, node):
        node.expr = self._simplify(node.expr) if isinstance(node.expr, c_ast.TernaryOp) else node.expr
        self.visit(node.expr)

    def simplify(self, node):
        # copy a node in order not to mess with parameter
        node = copy.copy(node)
        if isinstance(node, c_ast.TernaryOp):
            node = self._simplify(node)
        self.visit(node)
        return node


class TypeSystem:
    _EXPR_NODES = (c_ast.BinaryOp, c_ast.TernaryOp, c_ast.UnaryOp, c_ast.ID, c_ast.Constant, c_ast.ArrayRef)

    def __init__(self, types=None):
        if types:
            self._types = types
        else:
            self._types = OrderedDict()

    def __str__(self):
        # convert AST representation to code representation for better human-readability
        return '{{{}}}'.format(
            ', '.join('{}: [{}, {}]'.format(name,
                                            aligned if aligned == '*' else _generator.visit(aligned),
                                            shadow if shadow == '*' else _generator.visit(shadow))
                      for name, (aligned, shadow) in self._types.items()
                      )
        )

    def __repr__(self):
        return self._types.__repr__()

    def copy(self):
        return TypeSystem(copy.deepcopy(self._types))

    def clear(self):
        self._types.clear()

    def names(self):
        return self._types.keys()

    def dynamic_variables(self):
        dynamics = set()
        for name, (align, shadow) in self._types.items():
            if align == '*':
                dynamics.add((name, True))
            if shadow == '*':
                dynamics.add((name, False))
        return dynamics

    def _simplify_distance(self, distance, conditions):
        simplifier = _Simplifier(conditions)
        return simplifier.simplify(distance)

    def __eq__(self, other):
        if isinstance(other, TypeSystem):
            return self._types.__repr__() == other.__repr__()
        else:
            return False

    def diff(self, other):
        assert isinstance(other, TypeSystem)
        for name in other.names():
            if name not in self._types:
                yield (name, True)
                yield (name, False)
            else:
                aligned, shadow = self._types[name]
                other_aligned, other_shadow = other.get_raw_distance(name)
                if not is_node_equal(aligned, other_aligned):
                    yield (name, True)
                if not is_node_equal(shadow, other_shadow):
                    yield (name, False)

    def merge(self, other):
        assert isinstance(other, TypeSystem)
        for name in other.names():
            if name not in self._types:
                # TODO: break PEP8, maybe expose an interface to access internal dict
                self._types[name] = other._types[name]
            else:
                cur_align, cur_shadow = self._types[name]
                other_align, other_shadow = other.get_raw_distance(name)
                if not (cur_align == other_align == '*' or is_node_equal(cur_align, other_align)):
                    self._types[name][0] = '*'
                if not (cur_shadow == other_shadow == '*' or is_node_equal(cur_shadow, other_shadow)):
                    self._types[name][1] = '*'

    def get_raw_distance(self, name):
        """ return the raw distance, without simplification and contains '*' type.
        :param name: The name of the variable.
        :return: (Aligned raw distance, Shadow raw distance), both of ast node type.
        """
        return self._types[name]

    def get_distance(self, name, conditions=None):
        """ get the distance(align, shadow) of a variable. Simplifies the distance if condition and is_true is given.
        :param name: The name of the variable.
        :param conditions: The condition to apply, can either be `str` or `c_ast.Node`
        :return: (Aligned distance, Shadow distance) of the variable.
        """
        aligned, shadow = self._types[name]
        if aligned == '*':
            aligned = '__LANG_distance_{}'.format(name)
        else:
            if conditions and len(conditions) != 0:
                aligned = _generator.visit(self._simplify_distance(aligned, conditions))
            else:
                aligned = _generator.visit(aligned)
        if shadow == '*':
            shadow = '__LANG_distance_shadow_{}'.format(name)
        else:
            if conditions and len(conditions) != 0:
                shadow = _generator.visit(self._simplify_distance(shadow, conditions))
            else:
                shadow = _generator.visit(shadow)
        return aligned, shadow

    def update_distance(self, name, aligned, shadow):
        aligned = '*' if aligned == '*' else convert_to_ast(aligned)
        shadow = '*' if shadow == '*' else convert_to_ast(shadow)
        if name not in self._types:
            self._types[name] = [aligned, shadow]
        else:
            cur_aligned, cur_shadow = self._types[name]
            if not is_node_equal(cur_aligned, aligned):
                self._types[name][0] = aligned
            if not is_node_equal(cur_shadow, shadow):
                self._types[name][1] = shadow