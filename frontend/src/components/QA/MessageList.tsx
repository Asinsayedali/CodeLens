import React from 'react';
import { CodeSnippet } from '../../types';

interface Message {
  type: 'question' | 'answer';
  content: string;
  codeSnippets?: CodeSnippet[];
  confidence?: number;
  timestamp?: string;
}

interface MessageListProps {
  messages: Message[];
  loading?: boolean;
}

// Minimal inline markdown renderer — handles bold, inline code, headers, lists
function renderMarkdown(text: string): React.ReactNode[] {
  const lines = text.split('\n');
  const nodes: React.ReactNode[] = [];

  lines.forEach((line, i) => {
    // Heading
    const h3 = line.match(/^### (.+)/);
    const h2 = line.match(/^## (.+)/);
    const h1 = line.match(/^# (.+)/);
    if (h1) { nodes.push(<p key={i} className="text-base font-bold text-white mt-3 mb-1">{h1[1]}</p>); return; }
    if (h2) { nodes.push(<p key={i} className="text-sm font-bold text-white mt-3 mb-1">{h2[1]}</p>); return; }
    if (h3) { nodes.push(<p key={i} className="text-sm font-semibold text-gray-200 mt-2 mb-0.5">{h3[1]}</p>); return; }

    // Bullet list
    const bullet = line.match(/^[-*] (.+)/);
    if (bullet) {
      nodes.push(
        <div key={i} className="flex gap-2 text-sm text-gray-300">
          <span className="text-gray-500 mt-0.5">•</span>
          <span>{inlineFormat(bullet[1])}</span>
        </div>
      );
      return;
    }

    // Numbered list
    const numbered = line.match(/^(\d+)\. (.+)/);
    if (numbered) {
      nodes.push(
        <div key={i} className="flex gap-2 text-sm text-gray-300">
          <span className="text-gray-500 min-w-[1.2rem]">{numbered[1]}.</span>
          <span>{inlineFormat(numbered[2])}</span>
        </div>
      );
      return;
    }

    // Code block markers — handled below at block level, skip
    if (line.startsWith('```')) { nodes.push(<span key={i} />); return; }

    // Empty line
    if (!line.trim()) { nodes.push(<div key={i} className="h-2" />); return; }

    // Normal paragraph line
    nodes.push(
      <p key={i} className="text-sm text-gray-300 leading-relaxed">
        {inlineFormat(line)}
      </p>
    );
  });

  return nodes;
}

function inlineFormat(text: string): React.ReactNode {
  // Split on **bold**, *italic*, `code`
  const parts = text.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g);
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**'))
      return <strong key={i} className="text-white font-semibold">{part.slice(2, -2)}</strong>;
    if (part.startsWith('*') && part.endsWith('*'))
      return <em key={i} className="text-gray-200 italic">{part.slice(1, -1)}</em>;
    if (part.startsWith('`') && part.endsWith('`'))
      return <code key={i} className="text-green-400 bg-[#111] px-1 py-0.5 rounded text-xs font-mono">{part.slice(1, -1)}</code>;
    return part;
  });
}

// Extract code blocks from raw text and render separately
function renderContent(content: string): React.ReactNode {
  const blocks = content.split(/(```[\s\S]*?```)/g);
  return (
    <div className="space-y-1">
      {blocks.map((block, i) => {
        if (block.startsWith('```')) {
          const lines = block.split('\n');
          const lang = lines[0].replace('```', '').trim();
          const code = lines.slice(1, -1).join('\n');
          return (
            <div key={i} className="rounded-lg overflow-hidden bg-black border border-[#222] my-2">
              {lang && (
                <div className="px-3 py-1 bg-[#111] border-b border-[#222] text-xs text-gray-500 font-mono">
                  {lang}
                </div>
              )}
              <pre className="p-3 overflow-x-auto text-xs text-gray-300 font-mono leading-relaxed">{code}</pre>
            </div>
          );
        }
        return <div key={i}>{renderMarkdown(block)}</div>;
      })}
    </div>
  );
}

export const MessageList: React.FC<MessageListProps> = ({ messages, loading }) => {
  return (
    <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4 bg-black">
      {messages.length === 0 && !loading ? (
        <div className="flex flex-col items-center justify-center h-full text-center">
          <div className="w-16 h-16 rounded-2xl bg-[#111] border border-[#222] flex items-center justify-center mb-4 text-2xl">
            💬
          </div>
          <p className="text-gray-400 font-medium">No conversation yet</p>
          <p className="text-gray-600 text-sm mt-1">Select a suggestion below or type a question</p>
        </div>
      ) : (
        messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${message.type === 'question' ? 'justify-end' : 'justify-start'}`}
          >
            {message.type === 'question' ? (
              /* User bubble */
              <div className="max-w-[70%] bg-blue-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 shadow-lg" role="article" aria-label="User question">
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              </div>
            ) : (
              /* AI answer */
              <div className="max-w-[85%] space-y-3" role="article" aria-label="AI response">
                <div className="bg-[#111] border border-[#222] rounded-2xl rounded-tl-sm px-5 py-4 shadow-lg">
                  {renderContent(message.content)}

                  {/* Confidence bar */}
                  {message.confidence !== undefined && message.confidence > 0 && (
                    <div className="flex items-center gap-2 mt-4 pt-3 border-t border-[#222]">
                      <span className="text-xs text-gray-600">Relevance</span>
                      <div className="flex-1 bg-[#1c1c1c] rounded-full h-1 max-w-[120px]">
                        <div
                          className={`h-1 rounded-full transition-all ${
                            message.confidence > 0.7 ? 'bg-green-500' :
                            message.confidence > 0.4 ? 'bg-yellow-500' : 'bg-orange-500'
                          }`}
                          style={{ width: `${Math.min(message.confidence * 100, 100)}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-600">{(message.confidence * 100).toFixed(0)}%</span>
                      {message.timestamp && (
                        <span className="text-xs text-gray-700 ml-auto">
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {/* Code snippets used */}
                {message.codeSnippets && message.codeSnippets.length > 0 && (
                  <details className="group">
                    <summary className="cursor-pointer text-xs text-gray-600 hover:text-gray-400 transition-colors flex items-center gap-1.5 px-1 list-none">
                      <span className="group-open:rotate-90 transition-transform inline-block" aria-hidden="true">▶</span>
                      {message.codeSnippets.length} source snippet{message.codeSnippets.length > 1 ? 's' : ''} used
                    </summary>
                    <div className="mt-2 space-y-2">
                      {message.codeSnippets.map((snippet, idx) => (
                        <div key={idx} className="bg-[#111] border border-[#222] rounded-lg overflow-hidden">
                          <div className="bg-black px-3 py-1.5 flex items-center justify-between border-b border-[#222]">
                            <span className="text-xs text-blue-400 font-mono truncate max-w-[80%]">
                              {snippet.file_path}
                            </span>
                            <span className="text-xs text-gray-600 flex-shrink-0 ml-2">
                              {(snippet.similarity * 100).toFixed(0)}% match
                            </span>
                          </div>
                          <pre className="p-3 text-xs text-gray-400 font-mono overflow-x-auto leading-relaxed max-h-40">
                            {snippet.code}
                          </pre>
                        </div>
                      ))}
                    </div>
                  </details>
                )}
              </div>
            )}
          </div>
        ))
      )}

      {loading && (
        <div className="flex justify-start">
          <div className="bg-[#111] border border-[#222] rounded-2xl rounded-tl-sm px-5 py-4 shadow-lg">
            <div className="flex items-center gap-2">
              <div className="flex gap-1">
                {[0, 150, 300].map(delay => (
                  <div
                    key={delay}
                    className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"
                    style={{ animationDelay: `${delay}ms` }}
                    aria-hidden="true"
                  />
                ))}
              </div>
              <span className="text-xs text-gray-500">Thinking...</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Made with Bob
