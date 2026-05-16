import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { projectsApi } from '../../services/api';
import { Project } from '../../types';
import { DocViewer } from '../Documentation';
import { DependencyGraph } from '../Graph';
import { ChatInterface } from '../QA';

const TABS = [
  { id: 'docs',  label: 'Documentation' },
  { id: 'graph', label: 'Graph' },
  { id: 'qa',    label: 'Q&A' },
];

export default function ProjectLayout() {
  const { projectId, tab } = useParams<{ projectId: string; tab: string }>();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!projectId) return;
    projectsApi
      .getById(parseInt(projectId, 10))
      .then(res => setProject(res.data))
      .catch(() => navigate('/dashboard', { replace: true }))
      .finally(() => setLoading(false));
  }, [projectId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
        <div className="text-center">
          <div className="spinner w-10 h-10 mx-auto mb-4" />
          <p className="text-gray-400 text-sm">Loading project…</p>
        </div>
      </div>
    );
  }

  const id = parseInt(projectId!, 10);
  const activeTab = tab && TABS.some(t => t.id === tab) ? tab : 'docs';

  return (
    <div className="h-screen bg-gray-950 text-white flex flex-col overflow-hidden">
      {/* Header */}
      <header className="bg-gray-950 border-b border-gray-800 px-6 py-3 flex-shrink-0">
        <div className="flex items-center justify-between">
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 min-w-0">
            <Link
              to="/dashboard"
              className="text-lg font-bold tracking-tight text-gradient-primary hover:opacity-80 transition-opacity flex-shrink-0"
            >
              CodeLens
            </Link>
            <span className="text-gray-700 flex-shrink-0">/</span>
            <span className="text-gray-400 text-sm font-medium truncate">{project?.name}</span>
          </div>

          {/* Tab navigation */}
          <nav className="flex items-center gap-1" role="navigation">
            {TABS.map(t => (
              <button
                key={t.id}
                onClick={() => navigate(`/projects/${projectId}/${t.id}`)}
                className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors duration-150 ${
                  activeTab === t.id
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`}
                aria-current={activeTab === t.id ? 'page' : undefined}
              >
                {t.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* Content — exact height so ReactFlow and other full-height views work */}
      <main className="h-[calc(100vh-53px)] overflow-hidden">
        {activeTab === 'docs'  && <DocViewer projectId={id} />}
        {activeTab === 'graph' && <DependencyGraph projectId={id} />}
        {activeTab === 'qa'    && <ChatInterface projectId={id} />}
      </main>
    </div>
  );
}

// Made with Bob
