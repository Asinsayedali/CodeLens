"""Graph serialization service for converting to React Flow format"""

import json
import math
from typing import List, Dict, Any, Tuple
from app.schemas.graph import (
    GraphNodeResponse,
    GraphEdgeResponse,
    ReactFlowNode,
    ReactFlowEdge,
    ReactFlowNodeData,
    ReactFlowPosition,
    ReactFlowGraphData
)


class GraphSerializer:
    """Serialize graph data to React Flow compatible format"""
    
    # Node type to React Flow type mapping
    NODE_TYPE_MAP = {
        'file': 'fileNode',
        'class': 'classNode',
        'function': 'functionNode',
        'method': 'methodNode'
    }
    
    # Edge type styling
    EDGE_TYPE_MAP = {
        'imports': {'animated': True, 'type': 'smoothstep'},
        'contains': {'animated': False, 'type': 'default'},
        'calls': {'animated': True, 'type': 'straight'},
        'inherits': {'animated': False, 'type': 'step'}
    }
    
    def __init__(self):
        self.node_positions: Dict[str, Tuple[float, float]] = {}
    
    def serialize_to_react_flow(
        self,
        nodes: List[GraphNodeResponse],
        edges: List[GraphEdgeResponse],
        stats: Dict[str, Any] | None = None
    ) -> ReactFlowGraphData:
        """Convert graph data to React Flow format"""
        
        # Calculate layout positions
        self._calculate_layout(nodes, edges)
        
        # Convert nodes
        react_flow_nodes = []
        for node in nodes:
            react_flow_node = self._convert_node(node)
            react_flow_nodes.append(react_flow_node)
        
        # Convert edges
        react_flow_edges = []
        for edge in edges:
            react_flow_edge = self._convert_edge(edge)
            react_flow_edges.append(react_flow_edge)
        
        return ReactFlowGraphData(
            nodes=react_flow_nodes,
            edges=react_flow_edges,
            stats=stats
        )
    
    def _convert_node(self, node: GraphNodeResponse) -> ReactFlowNode:
        """Convert a graph node to React Flow format"""
        
        # Parse metadata
        metadata = {}
        if node.node_metadata:
            try:
                metadata = json.loads(node.node_metadata)
            except json.JSONDecodeError:
                pass
        
        # Get position
        position = self.node_positions.get(
            node.node_id,
            (0.0, 0.0)
        )
        
        # Determine node type for React Flow
        react_flow_type = self.NODE_TYPE_MAP.get(node.node_type, 'default')
        
        return ReactFlowNode(
            id=node.node_id,
            type=react_flow_type,
            data=ReactFlowNodeData(
                label=node.name,
                type=node.node_type,
                file_path=node.file_path,
                line_number=node.line_number,
                importance_score=node.importance_score,
                metadata=metadata
            ),
            position=ReactFlowPosition(x=position[0], y=position[1])
        )
    
    def _convert_edge(self, edge: GraphEdgeResponse) -> ReactFlowEdge:
        """Convert a graph edge to React Flow format"""
        
        # Get edge styling based on type
        edge_config = self.EDGE_TYPE_MAP.get(
            edge.edge_type,
            {'animated': False, 'type': 'default'}
        )
        
        return ReactFlowEdge(
            id=f"{edge.source_node_id}-{edge.target_node_id}",
            source=edge.source_node_id,
            target=edge.target_node_id,
            type=edge_config['type'],
            label=edge.edge_type,
            animated=edge_config['animated']
        )
    
    def _calculate_layout(
        self,
        nodes: List[GraphNodeResponse],
        edges: List[GraphEdgeResponse]
    ):
        """Calculate node positions using a force-directed layout algorithm"""
        
        if not nodes:
            return
        
        # Group nodes by type for better layout
        node_groups = self._group_nodes_by_type(nodes)
        
        # Build adjacency list for layout calculation
        adjacency = self._build_adjacency_list(edges)
        
        # Calculate positions based on node type and relationships
        y_offset = 0
        for node_type, type_nodes in node_groups.items():
            x_offset = 0
            nodes_per_row = math.ceil(math.sqrt(len(type_nodes)))
            
            for i, node in enumerate(type_nodes):
                row = i // nodes_per_row
                col = i % nodes_per_row
                
                x = col * 300 + x_offset
                y = row * 150 + y_offset
                
                self.node_positions[node.node_id] = (x, y)
            
            # Offset for next node type group
            y_offset += (len(type_nodes) // nodes_per_row + 1) * 150 + 100
    
    def _group_nodes_by_type(
        self,
        nodes: List[GraphNodeResponse]
    ) -> Dict[str, List[GraphNodeResponse]]:
        """Group nodes by their type"""
        groups = {}
        for node in nodes:
            if node.node_type not in groups:
                groups[node.node_type] = []
            groups[node.node_type].append(node)
        return groups
    
    def _build_adjacency_list(
        self,
        edges: List[GraphEdgeResponse]
    ) -> Dict[str, List[str]]:
        """Build adjacency list from edges"""
        adjacency = {}
        for edge in edges:
            if edge.source_node_id not in adjacency:
                adjacency[edge.source_node_id] = []
            adjacency[edge.source_node_id].append(edge.target_node_id)
        return adjacency
    
    def calculate_hierarchical_layout(
        self,
        nodes: List[GraphNodeResponse],
        edges: List[GraphEdgeResponse]
    ):
        """Calculate hierarchical layout for better visualization of dependencies"""
        
        if not nodes:
            return
        
        # Build graph structure
        adjacency = self._build_adjacency_list(edges)
        in_degree = {node.node_id: 0 for node in nodes}
        
        for edge in edges:
            in_degree[edge.target_node_id] = in_degree.get(edge.target_node_id, 0) + 1
        
        # Topological sort to determine levels
        levels = {}
        queue = [node.node_id for node in nodes if in_degree[node.node_id] == 0]
        current_level = 0
        
        while queue:
            next_queue = []
            for node_id in queue:
                levels[node_id] = current_level
                
                # Process neighbors
                for neighbor in adjacency.get(node_id, []):
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        next_queue.append(neighbor)
            
            queue = next_queue
            current_level += 1
        
        # Assign remaining nodes (cycles) to last level
        for node in nodes:
            if node.node_id not in levels:
                levels[node.node_id] = current_level
        
        # Calculate positions based on levels
        level_nodes = {}
        for node_id, level in levels.items():
            if level not in level_nodes:
                level_nodes[level] = []
            level_nodes[level].append(node_id)
        
        # Position nodes
        for level, node_ids in level_nodes.items():
            y = level * 200
            x_spacing = 300
            total_width = len(node_ids) * x_spacing
            x_start = -total_width / 2
            
            for i, node_id in enumerate(node_ids):
                x = x_start + i * x_spacing
                self.node_positions[node_id] = (x, y)

# Made with Bob