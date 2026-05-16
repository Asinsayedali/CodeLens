// Type definitions for Grasp

export interface Project {
  id: number;
  name: string;
  repo_url?: string;
  local_path: string;
  language?: string;
  total_files?: number;
  total_lines?: number;
  created_at: string;
  last_analyzed?: string;
  status: 'pending' | 'analyzing' | 'completed' | 'failed';
}

export interface GraphNode {
  id: string;
  type: 'file' | 'class' | 'function' | 'module';
  name: string;
  file_path?: string;
  line_number?: number;
  importance_score?: number;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: 'import' | 'call' | 'extends' | 'implements';
  weight?: number;
}

// React Flow compatible types
export interface ReactFlowNodeData {
  label: string;
  type: string;
  file_path?: string;
  line_number?: number;
  importance_score?: number;
  metadata?: Record<string, any>;
}

export interface ReactFlowNode {
  id: string;
  type: string;
  data: ReactFlowNodeData;
  position: { x: number; y: number };
}

export interface ReactFlowEdge {
  id: string;
  source: string;
  target: string;
  type?: string;
  label?: string;
  animated?: boolean;
}

export interface GraphData {
  nodes: ReactFlowNode[];
  edges: ReactFlowEdge[];
  stats?: {
    total_nodes: number;
    total_edges: number;
    node_types: Record<string, number>;
    edge_types: Record<string, number>;
  };
}

// API response types (match backend GraphNodeResponse / GraphEdgeResponse)
export interface ApiGraphNode {
  id: number;
  project_id: number;
  node_id: string;
  node_type: string;
  name: string;
  file_path?: string;
  line_number?: number;
  importance_score: number;
  node_metadata?: string;
}

export interface ApiGraphEdge {
  id: number;
  project_id: number;
  source_node_id: string;
  target_node_id: string;
  edge_type: string;
  weight: number;
}

export interface NodeDetails {
  node: ApiGraphNode;
  incoming_edges: ApiGraphEdge[];
  outgoing_edges: ApiGraphEdge[];
  related_nodes: ApiGraphNode[];
  metadata?: Record<string, any>;
}

export interface Documentation {
  id: number;
  section_name: string;
  content: string;
  order_index: number;
}

export interface DocumentationResponse {
  project_id: number;
  project_name: string;
  documentation: Record<string, string>;
  generated_at?: string;
}

export interface DocGenerationRequest {
  section?: 'overview' | 'getting_started' | 'architecture' | 'api';
}

export interface DocGenerationResponse {
  status: string;
  message: string;
  documentation?: Record<string, string>;
}

export interface CodeSnippet {
  file_path: string;
  code: string;
  similarity: number;
}

export interface QAResponse {
  answer: string;
  code_snippets: CodeSnippet[];
  confidence: number;
  timestamp: string | null;
}

export interface QAMessage {
  id: number;
  question: string;
  answer: string;
  timestamp: string;
}

export interface SuggestedQuestions {
  suggestions: string[];
}

export interface TechDebtItem {
  id: number;
  title: string;
  description?: string;
  file_path?: string;
  line_number?: number;
  severity: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  priority: number;
  estimated_effort?: string;
}

// Made with Bob
