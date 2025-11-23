import { LucideIcon } from 'lucide-react';

interface StatCardProps {
    title: string;
    value: string | number;
    icon: LucideIcon;
    trend?: string;
    trendUp?: boolean;
    color: 'blue' | 'purple' | 'pink' | 'emerald';
    suggestion?: string;
}

export function StatCard({ title, value, icon: Icon, trend, trendUp, color, suggestion }: StatCardProps) {
    const colorStyles = {
        blue: 'bg-blue-50 text-blue-500',
        purple: 'bg-purple-50 text-purple-500',
        pink: 'bg-pink-50 text-pink-500',
        emerald: 'bg-emerald-50 text-emerald-500',
    };

    const trendStyles = trendUp ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600';

    return (
        <div className="bg-white/80 backdrop-blur-sm p-6 rounded-3xl shadow-sm border border-white/50 hover:-translate-y-1 transition-transform duration-300">
            <div className="flex justify-between items-start mb-4">
                <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${colorStyles[color]}`}>
                    <Icon className="w-6 h-6" />
                </div>
                {trend && (
                    <span className={`text-xs font-bold px-2 py-1 rounded-lg ${trendStyles}`}>
                        {trend}
                    </span>
                )}
            </div>
            <div className="text-3xl font-bold text-slate-800 mb-1">{value}</div>
            <div className="text-sm text-slate-500 font-medium">{title}</div>

            {suggestion && (
                <div className="mt-4 pt-4 border-t border-slate-100">
                    <div className="flex items-center gap-2 text-xs text-amber-600 bg-amber-50 p-2 rounded-lg">
                        <span className="font-bold">💡 AI:</span>
                        <span>{suggestion}</span>
                    </div>
                </div>
            )}
        </div>
    );
}
