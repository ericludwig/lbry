"use client";
import { useEffect, useState } from "react";
import { Users, Search, Filter } from "lucide-react";
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
}

const STATUS_LABELS: Record<string, string> = {
  pending: "Pending",
  trial: "Free Trial",
  active: "Active",
  opted_out: "Opted Out",
  payment_failed: "Payment Failed",
};

export default function ResidentsPage() {
  const [residents, setResidents] = useState<Resident[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  useEffect(() => {
    residentsApi.list(statusFilter ? { status: statusFilter } : {})
      .then((r) => setResidents(r.data))
      .finally(() => setLoading(false));
  }, [statusFilter]);

  const filtered = residents.filter((r) => {
    const q = search.toLowerCase();
    return (
      r.first_name.toLowerCase().includes(q) ||
      r.last_name.toLowerCase().includes(q) ||
      r.email.toLowerCase().includes(q) ||
      r.unit_number?.toLowerCase().includes(q)
    );
  });

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Residents</h1>
        <p className="text-gray-500 mt-1">All residents and their enrollment status</p>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            className="input pl-9"
            placeholder="Search by name, email, unit..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select
          className="input w-48"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All statuses</option>
          {Object.entries(STATUS_LABELS).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-100 bg-gray-50">
              {["Resident", "Unit", "Monthly Rent", "Lease Start", "Enrollment Status", "Enrolled On"].map((h) => (
                <th key={h} className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wide">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={6} className="text-center py-12 text-gray-400">Loading...</td>
              </tr>
            ) : filtered.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-12">
                  <Users className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                  <p className="text-gray-500 text-sm">No residents found</p>
                </td>
              </tr>
            ) : (
              filtered.map((r) => (
                <tr key={r.id} className="border-b border-gray-50 hover:bg-gray-50/50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="font-medium text-gray-900">{r.first_name} {r.last_name}</div>
                    <div className="text-sm text-gray-500">{r.email}</div>
                  </td>
                  <td className="px-6 py-4 text-gray-700 text-sm">{r.unit_number || "-"}</td>
                  <td className="px-6 py-4 text-gray-700 text-sm">{formatCents(r.monthly_rent_cents)}</td>
                  <td className="px-6 py-4 text-gray-700 text-sm">{formatDate(r.lease_start_date)}</td>
                  <td className="px-6 py-4">
                    <span className={`badge ${getStatusColor(r.enrollment_status)}`}>
                      {STATUS_LABELS[r.enrollment_status] || r.enrollment_status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-gray-500 text-sm">
                    {r.enrollment_date ? formatDate(r.enrollment_date) : "-"}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {!loading && (
        <div className="mt-4 text-sm text-gray-400">
          Showing {filtered.length} of {residents.length} residents
        </div>
      )}
    </div>
  );
}
