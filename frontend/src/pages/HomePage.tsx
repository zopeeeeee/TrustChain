import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { ArrowRight, ShieldCheck, FileVideo, Cpu } from "lucide-react";
import { getStats } from "../lib/api";
import type { StatsResponse } from "../lib/api";

export default function HomePage() {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getStats()
      .then((data) => {
        setStats(data);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  const statValue = (value: number | undefined) => {
    if (loading || value === undefined) return "--";
    return value;
  };

  return (
    <div className="min-h-[calc(100vh-73px)] flex items-center justify-center p-6 md:p-12 overflow-hidden">
      {/* Background radial gradient to give it a subtle premium feel without being distracting */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(0,0,0,0.03),transparent_50%)] pointer-events-none" />

      <div className="max-w-7xl w-full grid grid-cols-1 lg:grid-cols-2 gap-16 lg:gap-24 items-center relative z-10">

        {/* Left Side: Massive Typography Hero */}
        <div className="flex flex-col items-start text-left max-w-2xl fade-in-up">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-100 border border-zinc-200 text-xs font-medium text-zinc-600 mb-8">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            Dual-Stream Engine Online
          </div>

          <h1 className="text-5xl md:text-7xl font-bold tracking-tighter text-zinc-900 leading-[1.05] mb-6">
            Truth is now
            <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-zinc-800 to-zinc-500">
              verifiable.
            </span>
          </h1>

          <p className="text-lg md:text-xl text-zinc-500 max-w-lg mb-10 leading-relaxed font-light">
            Advanced dual-stream deepfake detection. We analyze visual anomalies and audio discordance, backed by immutable blockchain proof.
          </p>

          {/* Minimalist CTAs */}
          <div className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto delay-100 fade-in-up">
            <Link
              to="/upload"
              className="group inline-flex items-center justify-center gap-2 rounded-full bg-zinc-900 px-8 py-4 text-sm font-medium text-white transition-all shadow-xl shadow-zinc-900/10 hover:shadow-zinc-900/20 hover-scale outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-zinc-900"
            >
              Start Analysis
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>
        </div>

        {/* Right Side: Narrative / Abstract Visual Element */}
        <div className="relative w-full aspect-[4/3] sm:aspect-square lg:aspect-[4/5] perspective-1000 delay-200 fade-in-up">
          {/* Main decorative card representing the AI engine */}
          <div className="absolute inset-4 md:inset-8 bg-white border border-zinc-200/60 rounded-[2rem] shadow-2xl shadow-zinc-200/50 p-8 flex flex-col justify-between overflow-hidden group">

            <div className="relative z-10 flex justify-between items-start">
              <ShieldCheck className="w-10 h-10 text-zinc-800" strokeWidth={1.5} />
              <div className="text-right">
                <p className="text-xs uppercase tracking-widest text-zinc-400 font-semibold mb-1">
                  System Status
                </p>
                <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-zinc-50 border border-zinc-100">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-zinc-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-zinc-500"></span>
                  </span>
                  <span className="text-xs font-mono text-zinc-500">Active</span>
                </div>
              </div>
            </div>

            {/* Simulated Live Processing Stack */}
            <div className="relative z-10 space-y-4 my-auto">
              <div className="w-full bg-zinc-50 rounded-xl border border-zinc-100 p-4 transition-all duration-500 group-hover:border-zinc-300 group-hover:shadow-sm">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-white rounded-lg border border-zinc-100 shadow-sm">
                    <FileVideo className="w-5 h-5 text-zinc-600" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-zinc-900">Spatial Anomalies</h3>
                    <p className="text-xs text-zinc-500 font-mono">ResNet-50 Feature Extractor</p>
                  </div>
                </div>
              </div>

              <div className="w-full bg-zinc-50 rounded-xl border border-zinc-100 p-4 transition-all duration-500 delay-75 group-hover:border-zinc-300 group-hover:shadow-sm transform translate-x-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-white rounded-lg border border-zinc-100 shadow-sm">
                    <Cpu className="w-5 h-5 text-zinc-600" />
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-zinc-900">Temporal Inconsistencies</h3>
                    <p className="text-xs text-zinc-500 font-mono">LSTM Sequence Analysis</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Global Stats Footer inside the card */}
            <div className="relative z-10 border-t border-zinc-100 pt-6 mt-6 pb-2">
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <p className="text-xs text-zinc-400 font-medium tracking-wide">Analyses</p>
                  <p className="text-xl font-semibold text-zinc-900 tabular-nums tracking-tight">
                    {statValue(stats?.total)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-zinc-400 font-medium tracking-wide">Real</p>
                  <p className="text-xl font-semibold text-zinc-900 tabular-nums tracking-tight">
                    {statValue(stats?.real)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-zinc-400 font-medium tracking-wide">Fake</p>
                  <p className="text-xl font-semibold text-zinc-900 tabular-nums tracking-tight">
                    {statValue(stats?.fake)}
                  </p>
                </div>
              </div>
            </div>

            {/* Abstract ambient backdrop to the card */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-zinc-100 rounded-full blur-3xl -mr-32 -mt-32 opacity-50 pointer-events-none transition-opacity duration-700 group-hover:opacity-80" />
          </div>
        </div>

      </div>
    </div>
  );
}
