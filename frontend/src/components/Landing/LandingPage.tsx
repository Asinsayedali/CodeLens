import { useNavigate } from 'react-router-dom';

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-950 text-white overflow-x-hidden">
      {/* Ambient glow */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 -left-40 w-[600px] h-[600px] bg-blue-600/8 rounded-full blur-3xl" />
        <div className="absolute top-1/2 -right-60 w-[500px] h-[500px] bg-purple-600/6 rounded-full blur-3xl" />
      </div>

      {/* Header */}
      <header className="relative border-b border-gray-800/60 backdrop-blur-sm sticky top-0 z-10 bg-gray-950/80">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-sm font-bold shadow-lg shadow-blue-500/20">
              CL
            </div>
            <span className="text-lg font-bold text-gradient-primary">CodeLens</span>
          </div>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-blue-500/20"
          >
            Open Dashboard
          </button>
        </div>
      </header>

      {/* Hero */}
      <section className="relative max-w-7xl mx-auto px-6 pt-24 pb-20">
        <div className="text-center max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-blue-500/10 border border-blue-500/20 rounded-full text-sm text-blue-400 mb-8">
            <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse" />
            Powered by IBM watsonx.ai
          </div>

          <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-[1.1] tracking-tight">
            Understand any codebase
            <br />
            <span className="text-gradient-primary">in seconds</span>
          </h1>

          <p className="text-lg text-gray-400 mb-10 leading-relaxed max-w-2xl mx-auto">
            CodeLens parses your repository, builds a knowledge graph, generates AI documentation,
            and lets you ask natural-language questions — all in one place.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <button
              onClick={() => navigate('/dashboard')}
              className="px-8 py-3.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-base font-semibold transition-colors shadow-xl shadow-blue-500/20 flex items-center gap-2"
            >
              Get Started <span aria-hidden="true">→</span>
            </button>
            <button
              onClick={() => navigate('/dashboard')}
              className="px-8 py-3.5 bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white rounded-xl text-base font-semibold transition-colors border border-gray-700 flex items-center gap-2"
            >
              View Projects
            </button>
          </div>
        </div>

        {/* Fake terminal preview */}
        <div className="mt-16 max-w-3xl mx-auto">
          <div className="rounded-2xl border border-gray-700/60 bg-gray-900/80 overflow-hidden shadow-2xl shadow-black/40 backdrop-blur-sm">
            {/* Window chrome */}
            <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-800 bg-gray-900">
              <div className="w-3 h-3 rounded-full bg-red-500/70" />
              <div className="w-3 h-3 rounded-full bg-yellow-500/70" />
              <div className="w-3 h-3 rounded-full bg-green-500/70" />
              <span className="ml-3 text-xs text-gray-500 font-mono">CodeLens · Graph View</span>
            </div>
            {/* Content mockup */}
            <div className="p-6 font-mono text-xs space-y-2 text-gray-400">
              <div className="flex items-center gap-3">
                <span className="text-blue-400">■</span>
                <span className="text-gray-300">app.py</span>
                <span className="text-gray-600 ml-auto">348 lines</span>
              </div>
              <div className="flex items-center gap-3 pl-6">
                <span className="text-green-400">◆</span>
                <span className="text-green-300">create_app()</span>
                <span className="ml-2 text-gray-600">→ routes.py</span>
              </div>
              <div className="flex items-center gap-3 pl-6">
                <span className="text-green-400">◆</span>
                <span className="text-green-300">run_server()</span>
                <span className="ml-2 text-gray-600">→ config.py</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-blue-400">■</span>
                <span className="text-gray-300">models/user.py</span>
                <span className="text-gray-600 ml-auto">124 lines</span>
              </div>
              <div className="flex items-center gap-3 pl-6">
                <span className="text-purple-400">●</span>
                <span className="text-purple-300">User</span>
                <span className="ml-2 text-gray-600">importance 0.92</span>
              </div>
              <div className="mt-4 pt-4 border-t border-gray-800 text-gray-500">
                <span className="text-blue-400">?</span>
                <span className="ml-2 text-gray-300">What does </span>
                <span className="text-green-300">create_app</span>
                <span className="text-gray-300"> return?</span>
              </div>
              <div className="pl-4 text-gray-400 leading-relaxed">
                <span className="text-gray-500">› </span>
                Returns a configured Flask application instance with all blueprints registered and middleware applied...
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="relative py-24 border-t border-gray-800/50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-3">Everything you need</h2>
            <p className="text-gray-400">Three tools, one workflow</p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                icon: '📊',
                color: 'blue',
                title: 'Dependency Graph',
                desc: 'Interactive visualization of files, classes, and functions. Hierarchical and force-directed layouts. Click any node to inspect it and ask questions.',
              },
              {
                icon: '📚',
                color: 'purple',
                title: 'AI Documentation',
                desc: 'Project overview, getting started guide, architecture diagram, and API docs — generated automatically from your source code using IBM watsonx.ai.',
              },
              {
                icon: '💬',
                color: 'green',
                title: 'Code Q&A',
                desc: 'Ask anything in plain English. Powered by semantic search over your indexed codebase and Llama 3.3 70B for accurate, grounded answers.',
              },
            ].map(f => (
              <div
                key={f.title}
                className={`glass-effect rounded-2xl p-8 hover:border-${f.color}-500/30 transition-all duration-300 group`}
              >
                <div className={`w-12 h-12 rounded-xl bg-${f.color}-500/10 border border-${f.color}-500/20 flex items-center justify-center text-2xl mb-5 group-hover:scale-110 transition-transform`}>
                  {f.icon}
                </div>
                <h3 className="text-lg font-semibold mb-3">{f.title}</h3>
                <p className="text-gray-400 text-sm leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="relative py-24 border-t border-gray-800/50">
        <div className="max-w-4xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-3">How it works</h2>
            <p className="text-gray-400">Three steps from repo to insight</p>
          </div>

          <div className="space-y-6">
            {[
              {
                n: 1, color: 'bg-blue-600',
                title: 'Analyze your repository',
                desc: 'Paste a local path or GitHub URL. CodeLens parses every file and builds a graph of files, classes, functions, and their relationships.',
              },
              {
                n: 2, color: 'bg-purple-600',
                title: 'Generate documentation',
                desc: 'One click generates a full docs suite: project overview, getting started guide, architecture flowchart, and API reference.',
              },
              {
                n: 3, color: 'bg-green-600',
                title: 'Explore and ask questions',
                desc: 'Navigate the dependency graph, read the docs, or type a question. Click any node in the graph to ask about that specific function or class.',
              },
            ].map(s => (
              <div key={s.n} className="flex gap-5 items-start bg-gray-900/50 rounded-2xl p-6 border border-gray-800/60">
                <div className={`flex-shrink-0 w-10 h-10 rounded-full ${s.color} flex items-center justify-center text-sm font-bold shadow-lg`}>
                  {s.n}
                </div>
                <div>
                  <h3 className="text-base font-semibold mb-1.5">{s.title}</h3>
                  <p className="text-gray-400 text-sm leading-relaxed">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative py-24 border-t border-gray-800/50">
        <div className="max-w-2xl mx-auto px-6 text-center">
          <h2 className="text-4xl font-bold mb-4">Ready to explore your code?</h2>
          <p className="text-gray-400 mb-10">
            Add your first project in under a minute.
          </p>
          <button
            onClick={() => navigate('/dashboard')}
            className="px-10 py-4 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-lg font-semibold transition-colors shadow-2xl shadow-blue-500/20 inline-flex items-center gap-3"
          >
            Open Dashboard <span aria-hidden="true">→</span>
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative border-t border-gray-800/50 py-8">
        <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-blue-500 to-blue-700 flex items-center justify-center text-xs font-bold">
              CL
            </div>
            <span className="text-gray-500 text-sm">CodeLens</span>
          </div>
          <p className="text-gray-600 text-sm">Powered by IBM watsonx.ai · Made with Bob</p>
        </div>
      </footer>
    </div>
  );
}

// Made with Bob
