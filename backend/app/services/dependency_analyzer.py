"""Dependency analyzer for extracting relationships between code entities"""

from pathlib import Path
from typing import Dict, List, Set, Any, Tuple


class DependencyAnalyzer:
    """Analyze dependencies between code entities"""
    
    def __init__(self):
        self.file_map: Dict[str, Dict[str, Any]] = {}  # file_path -> analysis result
        self.module_map: Dict[str, str] = {}  # module_name -> file_path
    
    def add_file_analysis(self, file_path: Path, analysis: Dict[str, Any], repo_root: Path):
        """Add analysis result for a file"""
        rel_path = str(file_path.relative_to(repo_root))
        self.file_map[rel_path] = analysis
        
        # Build module map for Python files
        if file_path.suffix == '.py':
            module_name = self._path_to_module(file_path, repo_root)
            self.module_map[module_name] = rel_path
    
    def _path_to_module(self, file_path: Path, repo_root: Path) -> str:
        """Convert file path to Python module name"""
        rel_path = file_path.relative_to(repo_root)
        
        # Remove .py extension
        if rel_path.stem == '__init__':
            # For __init__.py, use parent directory
            parts = rel_path.parent.parts
        else:
            parts = rel_path.with_suffix('').parts
        
        return '.'.join(parts)
    
    def _resolve_import(self, import_module: str, current_file: str) -> str:
        """Resolve import to actual file path"""
        # Try direct module lookup
        if import_module in self.module_map:
            return self.module_map[import_module]
        
        # Try with __init__
        init_module = f"{import_module}.__init__"
        if init_module in self.module_map:
            return self.module_map[init_module]
        
        # Try relative imports
        current_dir = str(Path(current_file).parent)
        for module_name, file_path in self.module_map.items():
            if file_path.startswith(current_dir) and module_name.endswith(import_module):
                return file_path
        
        return None
    
    def extract_dependencies(self) -> List[Dict[str, Any]]:
        """
        Extract all dependencies between files
        
        Returns:
            List of dependency relationships with:
            - source: source file path
            - target: target file path
            - type: dependency type (import, call, etc.)
            - details: additional information
        """
        dependencies = []
        
        for file_path, analysis in self.file_map.items():
            # Process imports
            for imp in analysis.get('imports', []):
                module = imp.get('module') or imp.get('from_module', '')
                
                # Resolve to actual file
                target_file = self._resolve_import(module, file_path)
                
                if target_file and target_file != file_path:
                    dependencies.append({
                        'source': file_path,
                        'target': target_file,
                        'type': 'imports',
                        'details': {
                            'module': module,
                            'line': imp.get('line')
                        }
                    })
            
            # Process function calls (for internal dependencies)
            for call in analysis.get('calls', []):
                func_name = call.get('function', '')
                
                # Try to find which file defines this function
                target_file = self._find_function_definition(func_name, file_path)
                
                if target_file and target_file != file_path:
                    dependencies.append({
                        'source': file_path,
                        'target': target_file,
                        'type': 'calls',
                        'details': {
                            'function': func_name,
                            'line': call.get('line')
                        }
                    })
        
        return dependencies
    
    def _find_function_definition(self, func_name: str, current_file: str) -> str:
        """Find which file defines a function"""
        # Simple heuristic: look for function in imported modules
        current_analysis = self.file_map.get(current_file, {})
        
        for imp in current_analysis.get('imports', []):
            module = imp.get('module') or imp.get('from_module', '')
            target_file = self._resolve_import(module, current_file)
            
            if target_file:
                target_analysis = self.file_map.get(target_file, {})
                
                # Check if function is defined in target file
                for func in target_analysis.get('functions', []):
                    if func.get('name') == func_name:
                        return target_file
                
                # Check classes and methods
                for cls in target_analysis.get('classes', []):
                    if func_name in cls.get('methods', []):
                        return target_file
        
        return None
    
    def get_file_dependencies(self, file_path: str) -> Dict[str, List[str]]:
        """
        Get dependencies for a specific file
        
        Returns:
            Dict with 'imports' and 'imported_by' lists
        """
        imports = []
        imported_by = []
        
        for dep in self.extract_dependencies():
            if dep['source'] == file_path:
                imports.append(dep['target'])
            elif dep['target'] == file_path:
                imported_by.append(dep['source'])
        
        return {
            'imports': list(set(imports)),
            'imported_by': list(set(imported_by))
        }
    
    def calculate_importance_scores(self) -> Dict[str, float]:
        """
        Calculate importance score for each file based on:
        - Number of files that depend on it
        - Number of dependencies it has
        - Centrality in the dependency graph
        """
        scores = {}
        dependencies = self.extract_dependencies()
        
        # Count incoming and outgoing dependencies
        incoming = {}
        outgoing = {}
        
        for dep in dependencies:
            source = dep['source']
            target = dep['target']
            
            incoming[target] = incoming.get(target, 0) + 1
            outgoing[source] = outgoing.get(source, 0) + 1
        
        # Calculate scores
        for file_path in self.file_map.keys():
            in_count = incoming.get(file_path, 0)
            out_count = outgoing.get(file_path, 0)
            
            # Files with more incoming dependencies are more important
            # Files with fewer outgoing dependencies are more self-contained
            score = in_count * 2 + (1 / (out_count + 1))
            scores[file_path] = score
        
        # Normalize scores to 0-1 range
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                scores = {k: v / max_score for k, v in scores.items()}
        
        return scores

# Made with Bob
