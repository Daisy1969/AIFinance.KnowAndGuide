"use client";

import { useState } from "react";
import InvestorProfileForm from "@/components/InvestorProfileForm";
import ChatInterface from "@/components/ChatInterface";

export default function Home() {
    const [results, setResults] = useState(null);

    return (
        <main className="flex min-h-screen flex-col items-center p-6 lg:p-12 bg-slate-900 text-white selection:bg-blue-500/30">
            {/* Navbar-ish Header */}
            <div className="w-full max-w-7xl flex justify-between items-center mb-16 opacity-80">
                <div className="text-sm font-mono text-slate-400 border border-slate-800 px-3 py-1 rounded-full bg-slate-800/50">
                    System Status: <span className="text-emerald-500">Active</span>
                </div>
                <div className="text-sm font-mono text-slate-500">
                    v1.0.4 AGENTIC
                </div>
            </div>

            <div className="flex flex-col items-center mb-16 text-center space-y-4">
                <h1 className="text-5xl lg:text-7xl font-extrabold tracking-tight">
                    <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-indigo-500 to-emerald-500 animate-gradient-x">
                        AIFinance.KnowAndGuide
                    </span>
                </h1>
                <p className="text-lg text-slate-400 max-w-2xl font-light">
                    Autonomous Financial Intelligence. Connect, Strategize, and Execute.
                </p>
            </div>

            <div className="flex flex-col lg:flex-row w-full max-w-7xl gap-8 lg:h-[700px]">
                {/* Left Col: Inputs */}
                <div className="w-full lg:w-1/3 flex flex-col gap-6">
                    <InvestorProfileForm onComplete={setResults} />

                    {/* Info Block */}
                    <div className="p-6 bg-slate-800/50 border border-slate-700/50 rounded-xl">
                        <h3 className="text-sm font-bold text-slate-300 mb-2">How it works</h3>
                        <ul className="text-xs text-slate-400 space-y-2 list-disc pl-4">
                            <li>AI scans market data via Yahoo Finance & Scrapers.</li>
                            <li>Optimizes using Modern Portfolio Theory (MVO).</li>
                            <li>Connects to Superhero via Client-Side Agent.</li>
                            <li>You retain full control of execution.</li>
                        </ul>
                    </div>
                </div>

                {/* Right Col: Output */}
                <div className="w-full lg:w-2/3 h-full">
                    {results ? (
                        <ChatInterface results={results} />
                    ) : (
                        <div className="h-full min-h-[400px] flex flex-col items-center justify-center border-2 border-dashed border-slate-800 rounded-xl bg-slate-900/30 text-slate-500 transition-all">
                            <div className="w-16 h-16 mb-4 rounded-full bg-slate-800 flex items-center justify-center text-3xl">🤖</div>
                            <p className="font-mono text-sm">Awaiting Investment Profile...</p>
                        </div>
                    )}
                </div>
            </div>
        </main>
    );
}
