import React from 'react';

interface GraphControlsProps {
  searchTerm: string;
  onSearchChange: (term: string) => void;
  filterType: string;
  onFilterChange: (type: string) => void;
  onLayoutChange: (layout: 'hierarchical' | 'force') => void;
  activeLayout: 'hierarchical' | 'force';
  stats?: {
    total_nodes: number;
    total_edges: number;
    node_types: Record<string, number>;
    edge_types: Record<string, number>;
  };
}

const GraphControls: React.FC<GraphControlsProps> = ({
  searchTerm,
  onSearchChange,
  filterType,
  onFilterChange,
  onLayoutChange,
  activeLayout,
  stats,
}) => {
  return (
    <div className="space-y-3 min-w-[220px]">
      {/* Search */}
      <div>
        <label className="block text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-1.5">
          Search
        </label>
        <div className="relative">
          <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-500 text-xs">🔍</span>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search nodes..."
            className="w-full pl-7 pr-3 py-1.5 bg-gray-800/80 border border-gray-600/60 rounded-lg text-xs text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
            aria-label="Search nodes"
          />
        </div>
      </div>

      {/* Filter */}
      <div>
        <label className="block text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-1.5">
          Filter
        </label>
        <select
          value={filterType}
          onChange={(e) => onFilterChange(e.target.value)}
          className="w-full px-2.5 py-1.5 bg-gray-800/80 border border-gray-600/60 rounded-lg text-xs text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors cursor-pointer"
          aria-label="Filter by node type"
        >
          <option value="all">All Types</option>
          <option value="fileNode">Files</option>
          <option value="classNode">Classes</option>
          <option value="functionNode">Functions</option>
        </select>
      </div>

      {/* Layout */}
      <div>
        <label className="block text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-1.5">
          Layout
        </label>
        <div className="flex gap-1.5">
          {(['hierarchical', 'force'] as const).map(layout => (
            <button
              key={layout}
              onClick={() => onLayoutChange(layout)}
              className={`flex-1 py-1.5 text-xs rounded-lg border transition-all duration-150 font-medium capitalize ${
                activeLayout === layout
                  ? 'bg-blue-600 border-blue-500 text-white shadow-sm shadow-blue-500/20'
                  : 'bg-gray-800/80 border-gray-600/60 text-gray-400 hover:border-gray-500 hover:text-gray-200 hover:bg-gray-800'
              }`}
              aria-pressed={activeLayout === layout}
              aria-label={`${layout} layout`}
            >
              {layout}
            </button>
          ))}
        </div>
      </div>

      {/* Stats */}
      {stats && (
        <div className="pt-2 border-t border-gray-700/50">
          <label className="block text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-1.5">
            Stats
          </label>
          <div className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="text-gray-400">Nodes</span>
              <span className="text-white font-medium">{stats.total_nodes}</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-gray-400">Edges</span>
              <span className="text-white font-medium">{stats.total_edges}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GraphControls;

// Made with Bob
