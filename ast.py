
class AST(object):
    _fields = []

    def __init__(self, *args, **kwargs):
        assert len(args) == len(self._fields)
        for name, value in zip(self._fields, args):
            setattr(self, name, value)
        # Assign additional keyword arguments if supplied
        for name, value in kwargs.items():
            setattr(self, name, value)

    def __repr__(self):
        excluded = {"lineno"}
        return "{}[{}]".format(self.__class__.__name__,
                               {key: value
                                for key, value in vars(self).items()
                                if not key.startswith("_") and not key in excluded})


class Literal(AST):
    _fields = ['value']


class Typename(AST):
    _fields = ['name']


class Location(AST):
    _fields = ['name']


class LoadLocation(AST):
    _fields = ['location']


class Unaryop(AST):
    _fields = ['op', 'expr']


class Binop(AST):
    _fields = ['op', 'left', 'right']


class Relop(AST):
    _fields = ['op', 'left', 'right']


class AssignmentStatement(AST):
    _fields = ['location', 'expr']


class PrintStatement(AST):
    _fields = ['expr']


class Statements(AST):
    _fields = ['statements']

    def append(self, stmt):
        self.statements.append(stmt)

    def __len__(self):
        return len(self.statements)


class Program(AST):
    _fields = ['statements']


class VarDeclaration(AST):
    _fields = ['name', 'typename', 'expr']


class ConstDeclaration(AST):
    _fields = ['name', 'expr']


class IfStatement(AST):
    _fields = ['expr', 'truebranch', 'falsebranch']


class WhileStatement(AST):
    _fields = ['expr', 'truebranch']


class FuncStatement(AST):
    _fields = ['name', 'returntype', 'parameters', 'expr']


class FuncParameterList(AST):
    _fields = ['parameters']

    def append(self, stmt):
        self.parameters.append(stmt)

    def __len__(self):
        return len(self.parameters)


class FuncParameter(VarDeclaration):
    pass


class FuncCall(AST):
    _fields = ['name', 'arguments']


class FuncCallArguments(AST):
    _fields = ['arguments']

    def append(self, stmt):
        self.arguments.append(stmt)

    def __len__(self):
        return len(self.arguments)


class FuncCallArgument(AST):
    _fields = ['expr']


class ReturnStatement(AST):
    _fields = ['expr']



class NodeVisitor(object):

    def visit(self, node):
        if node:
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, self.generic_visit)
            return visitor(node)
        else:
            return None

    def generic_visit(self, node):

        for field in getattr(node, "_fields"):
            value = getattr(node, field, None)
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, AST):
                        self.visit(item)
            elif isinstance(value, AST):
                self.visit(value)


class NodeTransformer(NodeVisitor):

    def generic_visit(self, node):
        for field in getattr(node, "_fields"):
            value = getattr(node, field, None)
            if isinstance(value, list):
                newvalues = []
                for item in value:
                    if isinstance(item, AST):
                        newnode = self.visit(item)
                        if newnode is not None:
                            newvalues.append(newnode)
                    else:
                        newvalues.append()
                value[:] = newvalues
            elif isinstance(value, AST):
                newnode = self.visit(value)
                if newnode is None:
                    delattr(node, field)
                else:
                    setattr(node, field, newnode)
        return node


# DO NOT MODIFY
def flatten(top):

    class Flattener(NodeVisitor):
        def __init__(self):
            self.depth = 0
            self.nodes = []

        def generic_visit(self, node):
            self.nodes.append((self.depth, node))
            self.depth += 1
            NodeVisitor.generic_visit(self, node)
            self.depth -= 1

    d = Flattener()
    d.visit(top)
    return d.nodes
