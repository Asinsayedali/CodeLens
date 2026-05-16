"""Graph builder for creating dependency graph structure"""

from pathlib import Path
from typing import Dict, List, Any, Tuple
import json
from sqlalchemy.orm import Session
from app.database import GraphNode, GraphEdge


class GraphBuilder:
    """Build graph structure from analysis results"""
    
    def __init__(self, project_id: int, repo_root: Path):
        self.project_id = project_id
        self.repo_root = repo_root
        self.nodes: List[Dict[str, Any]] = []
        self.edges: List[Dict[str, Any]] = []
        self.node_id_map: Dict[str, str] = {}  # entity_key -> node_id
    
    def _generate_node_id(self, file_path: str, entity_type: str, entity_name: str) -> str:
        """Generate unique node ID"""
        return f"{self.project_id}:{file_path}:{entity_type}:{entity_name}"
    
    def add_file_node(self, file_path: str, language: str, analysis: Dict[str, Any]):
        """Add a file node to the graph"""
        node_id = self._generate_node_id(file_path, 'file', file_path)
        
        self.nodes.append({
            'node_id': node_id,
            'node_type': 'file',
            'name': Path(file_path).name,
            'file_path': file_path,
            'line_number': None,
            'importance_score': 0.0,
            'node_metadata': json.dumps({
                'language': language,
                'full_path': file_path,
                'num_imports': len(analysis.get('imports', [])),
                'num_classes': len(analysis.get('classes', [])),
                'num_functions': len(analysis.get('functions', []))
            })
        })
        
        self.node_id_map[f"file:{file_path}"] = node_id
    
    def add_class_node(self, file_path: str, class_info: Dict[str, Any]):
        """Add a class node to the graph"""
        class_name = class_info['name']
        node_id = self._generate_node_id(file_path, 'class', class_name)
        
        self.nodes.append({
            'node_id': node_id,
            'node_type': 'class',
            'name': class_name,
            'file_path': file_path,
            'line_number': class_info.get('line'),
            'importance_score': 0.0,
            'node_metadata': json.dumps({
                'bases': class_info.get('bases', []),
                'methods': class_info.get('methods', []),
                'docstring': class_info.get('docstring')
            })
        })
        
        self.node_id_map[f"class:{file_path}:{class_name}"] = node_id
        
        # Add edge from file to class
        file_node_id = self.node_id_map.get(f"file:{file_path}")
        if file_node_id:
            self.edges.append({
                'source_node_id': file_node_id,
                'target_node_id': node_id,
                'edge_type': 'contains',
                'weight': 1
            })
    
    def add_function_node(self, file_path: str, func_info: Dict[str, Any]):
        """Add a function node to the graph"""
        func_name = func_info['name']
        node_id = self._generate_node_id(file_path, 'function', func_name)
        
        self.nodes.append({
            'node_id': node_id,
            'node_type': 'function',
            'name': func_name,
            'file_path': file_path,
            'line_number': func_info.get('line'),
            'importance_score': 0.0,
            'node_metadata': json.dumps({
                'args': func_info.get('args', []),
                'is_async': func_info.get('is_async', False),
                'docstring': func_info.get('docstring'),
                'type': func_info.get('type', 'function')
            })
        })
        
        self.node_id_map[f"function:{file_path}:{func_name}"] = node_id
        
        # Add edge from file to function
        file_node_id = self.node_id_map.get(f"file:{file_path}")
        if file_node_id:
            self.edges.append({
                'source_node_id': file_node_id,
                'target_node_id': node_id,
                'edge_type': 'contains',
                'weight': 1
            })
    
    def add_dependency_edge(self, source_file: str, target_file: str, edge_type: str, details: Dict[str, Any]):
        """Add a dependency edge between files"""
        source_node_id = self.node_id_map.get(f"file:{source_file}")
        target_node_id = self.node_id_map.get(f"file:{target_file}")
        
        if source_node_id and target_node_id:
            self.edges.append({
                'source_node_id': source_node_id,
                'target_node_id': target_node_id,
                'edge_type': edge_type,
                'weight': 1
            })
    
    def update_importance_scores(self, scores: Dict[str, float]):
        """Update importance scores for file nodes"""
        for node in self.nodes:
            if node['node_type'] == 'file':
                file_path = node['file_path']
                if file_path in scores:
                    node['importance_score'] = scores[file_path]
    
    def save_to_database(self, db: Session):
        """Save graph to database"""
        # Save nodes
        node_objects = []
        for node_data in self.nodes:
            node = GraphNode(
                project_id=self.project_id,
                **node_data
            )
            node_objects.append(node)
        
        db.bulk_save_objects(node_objects)
        db.commit()
        
        # Save edges
        edge_objects = []
        for edge_data in self.edges:
            edge = GraphEdge(
                project_id=self.project_id,
                **edge_data
            )
            edge_objects.append(edge)
        
        db.bulk_save_objects(edge_objects)
        db.commit()
        
        print(f"✅ Saved {len(node_objects)} nodes and {len(edge_objects)} edges to database")
    
    def get_graph_data(self) -> Dict[str, Any]:
        """Get graph data for visualization"""
        return {
            'nodes': self.nodes,
            'edges': self.edges,
            'stats': {
                'total_nodes': len(self.nodes),
                'total_edges': len(self.edges),
                'node_types': self._count_node_types(),
                'edge_types': self._count_edge_types()
            }
        }
    
    def _count_node_types(self) -> Dict[str, int]:
        """Count nodes by type"""
        counts = {}
        for node in self.nodes:
            node_type = node['node_type']
            counts[node_type] = counts.get(node_type, 0) + 1
        return counts
    
    def _count_edge_types(self) -> Dict[str, int]:
        """Count edges by type"""
        counts = {}
        for edge in self.edges:
            edge_type = edge['edge_type']
            counts[edge_type] = counts.get(edge_type, 0) + 1
        return counts

# Made with Bob
