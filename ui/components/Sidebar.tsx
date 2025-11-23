"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Rocket, Users, FileText, Briefcase, Activity } from 'lucide-react';
import { clsx } from 'clsx';

const navItems = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Mission Control', href: '/mission-control', icon: Rocket },
    { name: 'Candidates', href: '/candidates', icon: Users },
    { name: 'Applications', href: '/applications', icon: FileText },
    { name: 'Jobs', href: '/jobs', icon: Briefcase },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="w-64 bg-white/90 backdrop-blur-xl border-r border-slate-200 h-screen flex flex-col fixed left-0 top-0 z-20 shadow-sm">
            <div className="p-8 flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-500 flex items-center justify-center text-white shadow-lg shadow-violet-500/30">
                    <Activity className="w-6 h-6" />
                </div>
                <span className="font-bold text-xl tracking-tight text-slate-800">
                    Hifadhi<span className="text-violet-500">.ai</span>
                </span>
            </div>

            <nav className="flex-1 px-4 space-y-2">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.name}
                            href={item.href}
                            className={clsx(
                                "flex items-center gap-3 px-4 py-3 rounded-xl transition-all group",
                                isActive
                                    ? "bg-violet-50 text-violet-600 font-medium"
                                    : "text-slate-600 hover:bg-slate-50 hover:text-violet-600"
                            )}
                        >
                            <item.icon className={clsx("w-5 h-5 transition-transform group-hover:scale-110", isActive && "text-violet-600")} />
                            <span>{item.name}</span>
                            {item.name === 'Mission Control' && (
                                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse ml-auto" />
                            )}
                        </Link>
                    );
                })}
            </nav>

            <div className="p-6">
                <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100">
                    <div className="flex items-center gap-3 mb-2">
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                        <span className="text-xs font-semibold text-violet-700 uppercase tracking-wider">System Status</span>
                    </div>
                    <p className="text-xs text-slate-600">AI Agents Online & Ready</p>
                </div>
            </div>
        </aside>
    );
}
