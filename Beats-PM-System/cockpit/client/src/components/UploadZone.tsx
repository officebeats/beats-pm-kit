import React, { useCallback, useState } from 'react';
import { Upload, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import clsx from 'clsx';
import axios from 'axios';

export const UploadZone: React.FC = () => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length === 0) return;

    await uploadFiles(files);
  }, []);

  const handleFileInput = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      await uploadFiles(Array.from(e.target.files));
    }
  }, []);

  const uploadFiles = async (files: File[]) => {
    setUploadStatus('uploading');
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    try {
      const API_URL = import.meta.env.DEV ? 'http://localhost:3000/api/upload' : '/api/upload';
      
      await axios.post(API_URL, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setUploadStatus('success');
      setMessage(`Sent ${files.length} items to the Brain.`);
      
      setTimeout(() => {
        setUploadStatus('idle');
        setMessage('');
      }, 3000);
    } catch (error) {
      console.error('Upload failed', error);
      setUploadStatus('error');
      setMessage('Connection failed.');
    }
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={clsx(
        "relative group cursor-pointer transition-all duration-700 ease-[cubic-bezier(0.23,1,0.32,1)]",
        "rounded-[48px] p-12 flex flex-col items-center justify-center text-center h-[360px] w-full overflow-hidden",
        "border-2",
        
        isDragging 
          ? "bg-clay-accent/5 border-clay-accent border-dashed shadow-[0_0_40px_rgba(124,58,237,0.15)] scale-[0.99]" 
          : "bg-white/60 backdrop-blur-xl border-transparent shadow-clay-card hover:-translate-y-2 hover:shadow-clay-button-hover hover:border-clay-accent/20"
      )}
    >
      <input 
        type="file" 
        multiple 
        onChange={handleFileInput} 
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-50"
      />

      {/* Background Decorative Gradient */}
      <div className={clsx(
          "absolute inset-0 bg-gradient-to-br from-clay-accent/5 to-transparent transition-opacity duration-1000",
          isDragging ? "opacity-100" : "opacity-0"
      )} />

      <div className="z-10 flex flex-col items-center space-y-8 pointer-events-none">
        
        {/* Dynamic Icon Orb */}
        <div className={clsx(
            "w-28 h-28 rounded-3xl flex items-center justify-center transition-all duration-700 ease-out",
            isDragging 
                ? "bg-white shadow-xl scale-110 rotate-6" 
                : "bg-white shadow-clay-button group-hover:bg-clay-accent/5"
        )}>

             {uploadStatus === 'idle' && <Upload className={clsx("w-12 h-12 transition-all duration-500", isDragging ? "text-clay-accent" : "text-clay-accent/40 group-hover:text-clay-accent")} />}
             {uploadStatus === 'uploading' && <Loader2 className="w-12 h-12 text-clay-accent animate-spin" />}
             {uploadStatus === 'success' && <CheckCircle className="w-12 h-12 text-clay-accent-success" />}
             {uploadStatus === 'error' && <AlertCircle className="w-12 h-12 text-clay-accent-warning" />}
        </div>

        <div className="space-y-3">
          <h3 className="font-display font-black text-3xl text-clay-foreground tracking-tight">
            {uploadStatus === 'idle' ? (isDragging ? "Release to Integrate" : "Context Drop Zone") : ""}
            {uploadStatus === 'uploading' && "Absorbing Knowledge..."}
            {uploadStatus === 'success' && "Context Acquired!"}
            {uploadStatus === 'error' && "Upload Failed"}
          </h3>
          
          {uploadStatus === 'idle' && (
              <p className="text-clay-muted font-medium max-w-sm mx-auto leading-relaxed text-lg opacity-80">
                Drag spec docs, data, or images here to feed the <span className="text-clay-accent font-bold">Antigravity Brain</span>.
              </p>
          )}
           {message && (
               <div className="bg-clay-accent/10 px-4 py-2 rounded-full inline-block">
                   <p className="text-clay-accent font-black text-sm uppercase tracking-widest">{message}</p>
               </div>
           )}
        </div>
      </div>

       {/* Suble side accents instead of overlapping icons */}
       <div className="absolute top-8 left-8 w-1.5 h-16 bg-gradient-to-b from-clay-accent/20 to-transparent rounded-full opacity-50" />
       <div className="absolute bottom-8 right-8 w-1.5 h-16 bg-gradient-to-t from-clay-accent-secondary/20 to-transparent rounded-full opacity-50" />
    </div>
  );
};

