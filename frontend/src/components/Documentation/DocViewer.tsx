import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { docsApi } from '../../services/api';
import type { DocumentationResponse } from '../../types';
import { MermaidDiagram } from './MermaidDiagram';

interface DocViewerProps {
  projectId: number;
}

interface SectionInfo {
  key: string;
  title: string;
  icon: string;
}

const SECTIONS: SectionInfo[] = [
  { key: 'overview',       title: 'Project Overview', icon: '📋' },
  { key: 'getting_started', title: 'Getting Started',  icon: '🚀' },
  { key: 'architecture',   title: 'Architecture',      icon: '🏗️' },
  { key: 'api',            title: 'API Docs',          icon: '🔌' },
];

export const DocViewer: React.FC<DocViewerProps> = ({ projectId }) => {
  const [documentation, setDocumentation] = useState<Record<string, string> | null>(null);
  const [activeSection, setActiveSection] = useState<string>('overview');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generating, setGenerating] = useState(false);
  const [regeneratingSection, setRegeneratingSection] = useState<string | null>(null);

  useEffect(() => {
    loadDocumentation();
  }, [projectId]);

  const loadDocumentation = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await docsApi.getDocs(projectId);
      const data: DocumentationResponse = response.data;
      setDocumentation(data.documentation);
      const available = Object.keys(data.documentation);
      if (available.length > 0) setActiveSection(available[0]);
    } catch (err: any) {
      setError(err.response?.status === 404 ? 'not_generated' : 'load_error');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateAll = async () => {
    try {
      setGenerating(true);
      setError(null);
      await docsApi.generateDocs(projectId);
      await loadDocumentation();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate documentation');
    } finally {
      setGenerating(false);
    }
  };

  const handleRegenerateSection = async (section: string) => {
    try {
      setRegeneratingSection(section);
      setError(null);
      await docsApi.regenerateSection(projectId, section);
      await loadDocumentation();
    } catch (err: any) {
      setError(err.response?.data?.detail || `Failed to regenerate ${section}`);
    } finally {
      setRegeneratingSection(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full bg-black">
        <div className="text-center">
          <div className="spinner w-10 h-10 mx-auto mb-4" />
          <p className="text-gray-400 text-sm">Loading documentation...</p>
        </div>
      </div>
    );
  }

  if (error === 'not_generated' || (!documentation && !error)) {
    return (
      <div className="flex items-center justify-center h-full bg-black">
        <div className="text-center max-w-sm">
          <div className="text-5xl mb-5">📚</div>
          <h3 className="text-xl font-semibold text-white mb-2">No Documentation Yet</h3>
          <p className="text-gray-400 text-sm mb-8">
            Generate AI-powered documentation for this project using IBM WatsonX.
          </p>
          <button
            onClick={handleGenerateAll}
            disabled={generating}
            className="inline-flex items-center gap-2 px-6 py-3 bg-white text-gray-900 font-semibold rounded-xl hover:bg-gray-100 active:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm shadow-lg"
          >
            {generating ? (
              <>
                <span className="spinner w-4 h-4 border-gray-900 border-t-transparent" />
                Generating...
              </>
            ) : (
              <>
                <span aria-hidden="true">✨</span> Generate Documentation
              </>
            )}
          </button>
        </div>
      </div>
    );
  }

  const availableSections = SECTIONS.filter(s => documentation?.[s.key]);
  const currentContent = documentation?.[activeSection] || '';

  return (
    <div className="flex h-full bg-black text-white">
      {/* Sidebar */}
      <div className="w-56 shrink-0 bg-[#111] border-r border-[#222] flex flex-col">
        <div className="px-4 py-4 border-b border-[#222]">
          <h2 className="font-semibold text-sm text-white flex items-center gap-2">
            <span>📚</span> Documentation
          </h2>
        </div>

        <nav className="flex-1 p-2 space-y-0.5 overflow-y-auto">
          {availableSections.map((section) => (
            <button
              key={section.key}
              onClick={() => setActiveSection(section.key)}
              className={`w-full text-left px-3 py-2.5 rounded-lg text-sm transition-colors flex items-center gap-2 ${
                activeSection === section.key
                  ? 'bg-white text-gray-900 font-medium'
                  : 'text-gray-400 hover:bg-[#1c1c1c] hover:text-white'
              }`}
            >
              <span className="text-base leading-none">{section.icon}</span>
              {section.title}
            </button>
          ))}
        </nav>

        <div className="p-3 border-t border-[#222]">
          <button
            onClick={handleGenerateAll}
            disabled={generating}
            className="w-full py-2 bg-white text-gray-900 text-xs font-semibold rounded-lg hover:bg-gray-100 active:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
          >
            {generating ? (
              <span className="flex items-center justify-center gap-2">
                <span className="spinner w-3 h-3 border-gray-900 border-t-transparent" />
                Generating...
              </span>
            ) : (
              'Regenerate All'
            )}
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-8 py-8">
          {/* Section header */}
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-2xl font-bold text-white flex items-center gap-3">
              <span>{SECTIONS.find(s => s.key === activeSection)?.icon}</span>
              {SECTIONS.find(s => s.key === activeSection)?.title}
            </h1>
            <button
              onClick={() => handleRegenerateSection(activeSection)}
              disabled={regeneratingSection === activeSection}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-[#1c1c1c] text-gray-300 text-xs rounded-lg border border-[#2e2e2e] hover:bg-[#282828] hover:text-white active:bg-[#333] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {regeneratingSection === activeSection ? (
                <>
                  <span className="spinner w-3 h-3" />
                  Regenerating...
                </>
              ) : (
                <>
                  <span aria-hidden="true">🔄</span> Regenerate
                </>
              )}
            </button>
          </div>

          {error && error !== 'not_generated' && (
            <div className="mb-6 p-4 bg-red-900/30 border border-red-700/50 rounded-xl">
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          )}

          {/* Markdown content */}
          <div className="prose-container">
            <ReactMarkdown
              components={{
                h1: ({ ...props }) => (
                  <h1 className="text-2xl font-bold text-white mt-8 mb-4 first:mt-0 pb-2 border-b border-[#222]" {...props} />
                ),
                h2: ({ ...props }) => (
                  <h2 className="text-xl font-semibold text-white mt-7 mb-3" {...props} />
                ),
                h3: ({ ...props }) => (
                  <h3 className="text-base font-semibold text-gray-200 mt-5 mb-2" {...props} />
                ),
                p: ({ ...props }) => (
                  <p className="text-gray-300 mb-4 leading-relaxed text-sm" {...props} />
                ),
                ul: ({ ...props }) => (
                  <ul className="list-disc list-outside pl-5 mb-4 space-y-1.5" {...props} />
                ),
                ol: ({ ...props }) => (
                  <ol className="list-decimal list-outside pl-5 mb-4 space-y-1.5" {...props} />
                ),
                li: ({ ...props }) => (
                  <li className="text-gray-300 text-sm leading-relaxed" {...props} />
                ),
                code: ({ inline, className, children, ...props }: any) => {
                  const lang = (className || '').replace('language-', '');
                  const code = String(children).trim();
                  if (!inline && lang === 'mermaid') {
                    return <MermaidDiagram chart={code} />;
                  }
                  return inline ? (
                    <code className="bg-[#1c1c1c] text-green-400 px-1.5 py-0.5 rounded text-xs font-mono whitespace-nowrap" {...props}>{children}</code>
                  ) : (
                    <code className="block bg-[#111] border border-[#2e2e2e]/60 text-gray-200 p-4 rounded-xl overflow-x-auto text-xs font-mono leading-relaxed" {...props}>{children}</code>
                  );
                },
                pre: ({ ...props }) => (
                  <pre className="mb-4 overflow-x-auto" {...props} />
                ),
                blockquote: ({ ...props }) => (
                  <blockquote className="border-l-2 border-gray-600 pl-4 text-gray-400 italic my-4 text-sm" {...props} />
                ),
                a: ({ ...props }) => (
                  <a className="text-blue-400 hover:text-blue-300 underline underline-offset-2" {...props} />
                ),
                strong: ({ ...props }) => (
                  <strong className="font-semibold text-white" {...props} />
                ),
                hr: ({ ...props }) => (
                  <hr className="border-[#222] my-6" {...props} />
                ),
                table: ({ ...props }) => (
                  <div className="overflow-x-auto mb-4 rounded-xl border border-[#2e2e2e]/60">
                    <table className="min-w-full text-sm" {...props} />
                  </div>
                ),
                th: ({ ...props }) => (
                  <th className="px-4 py-2.5 bg-[#1c1c1c] text-left text-xs font-semibold text-gray-300 uppercase tracking-wider" {...props} />
                ),
                td: ({ ...props }) => (
                  <td className="px-4 py-2.5 text-gray-300 text-sm border-t border-[#2e2e2e]/40" {...props} />
                ),
              }}
            >
              {currentContent}
            </ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DocViewer;

// Made with Bob
