"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { motion } from 'framer-motion';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export default function ChatInterface({ results }: { results: any }) {
    if (!results) return null;

    const { risk_profile, optimization } = results;
    const weights = optimization.weights || {};

    const chartData = Object.keys(weights).map((key, index) => ({
        name: key.replace('.AX', ''),
        value: parseFloat((weights[key] * 100).toFixed(1))
    })).filter(item => item.value > 0);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex-1 p-6 bg-slate-800 rounded-xl border border-slate-700 shadow-2xl h-full flex flex-col"
        >
            <div className="bg-slate-900/80 p-5 rounded-lg mb-6 border-l-4 border-emerald-500 backdrop-blur-sm">
                <div className="flex items-center gap-2 mb-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                    <p className="text-emerald-400 font-mono text-xs uppercase tracking-wide">AI Agent System</p>
                </div>
                <p className="text-slate-200 text-sm leading-relaxed">
                    I have analyzed market conditions and your profile. A
                    <span className="font-bold text-white mx-1 text-base underline decoration-blue-500 decoration-2 underline-offset-2">
                        {risk_profile.replace('_', ' ').toUpperCase()}
                    </span>
                    portfolio is optimal. This allocation targets a Sharpe Ratio of
                    <span className="text-emerald-400 font-bold ml-1">{optimization.performance?.sharpe_ratio?.toFixed(2)}</span>.
                </p>
            </div>

            <div className="flex-1 min-h-[300px] w-full relative">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={chartData}
                            cx="50%"
                            cy="50%"
                            innerRadius={80}
                            outerRadius={100}
                            fill="#8884d8"
                            paddingAngle={5}
                            dataKey="value"
                            startAngle={90}
                            endAngle={-270}
                        >
                            {chartData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="rgba(0,0,0,0)" />
                            ))}
                        </Pie>
                        <Tooltip
                            contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }}
                            itemStyle={{ color: '#e2e8f0' }}
                        />
                        <Legend verticalAlign="bottom" height={36} />
                    </PieChart>
                </ResponsiveContainer>

                {/* Center Text Overlay */}
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-[60%] text-center">
                    <p className="text-3xl font-bold text-white">{(optimization.performance?.expected_return * 100).toFixed(1)}%</p>
                    <p className="text-xs text-slate-400 uppercase tracking-widest">Return</p>
                </div>
            </div>

            <div className="mt-8 grid grid-cols-3 gap-4 text-center">
                <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-700/50">
                    <p className="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Expected Return</p>
                    <p className="font-bold text-emerald-400 text-lg">
                        {(optimization.performance?.expected_return * 100).toFixed(1)}%
                    </p>
                </div>
                <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-700/50">
                    <p className="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Risk (Vol)</p>
                    <p className="font-bold text-orange-400 text-lg">
                        {(optimization.performance?.volatility * 100).toFixed(1)}%
                    </p>
                </div>
                <div className="bg-slate-900/50 p-3 rounded-lg border border-slate-700/50">
                    <p className="text-[10px] uppercase tracking-widest text-slate-500 mb-1">Sharpe Ratio</p>
                    <p className="font-bold text-blue-400 text-lg">
                        {(optimization.performance?.sharpe_ratio).toFixed(2)}
                    </p>
                </div>
            </div>

            <div className="mt-8 pt-4 border-t border-slate-700/50">
                <button className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-4 px-6 rounded-xl flex items-center justify-center gap-2 transform transition hover:scale-[1.02] shadow-lg shadow-emerald-900/20 group">
                    <span className="group-hover:translate-x-1 transition-transform">Connect Superhero & Draft Trades ➞</span>
                </button>
                <p className="text-[10px] text-slate-500 mt-3 text-center opacity-60">
                    *General Advice Warning: This is a model only. The AI is a tool, not a human adviser. Read PDS.
                </p>
            </div>
        </motion.div>
    );
}
