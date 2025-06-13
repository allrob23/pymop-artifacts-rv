'''
This module extends the python import behavior.
The new behavior modifies the code on the fly before
importing any module.

This script is placed within sitecustomize.py is important
so that it runs as early as possible during the python
interpreter initialization sequence.
'''
print('Pythonmop sitecustomize started...')

import ast
import importlib
import importlib.abc
import importlib.util
import sys
import os
# import difflib
import builtins
import timeit
import atexit

# Initialize AST_time at module level
AST_time = 0.0

original__list = builtins.list
original__isinstance = builtins.isinstance

list___original_sort = list.sort
list___original_append = list.append
list___original___contains__ = list.__contains__
list___original___init__ = list.__init__
list___original___setitem__ = list.__setitem__
list___original_extend = list.extend
list___original_insert = list.insert
list___original_pop = list.pop
list___original_remove = list.remove
list___original_clear = list.clear

class InstrumentableList(list):
    def __init__(self, *args, **kwargs):
        return list___original___init__(self, *args, **kwargs)
    
    def __hash__(self):
        return super.__hash__(super)
    
    def __setitem__(self, *args, **kwargs):
        return list___original___setitem__(self, *args, **kwargs)

    def __contains__(self, *args, **kwargs):
        return list___original___contains__(self, *args, **kwargs)

    def append(self, *args, **kwargs):
        return list___original_append(self, *args, **kwargs)
    
    def extend(self, *args, **kwargs):
        return list___original_extend(self, *args, **kwargs)
    
    def insert(self, *args, **kwargs):
        return list___original_insert(self, *args, **kwargs)
    
    def pop(self, *args, **kwargs):
        return list___original_pop(self, *args, **kwargs)
    
    def remove(self, *args, **kwargs):
        return list___original_remove(self, *args, **kwargs)
    
    def clear(self, *args, **kwargs):
        return list___original_clear(self, *args, **kwargs)
    
    def sort(self, *args, **kwargs):
        return list___original_sort(self, *args, **kwargs)

original_dict = builtins.dict

dict___original___init__ = dict.__init__
dict___original___setitem__ = dict.__setitem__
dict___original___delitem__ = dict.__delitem__
dict___original_update = dict.update
dict___original_pop = dict.pop
dict___original_popitem = dict.popitem
dict___original_clear = dict.clear
dict___original_setdefault = dict.setdefault

class InstrumentedDict(dict):
    def __init__(self, *args, **kwargs):
        return dict___original___init__(self, *args, **kwargs)
    
    def __hash__(self):
        return super.__hash__(super)
    
    def __setitem__(self, *args, **kwargs):
        return dict___original___setitem__(self, *args, **kwargs)
    
    def update(self, *args, **kwargs):
        return dict___original_update(self, *args, **kwargs)
    
    def pop(self, *args, **kwargs):
        return dict___original_pop(self, *args, **kwargs)
    
    def popitem(self):
        return dict___original_popitem(self)
    
    def clear(self):
        return dict___original_clear(self)
    
    def setdefault(self, *args, **kwargs):
        return dict___original_setdefault(self, *args, **kwargs)

    def __delitem__(self, key):  # Add this method
        return dict___original___delitem__(self, key)

original_str = builtins.str
original_type = builtins.type

def patched_maketrans(arg):
    if original_type(arg) is InstrumentedDict:
        # We need to pass an original builtins.dict to str.maketrans
        # because str.maketrans expects a builtins.dict as argument and does not accept
        # our custom subclass of dict.
        return original_str.maketrans({k: v for k, v in arg.items()})
    return original_str.maketrans(arg)


def patched_type(obj):
    '''
    This is a hack to make type(obj) return the original type of the object.
    This is important because some logic rely on the fact that an object is a list for example.
    '''
    if original_type(obj) == InstrumentableList:
        return builtins.list
    elif original_type(obj) == InstrumentedDict:
        return builtins.dict
    else:
        return original_type(obj)

class PyMopInjectedBuiltins():
    def __init__(self):
        self.dict = InstrumentedDict
        self.list = InstrumentableList
        self.str_maketrans = patched_maketrans
        self.type = patched_type

class OriginalBuiltins():
    def __init__(self) -> None:
        self.dict = builtins.dict
        self.list = builtins.list

____original__builtins____ = OriginalBuiltins()
____pymop__injected__builtins____ = PyMopInjectedBuiltins()


sys.path.insert(0, os.path.dirname(__file__))

class Delegator:
    def __init__(self, wrapped):
        self._wrapped = wrapped

    def __getattr__(self, name):
        # Delegate all unknown attributes to the wrapped object
        return getattr(self._wrapped, name)

    def __dir__(self):
        # Include wrapped object's attributes in dir()
        return sorted(set(dir(type(self)) + dir(self._wrapped)))
    
def safe_wrapped_builtin_call(name: str, args, keywords, lineno, col_offset):
    """
    Returns AST for:
    (____pymop__injected__builtins____.list if list is ____original__builtins____.list else list)(...)
    """
    name_node = ast.Name(id=name, ctx=ast.Load())
    safe_call = ast.Call(
        func=ast.IfExp(
            test=ast.Compare(
                left=name_node,
                ops=[ast.Is()],
                comparators=[
                    ast.Attribute(
                        value=ast.Name(id="____original__builtins____", ctx=ast.Load()),
                        attr=name,
                        ctx=ast.Load(),
                    )
                ],
            ),
            body=ast.Attribute(
                value=ast.Name(id="____pymop__injected__builtins____", ctx=ast.Load()),
                attr=name,
                ctx=ast.Load(),
            ),
            orelse=name_node,
        ),
        args=args,
        keywords=keywords,
    )

    ast.fix_missing_locations(safe_call)
    return safe_call

'''
## Notes
1. We don't handle dict unpacking. like {**a, **b}
2. We make sure to import builtins and use builtins.list/builtins.dict to avoid conflicts with local variables called list/dict.
   for example:
   def foo():
       dict = {}  # <-- this gets transformed into dict = dict() which raises an Exception "UnboundLocalError: cannot access local variable 'dict' where it is not associated with a value"
       print(list)

3. instead of adding a new finder, we replace existing ones with
   a wrapper that delegates to the old finder, but modifies the code.
   This is important because if we add a new finder at the beginning
   of sys.meta_path, it will be used instead of default ones breaking functionality.

4. Make sure to not import any module before __future__ imports. We find the first regular import
   and insert the builtins import right before it.

5. We don't transform list/dict literals in assignment targets.

6. We don't transform list/dict literals that occur at the beginning of the file before any
   imports as they may appear before __future__ imports and we can't add builtins imports before them.

7. prefer making modules available globally instead of importing them.
8. User code may have "builtins" name as a local variable which would overshadow the globally available builtins.
   We use a special name to avoid this.
'''
class LiteralTransformer(ast.NodeTransformer):
    def __init__(self, path):
        self.path = path
        self.context_stack = []

    def _read_line(self, path, lineno):
        try:
            with open(path, 'r') as f:
                return f.readlines()[lineno - 1]
        except (IOError, IndexError):
            return ""
        
    def _is_type_annotation(self, node):
        if not self.context_stack:
            return False
        
        for ancestor in reversed(self.context_stack):
            if isinstance(ancestor, (ast.Subscript)):
                return True

        return False

    def _in_assignment_target(self, node):
        """
        Returns True if `node` is used as part of a destructuring target pattern.
        We walk up the context stack to detect whether `node` is part of any assignment/loop/with target.
        """

        # No context, no chance
        if not self.context_stack:
            return False

        # Fast skip: if the direct parent is not a List, Tuple, Starred, or known construct,
        # there's no reason to check further up.
        parent = self.context_stack[-1]
        if not isinstance(parent, (ast.List, ast.Tuple, ast.Starred,
                                ast.Assign, ast.AnnAssign, ast.AugAssign,
                                ast.For, ast.AsyncFor, ast.withitem, ast.comprehension)):
            return False

        # Walk up the context stack to see if we're inside a target
        for ancestor in reversed(self.context_stack):
            # a, [b, c] = value
            if isinstance(ancestor, ast.Assign):
                if any(self._node_in_target(node, t) for t in ancestor.targets):
                    return True

            # x: int = value
            elif isinstance(ancestor, (ast.AnnAssign, ast.AugAssign)):
                if self._node_in_target(node, ancestor.target):
                    return True

            # for (a, [b, c]) in items
            elif isinstance(ancestor, (ast.For, ast.AsyncFor)):
                if self._node_in_target(node, ancestor.target):
                    return True

            # with open(...) as (a, [b, c])
            elif isinstance(ancestor, ast.withitem) and ancestor.optional_vars:
                if self._node_in_target(node, ancestor.optional_vars):
                    return True
            
            # for a in b:
            elif isinstance(ancestor, ast.comprehension):
                if self._node_in_target(node, ancestor.target):
                    return True

        return False

    def _node_in_target(self, needle, target):
        if needle is target:
            return True
        if isinstance(target, (ast.Tuple, ast.List)):
            return any(self._node_in_target(needle, elt) for elt in target.elts)
        return False

    def generic_visit(self, node):
        self.context_stack.append(node)
        result = super().generic_visit(node)
        self.context_stack.pop()
        return result

    def visit_List(self, node):
        if self._in_assignment_target(node):
            return node

        

        if self._is_type_annotation(node):
            return node

        new_node = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="____pymop__injected__builtins____", ctx=ast.Load()),
                attr="list",
                ctx=ast.Load(),
            ),
            args=[ast.List(elts=node.elts, ctx=ast.Load())],
            keywords=[],
        )

        ast.fix_missing_locations(new_node)

        return new_node

    def visit_Dict(self, node):
        self.generic_visit(node)

        if any(k is None for k in node.keys):
            return node

        if not node.keys:
            new_node = ast.Call(
                func=ast.Attribute(value=ast.Name(id="____pymop__injected__builtins____", ctx=ast.Load()), attr="dict", ctx=ast.Load()),
                args=[],
                keywords=[],
                lineno=node.lineno,
                col_offset=node.col_offset,
                end_lineno=node.end_lineno,
                end_col_offset=node.end_col_offset,
            )

            ast.fix_missing_locations(new_node)
            return new_node

        key_value_pairs = [
            ast.Tuple(elts=[k, v], ctx=ast.Load())
            for k, v in zip(node.keys, node.values)
        ]

        new_node = ast.Call(
            func=ast.Attribute(value=ast.Name(id="____pymop__injected__builtins____", ctx=ast.Load()), attr="dict", ctx=ast.Load()),
            args=[ast.List(elts=key_value_pairs, ctx=ast.Load())],
            keywords=[],
            lineno=node.lineno,
            col_offset=node.col_offset,
            end_lineno=node.end_lineno,
            end_col_offset=node.end_col_offset,
        )

        ast.fix_missing_locations(new_node)
        return new_node
        
    def visit_Call(self, node):
        self.generic_visit(node)

        if isinstance(node.func, ast.Name) and node.func.id in ("dict", "list"):
            node = safe_wrapped_builtin_call(
                name=node.func.id,
                args=node.args,
                keywords=node.keywords,
                lineno=node.lineno,
                col_offset=node.col_offset
            )

            ast.fix_missing_locations(node)
            return node
    
        # Transform str.maketrans into ____pymop__injected__builtins____.str_maketrans
        # because str.maketrans expects a builtins.dict as argument and does not accept
        # our custom subclass of dict.
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "str" and node.func.attr == "maketrans":
            node = ast.Call(
                func=ast.Attribute(value=ast.Name(id="____pymop__injected__builtins____", ctx=ast.Load()), attr="str_maketrans", ctx=ast.Load()),
                args=node.args,
                keywords=node.keywords,
            )

            ast.fix_missing_locations(node)
            return node

        # Transform type(obj) into ____pymop__injected__builtins____.type(obj)
        if isinstance(node.func, ast.Name) and node.func.id == "type" and len(node.args) == 1:
            node = ast.Call(
                func=ast.Attribute(value=ast.Name(id="____pymop__injected__builtins____", ctx=ast.Load()), attr="type", ctx=ast.Load()),
                args=node.args,
                keywords=node.keywords,
            )

            ast.fix_missing_locations(node)
            return node
        
        return node

class ASTLoaderWrapper(Delegator, importlib.abc.Loader):
    def __init__(self, loader, origin):
        super().__init__(loader)
        self.origin = origin

    def exec_module(self, module):
        global AST_time  # Add global declaration
        source = self._wrapped.get_data(self.origin)
        start_time = timeit.default_timer()
        old_tree = ast.parse(source, filename=self.origin)

        # orig_code = ast.unparse(old_tree)
        # print('original code\n', orig_code)

        # Code Transformation:
        tree = LiteralTransformer(self.origin).visit(old_tree)

        '''
        We don't need to transform the entire tree as we're not adding
        any new nodes. We only call it on transformed nodes directly.
        '''
        ast.fix_missing_locations(tree)

        # # '''
        # # Debugging code.
        # # '''
        # try:
        #     new_code = ast.unparse(tree)
        #     diff = difflib.ndiff(orig_code.splitlines(), new_code.splitlines())
        #     print('diff of file', self.origin, '\n')
        #     print('\n'.join(diff))
        # except Exception as e:
        #     print('error', e)
        #     pass

        code = compile(tree, self.origin, 'exec')
        module_time = timeit.default_timer() - start_time
        AST_time += module_time

        # add builtins to the module's __dict__
        module.__dict__['____pymop__injected__builtins____'] = ____pymop__injected__builtins____
        module.__dict__['____original__builtins____'] = ____original__builtins____
        exec(code, module.__dict__)

'''
This class is called when Python tries to import a module.
We want to intercept the import and return our own loader,
which will transform the module's AST and compile it.
'''
class ASTMetaPathFinderWrapper(Delegator, importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        # print('ASTMetaPathFinderWrapper find_spec', fullname, path, target)
        spec = self._wrapped.find_spec(fullname, path, target)

        if not spec or not spec.origin or not spec.origin.endswith('.py'):
            return spec

        loader = getattr(spec, "loader", None)
        if not loader or not hasattr(loader, "get_data"):
            return spec
        
        # This ignores python's source code. There should be a better way to do this.
        if 'python3' in spec.origin and 'lib' in spec.origin and not 'site-packages' in spec.origin:
            return spec
        
        if 'numpy/core/_ufunc_config.py' in spec.origin:
            return spec

        spec.loader = ASTLoaderWrapper(loader, spec.origin)
        return spec


class SpecialMetaPathList(list):
    def append(self, *args, **kwargs):
        original_finder = args[0] if args else kwargs['object']
        if isinstance(original_finder, ASTMetaPathFinderWrapper):
            return super().append(original_finder)

        new_object = ASTMetaPathFinderWrapper(original_finder)
        return super().append(new_object)
    
    def insert(self, index, *args, **kwargs):
        original_finder = args[0] if args else kwargs['object']
        if isinstance(original_finder, ASTMetaPathFinderWrapper):
            return super().insert(index, original_finder)

        new_object = ASTMetaPathFinderWrapper(original_finder)
        return super().insert(index, new_object)

'''
This is the main entry point for the module transformer.
It inserts the ASTFinder into sys.meta_path, which is consulted
whenever Python tries to import a module.
'''
new_meta_path = SpecialMetaPathList()
for i, finder in enumerate(sys.meta_path):
    # print('Replacing Finder', finder, type(finder))
    new_meta_path.append(ASTMetaPathFinderWrapper(finder))

sys.meta_path = new_meta_path
# print('sys.meta_path', sys.meta_path)

'''
Force python to reload all previously imported modules
by going through all loaded modules and reload them

'''
import importlib
importlib.invalidate_caches()

loaded_modules = [*sys.modules.values()]

for module in loaded_modules:
    if 'importlib' not in module.__name__ and \
        '__main__' not in module.__name__ and \
        'typing.io' not in module.__name__ \
        and 'typing.re' not in module.__name__:
        importlib.reload(module)

print('Pythonmop sitecustomize finished...')
atexit.register(lambda: print(f'Pythonmop AST time: {AST_time:.6f} seconds'))