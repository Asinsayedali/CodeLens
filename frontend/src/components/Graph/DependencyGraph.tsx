import React, { useCallback, useEffect, useState } from 'react';
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Node,
  BackgroundVariant,
  Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { graphApi } from '../../services/api';
import { GraphData, ReactFlowNode } from '../../types';
import { nodeTypes } from './CustomNodes';
import GraphControls from './GraphControls';
import NodeDetails from './NodeDetails';

interface DependencyGraphProps {
  projectId: number;
}

const DependencyGraph: React.FC<DependencyGraphProps> = ({ projectId }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<ReactFlowNode | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [graphStats, setGraphStats] = useState<any>(null);
  const [activeLayout, setActiveLayout] = useState<'hierarchical' | 'force'>('hierarchical');

  useEffect(() => {
    loadGraphData('hierarchical');
  }, [projectId]);

  const loadGraphData = async (layout: 'hierarchical' | 'force' = 'hierarchical') => {
    try {
      setLoading(true);
      setError(null);
      setActiveLayout(layout);
      const response = await graphApi.getReactFlowGraph(projectId, layout);
      const data: GraphData = response.data;
      setNodes(data.nodes);
      setEdges(data.edges);
      setGraphStats(data.stats);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load graph data');
    } finally {
      setLoading(false);
    }
  };

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
    setSelectedNode(node as ReactFlowNode);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
  }, []);

  // Filter nodes based on search and type
  const filteredNodes = nodes.filter((node) => {
    const matchesSearch =
      searchTerm === '' ||
      node.data.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (node.data.file_path && node.data.file_path.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesType = filterType === 'all' || node.type === filterType;
    return matchesSearch && matchesType;
  });

  const visibleNodeIds = new Set(filteredNodes.map(n => n.id));

  // Dim edges not connected to the selected node
  const selectedNodeId = selectedNode?.id ?? null;
  const filteredEdges = edges
    .filter(e => visibleNodeIds.has(e.source) && visibleNodeIds.has(e.target))
    .map(e => {
      const connected =
        selectedNodeId === null ||
        e.source === selectedNodeId ||
        e.target === selectedNodeId;
      return {
        ...e,
        animated: connected && selectedNodeId !== null,
        style: {
          stroke: connected
            ? e.source === selectedNodeId
              ? 'var(--color-graph-edge-outgoing)'
              : 'var(--color-graph-edge-incoming)'
            : 'var(--color-gray-700)',
          strokeWidth: connected && selectedNodeId !== null ? 2 : 1,
          opacity: selectedNodeId === null || connected ? 1 : 0.2,
        },
      };
    });

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full bg-black">
        <div className="text-center">
          <div className="spinner w-12 h-12 mx-auto" />
          <p className="mt-4 text-gray-400 text-sm">Loading dependency graph...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full bg-black">
        <div className="text-center max-w-md px-6">
          <div className="w-16 h-16 rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mx-auto mb-4 text-2xl">
            ⚠️
          </div>
          <p className="text-red-400 font-semibold mb-2">Failed to load graph</p>
          <p className="text-gray-400 text-sm mb-6">{error}</p>
          <button
            onClick={() => loadGraphData()}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full relative">
      <ReactFlow
        nodes={filteredNodes}
        edges={filteredEdges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
        className="bg-black"
        defaultEdgeOptions={{
          style: { stroke: 'var(--color-gray-700)', strokeWidth: 1 },
        }}
      >
        <Background variant={BackgroundVariant.Dots} gap={16} size={1} color="var(--color-gray-800)" />
        <Controls className="!bg-[#111] !border-[#2e2e2e] !shadow-lg [&_button]:transition-colors [&_button:hover]:bg-[#1c1c1c]" />
        <MiniMap
          nodeColor={(node) => {
            switch (node.type) {
              case 'fileNode':     return 'var(--color-graph-file)';
              case 'classNode':    return 'var(--color-graph-class)';
              case 'functionNode':
              case 'methodNode':   return 'var(--color-graph-function)';
              default:             return 'var(--color-gray-500)';
            }
          }}
          style={{ background: 'var(--color-gray-900)', border: '1px solid var(--color-gray-700)' }}
          maskColor="rgba(0,0,0,0.4)"
        />

        {/* Controls panel */}
        <Panel position="top-left" className="m-3">
          <div className="glass-effect rounded-xl shadow-2xl p-4">
            <GraphControls
              searchTerm={searchTerm}
              onSearchChange={setSearchTerm}
              filterType={filterType}
              onFilterChange={setFilterType}
              onLayoutChange={loadGraphData}
              activeLayout={activeLayout}
              stats={graphStats}
            />
          </div>
        </Panel>

        {/* Legend */}
        <Panel position="top-right" className="m-3">
          <div className="glass-effect rounded-xl shadow-2xl p-3">
            <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-2">Legend</p>
            <div className="space-y-1.5">
              {[
                { color: 'bg-blue-500',   label: 'File' },
                { color: 'bg-purple-500', label: 'Class' },
                { color: 'bg-green-500',  label: 'Function' },
              ].map(({ color, label }) => (
                <div key={label} className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${color}`} />
                  <span className="text-xs text-gray-300">{label}</span>
                </div>
              ))}
            </div>
            {selectedNode && (
              <div className="mt-3 pt-2.5 border-t border-[#2e2e2e]/50 space-y-1.5">
                <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">Edges</p>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-0.5 bg-cyan-400 rounded" />
                  <span className="text-xs text-gray-300">Outgoing</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-0.5 bg-orange-400 rounded" />
                  <span className="text-xs text-gray-300">Incoming</span>
                </div>
              </div>
            )}
          </div>
        </Panel>
      </ReactFlow>

      {/* Node Details Sidebar */}
      {selectedNode && (
        <div
          className="absolute right-3 top-3 bottom-3 w-[480px] glass-effect rounded-xl shadow-2xl overflow-hidden flex flex-col z-10"
          style={{ maxHeight: 'calc(100% - 24px)' }}
          role="complementary"
          aria-label="Node details panel"
        >
          <NodeDetails
            projectId={projectId}
            node={selectedNode}
            onClose={() => setSelectedNode(null)}
          />
        </div>
      )}
    </div>
  );
};

export default DependencyGraph;

// Made with Bob
