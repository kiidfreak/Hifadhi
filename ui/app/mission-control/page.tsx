"use client";

import { useState, useEffect, useRef } from 'react';
import { Rocket, Play, CheckCircle, Search, Calendar, ClipboardCheck, Info } from 'lucide-react';
import { fetchAgents, fetchEvents, startMission } from '@/lib/api';
import { clsx } from 'clsx';

export default function MissionControl() {
    const [mission, setMission] = useState('');
    const [agents, setAgents] = useState<any>({});
    const [events, setEvents] = useState<any[]>([]);
    const [missionResult, setMissionResult] = useState<any>(null);
    const logEndRef = useRef<HTMLDivElement>(null);

    // Poll for agents and events
    useEffect(() => {
        const interval = setInterval(async () => {
            try {
                const [agentsData, eventsData] = await Promise.all([fetchAgents(), fetchEvents()]);
                setAgents(agentsData);
                setEvents(eventsData.events.reverse()); // Newest first

                // Check for completion
                const lastEvent = eventsData.events[eventsData.events.length - 1];
                if (lastEvent && lastEvent.type === 'MISSION_COMPLETED') {
                    setMissionResult(lastEvent.payload);
                }
            } catch (e) {
                console.error("Polling error", e);
            }
        }, 1000);
        return () => clearInterval(interval);
    }, []);

    const handleStartMission = async () => {
        if (!mission) return;
        setMissionResult(null);
        try {
            await startMission(mission);
            setMission('');
        } catch (e) {
            alert('Failed to start mission');
        }
    };

    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <header>
                <h1 className="text-3xl font-bold text-slate-800">Mission Control</h1>
                <p className="text-slate-500">Orchestrate your AI workforce</p>
            </header>

            {/* Mission Input */}
            <div className="bg-gradient-to-br from-violet-600 to-indigo-600 rounded-3xl p-8 shadow-lg text-white relative overflow-hidden">
                <div className="absolute top-0 right-0 w-40 h-40 bg-white opacity-10 rounded-full -mr-20 -mt-20 blur-3xl"></div>
                <h3 className="text-2xl font-bold mb-2 relative z-10">🚀 Start a New Mission</h3>
                <p className="text-white/80 mb-6 relative z-10">Describe what you want the AI agents to accomplish</p>
                <div className="flex gap-3 relative z-10">
                    <input
                        type="text"
                        value={mission}
                        onChange={(e) => setMission(e.target.value)}
                        placeholder="e.g., Hire a Senior Python Developer in Nairobi"
                        className="flex-1 px-6 py-4 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/60 focus:outline-none focus:ring-2 focus:ring-white/50 text-lg"
                        onKeyDown={(e) => e.key === 'Enter' && handleStartMission()}
                    />
                    <button
                        onClick={handleStartMission}
                        className="px-8 py-4 bg-white text-violet-600 font-bold rounded-xl hover:bg-slate-100 transition-colors shadow-lg flex items-center gap-2"
                    >
                        <Play className="w-5 h-5 fill-current" /> Start
                    </button>
                </div>
            </div>

            {/* Agents Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {Object.entries(agents).map(([name, state]: [string, any]) => {
                    const isWorking = state.status === 'working';
                    return (
                        <div key={name} className={clsx(
                            "p-6 rounded-2xl border transition-all duration-300",
                            isWorking ? "bg-white border-violet-200 shadow-md scale-105" : "bg-slate-50 border-slate-100"
                        )}>
                            <div className="flex items-center gap-3 mb-3">
                                <div className="w-10 h-10 rounded-xl bg-violet-100 text-violet-600 flex items-center justify-center shadow-sm">
                                    <Rocket className="w-5 h-5" />
                                </div>
                                <div className="font-bold text-slate-700">{name}</div>
                            </div>
                            <div className={clsx(
                                "text-xs px-3 py-1.5 rounded-lg inline-block font-bold mb-2 uppercase",
                                state.status === 'idle' ? 'bg-green-100 text-green-700' :
                                    state.status === 'working' ? 'bg-amber-100 text-amber-700 animate-pulse' : 'bg-slate-200 text-slate-600'
                            )}>
                                {state.status}
                            </div>
                            <p className="text-xs text-slate-500 mt-3 leading-relaxed min-h-[3rem]">
                                {state.last_thought ? state.last_thought.slice(0, 200) + (state.last_thought.length > 200 ? '...' : '') : <span className="italic text-slate-400">Waiting for tasks...</span>}
                            </p>
                        </div>
                    );
                })}
            </div>

            {/* Mission Results */}
            {missionResult && (
                <div className="bg-white rounded-3xl shadow-lg p-8 border-l-4 border-green-500 animate-in slide-in-from-bottom-4">
                    <div className="flex justify-between items-start mb-6">
                        <div>
                            <h3 className="text-2xl font-bold text-slate-800 flex items-center gap-2">
                                Mission Accomplished! <span className="text-2xl">🎉</span>
                            </h3>
                            <p className="text-slate-600 mt-2 text-lg">{missionResult.summary}</p>
                        </div>
                        <button onClick={() => setMissionResult(null)} className="text-slate-400 hover:text-slate-600">
                            <span className="sr-only">Close</span>
                            ✕
                        </button>
                    </div>

                    <div className="bg-slate-50 rounded-xl p-6 mb-6">
                        <h4 className="text-sm font-bold text-slate-700 mb-4 uppercase tracking-wider">Actions Taken</h4>
                        <ul className="space-y-3">
                            {missionResult.actions_taken?.map((action: string, i: number) => (
                                <li key={i} className="flex items-center gap-3 text-slate-700">
                                    <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                                    {action}
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div className="flex flex-wrap gap-3">
                        {missionResult.next_steps?.map((step: any, i: number) => (
                            <button
                                key={i}
                                className="px-6 py-3 bg-white border border-slate-200 rounded-xl text-sm font-bold text-slate-700 hover:bg-violet-50 hover:text-violet-600 hover:border-violet-200 transition-all shadow-sm"
                                onClick={() => {
                                    if (step.action === 'start_screening') {
                                        startMission('Screen the candidates found');
                                        setMissionResult(null);
                                    }
                                }}
                            >
                                {step.label}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Activity Log */}
            <div className="bg-white/80 backdrop-blur-sm rounded-3xl shadow-sm p-6 border border-white/50">
                <h3 className="text-lg font-bold text-slate-800 mb-4">Mission Activity Log</h3>
                <div className="space-y-3 max-h-96 overflow-y-auto pr-2 custom-scrollbar">
                    {events.filter(e => ['CANDIDATE_FOUND', 'MISSION_COMPLETED', 'AGENT_ACTION', 'CANDIDATE_SCREENED'].includes(e.type)).map((e, i) => {
                        let icon = Info;
                        let color = 'border-blue-500';
                        let msg = '';

                        if (e.type === 'CANDIDATE_FOUND') {
                            msg = `Found candidate: ${e.payload.name}`;
                            icon = Search;
                        } else if (e.type === 'MISSION_COMPLETED') {
                            msg = `Mission Completed: ${e.payload.summary}`;
                            icon = CheckCircle;
                            color = 'border-green-500';
                        } else if (e.type === 'CANDIDATE_SCREENED') {
                            msg = `Screened: ${e.payload.decision} (${e.payload.score}%)`;
                            icon = ClipboardCheck;
                            color = 'border-purple-500';
                        } else {
                            msg = `Event: ${e.type}`;
                        }

                        const Icon = icon;

                        return (
                            <div key={i} className={`bg-slate-50 p-4 rounded-xl text-sm text-slate-700 border-l-4 ${color} hover:bg-slate-100 transition-colors`}>
                                <div className="flex items-center justify-between">
                                    <span className="flex items-center gap-2">
                                        <Icon className="w-4 h-4 text-slate-400" />
                                        {msg}
                                    </span>
                                    <span className="text-xs text-slate-400">{new Date(e.timestamp).toLocaleTimeString()}</span>
                                </div>
                            </div>
                        );
                    })}
                    {events.length === 0 && (
                        <p className="text-center text-slate-400 py-8 italic">No active missions. Start one above!</p>
                    )}
                </div>
            </div>
        </div>
    );
}
