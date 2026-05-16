import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { ReactFlowNodeData } from '../../types';

const FileNode: React.FC<NodeProps<ReactFlowNodeData>> = ({ data, selected }) => (
  <div
    className={`px-3 py-2 rounded-lg border transition-all duration-200 cursor-pointer ${
      selected
        ? 'border-blue-400 bg-blue-950/70 shadow-lg shadow-blue-500/25 ring-2 ring-blue-400/30'
        : 'border-blue-700/40 bg-gray-900/95 hover:border-blue-500/60 hover:bg-blue-950/30 hover:shadow-md'
    }`}
    style={{ minWidth: '130px', maxWidth: '210px' }}
  >
    <Handle type="target" position={Position.Top} style={{ background: 'var(--color-graph-file)', width: 8, height: 8, border: '2px solid rgba(30, 58, 95, 0.8)' }} />
    <div className="flex items-center gap-2">
      <span className="text-blue-400 text-sm shrink-0 leading-none" aria-hidden="true">📄</span>
      <div className="min-w-0">
        <div className="font-semibold text-xs text-blue-100 truncate leading-tight">{data.label}</div>
        {data.file_path && (
          <div className="text-[10px] text-blue-400/50 truncate mt-0.5 font-mono">{data.file_path}</div>
        )}
      </div>
    </div>
    <Handle type="source" position={Position.Bottom} style={{ background: 'var(--color-graph-file)', width: 8, height: 8, border: '2px solid rgba(30, 58, 95, 0.8)' }} />
  </div>
);

const ClassNode: React.FC<NodeProps<ReactFlowNodeData>> = ({ data, selected }) => (
  <div
    className={`px-3 py-2 rounded-lg border transition-all duration-200 cursor-pointer ${
      selected
        ? 'border-purple-400 bg-purple-950/70 shadow-lg shadow-purple-500/25 ring-2 ring-purple-400/30'
        : 'border-purple-700/40 bg-gray-900/95 hover:border-purple-500/60 hover:bg-purple-950/30 hover:shadow-md'
    }`}
    style={{ minWidth: '110px', maxWidth: '190px' }}
  >
    <Handle type="target" position={Position.Top} style={{ background: 'var(--color-graph-class)', width: 8, height: 8, border: '2px solid rgba(59, 31, 94, 0.8)' }} />
    <div className="flex items-center gap-2">
      <span className="text-purple-400 text-sm shrink-0 leading-none" aria-hidden="true">◆</span>
      <div className="min-w-0">
        <div className="font-semibold text-xs text-purple-100 truncate leading-tight">{data.label}</div>
        <div className="text-[10px] text-purple-400/50 mt-0.5 uppercase tracking-wide">class</div>
      </div>
    </div>
    <Handle type="source" position={Position.Bottom} style={{ background: 'var(--color-graph-class)', width: 8, height: 8, border: '2px solid rgba(59, 31, 94, 0.8)' }} />
  </div>
);

const FunctionNode: React.FC<NodeProps<ReactFlowNodeData>> = ({ data, selected }) => (
  <div
    className={`px-2.5 py-1.5 rounded-md border transition-all duration-200 cursor-pointer ${
      selected
        ? 'border-green-400 bg-green-950/70 shadow-md shadow-green-500/20 ring-2 ring-green-400/30'
        : 'border-green-700/40 bg-gray-900/95 hover:border-green-500/60 hover:bg-green-950/30 hover:shadow-md'
    }`}
    style={{ minWidth: '90px', maxWidth: '170px' }}
  >
    <Handle type="target" position={Position.Top} style={{ background: 'var(--color-graph-function)', width: 6, height: 6, border: '2px solid rgba(20, 83, 45, 0.8)' }} />
    <div className="flex items-center gap-1.5">
      <span className="text-green-400 text-xs shrink-0 leading-none font-mono" aria-hidden="true">ƒ</span>
      <div className="min-w-0">
        <div className="font-medium text-xs text-green-100 truncate leading-tight">{data.label}</div>
        <div className="text-[10px] text-green-400/50 mt-0.5 uppercase tracking-wide">function</div>
      </div>
    </div>
    <Handle type="source" position={Position.Bottom} style={{ background: 'var(--color-graph-function)', width: 6, height: 6, border: '2px solid rgba(20, 83, 45, 0.8)' }} />
  </div>
);

const DefaultNode: React.FC<NodeProps<ReactFlowNodeData>> = ({ data, selected }) => (
  <div
    className={`px-2.5 py-1.5 rounded border transition-all duration-200 cursor-pointer ${
      selected
        ? 'border-gray-400 bg-gray-700 shadow-md ring-2 ring-gray-400/30'
        : 'border-gray-600/40 bg-gray-900/95 hover:border-gray-500/60 hover:shadow-md'
    }`}
  >
    <Handle type="target" position={Position.Top} style={{ background: 'var(--color-gray-400)', width: 6, height: 6 }} />
    <div className="text-xs text-gray-200 truncate font-medium">{data.label}</div>
    <Handle type="source" position={Position.Bottom} style={{ background: 'var(--color-gray-400)', width: 6, height: 6 }} />
  </div>
);

export { FileNode, ClassNode, FunctionNode, DefaultNode };

export const nodeTypes = {
  fileNode: FileNode,
  classNode: ClassNode,
  functionNode: FunctionNode,
  methodNode: FunctionNode,
  default: DefaultNode,
};

// Made with Bob
