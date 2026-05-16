import { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: false,
  theme: 'base',
  themeVariables: {
    primaryColor: '#1d4ed8',
    primaryTextColor: '#f1f5f9',
    primaryBorderColor: '#60a5fa',
    secondaryColor: '#1e293b',
    tertiaryColor: '#0f172a',
    lineColor: '#94a3b8',
    edgeLabelBackground: '#1e293b',
    clusterBkg: '#0f172a',
    clusterBorder: '#475569',
    titleColor: '#f1f5f9',
    background: 'transparent',
    mainBkg: '#1d4ed8',
    nodeBorder: '#60a5fa',
    fontFamily: 'ui-monospace, SFMono-Regular, Menlo, monospace',
    fontSize: '13px',
  },
  flowchart: {
    useMaxWidth: true,
    htmlLabels: true,
    curve: 'basis',
    padding: 20,
  },
});

interface MermaidDiagramProps {
  chart: string;
}

export const MermaidDiagram = ({ chart }: MermaidDiagramProps) => {
  const mermaidRef = useRef<HTMLDivElement>(null);
  const [status, setStatus] = useState<'loading' | 'ok' | 'error'>('loading');
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (!mermaidRef.current || !chart.trim()) {
      setStatus('error');
      setErrorMsg('No diagram content');
      return;
    }

    setStatus('loading');
    setErrorMsg('');

    const el = mermaidRef.current;
    el.removeAttribute('data-processed');
    el.innerHTML = '';
    el.textContent = chart;

    mermaid
      .run({ nodes: [el], suppressErrors: false })
      .then(() => setStatus('ok'))
      .catch(err => {
        setErrorMsg(String(err));
        setStatus('error');
      });
  }, [chart]);

  return (
    <div className="my-6 space-y-2">
      <div className="flex items-center justify-between px-1">
        <span className="text-xs text-gray-500 font-medium uppercase tracking-wider">
          Architecture Diagram
        </span>
        {status === 'ok' && (
          <span className="text-[10px] text-gray-600 bg-[#111] border border-[#222] px-2 py-0.5 rounded-full">
            Mermaid · flowchart
          </span>
        )}
      </div>

      <div className="relative w-full rounded-xl border border-[#2e2e2e]/60 bg-black p-6 overflow-x-auto" style={{ minHeight: status !== 'ok' ? '180px' : undefined }}>
        {status === 'loading' && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="spinner w-6 h-6" />
          </div>
        )}

        {status === 'error' && (
          <div className="space-y-2">
            <p className="text-xs text-red-400 font-medium">Diagram could not be rendered</p>
            {errorMsg && (
              <pre className="text-xs text-gray-600 overflow-x-auto whitespace-pre-wrap">{errorMsg}</pre>
            )}
            <pre className="text-xs text-gray-500 overflow-x-auto whitespace-pre-wrap">{chart}</pre>
          </div>
        )}

        {/* mermaid.run() mutates this element in-place — no temp DOM, no flicker */}
        <div
          ref={mermaidRef}
          className="mermaid"
          style={{ visibility: status === 'ok' ? 'visible' : 'hidden' }}
        />
      </div>
    </div>
  );
};

// Made with Bob
