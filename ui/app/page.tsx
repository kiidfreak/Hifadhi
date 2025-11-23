"use client";

import { useEffect, useState } from 'react';
import { Users, FileText, CalendarCheck, CheckCircle, Rocket, UserPlus } from 'lucide-react';
import { StatCard } from '@/components/StatCard';
import { fetchDashboardData } from '@/lib/api';
import Link from 'next/link';

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const data = await fetchDashboardData();
        setStats(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const getSuggestion = (type: string, val: number) => {
    const msgs: Record<string, string> = {
      candidates: val > 50 ? "Great talent pool! Use AI to screen top 10%." : "Low candidate count. Boost job posts.",
      applications: val > 20 ? "High volume. Enable auto-screening." : "Check job descriptions to attract more applicants.",
      interviews: val > 5 ? "Busy week! Ensure interviewers are prepped." : "Schedule more screenings to fill pipeline.",
      hires: val > 2 ? "On track with hiring goals! 🎉" : "Focus on closing candidates in offer stage."
    };
    return msgs[type];
  };

  if (loading) return <div className="flex items-center justify-center h-full text-slate-400">Loading Dashboard...</div>;

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <header className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-800">Dashboard</h1>
          <p className="text-slate-500">Welcome back, Admin</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right hidden sm:block">
            <div className="text-sm font-bold text-slate-800">Admin User</div>
            <div className="text-xs text-slate-500">HR Manager</div>
          </div>
          <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-400 to-cyan-300 shadow-md border-2 border-white"></div>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Link href="/candidates" className="block">
          <StatCard
            title="Total Candidates"
            value={stats?.total_candidates || 0}
            icon={Users}
            color="blue"
            trend="+12%"
            trendUp={true}
            suggestion={getSuggestion('candidates', stats?.total_candidates || 0)}
          />
        </Link>
        <Link href="/applications" className="block">
          <StatCard
            title="Active Applications"
            value={stats?.active_applications || 0}
            icon={FileText}
            color="purple"
            trend="Active"
            trendUp={true}
            suggestion={getSuggestion('applications', stats?.active_applications || 0)}
          />
        </Link>
        <Link href="/mission-control" className="block">
          <StatCard
            title="Interviews Set"
            value={stats?.interviews_scheduled || 0}
            icon={CalendarCheck}
            color="pink"
            suggestion={getSuggestion('interviews', stats?.interviews_scheduled || 0)}
          />
        </Link>
        <Link href="/applications" className="block">
          <StatCard
            title="Hired This Month"
            value={stats?.hired_this_month || 0}
            icon={CheckCircle}
            color="emerald"
            suggestion={getSuggestion('hires', stats?.hired_this_month || 0)}
          />
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white/80 backdrop-blur-sm rounded-3xl p-6 shadow-sm border border-white/50">
          <h3 className="text-lg font-bold text-slate-800 mb-4">Recent Activity</h3>
          <div className="text-slate-400 text-center py-8 italic">
            Activity feed coming soon...
          </div>
        </div>

        <div className="bg-gradient-to-br from-violet-600 to-indigo-600 rounded-3xl p-6 shadow-lg text-white relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-white opacity-10 rounded-full -mr-10 -mt-10 blur-2xl"></div>
          <div className="absolute bottom-0 left-0 w-24 h-24 bg-fuchsia-500 opacity-20 rounded-full -ml-10 -mb-10 blur-xl"></div>

          <h3 className="text-lg font-bold mb-2 relative z-10">Quick Actions</h3>
          <p className="text-white/80 text-sm mb-6 relative z-10">Use AI agents to speed up your workflow.</p>

          <div className="space-y-3 relative z-10">
            <Link href="/mission-control" className="block w-full py-3 px-4 bg-white/20 hover:bg-white/30 backdrop-blur-md rounded-xl flex items-center gap-3 transition-all border border-white/10">
              <Rocket className="w-5 h-5" />
              Launch Mission
            </Link>
            <Link href="/candidates" className="block w-full py-3 px-4 bg-white/20 hover:bg-white/30 backdrop-blur-md rounded-xl flex items-center gap-3 transition-all border border-white/10">
              <UserPlus className="w-5 h-5" />
              View Candidates
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
