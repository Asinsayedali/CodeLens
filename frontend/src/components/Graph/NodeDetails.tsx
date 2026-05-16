import React, { useEffect, useRef, useState } from 'react';
import { graphApi } from '../../services/api';
import { ReactFlowNode, NodeDetails as NodeDetailsType } from '../../types';

interface NodeDetailsProps {
  projectId: number;
  node: ReactFlowNode;
  onClose: () => void;
}

interface QAMessage {
  type: 'question' | 'answer';
  text: string;
}

const TYPE_STYLES: Record<string, { badge: string }> = {
  file:     { badge: 'bg-blue-500/20 text-blue-300 border-blue-500/40' },
  class:    { badge: 'bg-purple-500/20 text-purple-300 border-purple-500/40' },
  function: { badge: 'bg-green-500/20 text-green-300 border-green-500/40' },
  method:   { badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' },
};

const TYPE_ICONS: Record<string, string> = {
  file: '📄', class: '◆', function: 'ƒ', method: 'ƒ',
};

const METADATA_KEYS = ['full_path', 'num_imports', 'num_classes', 'num_functions', 'num_methods'];
const METADATA_LABELS: Record<string, string> = {
  full_path: 'Path',
  num_imports: 'Imports',
  num_classes: 'Classes',
  num_functions: 'Functions',
  num_methods: 'Methods',
};

const PREVIEW_COUNT = 5;

// Minimal inline markdown — bold, inline code, bullet lists
function renderAnswer(text: string): React.ReactNode {
  return text.split('\n').map((line, i) => {
    if (!line.trim()) return <div key={i} className="h-1.5" />;
    const bullet = line.match(/^[-*] (.+)/);
    if (bullet) {
      return (
        <div key={i} className="flex gap-1.5 text-xs text-gray-300 leading-relaxed">
          <span className="text-gray-600 mt-0.5 shrink-0">•</span>
          <span>{inlineFmt(bullet[1])}</span>
        </div>
      );
    }
    const h = line.match(/^#{1,3} (.+)/);
    if (h) return <p key={i} className="text-xs font-semibold text-white mt-2 mb-0.5">{h[1]}</p>;
    return <p key={i} className="text-xs text-gray-300 leading-relaxed">{inlineFmt(line)}</p>;
  });
}

function inlineFmt(text: string): React.ReactNode {
  return text.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**'))
      return <strong key={i} className="text-white font-semibold">{part.slice(2, -2)}</strong>;
    if (part.startsWith('`') && part.endsWith('`'))
      return <code key={i} className="text-green-400 bg-gray-950 px-1 rounded text-[10px] font-mono">{part.slice(1, -1)}</code>;
    return part;
  });
}

const NodeDetails: React.FC<NodeDetailsProps> = ({ projectId, node, onClose }) => {
  const [details, setDetails] = useState<NodeDetailsType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAllIncoming, setShowAllIncoming] = useState(false);
  const [showAllOutgoing, setShowAllOutgoing] = useState(false);
  const [showAllRelated, setShowAllRelated] = useState(false);

  // Q&A state
  const [qaMessages, setQaMessages] = useState<QAMessage[]>([]);
  const [qaInput, setQaInput] = useState('');
  const [qaLoading, setQaLoading] = useState(false);
  const [filesUsed, setFilesUsed] = useState<string[]>([]);
  const qaEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    setShowAllIncoming(false);
    setShowAllOutgoing(false);
    setShowAllRelated(false);
    setQaMessages([]);
    setQaInput('');
    setFilesUsed([]);
    loadNodeDetails();
  }, [node.id]);

  useEffect(() => {
    qaEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [qaMessages]);

  const loadNodeDetails = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await graphApi.getNodeDetails(projectId, node.id);
      setDetails(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load node details');
    } finally {
      setLoading(false);
    }
  };

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    const q = qaInput.trim();
    if (!q || qaLoading) return;
    setQaInput('');
    setQaMessages(prev => [...prev, { type: 'question', text: q }]);
    setQaLoading(true);
    try {
      const res = await graphApi.askAboutNode(projectId, node.id, q);
      setQaMessages(prev => [...prev, { type: 'answer', text: res.data.answer }]);
      if (res.data.files_used?.length) setFilesUsed(res.data.files_used);
    } catch (err: any) {
      setQaMessages(prev => [
        ...prev,
        { type: 'answer', text: `Error: ${err.response?.data?.detail || 'Failed to get answer'}` },
      ]);
    } finally {
      setQaLoading(false);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  };

  // Quick question suggestions
  const quickQuestions = node.data.type === 'function' || node.data.type === 'method'
    ? [
        `What does \`${node.data.label}\` do?`,
        `What parameters does \`${node.data.label}\` take?`,
        `What does \`${node.data.label}\` return?`,
        `Where is \`${node.data.label}\` called from?`,
      ]
    : node.data.type === 'class'
    ? [
        `What is the \`${node.data.label}\` class responsible for?`,
        `What methods does \`${node.data.label}\` have?`,
        `How is \`${node.data.label}\` used in the project?`,
      ]
    : [
        `What does this file contain?`,
        `What is the purpose of \`${node.data.label}\`?`,
        `What are the main functions in this file?`,
      ];

  const typeStyle = TYPE_STYLES[node.data.type] ?? { badge: 'bg-gray-500/20 text-gray-300 border-gray-500/40' };
  const typeIcon = TYPE_ICONS[node.data.type] ?? '●';
  const metadata = node.data.metadata ?? {};
  const metaEntries = METADATA_KEYS.filter(k => metadata[k] != null);
  const relatedTypeColor = (t: string) =>
    t === 'file' ? 'text-blue-400' : t === 'class' ? 'text-purple-400' : 'text-green-400';

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-start justify-between p-4 border-b border-gray-700/60 gap-2 flex-shrink-0">
        <div className="flex-1 min-w-0">
          <span className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium border mb-1.5 ${typeStyle.badge}`}>
            {typeIcon} {node.data.type}
          </span>
          <h3 className="font-bold text-sm text-white truncate" title={node.data.label}>
            {node.data.label}
          </h3>
          {node.data.file_path && (
            <p className="text-[10px] text-gray-600 truncate mt-0.5" title={node.data.file_path}>
              {node.data.file_path}
            </p>
          )}
        </div>
        <button
          onClick={onClose}
          className="shrink-0 w-6 h-6 flex items-center justify-center rounded-full text-gray-500 hover:text-white hover:bg-gray-700 transition-all text-xs mt-0.5"
        >
          ✕
        </button>
      </div>

      {/* Scrollable body */}
      <div className="flex-1 overflow-y-auto min-h-0">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-7 w-7 border-b-2 border-blue-500" />
          </div>
        ) : error ? (
          <div className="text-center py-8 px-4">
            <p className="text-red-400 text-xs mb-2">{error}</p>
            <button onClick={loadNodeDetails} className="text-blue-400 text-xs hover:text-blue-300 underline">Retry</button>
          </div>
        ) : (
          <div className="divide-y divide-gray-700/40">
            {/* Metadata */}
            {metaEntries.length > 0 && (
              <div className="p-4 space-y-2">
                {metaEntries.map(key => (
                  <div key={key} className="flex items-start justify-between gap-3 text-xs">
                    <span className="text-gray-500 shrink-0">{METADATA_LABELS[key]}</span>
                    <span className="text-gray-200 font-mono break-all text-right">{String(metadata[key])}</span>
                  </div>
                ))}
                {node.data.line_number && (
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-500">Line</span>
                    <span className="text-gray-200 font-mono">{node.data.line_number}</span>
                  </div>
                )}
                {node.data.importance_score !== undefined && (
                  <div className="space-y-1.5 pt-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-500">Importance</span>
                      <span className="text-gray-200 font-mono">{node.data.importance_score.toFixed(2)}</span>
                    </div>
                    <div className="w-full bg-gray-700/60 rounded-full h-1">
                      <div
                        className="bg-blue-500 h-1 rounded-full"
                        style={{ width: `${Math.min(node.data.importance_score * 100, 100)}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Incoming */}
            {details && (
              <div className="p-4">
                <div className="flex items-center gap-2 mb-2.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-orange-400 shrink-0" />
                  <span className="font-semibold text-xs text-white">Incoming</span>
                  <span className="ml-auto text-[10px] text-gray-500 bg-gray-800 px-1.5 py-0.5 rounded-full">
                    {details.incoming_edges.length}
                  </span>
                </div>
                {details.incoming_edges.length > 0 ? (
                  <div className="space-y-1">
                    {(showAllIncoming ? details.incoming_edges : details.incoming_edges.slice(0, PREVIEW_COUNT)).map((edge, i) => (
                      <div key={i} className="flex items-center gap-2 py-1 px-2 rounded bg-gray-800/50 text-xs">
                        <span className="text-orange-400 font-medium shrink-0">{edge.edge_type}</span>
                        <span className="text-gray-300 truncate">{edge.source_node_id.split(':').pop()}</span>
                      </div>
                    ))}
                    {details.incoming_edges.length > PREVIEW_COUNT && (
                      <button onClick={() => setShowAllIncoming(v => !v)} className="w-full text-left text-xs text-blue-400 hover:text-blue-300 py-1.5 px-2 hover:bg-gray-800/40 rounded transition-colors">
                        {showAllIncoming ? '▲ Show less' : `▼ Show ${details.incoming_edges.length - PREVIEW_COUNT} more`}
                      </button>
                    )}
                  </div>
                ) : <p className="text-gray-600 text-xs">None</p>}
              </div>
            )}

            {/* Outgoing */}
            {details && (
              <div className="p-4">
                <div className="flex items-center gap-2 mb-2.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-cyan-400 shrink-0" />
                  <span className="font-semibold text-xs text-white">Outgoing</span>
                  <span className="ml-auto text-[10px] text-gray-500 bg-gray-800 px-1.5 py-0.5 rounded-full">
                    {details.outgoing_edges.length}
                  </span>
                </div>
                {details.outgoing_edges.length > 0 ? (
                  <div className="space-y-1">
                    {(showAllOutgoing ? details.outgoing_edges : details.outgoing_edges.slice(0, PREVIEW_COUNT)).map((edge, i) => (
                      <div key={i} className="flex items-center gap-2 py-1 px-2 rounded bg-gray-800/50 text-xs">
                        <span className="text-cyan-400 font-medium shrink-0">{edge.edge_type}</span>
                        <span className="text-gray-300 truncate">{edge.target_node_id.split(':').pop()}</span>
                      </div>
                    ))}
                    {details.outgoing_edges.length > PREVIEW_COUNT && (
                      <button onClick={() => setShowAllOutgoing(v => !v)} className="w-full text-left text-xs text-blue-400 hover:text-blue-300 py-1.5 px-2 hover:bg-gray-800/40 rounded transition-colors">
                        {showAllOutgoing ? '▲ Show less' : `▼ Show ${details.outgoing_edges.length - PREVIEW_COUNT} more`}
                      </button>
                    )}
                  </div>
                ) : <p className="text-gray-600 text-xs">None</p>}
              </div>
            )}

            {/* Related */}
            {details && (
              <div className="p-4">
                <div className="flex items-center gap-2 mb-2.5">
                  <div className="w-1.5 h-1.5 rounded-full bg-purple-400 shrink-0" />
                  <span className="font-semibold text-xs text-white">Related</span>
                  <span className="ml-auto text-[10px] text-gray-500 bg-gray-800 px-1.5 py-0.5 rounded-full">
                    {details.related_nodes.length}
                  </span>
                </div>
                {details.related_nodes.length > 0 ? (
                  <div className="space-y-1">
                    {(showAllRelated ? details.related_nodes : details.related_nodes.slice(0, PREVIEW_COUNT)).map((rn, i) => (
                      <div key={i} className="flex items-center gap-2 py-1 px-2 rounded bg-gray-800/50 text-xs">
                        <span className={`font-medium shrink-0 capitalize ${relatedTypeColor(rn.node_type)}`}>{rn.node_type}</span>
                        <span className="text-gray-300 truncate">{rn.name}</span>
                      </div>
                    ))}
                    {details.related_nodes.length > PREVIEW_COUNT && (
                      <button onClick={() => setShowAllRelated(v => !v)} className="w-full text-left text-xs text-blue-400 hover:text-blue-300 py-1.5 px-2 hover:bg-gray-800/40 rounded transition-colors">
                        {showAllRelated ? '▲ Show less' : `▼ Show ${details.related_nodes.length - PREVIEW_COUNT} more`}
                      </button>
                    )}
                  </div>
                ) : <p className="text-gray-600 text-xs">None</p>}
              </div>
            )}

            {/* ── Ask about this node ── */}
            <div className="p-4">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-1.5 h-1.5 rounded-full bg-blue-400 shrink-0" />
                <span className="font-semibold text-xs text-white">Ask about this node</span>
              </div>

              {/* Quick questions */}
              {qaMessages.length === 0 && (
                <div className="flex flex-wrap gap-1.5 mb-3">
                  {quickQuestions.map((q, i) => (
                    <button
                      key={i}
                      onClick={() => setQaInput(q)}
                      className="text-[10px] px-2 py-1 bg-gray-800 hover:bg-gray-700 border border-gray-700 hover:border-gray-600 text-gray-400 hover:text-gray-200 rounded-lg transition-all text-left"
                    >
                      {q}
                    </button>
                  ))}
                </div>
              )}

              {/* Conversation */}
              {qaMessages.length > 0 && (
                <div className="space-y-3 mb-3 max-h-72 overflow-y-auto">
                  {qaMessages.map((msg, i) => (
                    <div key={i}>
                      {msg.type === 'question' ? (
                        <div className="flex justify-end">
                          <div className="bg-blue-600 text-white text-xs px-3 py-2 rounded-xl rounded-tr-sm max-w-[85%]">
                            {msg.text}
                          </div>
                        </div>
                      ) : (
                        <div className="bg-gray-800/80 border border-gray-700/60 rounded-xl rounded-tl-sm px-3 py-2.5 space-y-1">
                          {renderAnswer(msg.text)}
                        </div>
                      )}
                    </div>
                  ))}
                  {qaLoading && (
                    <div className="flex gap-1 px-3 py-2.5 bg-gray-800/80 border border-gray-700/60 rounded-xl rounded-tl-sm w-fit">
                      {[0, 150, 300].map(d => (
                        <div key={d} className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: `${d}ms` }} />
                      ))}
                    </div>
                  )}
                  <div ref={qaEndRef} />
                </div>
              )}

              {/* Files used */}
              {filesUsed.length > 0 && (
                <div className="mb-2 flex flex-wrap gap-1">
                  {filesUsed.map((f, i) => (
                    <span key={i} className="text-[9px] text-gray-600 bg-gray-900 border border-gray-800 px-1.5 py-0.5 rounded font-mono truncate max-w-full">
                      {f}
                    </span>
                  ))}
                </div>
              )}

              {/* Input */}
              <form onSubmit={handleAsk} className="flex gap-2">
                <input
                  ref={inputRef}
                  type="text"
                  value={qaInput}
                  onChange={e => setQaInput(e.target.value)}
                  placeholder={`Ask about ${node.data.label}...`}
                  disabled={qaLoading}
                  className="flex-1 px-2.5 py-1.5 bg-gray-900 border border-gray-700 rounded-lg text-xs text-white placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-50 min-w-0"
                />
                <button
                  type="submit"
                  disabled={!qaInput.trim() || qaLoading}
                  className="px-2.5 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded-lg text-xs font-medium transition-colors shrink-0"
                >
                  {qaLoading ? '…' : 'Ask'}
                </button>
              </form>
              <p className="text-[10px] text-gray-700 mt-1.5">
                Uses actual source code — no embedding needed
              </p>
            </div>

          </div>
        )}
      </div>
    </div>
  );
};

export default NodeDetails;

// Made with Bob
