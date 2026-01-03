import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Image as ImageIcon, X, Loader2, Sparkles, Brain } from 'lucide-react';
import axios from 'axios';
import clsx from 'clsx';
import { io, Socket } from 'socket.io-client';
import ReactMarkdown from 'react-markdown';

interface Message {
    type: 'request' | 'response' | 'thinking';
    content: string;
    timestamp: string;
}

export const ChatInterface: React.FC = () => {
    const [message, setMessage] = useState('');
    const [images, setImages] = useState<File[]>([]);
    const [isSending, setIsSending] = useState(false);
    const [history, setHistory] = useState<Message[]>([]);
    const [currentThinking, setCurrentThinking] = useState<string>('');
    const [isConnected, setIsConnected] = useState(false);
    
    const socketRef = useRef<Socket | null>(null);
    const scrollRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const API_BASE = import.meta.env.DEV ? 'http://localhost:3000' : '';

    // Initial load and socket setup
    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const res = await axios.get(`${API_BASE}/api/history`);
                setHistory(res.data);
            } catch (e) {
                console.error("History fail", e);
            }
        };
        fetchHistory();

        const socket = io(API_BASE);
        socketRef.current = socket;

        socket.on('connect', () => setIsConnected(true));
        socket.on('disconnect', () => setIsConnected(false));

        socket.on('thinking', (data: { content: string }) => {
            setCurrentThinking(prev => prev + data.content);
        });

        socket.on('response', (data: Message) => {
            setHistory(prev => [...prev, { ...data, type: 'response' }]);
            setCurrentThinking(''); // CLEAR THINKING WHEN RESPONSE ARRIVES
        });

        socket.on('user-message', (data: Message) => {
            setHistory(prev => [...prev, { ...data, type: 'request' }]);
            setCurrentThinking(''); // Clear any stale thinking
        });

        return () => {
            socket.disconnect();
        };
    }, []);

    // Auto-scroll
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [history, currentThinking]);

    const handlePaste = useCallback((e: React.ClipboardEvent) => {
        const items = e.clipboardData.items;
        const newImages: File[] = [];
        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
                const blob = items[i].getAsFile();
                if (blob) newImages.push(blob);
            }
        }
        if (newImages.length > 0) {
            e.preventDefault();
            setImages(prev => [...prev, ...newImages]);
        }
    }, []);

    const removeImage = (index: number) => {
        setImages(prev => prev.filter((_, i) => i !== index));
    };

    const handleSubmit = async () => {
        if (!message.trim() && images.length === 0) return;
        
        setIsSending(true);
        const formData = new FormData();
        formData.append('message', message);
        images.forEach(img => formData.append('images', img));

        try {
            await axios.post(`${API_BASE}/api/chat`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            setMessage('');
            setImages([]);
            setCurrentThinking(''); // Clear previous thinking when new request starts
        } catch (error) {
            console.error("Chat Failed", error);
        } finally {
            setIsSending(false);
        }
    };

    return (
        <div className="flex flex-col h-full w-full overflow-hidden bg-white/40 backdrop-blur-md rounded-[32px] border border-white/50 shadow-clay-card">
            
            {/* 1. Chat History Area */}
            <div 
                ref={scrollRef}
                className="flex-1 overflow-y-auto p-4 lg:p-6 space-y-4 lg:space-y-6 custom-scrollbar"
            >
                {history.length === 0 && !currentThinking && (
                    <div className="h-full flex flex-col items-center justify-center text-clay-muted opacity-40">
                        <div className="relative mb-4">
                            <Sparkles className="w-12 h-12" />
                            <div className={clsx(
                                "absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-white",
                                isConnected ? "bg-clay-accent-success" : "bg-clay-muted"
                            )} />
                        </div>
                        <p className="font-black uppercase tracking-widest text-xs">
                            {isConnected ? "Awaiting Input" : "Connecting..."}
                        </p>
                    </div>
                )}

                {history.map((msg, i) => (
                    <div 
                        key={i} 
                        className={clsx(
                            "flex flex-col animate-in fade-in slide-in-from-bottom-2 duration-500",
                            msg.type === 'request' ? "items-end" : "items-start"
                        )}
                    >
                        <div className={clsx(
                            "max-w-[90%] p-4 lg:p-5 rounded-[24px] shadow-clay-card",
                            msg.type === 'request' 
                                ? "bg-white text-clay-foreground border-2 border-clay-accent/10" 
                                : "bg-clay-accent text-white"
                        )}>
                            <div className="prose prose-sm max-w-none prose-invert">
                                <ReactMarkdown>{msg.content}</ReactMarkdown>
                            </div>
                        </div>
                        <span className="mt-1 text-[9px] font-black uppercase tracking-widest text-clay-muted opacity-40 px-4">
                            {new Date(msg.timestamp).toLocaleTimeString()}
                        </span>
                    </div>
                ))}

                {/* 2. Thinking Stream (The "Work" View) */}
                {currentThinking && (
                    <div className="flex flex-col items-start animate-pulse">
                        <div className="flex items-center gap-3 mb-2 px-4">
                            <Brain className="w-4 h-4 text-clay-accent-secondary" />
                            <span className="text-[10px] font-black uppercase tracking-widest text-clay-accent-secondary">Thinking</span>
                        </div>
                        <div className="max-w-[95%] p-4 rounded-[24px] bg-clay-accent-secondary/5 border-2 border-dashed border-clay-accent-secondary/20 font-mono text-xs text-clay-muted whitespace-pre-wrap">
                            {currentThinking}
                        </div>
                    </div>
                )}
            </div>

            {/* 3. Input Console */}
            <div className={clsx(
                "relative bg-white/80 border-t border-gray-100 p-4 transition-all duration-500 shrink-0",
                "focus-within:bg-white"
            )}>
                
                {/* Images */}
                {images.length > 0 && (
                    <div className="flex gap-4 mb-4 overflow-x-auto pb-2 scrollbar-hide">
                        {images.map((img, idx) => (
                            <div key={idx} className="relative flex-none group">
                                <img 
                                    src={URL.createObjectURL(img)} 
                                    className="h-16 w-16 object-cover rounded-xl shadow-md border-2 border-white"
                                />
                                <button onClick={() => removeImage(idx)} className="absolute -top-2 -right-2 bg-clay-accent-secondary text-white rounded-full p-1 shadow-lg">
                                    <X className="w-3 h-3" />
                                </button>
                            </div>
                        ))}
                    </div>
                )}

                <div className="flex items-end gap-4">
                    <textarea
                        ref={textareaRef}
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        onPaste={handlePaste}
                        onKeyDown={(e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSubmit();
                            }
                        }}
                        placeholder="Push instruction..."
                        className="flex-1 bg-transparent border-0 focus:ring-0 text-clay-foreground text-base placeholder:text-clay-muted/30 resize-none max-h-[100px] font-medium py-1"
                    />

                    <div className="flex items-center gap-2">
                         <label className="cursor-pointer p-3 rounded-2xl bg-clay-accent/5 hover:bg-clay-accent/10 text-clay-muted hover:text-clay-accent transition-all">
                            <input type="file" multiple accept="image/*" onChange={(e) => e.target.files && setImages(prev => [...prev, ...Array.from(e.target.files!)])} className="hidden" />
                            <ImageIcon className="w-5 h-5" />
                        </label>
                        
                        <button 
                            onClick={handleSubmit}
                            disabled={isSending || (!message.trim() && images.length === 0)}
                            className={clsx(
                                "flex items-center justify-center p-3 rounded-xl transition-all duration-300",
                                (message.trim() || images.length > 0)
                                    ? "bg-clay-accent text-white shadow-clay-button hover:scale-110 active:scale-95"
                                    : "bg-gray-100 text-gray-300 cursor-not-allowed"
                            )}
                        >
                            {isSending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};
