import { Sidebar } from './components/Sidebar';
import { UploadZone } from './components/UploadZone';
import { ChatInterface } from './components/ChatInterface';
import { StatusPanel } from './components/StatusPanel';

function App() {
  return (
    <div className="flex min-h-screen relative overflow-hidden font-sans selection:bg-clay-accent/20">
      
      {/* 1. Animated Background Blobs */}
      <div className="fixed inset-0 pointer-events-none -z-10 overflow-hidden">
        <div className="clay-blob w-[50vh] h-[50vh] bg-clay-accent/10 top-[-10%] left-[-10%] animate-clay-float" />
        <div className="clay-blob w-[60vh] h-[60vh] bg-clay-accent-secondary/10 bottom-[-10%] right-[-10%] animate-clay-float-delayed" />
        <div className="clay-blob w-[40vh] h-[40vh] bg-clay-accent-tertiary/10 top-[20%] right-[20%] animate-clay-float-slow" />
      </div>

      {/* 2. Main Layout */}
      <Sidebar />
      
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative z-10 p-4 lg:p-8">
        
        {/* Compact Header */}
        <header className="flex flex-col md:flex-row justify-between items-center gap-2 mb-6 shrink-0">
          <div className="flex items-center gap-4">
            <h2 className="font-display font-black text-3xl lg:text-5xl text-clay-foreground tracking-tighter">
              Command <span className="text-transparent bg-clip-text bg-gradient-to-r from-clay-accent via-clay-accent-secondary to-clay-accent-tertiary">Center</span>
            </h2>
            <div className="hidden sm:flex items-center space-x-2 bg-white/80 backdrop-blur-md px-3 py-1.5 rounded-xl shadow-sm border border-white/50">
               <div className="relative">
                  <div className="w-2 h-2 rounded-full bg-clay-accent-success" />
                  <div className="absolute inset-0 w-2 h-2 rounded-full bg-clay-accent-success animate-ping opacity-50" />
               </div>
               <span className="font-black text-[10px] uppercase tracking-widest text-clay-foreground/60">LIVE</span>
            </div>
          </div>
          <p className="hidden md:block text-sm text-clay-muted font-medium tracking-tight opacity-80">Orchestrate intelligence.</p>
        </header>

        {/* Compact Bento Layout */}
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-6 overflow-hidden min-h-0">
          
          {/* Main Hero: Chat & Upload (Spans 8 cols) */}
          <div className="lg:col-span-8 flex flex-col gap-6 overflow-hidden min-h-0">
            <div className="flex-1 min-h-0 transform transition-all duration-500 hover:scale-[1.005]">
              <ChatInterface />
            </div>
            
            <div className="shrink-0 transform transition-all duration-500 hover:scale-[1.005]">
              <UploadZone />
            </div>
          </div>


          {/* Right Panel: Stats (Spans 4 cols) */}
          <div className="lg:col-span-4 flex flex-col gap-6 overflow-y-auto lg:overflow-visible pr-2 lg:pr-0 scrollbar-hide">
             {/* Stat Card 1 - Compact */}
            <div className="bg-gradient-to-br from-clay-accent to-clay-accent-secondary rounded-3xl shadow-clay-card p-6 text-white relative overflow-hidden group shrink-0">
                <div className="relative z-10">
                    <p className="text-white/60 font-black text-[10px] uppercase tracking-[0.2em] mb-1">Entities</p>
                    <h3 className="font-display font-black text-4xl tracking-tighter">08</h3>
                </div>
                <div className="absolute top-0 right-0 w-24 h-24 bg-white/10 rounded-full -translate-y-1/2 translate-x-1/2 blur-2xl" />
            </div>

            {/* Stat Card 2 - Compact */}
            <div className="glass-card rounded-3xl p-6 relative overflow-hidden group shrink-0">
                 <div className="flex justify-between items-start mb-2">
                    <p className="text-clay-muted font-black text-[10px] uppercase tracking-[0.2em] opacity-60">Neural Storage</p>
                    <span className="text-clay-accent-success font-black text-[9px] px-1.5 py-0.5 bg-clay-accent-success/10 rounded-md">OK</span>
                 </div>
                 
                 <div className="flex items-baseline space-x-1 mb-4">
                    <h3 className="font-display font-black text-3xl text-clay-foreground tracking-tighter">12.4</h3>
                    <span className="text-sm font-black text-clay-accent/40 tracking-tighter">%</span>
                 </div>
                 
                 <div className="w-full bg-gray-100/50 h-2 rounded-full overflow-hidden p-0.5 shadow-inner">
                    <div className="h-full bg-gradient-to-r from-clay-accent to-clay-accent-tertiary rounded-full w-[12.4%]" />
                 </div>
            </div>

             {/* Action Plan Status - Compacted inside scroll area or height-aware */}
             <div className="flex-1 min-h-0 overflow-y-auto custom-scrollbar">
                <StatusPanel />
             </div>

            {/* Intelligence Tip - Hidden on small height or last */}
             <div className="hidden xl:block bg-clay-accent-tertiary/5 border border-clay-accent-tertiary/10 rounded-3xl p-6 shrink-0">
                <p className="text-clay-foreground/70 font-medium text-xs leading-relaxed">
                    <span className="text-clay-accent-tertiary font-bold">Tip:</span> Drag folders into the <span className="font-bold">Drop Zone</span> to hydrate context.
                </p>
            </div>
          </div>

        </div>
      </main>

    </div>
  );
}

export default App;
