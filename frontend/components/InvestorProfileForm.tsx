"use client";

import { useState } from 'react';

type UserProfile = {
    age: number;
    horizon: string;
    goal_dividends: boolean;
    assets: string[];
};

export default function InvestorProfileForm({ onComplete }: { onComplete: (data: any) => void }) {
    const [profile, setProfile] = useState<UserProfile>({
        age: 30,
        horizon: 'medium',
        goal_dividends: false,
        assets: ['VAS', 'VGS', 'IVV', 'BHP', 'CSL', 'CBA', 'NDQ']
    });
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            const res = await fetch('/api/recommend', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(profile),
            });
            const data = await res.json();
            onComplete(data);
        } catch (error) {
            console.error("Optimization failed", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-6 bg-slate-800 rounded-xl border border-slate-700 w-full shadow-xl">
            <h2 className="text-xl font-bold mb-4 text-white flex items-center gap-2">
                <span className="w-2 h-6 bg-blue-500 rounded-full"></span>
                Investor Profile
            </h2>
            <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                    <label className="block text-xs uppercase tracking-wider text-slate-400 font-semibold mb-1">Age</label>
                    <input
                        type="number"
                        value={profile.age}
                        onChange={e => setProfile({ ...profile, age: parseInt(e.target.value) })}
                        className="w-full bg-slate-900 border border-slate-600 focus:border-blue-500 outline-none rounded-md p-3 text-white transition-all"
                    />
                </div>

                <div>
                    <label className="block text-xs uppercase tracking-wider text-slate-400 font-semibold mb-1">Trading Horizon</label>
                    <div className="grid grid-cols-3 gap-2">
                        {['short', 'medium', 'long'].map((opt) => (
                            <button
                                key={opt}
                                type="button"
                                onClick={() => setProfile({ ...profile, horizon: opt })}
                                className={`p-2 text-sm rounded-md border ${profile.horizon === opt ? 'bg-blue-600 border-blue-500 text-white' : 'bg-slate-900 border-slate-700 text-slate-400 hover:border-slate-500'}`}
                            >
                                {opt.charAt(0).toUpperCase() + opt.slice(1)}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="flex items-center p-3 bg-slate-900 rounded-lg border border-slate-700">
                    <input
                        type="checkbox"
                        checked={profile.goal_dividends}
                        onChange={e => setProfile({ ...profile, goal_dividends: e.target.checked })}
                        className="w-5 h-5 text-blue-600 bg-slate-800 border-slate-600 rounded focus:ring-blue-500"
                    />
                    <label className="ml-3 text-sm text-slate-300 font-medium">Prioritize Dividends</label>
                </div>

                <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-bold py-3 px-4 rounded-lg transform transition active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-900/20"
                >
                    {loading ? 'Analyzing...' : 'Generate AI Strategy'}
                </button>
            </form>
        </div>
    );
}
