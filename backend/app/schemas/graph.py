"""Graph schemas for API requests and responses"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel


class GraphNodeBase(BaseModel):
    """Base graph node schema"""
    node_id: str
    node_type: str
    name: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    importance_score: float = 0.0
    node_metadata: Optional[str] = None


class GraphNodeResponse(GraphNodeBase):
    """Schema for graph node response"""
    id: int
    project_id: int
    
    class Config:
        from_attributes = True


class GraphEdgeBase(BaseModel):
    """Base graph edge schema"""
    source_node_id: str
    target_node_id: str
    edge_type: str
    weight: int = 1


class GraphEdgeResponse(GraphEdgeBase):
    """Schema for graph edge response"""
    id: int
    project_id: int
    
    class Config:
        from_attributes = True


class GraphData(BaseModel):
    """Complete graph data for visualization"""
    nodes: List[GraphNodeResponse]
    edges: List[GraphEdgeResponse]
    stats: Optional[Dict[str, Any]] = None


# React Flow compatible schemas
class ReactFlowPosition(BaseModel):
    """Position for React Flow node"""
    x: float
    y: float


class ReactFlowNodeData(BaseModel):
    """Data payload for React Flow node"""
    label: str
    type: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    importance_score: float = 0.0
    metadata: Optional[Dict[str, Any]] = None


class ReactFlowNode(BaseModel):
    """React Flow compatible node"""
    id: str
    type: str = "default"
    data: ReactFlowNodeData
    position: ReactFlowPosition


class ReactFlowEdge(BaseModel):
    """React Flow compatible edge"""
    id: str
    source: str
    target: str
    type: str = "default"
    label: Optional[str] = None
    animated: bool = False


class ReactFlowGraphData(BaseModel):
    """React Flow compatible graph data"""
    nodes: List[ReactFlowNode]
    edges: List[ReactFlowEdge]
    stats: Optional[Dict[str, Any]] = None


class NodeDetailsResponse(BaseModel):
    """Detailed information about a specific node"""
    node: GraphNodeResponse
    incoming_edges: List[GraphEdgeResponse]
    outgoing_edges: List[GraphEdgeResponse]
    related_nodes: List[GraphNodeResponse]
    metadata: Optional[Dict[str, Any]] = None

# Made with Bob
