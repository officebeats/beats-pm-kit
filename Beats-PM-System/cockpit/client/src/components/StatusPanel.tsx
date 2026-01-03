import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { RefreshCw, CheckCircle2, Clock } from 'lucide-react';
import clsx from 'clsx';

export const StatusPanel: React.FC = () => {
    const [content, setContent] = useState<string>('');
    const [loading, setLoading] = useState<boolean>(true);
    const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

    const fetchStatus = async () => {
        setLoading(true);
        try {
            const API_URL = import.meta.env.DEV ? 'http://localhost:3000/api/status' : '/api/status';
            const response = await axios.get(API_URL);
            setContent(response.data.content);
            setLastUpdated(new Date());
        } catch (error) {
            console.error('Failed to fetch status:', error);
            setContent('### Error\nFailed to load Action Plan from Brain.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStatus();
        // Dynamic polling every 30 seconds
        const interval = setInterval(fetchStatus, 30000);
        return () => clearInterval(interval);
    }, []);

    return (
        <section className="glass-card rounded-[48px] p-10 min-h-[400px] flex flex-col transition-all duration-500 hover:shadow-2xl relative overflow-hidden group">
            <div className="absolute inset-0 bg-gradient-to-br from-clay-accent/5 to-transparent pointer-events-none" />
            
            <div className="relative z-10 flex flex-col h-full">
                <div className="flex justify-between items-center mb-8">
                    <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 bg-white rounded-2xl flex items-center justify-center shadow-clay-card group-hover:rotate-6 transition-transform duration-500">
                            <span className="text-2xl">🚀</span>
                        </div>
                        <div>
                            <h3 className="font-display font-black text-2xl text-clay-foreground tracking-tight">Active Strategy</h3>
                            <div className="flex items-center space-x-2 text-[10px] font-black text-clay-muted uppercase tracking-widest opacity-60">
                                <Clock className="w-3 h-3" />
                                <span>Updated {lastUpdated.toLocaleTimeString()}</span>
                            </div>
                        </div>
                    </div>
                    
                    <button 
                        onClick={fetchStatus}
                        disabled={loading}
                        className={clsx(
                            "p-3 rounded-2xl bg-white shadow-clay-button hover:shadow-clay-button-hover active:scale-95 transition-all",
                            loading && "animate-spin"
                        )}
                    >
                        <RefreshCw className={clsx("w-5 h-5 text-clay-accent", loading && "opacity-50")} />
                    </button>
                </div>

                <div className="flex-1 overflow-y-auto pr-4 custom-scrollbar max-h-[500px]">
                    <div className="prose prose-clay max-w-none">
                        <ReactMarkdown 
                            components={{
                                h1: ({node, ...props}) => <h1 className="text-3xl font-black text-clay-foreground mb-6" {...props} />,
                                h2: ({node, ...props}) => <h2 className="text-xl font-black text-clay-foreground mt-8 mb-4 flex items-center gap-2" {...props} />,
                                p: ({node, ...props}) => <p className="text-clay-muted font-medium leading-relaxed mb-4" {...props} />,
                                ul: ({node, ...props}) => <ul className="space-y-3 mb-6" {...props} />,
                                li: ({node, ...props}) => (
                                    <li className="flex items-start gap-3 group/item">
                                        <div className="mt-1.5 w-1.5 h-1.5 rounded-full bg-clay-accent/40" />
                                        <span className="text-clay-muted font-medium" {...props} />
                                    </li>
                                ),
                                // Custom Checkbox rendering
                                input: ({node, ...props}) => {
                                    if (props.type === 'checkbox') {
                                        return (
                                            <div className="inline-flex items-center mr-2">
                                                {props.checked ? (
                                                    <CheckCircle2 className="w-5 h-5 text-clay-accent-success" />
                                                ) : (
                                                    <div className="w-5 h-5 rounded-md border-2 border-clay-muted/20" />
                                                )}
                                            </div>
                                        );
                                    }
                                    return <input {...props} />;
                                }
                            }}
                        >
                            {content}
                        </ReactMarkdown>
                    </div>
                </div>

                {!content && !loading && (
                    <div className="flex flex-col items-center justify-center py-20 text-center">
                        <p className="text-clay-muted font-medium max-w-xs">
                            The system is currently listening for your next move. Send a message to get started.
                        </p>
                    </div>
                )}
            </div>
        </section>
    );
};
