import React from "react";
import { LayoutDashboard, Rocket, Layers, Ghost } from "lucide-react";
import clsx from "clsx";

export const Sidebar: React.FC<{
  currentView: string;
  setView: (v: string) => void;
}> = ({ currentView, setView }) => {
  return (
    <aside className="w-80 p-6 h-screen sticky top-0 z-50">
      <div className="h-full w-full glass-sidebar rounded-[40px] flex flex-col p-6 transition-all duration-500">
        {/* Brand Header */}
        <div className="flex items-center space-x-4 mb-12 px-2 mt-2">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-clay-accent to-clay-accent-secondary flex items-center justify-center shadow-lg transform transition-transform hover:rotate-3 duration-300">
            <Ghost className="w-7 h-7 text-white" />
          </div>
          <div>
            <h1 className="font-display font-black text-2xl text-clay-foreground tracking-tight leading-none">
              Beats
            </h1>
            <p className="text-xs text-clay-muted font-bold uppercase tracking-widest mt-1 opacity-60">
              Brain Mesh v2.5.0
            </p>
          </div>
        </div>

        {/* Navigation */}
        <nav className="space-y-3 flex-1">
          <NavItem
            icon={<LayoutDashboard />}
            label="Dashboard"
            active={currentView === "Dashboard"}
            onClick={() => setView("Dashboard")}
          />
          <NavItem
            icon={<Rocket />}
            label="Action Plan"
            active={currentView === "Action Plan"}
            onClick={() => setView("Action Plan")}
          />
          <NavItem
            icon={<Layers />}
            label="System Logic"
            active={currentView === "System Logic"}
            onClick={() => setView("System Logic")}
          />
        </nav>

        {/* Footer Status */}
        <div className="mt-auto pt-6 border-t border-clay-accent/5">
          <div className="bg-white/50 rounded-2xl p-4 flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="relative">
                <div className="w-3 h-3 rounded-full bg-clay-accent-success" />
                <div className="absolute inset-0 w-3 h-3 rounded-full bg-clay-accent-success animate-ping opacity-75" />
              </div>
              <span className="text-sm font-bold text-clay-foreground/80">
                System Active
              </span>
            </div>
            <div className="text-[10px] font-black text-clay-accent px-2 py-1 bg-clay-accent/10 rounded-lg">
              LOCAL
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
};

const NavItem = ({
  icon,
  label,
  onClick,
  active = false,
}: {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  active?: boolean;
}) => (
  <div
    onClick={onClick}
    className={clsx(
      "group flex items-center space-x-4 px-5 py-4 rounded-[24px] cursor-pointer transition-all duration-300 ease-out select-none",
      active
        ? "bg-white shadow-clay-button text-clay-accent"
        : "text-clay-muted hover:bg-white/60 hover:text-clay-accent hover:shadow-sm"
    )}
  >
    <div
      className={clsx(
        "p-2 rounded-xl transition-all duration-300",
        active
          ? "bg-clay-accent/10 scale-110"
          : "bg-transparent group-hover:bg-clay-accent/5 group-hover:scale-110"
      )}
    >
      <span className="[&>svg]:w-5 [&>svg]:h-5">{icon}</span>
    </div>
    <span className="font-bold text-base tracking-tight">{label}</span>
  </div>
);
