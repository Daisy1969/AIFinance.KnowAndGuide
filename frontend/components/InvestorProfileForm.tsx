"use client";

import React, { useState, useRef } from 'react';
import { Link, Loader, CheckCircle, AlertCircle } from 'lucide-react';

type UserProfile = {
    age: number;
    horizon: string;
    goal_dividends: boolean;
    assets: string[];
    currency: 'AUD' | 'USD';
};
const getApiUrl = () => {
    // @ts-ignore
    if (typeof process !== 'undefined' && process.env.NEXT_PUBLIC_API_URL) {
        // @ts-ignore
        return process.env.NEXT_PUBLIC_API_URL;
    }
    // @ts-ignore
    if (typeof process !== 'undefined' && process.env.NODE_ENV === 'production') {
        return 'https://aifinance-backendbackend.onrender.com';
    }
    return 'http://localhost:5001';
};
export default function InvestorProfileForm({ onComplete }: { onComplete: (data: any) => void }) {
    const [profile, setProfile] = useState<UserProfile>({
        age: 30,
        horizon: 'medium',
        goal_dividends: false,
        assets: ['VAS', 'VGS', 'IVV', 'BHP', 'CSL', 'CBA', 'NDQ'],
        currency: 'AUD'
    });
    const [loading, setLoading] = useState(false);

    // Superhero Connection State
    const [connectionStatus, setConnectionStatus] = useState<'idle' | 'input' | 'connecting' | 'waiting_for_login' | 'connected' | 'error'>('idle');
    const [connectionMessage, setConnectionMessage] = useState('');
    const [creds, setCreds] = useState({ username: '', password: '' });
    const [showPassword, setShowPassword] = useState(false);
    const pollInterval = useRef<NodeJS.Timeout | null>(null);

    const startConnection = () => {
        setConnectionStatus('input');
        setConnectionMessage('');
    };

    const submitCredentials = async () => {
        setConnectionStatus('connecting');
        setConnectionMessage('Starting secure session...');
        try {
            const API_BASE = getApiUrl();
            const res = await fetch(`${API_BASE}/api/connect-superhero`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(creds)
            });
            const data = await res.json();

            if (res.ok) {
                setConnectionStatus('waiting_for_login');
                setConnectionMessage('Session started. secure login in progress...');
                // Start polling
                pollInterval.current = setInterval(checkLoginStatus, 2000);
            } else {
                setConnectionStatus('error');
                setConnectionMessage(data.error || 'Failed to start session');
            }
        } catch (error) {
            setConnectionStatus('error');
            setConnectionMessage('Connection failed. Backend may be offline.');
        }
    };

    const checkLoginStatus = async () => {
        try {
            const API_BASE = getApiUrl();
            const res = await fetch(`${API_BASE}/api/superhero-status`);
            const data = await res.json();

            if (data.logged_in) {
                if (pollInterval.current) clearInterval(pollInterval.current);
                setConnectionStatus('connected');
                setConnectionMessage('Successfully logged in! Fetching holdings...');
                fetchHoldings();
            } else {
                if (data.message && data.message.includes("MFA")) {
                    setConnectionMessage("MFA Required. (Auto-MFA not yet implemented, please retry without MFA or check logs)");
                } else {
                    setConnectionMessage(data.message || 'Logging in...');
                }
            }
        } catch (error) {
            console.error("Polling error", error);
        }
    };

    const fetchHoldings = async () => {
        try {
            const API_BASE = getApiUrl();
            const res = await fetch(`${API_BASE}/api/superhero-holdings`);
            const data = await res.json();

            if (res.ok && data.raw_text) {
                // In a real scenario, we'd parse specific tickers. 
                // For now, we'll confirm specific known tickers if found in the text
                // or just notify success.
                // This is a placeholder for the parsing logic response
                setConnectionMessage('Holdings synced from Superhero!');

                // Optional: Update assets based on findings (mock logic for now as scraper is generic)
                // setProfile(p => ({ ...p, assets: [...p.assets, 'NEWLY_FOUND_TICKER'] }));
            }
        } catch (error) {
            setConnectionMessage('Failed to fetch holdings after login.');
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        try {
            const API_BASE = getApiUrl();
            const res = await fetch(`${API_BASE}/api/recommend`, {
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

            {/* Superhero Connection Section */}
            <div className="mb-6 p-4 bg-slate-900/50 rounded-lg border border-slate-700">
                <div className="flex items-center justify-between mb-2">
                    <h3 className="text-sm font-semibold text-slate-300">Connect Portfolio</h3>
                    <span className="text-xs text-slate-500">Secure Browser Agent</span>
                </div>

                {connectionStatus === 'connected' ? (
                    <div className="flex items-center gap-2 text-green-400 p-2 bg-green-900/20 rounded">
                        <CheckCircle size={18} />
                        <span className="text-sm font-medium">Superhero Connected</span>
                    </div>
                ) : connectionStatus === 'input' ? (
                    <div className="space-y-3">
                        <input
                            type="text"
                            placeholder="Email"
                            className="w-full bg-slate-800 border-slate-600 rounded p-2 text-sm text-white"
                            value={creds.username}
                            onChange={e => setCreds({ ...creds, username: e.target.value })}
                        />
                        <div className="relative">
                            <input
                                type={showPassword ? "text" : "password"}
                                placeholder="Password"
                                className="w-full bg-slate-800 border-slate-600 rounded p-2 text-sm text-white pr-10"
                                value={creds.password}
                                onChange={e => setCreds({ ...creds, password: e.target.value })}
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute right-2 top-1/2 -translate-y-1/2 text-[10px] text-slate-400 hover:text-white uppercase font-bold tracking-wider"
                            >
                                {showPassword ? 'HIDE' : 'SHOW'}
                            </button>
                        </div>
                        <div className="flex gap-2">
                            <button onClick={submitCredentials} className="flex-1 bg-blue-600 hover:bg-blue-500 text-white text-xs py-2 rounded">
                                Login
                            </button>
                            <button onClick={() => setConnectionStatus('idle')} className="flex-1 bg-slate-700 hover:bg-slate-600 text-white text-xs py-2 rounded">
                                Cancel
                            </button>
                        </div>
                    </div>
                ) : (
                    <button
                        type="button"
                        onClick={startConnection}
                        disabled={connectionStatus === 'connecting' || connectionStatus === 'waiting_for_login'}
                        className="w-full flex items-center justify-center gap-2 bg-[#2C2C54] hover:bg-[#3D3D75] text-white py-2 px-4 rounded transition-colors border border-slate-600 disabled:opacity-50"
                    >
                        {connectionStatus === 'waiting_for_login' || connectionStatus === 'connecting' ? (
                            <Loader className="animate-spin" size={16} />
                        ) : (
                            <Link size={16} />
                        )}
                        {connectionStatus === 'waiting_for_login' ? 'Logging in...' : connectionStatus === 'connecting' ? 'Starting...' : 'Connect Superhero Account'}
                    </button>
                )}

                {/* Status Messages */}
                {connectionMessage && (
                    <div className={`mt-2 text-xs flex items-center gap-1.5 ${connectionStatus === 'error' ? 'text-red-400' :
                        connectionStatus === 'connected' ? 'text-green-400' : 'text-blue-400'
                        }`}>
                        {(connectionStatus === 'waiting_for_login' || connectionStatus === 'connecting') && <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                        </span>}
                        {connectionMessage}
                    </div>
                )}

                {/* Debug Info Toggle */}
                <div className="mt-3 pt-3 border-t border-slate-800">
                    <details className="group">
                        <summary className="text-[10px] text-slate-500 cursor-pointer hover:text-slate-300 list-none flex items-center gap-1">
                            <span>▶</span> Debug Info
                        </summary>
                        <div className="mt-2 text-[10px] font-mono text-slate-400 bg-black/40 p-2 rounded overflow-x-auto">
                            <p>Status: {connectionStatus}</p>
                            <p>Last Message: {connectionMessage}</p>
                            <p>API: {getApiUrl()}</p>
                            <div className="mt-2 border-t border-slate-700 pt-2">
                                <p className="mb-1 text-[10px] text-slate-500">Live Browser View:</p>
                                <img
                                    src={`${getApiUrl()}/api/debug-screenshot?t=${Date.now()}`}
                                    alt="Backend Browser State"
                                    className="w-full rounded border border-slate-700 opacity-80 hover:opacity-100 transition-opacity"
                                />
                            </div>
                    </details>
                </div>
            </div>

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

                <div className="p-3 bg-slate-900 rounded-lg border border-slate-700">
                    <label className="block text-xs uppercase tracking-wider text-slate-400 font-semibold mb-2">Primary Currency</label>
                    <div className="flex bg-slate-800 rounded p-1">
                        {['AUD', 'USD'].map((curr) => (
                            <button
                                key={curr}
                                type="button"
                                onClick={() => setProfile({ ...profile, currency: curr as 'AUD' | 'USD' })}
                                className={`flex-1 py-1.5 text-sm font-medium rounded transition-all ${profile.currency === curr
                                    ? 'bg-blue-600 text-white shadow-lg'
                                    : 'text-slate-400 hover:text-white'
                                    }`}
                            >
                                {curr}
                            </button>
                        ))}
                    </div>
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
