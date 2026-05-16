"""AST analyzer for extracting code structure from Python and JavaScript/TypeScript files"""

import ast
from pathlib import Path
from typing import List, Dict, Any, Optional
import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
from tree_sitter import Language, Parser


class PythonASTAnalyzer:
    """Analyze Python files using the built-in ast module"""
    
    def __init__(self):
        pass
    
    def _get_name(self, node: ast.AST) -> str:
        """Extract name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return "unknown"
    
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a Python file and extract structure
        
        Returns:
            Dict containing:
            - imports: list of imported modules
            - classes: list of class definitions
            - functions: list of function definitions
            - calls: list of function calls
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source, filename=str(file_path))
            
            result = {
                'imports': [],
                'classes': [],
                'functions': [],
                'calls': []
            }
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        result['imports'].append({
                            'module': alias.name,
                            'alias': alias.asname,
                            'line': node.lineno
                        })
                
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        result['imports'].append({
                            'module': f"{module}.{alias.name}" if module else alias.name,
                            'from_module': module,
                            'name': alias.name,
                            'alias': alias.asname,
                            'line': node.lineno
                        })
                
                elif isinstance(node, ast.ClassDef):
                    result['classes'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'bases': [self._get_name(base) for base in node.bases],
                        'methods': [m.name for m in node.body if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))],
                        'docstring': ast.get_docstring(node)
                    })
                
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    result['functions'].append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'is_async': isinstance(node, ast.AsyncFunctionDef),
                        'docstring': ast.get_docstring(node)
                    })
                
                elif isinstance(node, ast.Call):
                    func_name = self._get_name(node.func)
                    if func_name != "unknown":
                        result['calls'].append({
                            'function': func_name,
                            'line': node.lineno
                        })
            
            return result
            
        except Exception as e:
            print(f"Error analyzing Python file {file_path}: {e}")
            return {
                'imports': [],
                'classes': [],
                'functions': [],
                'calls': [],
                'error': str(e)
            }


class JavaScriptASTAnalyzer:
    """Analyze JavaScript/TypeScript files using tree-sitter"""
    
    def __init__(self):
        # Initialize tree-sitter parsers
        self.js_language = Language(tsjavascript.language())
        self.js_parser = Parser(self.js_language)
    
    def _extract_imports(self, tree, source_bytes: bytes) -> List[Dict[str, Any]]:
        """Extract import statements"""
        imports = []
        
        query = self.js_language.query("""
            (import_statement) @import
        """)
        
        captures = query.captures(tree.root_node)
        
        for node, _ in captures:
            import_text = source_bytes[node.start_byte:node.end_byte].decode('utf-8')
            imports.append({
                'statement': import_text,
                'line': node.start_point[0] + 1
            })
        
        return imports
    
    def _extract_functions(self, tree, source_bytes: bytes) -> List[Dict[str, Any]]:
        """Extract function declarations"""
        functions = []
        
        query = self.js_language.query("""
            (function_declaration
                name: (identifier) @name) @function
            (arrow_function) @arrow
            (method_definition
                name: (property_identifier) @method_name) @method
        """)
        
        captures = query.captures(tree.root_node)
        
        for node, capture_name in captures:
            if capture_name == 'name':
                func_name = source_bytes[node.start_byte:node.end_byte].decode('utf-8')
                functions.append({
                    'name': func_name,
                    'line': node.start_point[0] + 1,
                    'type': 'function'
                })
            elif capture_name == 'method_name':
                method_name = source_bytes[node.start_byte:node.end_byte].decode('utf-8')
                functions.append({
                    'name': method_name,
                    'line': node.start_point[0] + 1,
                    'type': 'method'
                })
        
        return functions
    
    def _extract_classes(self, tree, source_bytes: bytes) -> List[Dict[str, Any]]:
        """Extract class declarations"""
        classes = []
        
        query = self.js_language.query("""
            (class_declaration
                name: (identifier) @name) @class
        """)
        
        captures = query.captures(tree.root_node)
        
        for node, capture_name in captures:
            if capture_name == 'name':
                class_name = source_bytes[node.start_byte:node.end_byte].decode('utf-8')
                classes.append({
                    'name': class_name,
                    'line': node.start_point[0] + 1
                })
        
        return classes
    
    def _extract_calls(self, tree, source_bytes: bytes) -> List[Dict[str, Any]]:
        """Extract function calls"""
        calls = []
        
        query = self.js_language.query("""
            (call_expression
                function: (identifier) @func_name) @call
            (call_expression
                function: (member_expression
                    property: (property_identifier) @method_name)) @method_call
        """)
        
        captures = query.captures(tree.root_node)
        
        for node, capture_name in captures:
            if capture_name in ['func_name', 'method_name']:
                func_name = source_bytes[node.start_byte:node.end_byte].decode('utf-8')
                calls.append({
                    'function': func_name,
                    'line': node.start_point[0] + 1
                })
        
        return calls
    
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a JavaScript/TypeScript file and extract structure
        
        Returns:
            Dict containing:
            - imports: list of import statements
            - classes: list of class definitions
            - functions: list of function definitions
            - calls: list of function calls
        """
        try:
            with open(file_path, 'rb') as f:
                source_bytes = f.read()
            
            tree = self.js_parser.parse(source_bytes)
            
            result = {
                'imports': self._extract_imports(tree, source_bytes),
                'classes': self._extract_classes(tree, source_bytes),
                'functions': self._extract_functions(tree, source_bytes),
                'calls': self._extract_calls(tree, source_bytes)
            }
            
            return result
            
        except Exception as e:
            print(f"Error analyzing JavaScript file {file_path}: {e}")
            return {
                'imports': [],
                'classes': [],
                'functions': [],
                'calls': [],
                'error': str(e)
            }


class ASTAnalyzer:
    """Unified AST analyzer that handles multiple languages"""
    
    def __init__(self):
        self.python_analyzer = PythonASTAnalyzer()
        self.js_analyzer = JavaScriptASTAnalyzer()
    
    def analyze_file(self, file_path: Path, language: str) -> Dict[str, Any]:
        """Analyze a file based on its language"""
        if language == 'python':
            return self.python_analyzer.analyze_file(file_path)
        elif language in ['javascript', 'typescript']:
            return self.js_analyzer.analyze_file(file_path)
        else:
            raise ValueError(f"Unsupported language: {language}")

# Made with Bob
