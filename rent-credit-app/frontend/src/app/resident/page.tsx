"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import {
  CheckCircle,
  Clock,
  TrendingUp,
  AlertTriangle,
  X,
  DollarSign,
  Calendar,
} from "lucide-react";
import { residentsApi } from "@/lib/api";
import { formatDate, formatCents, getStatusColor } from "@/lib/utils";

interface Resident {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  unit_number: string;
  lease_start_date: string;
  monthly_rent_cents: number;
  enrollment_status: string;
  enrollment_date: string | null;
  trial_end_date: string | null;
  retroactive_reporting_consent: boolean;
  retroactive_months_requested: number;
}

const STATUS_ICON: Record<string, React.ElementType> = {
  active: CheckCircle,
  trial: Clock,
  pending: Clock,
  opted_out: X,
  payment_failed: AlertTriangle,
};

const STATUS_LABEL: Record<string, string> = {
  active: "Actively Reporting",
  trial: "Free Trial",
  pending: "Enrollment Pending",
  opted_out: "Not Enrolled",
  payment_failed: "Payment Issue",
};

export default function ResidentDashboard() {
  const [resident, setResident] = useState<Resident | null>(null);
  const [loading, setLoading] = useState(true);
  const [showOptOut, setShowOptOut] = useState(false);
  const [optOutLoading, setOptOutLoading] = useState(false);

  useEffect(() => {
    residentsApi.getMe().then((r) => setResident(r.data)).finally(() => setLoading(false));
  }, []);

  const handleOptOut = async () => {
    setOptOutLoading(true);
    try {
      await residentsApi.optOut("resident_requested");
      setResident((r) => r ? { ...r, enrollment_status: "opted_out" } : r);
      setShowOptOut(false);
    } finally {
      setOptOutLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-20 text-gray-400">Loading your dashboard...</div>;
  }

  if (!resident) {
    return (
      <div className="text-center py-20">
        <p className="text-gray-500">Please sign in to view your dashboard.</p>
        <Link href="/auth/login" className="btn-primary mt-4 inline-flex">Sign In</Link>
      </div>
    );
  }

  const StatusIcon = STATUS_ICON[resident.enrollment_status] || Clock;
  const isActive = ["active", "trial"].includes(resident.enrollment_status);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome, {resident.first_name}
        </h1>
        <p className="text-gray-500 mt-1">Your rent credit reporting dashboard</p>
      </div>

      {/* Status Card */}
      <div className={`rounded-2xl p-6 mb-6 ${
        isActive ? "bg-gradient-to-r from-brand-600 to-brand-700 text-white" :
        resident.enrollment_status === "opted_out" ? "bg-gray-100 text-gray-700" :
        "bg-amber-50 border border-amber-200 text-amber-900"
      }`}>
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <StatusIcon className="h-5 w-5" />
              <span className="font-semibold text-lg">
                {STATUS_LABEL[resident.enrollment_status] || resident.enrollment_status}
              </span>
            </div>
            {resident.enrollment_status === "trial" && resident.trial_end_date && (
              <p className={`text-sm ${isActive ? "text-brand-200" : "text-amber-700"}`}>
                Free trial ends {formatDate(resident.trial_end_date)}. After that, $8.95/month billed with rent.
              </p>
            )}
            {resident.enrollment_status === "active" && (
              <p className="text-brand-200 text-sm">
                Your on-time rent payments are being reported to Experian, Equifax, and TransUnion.
              </p>
            )}
            {resident.enrollment_status === "opted_out" && (
              <p className="text-sm">You are not currently enrolled in rent credit reporting.</p>
            )}
          </div>
          {isActive && (
            <div className="bg-white/20 rounded-xl px-4 py-2 text-center">
              <div className="text-2xl font-bold">3</div>
              <div className="text-xs text-brand-200">Bureaus</div>
            </div>
          )}
        </div>
      </div>

      {/* Info Grid */}
      <div className="grid md:grid-cols-3 gap-5 mb-6">
        <div className="card">
          <div className="flex items-center gap-2 text-gray-500 text-sm mb-2">
            <DollarSign className="h-4 w-4" />
            Monthly Rent
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {formatCents(resident.monthly_rent_cents)}
          </div>
          <div className="text-xs text-gray-400 mt-1">Unit {resident.unit_number || "—"}</div>
        </div>

        <div className="card">
          <div className="flex items-center gap-2 text-gray-500 text-sm mb-2">
            <Calendar className="h-4 w-4" />
            Lease Start
          </div>
          <div className="text-lg font-bold text-gray-900">
            {formatDate(resident.lease_start_date)}
          </div>
          {resident.enrollment_date && (
            <div className="text-xs text-gray-400 mt-1">
              Enrolled {formatDate(resident.enrollment_date)}
            </div>
          )}
        </div>

        <div className="card">
          <div className="flex items-center gap-2 text-gray-500 text-sm mb-2">
            <TrendingUp className="h-4 w-4" />
            Service Fee
          </div>
          <div className="text-2xl font-bold text-gray-900">$8.95/mo</div>
          <div className="text-xs text-gray-400 mt-1">
            {resident.enrollment_status === "trial" ? "Free during trial" : "Billed with rent"}
          </div>
        </div>
      </div>

      {/* Retroactive Reporting */}
      {isActive && !resident.retroactive_reporting_consent && (
        <div className="card mb-6 border-l-4 border-brand-500">
          <h3 className="font-semibold text-gray-900 mb-2">
            Claim Up to 24 Months of Back-Reporting — Free
          </h3>
          <p className="text-gray-600 text-sm mb-4">
            Get credit for rent you&apos;ve already paid on time! We can report up to 24 months
            of past on-time rent payments from your current property to the credit bureaus.
          </p>
          <button className="btn-primary text-sm px-5 py-2.5">
            Request Back-Reporting
          </button>
        </div>
      )}

      {/* Links */}
      <div className="flex items-center justify-between">
        <Link href="/resident/history" className="text-brand-600 text-sm font-medium hover:underline">
          View full payment history →
        </Link>
        {isActive && (
          <button
            onClick={() => setShowOptOut(true)}
            className="text-sm text-gray-400 hover:text-red-500 transition-colors"
          >
            Cancel enrollment
          </button>
        )}
      </div>

      {/* Opt-Out Modal */}
      {showOptOut && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl p-8 max-w-md w-full shadow-xl">
            <h2 className="text-xl font-bold text-gray-900 mb-3">Cancel Enrollment?</h2>
            <p className="text-gray-600 text-sm mb-6">
              If you cancel, your rent payments will no longer be reported to the credit bureaus.
              This action takes effect immediately. You can re-enroll at any time.
            </p>
            <div className="flex gap-3">
              <button onClick={() => setShowOptOut(false)} className="btn-secondary flex-1 justify-center">
                Keep Enrollment
              </button>
              <button
                onClick={handleOptOut}
                disabled={optOutLoading}
                className="flex-1 justify-center inline-flex items-center px-6 py-3 rounded-lg bg-red-600 text-white font-semibold hover:bg-red-700 transition-colors disabled:opacity-60"
              >
                {optOutLoading ? "Cancelling..." : "Yes, Cancel"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
