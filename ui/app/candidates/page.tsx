"use client";

import { useState, useEffect } from 'react';
import { fetchCandidates } from '@/lib/api';
import { Modal } from '@/components/Modal';
import { Mail, Briefcase, GraduationCap, Code } from 'lucide-react';

export default function CandidatesPage() {
    const [candidates, setCandidates] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedCandidate, setSelectedCandidate] = useState<any>(null);

    useEffect(() => {
        async function load() {
            try {
                const data = await fetchCandidates();
                setCandidates(data.candidates);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        }
        load();
    }, []);

    if (loading) return <div className="text-center py-10 text-slate-400">Loading Candidates...</div>;

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <header>
                <h1 className="text-3xl font-bold text-slate-800">Candidates</h1>
                <p className="text-slate-500">Manage your talent pool</p>
            </header>

            <div className="bg-white rounded-3xl shadow-sm border border-slate-100 overflow-hidden">
                <table className="w-full">
                    <thead className="bg-slate-50 border-b border-slate-100">
                        <tr>
                            <th className="text-left p-4 font-semibold text-slate-600">Name</th>
                            <th className="text-left p-4 font-semibold text-slate-600">Email</th>
                            <th className="text-left p-4 font-semibold text-slate-600">Experience</th>
                            <th className="text-left p-4 font-semibold text-slate-600">Education</th>
                        </tr>
                    </thead>
                    <tbody>
                        {candidates.length === 0 ? (
                            <tr>
                                <td colSpan={4} className="p-8 text-center text-slate-500">No candidates found.</td>
                            </tr>
                        ) : (
                            candidates.map((c, i) => (
                                <tr
                                    key={i}
                                    onClick={() => setSelectedCandidate(c)}
                                    className="border-b border-slate-50 hover:bg-violet-50 cursor-pointer transition-colors last:border-0"
                                >
                                    <td className="p-4 font-medium text-violet-600 flex items-center gap-3">
                                        <div className="w-8 h-8 rounded-full bg-violet-100 flex items-center justify-center text-xs font-bold">
                                            {c.first_name[0]}{c.last_name[0]}
                                        </div>
                                        {c.first_name} {c.last_name}
                                    </td>
                                    <td className="p-4 text-slate-600">{c.email}</td>
                                    <td className="p-4 text-slate-600">{c.years_experience} yrs</td>
                                    <td className="p-4 text-slate-600">{c.education}</td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            <Modal
                isOpen={!!selectedCandidate}
                onClose={() => setSelectedCandidate(null)}
                title="Candidate Details"
            >
                {selectedCandidate && (
                    <div className="space-y-6">
                        <div className="flex items-center gap-6">
                            <div className="w-20 h-20 rounded-full bg-violet-100 text-violet-600 flex items-center justify-center text-2xl font-bold">
                                {selectedCandidate.first_name[0]}{selectedCandidate.last_name[0]}
                            </div>
                            <div>
                                <h2 className="text-2xl font-bold text-slate-800">{selectedCandidate.first_name} {selectedCandidate.last_name}</h2>
                                <p className="text-slate-500 flex items-center gap-2">
                                    <Mail className="w-4 h-4" /> {selectedCandidate.email}
                                </p>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-6">
                            <div className="bg-slate-50 p-4 rounded-xl">
                                <div className="text-xs font-bold text-slate-400 uppercase mb-1 flex items-center gap-2">
                                    <Briefcase className="w-3 h-3" /> Experience
                                </div>
                                <div className="font-semibold text-slate-800">{selectedCandidate.years_experience} Years</div>
                            </div>
                            <div className="bg-slate-50 p-4 rounded-xl">
                                <div className="text-xs font-bold text-slate-400 uppercase mb-1 flex items-center gap-2">
                                    <GraduationCap className="w-3 h-3" /> Education
                                </div>
                                <div className="font-semibold text-slate-800">{selectedCandidate.education}</div>
                            </div>
                            <div className="col-span-2 bg-slate-50 p-4 rounded-xl">
                                <div className="text-xs font-bold text-slate-400 uppercase mb-1 flex items-center gap-2">
                                    <Code className="w-3 h-3" /> Skills
                                </div>
                                <div className="flex flex-wrap gap-2 mt-2">
                                    {selectedCandidate.skills?.map((s: string) => (
                                        <span key={s} className="px-3 py-1 bg-white border border-slate-200 rounded-full text-sm text-slate-600">
                                            {s}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </Modal>
        </div>
    );
}
