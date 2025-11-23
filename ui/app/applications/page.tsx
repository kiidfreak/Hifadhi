"use client";

import { useState, useEffect } from 'react';
import { fetchApplications } from '@/lib/api';
import { Modal } from '@/components/Modal';
import { clsx } from 'clsx';

export default function ApplicationsPage() {
    const [applications, setApplications] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedApp, setSelectedApp] = useState<any>(null);

    useEffect(() => {
        async function load() {
            try {
                const data = await fetchApplications();
                setApplications(data.applications);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        }
        load();
    }, []);

    const getStatusColor = (status: string) => {
        const map: Record<string, string> = {
            'New': 'bg-blue-50 text-blue-600',
            'Screening': 'bg-purple-50 text-purple-600',
            'Interview': 'bg-amber-50 text-amber-600',
            'Offer': 'bg-green-50 text-green-600',
            'Hired': 'bg-emerald-100 text-emerald-700',
            'Rejected': 'bg-red-50 text-red-600',
        };
        return map[status] || 'bg-slate-100 text-slate-600';
    };

    if (loading) return <div className="text-center py-10 text-slate-400">Loading Applications...</div>;

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <header>
                <h1 className="text-3xl font-bold text-slate-800">Applications</h1>
                <p className="text-slate-500">Track candidate progress</p>
            </header>

            <div className="bg-white rounded-3xl shadow-sm border border-slate-100 overflow-hidden">
                <table className="w-full">
                    <thead className="bg-slate-50 border-b border-slate-100">
                        <tr>
                            <th className="text-left p-4 font-semibold text-slate-600">Candidate</th>
                            <th className="text-left p-4 font-semibold text-slate-600">Job</th>
                            <th className="text-left p-4 font-semibold text-slate-600">Status</th>
                            <th className="text-left p-4 font-semibold text-slate-600">AI Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        {applications.length === 0 ? (
                            <tr>
                                <td colSpan={4} className="p-8 text-center text-slate-500">No applications found.</td>
                            </tr>
                        ) : (
                            applications.map((a, i) => (
                                <tr
                                    key={i}
                                    onClick={() => setSelectedApp(a)}
                                    className="border-b border-slate-50 hover:bg-violet-50 cursor-pointer transition-colors last:border-0"
                                >
                                    <td className="p-4 font-medium text-violet-600">
                                        {a.first_name} {a.last_name}
                                    </td>
                                    <td className="p-4 text-slate-600">{a.job_title}</td>
                                    <td className="p-4">
                                        <span className={clsx("px-3 py-1 rounded-full text-xs font-medium", getStatusColor(a.status))}>
                                            {a.status}
                                        </span>
                                    </td>
                                    <td className="p-4 font-bold text-violet-600">{a.ai_screening_score}%</td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            <Modal
                isOpen={!!selectedApp}
                onClose={() => setSelectedApp(null)}
                title="Application Details"
            >
                {selectedApp && (
                    <div className="space-y-6">
                        <div className="flex justify-between items-start">
                            <div>
                                <h2 className="text-2xl font-bold text-slate-800">{selectedApp.first_name} {selectedApp.last_name}</h2>
                                <p className="text-violet-600 font-medium">{selectedApp.job_title}</p>
                            </div>
                            <span className={clsx("px-4 py-2 rounded-full text-sm font-bold", getStatusColor(selectedApp.status))}>
                                {selectedApp.status}
                            </span>
                        </div>

                        <div className="bg-slate-50 p-6 rounded-2xl border border-slate-100">
                            <div className="flex justify-between items-center mb-4">
                                <h4 className="font-bold text-slate-700">AI Screening Score</h4>
                                <span className="text-2xl font-bold text-violet-600">{selectedApp.ai_screening_score}%</span>
                            </div>
                            <div className="w-full h-3 bg-slate-200 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-violet-500 rounded-full transition-all duration-1000"
                                    style={{ width: `${selectedApp.ai_screening_score}%` }}
                                ></div>
                            </div>
                            <p className="text-sm text-slate-500 mt-4 leading-relaxed">
                                AI Analysis: Candidate shows strong match for required skills. Experience level aligns with job requirements.
                            </p>
                        </div>
                    </div>
                )}
            </Modal>
        </div>
    );
}
