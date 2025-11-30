"""
Security utilities for safe code execution.
Uses AST-based analysis to detect forbidden imports and dangerous constructs.
"""

import ast
from typing import Tuple, List, Set

# Forbidden modules that could be used for malicious purposes
FORBIDDEN_MODULES: Set[str] = {
    'os',
    'subprocess',
    'sys',
    'shutil',
    'socket',
    'importlib',
    'ctypes',
    'multiprocessing',
    'threading',
    'signal',
    'pty',
    'fcntl',
    'resource',
    'sysconfig',
    'builtins',
    '__builtins__',
    'code',
    'codeop',
    'gc',
    'inspect',
    'traceback',
    'linecache',
    'pickle',
    'shelve',
    'marshal',
    'dbm',
    'sqlite3',
    'urllib',
    'http',
    'ftplib',
    'smtplib',
    'telnetlib',
    'xmlrpc',
    'pathlib',  # Can be used for file system access
}

# Forbidden built-in functions/names
FORBIDDEN_BUILTINS: Set[str] = {
    'eval',
    'exec',
    'compile',
    'open',
    '__import__',
    'globals',
    'locals',
    'vars',
    'dir',
    'getattr',
    'setattr',
    'delattr',
    'hasattr',
    'breakpoint',
    'input',  # Could hang the process
    'memoryview',
    'type',  # Can be used to create new types dynamically
}


class SecurityVisitor(ast.NodeVisitor):
    """AST visitor to detect forbidden imports and function calls."""
    
    def __init__(self):
        self.violations: List[dict] = []
    
    def visit_Import(self, node: ast.Import):
        """Check regular imports: import os, import subprocess"""
        for alias in node.names:
            module_name = alias.name.split('.')[0]
            if module_name in FORBIDDEN_MODULES:
                self.violations.append({
                    'line': node.lineno,
                    'type': 'forbidden_import',
                    'message': f"Import of '{alias.name}' is not allowed for security reasons"
                })
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Check from imports: from os import path"""
        if node.module:
            module_name = node.module.split('.')[0]
            if module_name in FORBIDDEN_MODULES:
                self.violations.append({
                    'line': node.lineno,
                    'type': 'forbidden_import',
                    'message': f"Import from '{node.module}' is not allowed for security reasons"
                })
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call):
        """Check function calls for forbidden builtins."""
        if isinstance(node.func, ast.Name):
            if node.func.id in FORBIDDEN_BUILTINS:
                self.violations.append({
                    'line': node.lineno,
                    'type': 'forbidden_builtin',
                    'message': f"Use of '{node.func.id}()' is not allowed for security reasons"
                })
        self.generic_visit(node)
    
    def visit_Attribute(self, node: ast.Attribute):
        """Check for attempts to access __builtins__, __class__, etc."""
        if node.attr.startswith('__') and node.attr.endswith('__'):
            if node.attr not in {'__init__', '__str__', '__repr__', '__len__', 
                                  '__iter__', '__next__', '__getitem__', '__setitem__',
                                  '__contains__', '__eq__', '__ne__', '__lt__', 
                                  '__le__', '__gt__', '__ge__', '__hash__',
                                  '__add__', '__sub__', '__mul__', '__truediv__',
                                  '__floordiv__', '__mod__', '__pow__',
                                  '__and__', '__or__', '__xor__', '__invert__',
                                  '__neg__', '__pos__', '__abs__',
                                  '__enter__', '__exit__', '__call__'}:
                self.violations.append({
                    'line': node.lineno,
                    'type': 'forbidden_dunder',
                    'message': f"Access to '{node.attr}' is not allowed for security reasons"
                })
        self.generic_visit(node)


def validate_code(code: str) -> Tuple[bool, List[dict]]:
    """
    Validate Python code for security issues using AST analysis.
    
    Args:
        code: Python source code string
        
    Returns:
        Tuple of (is_safe, violations) where violations is a list of dicts
        with 'line', 'type', and 'message' keys
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, [{
            'line': e.lineno or 1,
            'type': 'syntax_error',
            'message': f"Syntax error: {e.msg}"
        }]
    
    visitor = SecurityVisitor()
    visitor.visit(tree)
    
    return len(visitor.violations) == 0, visitor.violations


def get_safe_globals() -> dict:
    """
    Return a restricted globals dict for code execution.
    Only includes safe built-in functions.
    """
    safe_builtins = {
        # Safe type constructors
        'int': int,
        'float': float,
        'str': str,
        'bool': bool,
        'list': list,
        'dict': dict,
        'set': set,
        'frozenset': frozenset,
        'tuple': tuple,
        'bytes': bytes,
        'bytearray': bytearray,
        'complex': complex,
        
        # Safe functions
        'abs': abs,
        'all': all,
        'any': any,
        'bin': bin,
        'chr': chr,
        'divmod': divmod,
        'enumerate': enumerate,
        'filter': filter,
        'format': format,
        'hex': hex,
        'id': id,
        'isinstance': isinstance,
        'issubclass': issubclass,
        'iter': iter,
        'len': len,
        'map': map,
        'max': max,
        'min': min,
        'next': next,
        'oct': oct,
        'ord': ord,
        'pow': pow,
        'print': print,
        'range': range,
        'repr': repr,
        'reversed': reversed,
        'round': round,
        'slice': slice,
        'sorted': sorted,
        'sum': sum,
        'zip': zip,
        
        # Constants
        'True': True,
        'False': False,
        'None': None,
        
        # Exceptions (for try/except)
        'Exception': Exception,
        'ValueError': ValueError,
        'TypeError': TypeError,
        'KeyError': KeyError,
        'IndexError': IndexError,
        'AttributeError': AttributeError,
        'ZeroDivisionError': ZeroDivisionError,
        'RuntimeError': RuntimeError,
        'StopIteration': StopIteration,
    }
    
    return {'__builtins__': safe_builtins}
