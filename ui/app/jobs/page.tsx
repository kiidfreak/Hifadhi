"use client";

import { useState, useEffect } from 'react';
import { fetchJobs } from '@/lib/api';
import { Modal } from '@/components/Modal';
import { MapPin, Building, Share2, Users, CheckCircle, AlertCircle } from 'lucide-react';

export default function JobsPage() {
    const [jobs, setJobs] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedJob, setSelectedJob] = useState<any>(null);

    useEffect(() => {
        async function load() {
            try {
                const data = await fetchJobs();
                setJobs(data.jobs);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        }
        load();
    }, []);

    const handleShare = () => {
        if (!selectedJob) return;
        const link = `https://hifadhi.ai/jobs/${selectedJob.job_id}`;
        navigator.clipboard.writeText(link);
        alert('Link copied to clipboard!');
    };

    if (loading) return <div className="text-center py-10 text-slate-400">Loading Jobs...</div>;

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            <header>
                <h1 className="text-3xl font-bold text-slate-800">Jobs</h1>
                <p className="text-slate-500">Open positions</p>
            </header>

            <div className="bg-white rounded-3xl shadow-sm border border-slate-100 overflow-hidden">
                <table className="w-full">
                    <thead className="bg-slate-50 border-b border-slate-100">
                        <tr>
                            <th className="text-left p-4 font-semibold text-slate-600">Title</th>
                            <th className="text-left p-4 font-semibold text-slate-600">Department</th>
                            <th className="text-left p-4 font-semibold text-slate-600">Location</th>
                            <th className="text-left p-4 font-semibold text-slate-600">Applicants</th>
                        </tr>
                    </thead>
                    <tbody>
                        {jobs.length === 0 ? (
                            <tr>
                                <td colSpan={4} className="p-8 text-center text-slate-500">No jobs found.</td>
                            </tr>
                        ) : (
                            jobs.map((j, i) => (
                                <tr
                                    key={i}
                                    onClick={() => setSelectedJob(j)}
                                    className="border-b border-slate-50 hover:bg-violet-50 cursor-pointer transition-colors last:border-0"
                                >
                                    <td className="p-4 font-medium text-violet-600">{j.title}</td>
                                    <td className="p-4 text-slate-600">{j.department}</td>
                                    <td className="p-4 text-slate-600">{j.location}</td>
                                    <td className="p-4 text-slate-600">{j.application_count}</td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            <Modal
                isOpen={!!selectedJob}
                onClose={() => setSelectedJob(null)}
                title="Job Details"
            >
                {selectedJob && (
                    <div className="space-y-6">
                        <div>
                            <h2 className="text-2xl font-bold text-slate-800 mb-2">{selectedJob.title}</h2>
                            <div className="flex gap-4 text-sm text-slate-500">
                                <span className="flex items-center gap-1"><Building className="w-4 h-4" /> {selectedJob.department}</span>
                                <span className="flex items-center gap-1"><MapPin className="w-4 h-4" /> {selectedJob.location}</span>
                            </div>
                        </div>

                        <div className="grid grid-cols-3 gap-4">
                            <div className="bg-blue-50 p-4 rounded-xl text-center">
                                <div className="text-2xl font-bold text-blue-600 flex justify-center items-center gap-2">
                                    <Users className="w-5 h-5" /> {selectedJob.application_count}
                                </div>
                                <div className="text-xs text-blue-400 font-bold uppercase mt-1">Applicants</div>
                            </div>
                            <div className="bg-green-50 p-4 rounded-xl text-center">
                                <div className="text-2xl font-bold text-green-600 flex justify-center items-center gap-2">
                                    <CheckCircle className="w-5 h-5" /> Active
                                </div>
                                <div className="text-xs text-green-400 font-bold uppercase mt-1">Status</div>
                            </div>
                            <div className="bg-purple-50 p-4 rounded-xl text-center">
                                <div className="text-2xl font-bold text-purple-600 flex justify-center items-center gap-2">
                                    <AlertCircle className="w-5 h-5" /> High
                                </div>
                                <div className="text-xs text-purple-400 font-bold uppercase mt-1">Priority</div>
                            </div>
                        </div>

                        <div className="bg-slate-50 p-4 rounded-xl">
                            <h4 className="font-bold text-slate-700 mb-2">Description</h4>
                            <p className="text-slate-600 text-sm leading-relaxed">
                                We are looking for a talented {selectedJob.title} to join our {selectedJob.department} team in {selectedJob.location}.
                                The ideal candidate will have experience in relevant technologies and a passion for innovation.
                            </p>
                        </div>

                        <div className="flex justify-end pt-4 border-t border-slate-100">
                            <button
                                onClick={handleShare}
                                className="px-6 py-3 bg-violet-600 text-white font-bold rounded-xl hover:bg-violet-700 transition-colors flex items-center gap-2 shadow-lg hover:shadow-violet-500/30"
                            >
                                <Share2 className="w-4 h-4" /> Share Hifadhi Link
                            </button>
                        </div>
                    </div>
                )}
            </Modal>
        </div>
    );
}
