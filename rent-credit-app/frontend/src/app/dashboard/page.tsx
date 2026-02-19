"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Users,
  DollarSign,
  TrendingUp,
  Building2,
  ArrowRight,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import { residentsApi, propertiesApi } from "@/lib/api";
import { formatCents } from "@/lib/utils";

interface Summary {
  total_enrolled: number;
  total_active: number;
  total_opted_out: number;
  total_trial: number;
  monthly_revenue_cents: number;
  monthly_pm_payout_cents: number;
}

export default function DashboardPage() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [properties, setProperties] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([residentsApi.getSummary(), propertiesApi.list()])
      .then(([s, p]) => {
        setSummary(s.data);
        setProperties(p.data);
      })
      .finally(() => setLoading(false));
  }, []);

  const annualPayout = (summary?.monthly_pm_payout_cents || 0) * 12;

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">Your rent credit reporting overview</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        {[
          {
            label: "Active Residents",
            value: loading ? "-" : summary?.total_active,
            sub: `${summary?.total_trial || 0} in trial`,
            icon: Users,
            color: "text-brand-600",
            bg: "bg-brand-50",
          },
          {
            label: "Monthly Revenue",
            value: loading ? "-" : formatCents(summary?.monthly_revenue_cents || 0),
            sub: "from resident fees",
            icon: DollarSign,
            color: "text-green-600",
            bg: "bg-green-50",
          },
          {
            label: "Your Monthly Payout",
            value: loading ? "-" : formatCents(summary?.monthly_pm_payout_cents || 0),
            sub: "$3.00 per enrolled resident",
            icon: TrendingUp,
            color: "text-purple-600",
            bg: "bg-purple-50",
          },
          {
            label: "Properties",
            value: loading ? "-" : properties.length,
            sub: "enrolled in RentReport",
            icon: Building2,
            color: "text-orange-600",
            bg: "bg-orange-50",
          },
        ].map((kpi) => (
          <div key={kpi.label} className="card">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-500">{kpi.label}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{kpi.value}</p>
                <p className="text-xs text-gray-400 mt-1">{kpi.sub}</p>
              </div>
              <div className={`${kpi.bg} p-2.5 rounded-lg`}>
                <kpi.icon className={`h-5 w-5 ${kpi.color}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Annual Projection */}
      {summary && summary.monthly_pm_payout_cents > 0 && (
        <div className="bg-gradient-to-r from-brand-600 to-brand-700 rounded-xl p-6 text-white mb-8">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-brand-200 text-sm font-medium">Projected Annual Revenue Share</p>
              <p className="text-3xl font-bold mt-1">{formatCents(annualPayout)}</p>
              <p className="text-brand-200 text-sm mt-1">
                Based on {summary.total_active} active residents × $3.00/month × 12 months
              </p>
            </div>
            <TrendingUp className="h-16 w-16 text-brand-300 opacity-50" />
          </div>
        </div>
      )}

      {/* Setup Checklist */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-4">Setup Checklist</h3>
          <div className="space-y-3">
            {[
              { label: "Create account", done: true },
              { label: "Add your first property", done: properties.length > 0 },
              { label: "Connect PMS integration", done: false },
              { label: "Connect Stripe for payouts", done: false },
            ].map((item) => (
              <div key={item.label} className="flex items-center gap-3">
                {item.done ? (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                ) : (
                  <AlertCircle className="h-5 w-5 text-gray-300" />
                )}
                <span className={`text-sm ${item.done ? "text-gray-900" : "text-gray-500"}`}>
                  {item.label}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h3 className="font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            {[
              { label: "Add a property", href: "/dashboard/properties" },
              { label: "Connect your PMS", href: "/dashboard/settings" },
              { label: "Set up Stripe payouts", href: "/dashboard/settings" },
              { label: "View residents", href: "/dashboard/residents" },
            ].map((action) => (
              <Link
                key={action.label}
                href={action.href}
                className="flex items-center justify-between p-3 rounded-lg border border-gray-100 hover:border-brand-200 hover:bg-brand-50 transition-colors group"
              >
                <span className="text-sm font-medium text-gray-700 group-hover:text-brand-700">
                  {action.label}
                </span>
                <ArrowRight className="h-4 w-4 text-gray-400 group-hover:text-brand-600" />
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
