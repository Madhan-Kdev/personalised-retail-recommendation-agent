import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, ShoppingCart, ArrowRight, RefreshCw, Cpu } from 'lucide-react';

export default function ConversationalAssistant({ activeCustomer, onInteract, messages, setMessages, loading, handleSend, input, setInput }) {
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  return (
    <div className="flex flex-col h-full bg-zinc-950 text-zinc-100">
      {/* Header */}
      <div className="p-4 border-b border-zinc-900 bg-zinc-900/40 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot className="w-4 h-4 text-zinc-400" />
          <span className="text-xs font-semibold uppercase tracking-wider text-zinc-200">AI Shopping Concierge</span>
        </div>
        <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-zinc-900 text-zinc-500 border border-zinc-850">
          Docked
        </span>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
        {messages.map((msg, index) => (
          <div key={index} className={`flex items-start gap-2.5 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div
              className={`w-7 h-7 rounded flex items-center justify-center shrink-0 border text-[10px] font-bold ${
                msg.role === 'user'
                  ? 'bg-zinc-900 text-zinc-300 border-zinc-800'
                  : 'bg-zinc-100 text-zinc-950 border-zinc-200'
              }`}
            >
              {msg.role === 'user' ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
            </div>

            <div className={`max-w-[85%] space-y-2.5 ${msg.role === 'user' ? 'text-right' : ''}`}>
              <div
                className={`p-3 rounded text-[11px] leading-relaxed whitespace-pre-line text-left ${
                  msg.role === 'user'
                    ? 'bg-zinc-900 text-zinc-200 border border-zinc-800'
                    : 'bg-zinc-950 text-zinc-300 border border-zinc-850'
                }`}
              >
                {msg.content}
              </div>

              {/* Product cards inside sidebar chat */}
              {msg.suggested_products && msg.suggested_products.length > 0 && (
                <div className="space-y-2 text-left">
                  {msg.suggested_products.map((p) => (
                    <div
                      key={p.id}
                      className="p-2.5 rounded bg-zinc-900 border border-zinc-850 flex items-center gap-3 group"
                    >
                      <img src={p.image_url} alt="" className="w-10 h-10 rounded object-cover bg-zinc-950 shrink-0 border border-zinc-850" />
                      <div className="flex-1 min-w-0">
                        <h4 className="text-[11px] font-semibold text-zinc-200 truncate">{p.title}</h4>
                        <div className="flex items-center justify-between mt-0.5">
                          <span className="text-[10px] font-mono text-zinc-300">${p.price.toFixed(2)}</span>
                          <button
                            onClick={() => onInteract(activeCustomer?.id, p.id, 'add_to_cart')}
                            className="px-2 py-0.5 rounded bg-zinc-100 hover:bg-zinc-200 text-zinc-950 font-semibold text-[9px] transition-colors flex items-center gap-1"
                          >
                            <ShoppingCart className="w-2.5 h-2.5" />
                            <span>Add</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Suggested Followups */}
              {msg.suggested_followups && msg.suggested_followups.length > 0 && index === messages.length - 1 && (
                <div className="flex flex-wrap gap-1 pt-1 text-left">
                  {msg.suggested_followups.map((fol, fIdx) => (
                    <button
                      key={fIdx}
                      onClick={() => handleSend(fol)}
                      className="text-[10px] px-2 py-1 rounded bg-zinc-900 hover:bg-zinc-850 text-zinc-400 hover:text-zinc-250 border border-zinc-850/60 transition-colors"
                    >
                      <span>{fol}</span>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-500">
              <Bot className="w-3.5 h-3.5 animate-pulse" />
            </div>
            <div className="px-3 py-2 rounded bg-zinc-950 border border-zinc-850 text-[10px] text-zinc-500 flex items-center gap-1.5 font-mono">
              <RefreshCw className="w-3 h-3 animate-spin" />
              <span>Analyzing intent...</span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Chat Input */}
      <div className="p-3 border-t border-zinc-900 bg-zinc-900/20">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-1.5"
        >
          <input
            type="text"
            placeholder="Ask AI Concierge..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            className="flex-1 bg-zinc-900 text-zinc-200 text-xs rounded px-3 py-2.5 border border-zinc-850 focus:border-zinc-800 focus:outline-none"
          />
          <button
            type="submit"
            disabled={!input.trim() || loading}
            className="p-2.5 rounded bg-zinc-100 hover:bg-zinc-200 text-zinc-950 transition-colors disabled:opacity-50"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </div>
  );
}
