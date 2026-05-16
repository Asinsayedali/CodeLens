import React, { useState, useEffect, useRef } from 'react';
import { qaApi } from '../../services/api';
import { QAResponse, CodeSnippet } from '../../types';
import { MessageList } from './MessageList';

interface ChatInterfaceProps {
  projectId: number;
}

interface Message {
  type: 'question' | 'answer';
  content: string;
  codeSnippets?: CodeSnippet[];
  confidence?: number;
  timestamp?: string;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({ projectId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [embeddingsGenerated, setEmbeddingsGenerated] = useState(false);
  const [generatingEmbeddings, setGeneratingEmbeddings] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(true);
  const [embedSuccess, setEmbedSuccess] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setSuggestions([]);
    setMessages([]);
    setEmbeddingsGenerated(false);
    loadSuggestions();
    loadHistory();
  }, [projectId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const loadSuggestions = async () => {
    try {
      const response = await qaApi.getSuggestions(projectId);
      setSuggestions(response.data.suggestions);
    } catch (error) {
      console.error('Error loading suggestions:', error);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await qaApi.getHistory(projectId, 20);
      const history = response.data;
      if (history.length > 0) {
        setEmbeddingsGenerated(true);
        const historyMessages: Message[] = [];
        history.forEach((item: any) => {
          historyMessages.push({ type: 'question', content: item.question });
          historyMessages.push({ type: 'answer', content: item.answer, timestamp: item.timestamp });
        });
        setMessages(historyMessages);
      }
    } catch (error) {
      console.error('Error loading history:', error);
    }
  };

  const handleGenerateEmbeddings = async () => {
    try {
      setGeneratingEmbeddings(true);
      setEmbedSuccess(null);
      const response = await qaApi.generateEmbeddings(projectId);
      setEmbeddingsGenerated(true);
      setEmbedSuccess(response.data.message || 'Embeddings generated successfully');
      setTimeout(() => setEmbedSuccess(null), 4000);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to generate embeddings');
    } finally {
      setGeneratingEmbeddings(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const question = input.trim();
    setInput('');
    setMessages(prev => [...prev, { type: 'question', content: question }]);
    setLoading(true);

    try {
      const response = await qaApi.ask(projectId, question, true);
      const data: QAResponse = response.data;
      setMessages(prev => [
        ...prev,
        {
          type: 'answer',
          content: data.answer,
          codeSnippets: data.code_snippets,
          confidence: data.confidence,
          timestamp: data.timestamp || undefined,
        },
      ]);
    } catch (error: any) {
      setMessages(prev => [
        ...prev,
        { type: 'answer', content: `Error: ${error.response?.data?.detail || 'Failed to get answer'}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
  };

  return (
    <div className="h-full flex flex-col bg-gray-950">
      {/* Header */}
      <div className="bg-gray-950 border-b border-gray-800 px-6 py-3 flex-shrink-0">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white">Ask about your codebase</h2>
            <p className="text-xs text-gray-500 mt-0.5">Powered by IBM granite-embedding + llama-3-3-70b</p>
          </div>

          <div className="flex items-center gap-3">
            {embedSuccess && (
              <span className="text-xs text-green-400 bg-green-400/10 border border-green-400/20 px-3 py-1.5 rounded-lg">
                ✓ {embedSuccess}
              </span>
            )}
            <button
              onClick={handleGenerateEmbeddings}
              disabled={generatingEmbeddings}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors duration-150 ${
                embeddingsGenerated
                  ? 'bg-gray-800 hover:bg-gray-700 active:bg-gray-600 text-gray-300 border border-gray-700'
                  : 'bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white shadow-sm'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {generatingEmbeddings ? (
                <>
                  <span className="spinner w-3.5 h-3.5" />
                  Indexing...
                </>
              ) : (
                <>
                  <span aria-hidden="true">↺</span>
                  {embeddingsGenerated ? 'Re-index' : 'Index Codebase'}
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-hidden flex flex-col min-h-0">
        <MessageList messages={messages} loading={loading} />
        <div ref={messagesEndRef} />
      </div>

      {/* Suggestions — always visible, collapsible */}
      {suggestions.length > 0 && (
        <div className="flex-shrink-0 border-t border-gray-800 bg-gray-950">
          <button
            onClick={() => setShowSuggestions(v => !v)}
            className="w-full px-6 py-2 flex items-center justify-between text-xs text-gray-500 hover:text-gray-400 transition-colors"
          >
            <span>Suggested questions from your graph</span>
            <span>{showSuggestions ? '▲' : '▼'}</span>
          </button>
          {showSuggestions && (
            <div className="px-6 pb-3 flex gap-2 overflow-x-auto scrollbar-hide">
              {suggestions.map((s, i) => (
                <button
                  key={i}
                  onClick={() => handleSuggestionClick(s)}
                  className="flex-shrink-0 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 active:bg-gray-600 border border-gray-700 hover:border-gray-600 text-gray-300 hover:text-white rounded-lg text-xs transition-colors whitespace-nowrap"
                >
                  {s}
                </button>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Input */}
      <div className="flex-shrink-0 border-t border-gray-800 bg-gray-950 px-6 py-4">
        {!embeddingsGenerated && (
          <p className="text-xs text-amber-400/80 mb-3 flex items-center gap-1.5">
            <span>⚠</span> Index your codebase first to enable Q&amp;A
          </p>
        )}
        <form onSubmit={handleSubmit} className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder={
              embeddingsGenerated
                ? 'Ask anything about your code...'
                : 'Click "Index Codebase" above to get started...'
            }
            disabled={!embeddingsGenerated || loading}
            className="flex-1 px-4 py-2.5 bg-gray-900 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-40 disabled:cursor-not-allowed text-sm transition-colors"
            aria-label="Ask a question about your code"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading || !embeddingsGenerated}
            className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 active:bg-blue-700 disabled:bg-gray-800 disabled:text-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors font-medium text-sm flex items-center gap-2 shadow-sm"
          >
            {loading ? (
              <>
                <span className="spinner w-3.5 h-3.5 border-white border-t-transparent" />
                Thinking
              </>
            ) : (
              'Send'
            )}
          </button>
        </form>
        <p className="text-xs text-gray-700 mt-2">Enter to send · IBM watsonx.ai</p>
      </div>
    </div>
  );
};

// Made with Bob
