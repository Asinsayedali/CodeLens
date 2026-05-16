import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { projectsApi } from '../../services/api';
import { Project } from '../../types';

export default function Dashboard() {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showNewProjectForm, setShowNewProjectForm] = useState(false);
  const [newProjectPath, setNewProjectPath] = useState('');
  const [newProjectName, setNewProjectName] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [deletingProjectId, setDeletingProjectId] = useState<number | null>(null);
  const [projectToDelete, setProjectToDelete] = useState<Project | null>(null);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await projectsApi.getAll();
      setProjects(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeRepository = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectPath.trim()) return;
    try {
      setAnalyzing(true);
      setError(null);
      await projectsApi.analyze(newProjectPath, newProjectName || undefined);
      setNewProjectPath('');
      setNewProjectName('');
      setShowNewProjectForm(false);
      await loadProjects();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to analyze repository');
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDeleteProject = async (project: Project) => {
    try {
      setDeletingProjectId(project.id);
      setError(null);
      await projectsApi.delete(project.id);
      setProjectToDelete(null);
      await loadProjects();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to delete project');
    } finally {
      setDeletingProjectId(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      {/* Header */}
      <header className="bg-gray-950 border-b border-gray-800 px-6 py-3 flex-shrink-0">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <Link to="/" className="text-lg font-bold tracking-tight text-gradient-primary hover:opacity-80 transition-opacity">
            Grasp
          </Link>
          <button
            onClick={() => setShowNewProjectForm(v => !v)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors shadow-sm"
          >
            <span className="text-lg leading-none">+</span> New Project
          </button>
        </div>
      </header>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto px-6 py-8 space-y-8">

          <div>
            <h2 className="text-xl font-semibold text-white">Projects</h2>
            <p className="text-gray-500 text-sm mt-1">
              {loading ? 'Loading…' : `${projects.length} project${projects.length !== 1 ? 's' : ''} analysed`}
            </p>
          </div>

          {/* New project form */}
          {showNewProjectForm && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
              <h3 className="text-base font-semibold mb-4 text-white">Analyse a Repository</h3>
              <form onSubmit={handleAnalyzeRepository} className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1.5">
                    Repository path or URL *
                  </label>
                  <input
                    type="text"
                    value={newProjectPath}
                    onChange={e => setNewProjectPath(e.target.value)}
                    placeholder="/path/to/repo  or  https://github.com/user/repo"
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-colors"
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-400 mb-1.5">
                    Project name (optional)
                  </label>
                  <input
                    type="text"
                    value={newProjectName}
                    onChange={e => setNewProjectName(e.target.value)}
                    placeholder="My Project"
                    className="w-full px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm transition-colors"
                  />
                </div>
                {error && <p className="text-red-400 text-xs">{error}</p>}
                <div className="flex gap-3">
                  <button
                    type="submit"
                    disabled={analyzing}
                    className="flex-1 py-2 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg text-sm font-medium transition-colors shadow-sm"
                  >
                    {analyzing ? (
                      <span className="flex items-center justify-center gap-2">
                        <span className="spinner w-4 h-4" />
                        Analysing…
                      </span>
                    ) : 'Analyse'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowNewProjectForm(false)}
                    className="px-4 py-2 bg-gray-800 hover:bg-gray-700 active:bg-gray-600 text-gray-300 hover:text-white rounded-lg text-sm font-medium transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          {error && !showNewProjectForm && (
            <div className="p-4 bg-red-900/20 border border-red-700/40 rounded-xl">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          {/* Project grid */}
          {loading ? (
            <div className="flex items-center justify-center py-20">
              <div className="spinner w-8 h-8" />
            </div>
          ) : projects.length === 0 ? (
            <div className="text-center py-20">
              <div className="w-16 h-16 rounded-2xl bg-gray-900 border border-gray-800 flex items-center justify-center mx-auto mb-4 text-2xl">
                📂
              </div>
              <p className="text-gray-400 font-medium">No projects yet</p>
              <p className="text-gray-600 text-sm mt-1">Click "New Project" to analyse a repository</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {projects.map(project => (
                <div
                  key={project.id}
                  className="group bg-gray-900 border border-gray-800 hover:border-blue-500/50 hover:shadow-lg hover:shadow-blue-500/10 rounded-xl p-5 transition-all duration-200 cursor-pointer"
                  onClick={() => navigate(`/projects/${project.id}/docs`)}
                >
                  {/* Card header */}
                  <div className="flex items-start justify-between mb-3">
                    <h3 className="font-semibold text-white group-hover:text-blue-400 transition-colors truncate pr-3">
                      {project.name}
                    </h3>
                    <span className={`flex-shrink-0 text-xs px-2 py-0.5 rounded-full font-medium ${
                      project.status === 'completed' ? 'bg-green-500/10 text-green-400 border border-green-500/20' :
                      project.status === 'analyzing' ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20' :
                      project.status === 'failed'    ? 'bg-red-500/10 text-red-400 border border-red-500/20' :
                      'bg-gray-800 text-gray-500 border border-gray-700'
                    }`}>
                      {project.status}
                    </span>
                  </div>

                  {/* Stats */}
                  <div className="space-y-1.5">
                    {project.language && (
                      <div className="flex items-center gap-2 text-xs">
                        <span className="w-14 text-gray-600">Language</span>
                        <span className="text-gray-300">{project.language}</span>
                      </div>
                    )}
                    {project.total_files !== undefined && (
                      <div className="flex items-center gap-2 text-xs">
                        <span className="w-14 text-gray-600">Files</span>
                        <span className="text-gray-300">{project.total_files}</span>
                      </div>
                    )}
                    {project.total_lines !== undefined && (
                      <div className="flex items-center gap-2 text-xs">
                        <span className="w-14 text-gray-600">Lines</span>
                        <span className="text-gray-300">{project.total_lines.toLocaleString()}</span>
                      </div>
                    )}
                  </div>

                  {/* Footer row */}
                  <div className="mt-4 pt-3 border-t border-gray-800 flex items-center gap-1.5">
                    {['docs', 'graph', 'qa'].map(tab => (
                      <span key={tab} className="text-[10px] text-gray-600 bg-gray-800 px-2 py-0.5 rounded-full capitalize">
                        {tab === 'qa' ? 'Q&A' : tab}
                      </span>
                    ))}

                    <div className="ml-auto flex items-center gap-2">
                      {/* Delete — inline in footer, revealed on hover */}
                      <button
                        onClick={e => { e.stopPropagation(); setProjectToDelete(project); }}
                        disabled={deletingProjectId === project.id}
                        className="p-1 rounded-md text-gray-600 hover:text-red-400 hover:bg-red-500/10 transition-all opacity-0 group-hover:opacity-100 disabled:opacity-30 disabled:cursor-not-allowed"
                        title="Delete project"
                      >
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>

                      <span className="text-xs text-blue-500 group-hover:text-blue-400 transition-colors">
                        Open →
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Delete confirmation modal */}
      {projectToDelete && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 max-w-md w-full shadow-2xl">
            <h3 className="text-lg font-semibold text-white mb-2">Delete Project</h3>
            <p className="text-gray-400 text-sm mb-6">
              Are you sure you want to delete{' '}
              <span className="text-white font-medium">{projectToDelete.name}</span>?
              This cannot be undone.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setProjectToDelete(null)}
                disabled={deletingProjectId !== null}
                className="flex-1 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDeleteProject(projectToDelete)}
                disabled={deletingProjectId !== null}
                className="flex-1 px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50 shadow-sm"
              >
                {deletingProjectId === projectToDelete.id ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="spinner w-4 h-4" /> Deleting...
                  </span>
                ) : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Made with Bob
