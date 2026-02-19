"use client";
import { useEffect, useState } from "react";
import { CheckCircle, AlertTriangle, MinusCircle } from "lucide-react";
import { residentsApi } from "@/lib/api";
import { formatDate, formatCents } from "@/lib/utils";
import { format, parseISO } from "date-fns";

interface Payment {
  id: string;
  payment_period_start: string;
  due_date: string;
  paid_date: string | null;
  amount_due_cents: number;
  amount_paid_cents: number | null;
  payment_status: string;
  reporting_status: string;
  reported_at: string | null;
  is_retroactive: boolean;
}

const REPORTING_ICON: Record<string, React.ElementType> = {
  reported: CheckCircle,
  skipped: AlertTriangle,
  pending: MinusCircle,
  retroactive: CheckCircle,
};

const REPORTING_COLOR: Record<string, string> = {
  reported: "text-green-500",
  skipped: "text-orange-400",
  pending: "text-gray-300",
  retroactive: "text-blue-500",
};

const REPORTING_LABEL: Record<string, string> = {
  reported: "Reported to bureaus",
  skipped: "Not reported (positive-only policy)",
  pending: "Pending",
  retroactive: "Back-reported",
  failed: "Reporting failed",
};

export default function PaymentHistoryPage() {
  const [payments, setPayments] = useState<Payment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    residentsApi.getMyPayments().then((r) => setPayments(r.data)).finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Payment Reporting History</h1>
        <p className="text-gray-500 mt-1">Every month we report your on-time rent to all 3 credit bureaus</p>
      </div>

      {/* Legend */}
      <div className="flex gap-6 mb-6 text-sm">
        {[
          { icon: CheckCircle, color: "text-green-500", label: "Reported" },
          { icon: AlertTriangle, color: "text-orange-400", label: "Not reported (late payment)" },
          { icon: MinusCircle, color: "text-gray-300", label: "Pending" },
        ].map(({ icon: Icon, color, label }) => (
          <div key={label} className="flex items-center gap-2 text-gray-600">
            <Icon className={`h-4 w-4 ${color}`} />
            {label}
          </div>
        ))}
      </div>

      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-100 bg-gray-50">
              {["Period", "Due Date", "Paid Date", "Amount", "Payment", "Bureau Reporting"].map((h) => (
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
            ) : payments.length === 0 ? (
              <tr>
                <td colSpan={6} className="text-center py-16">
                  <CheckCircle className="h-8 w-8 text-gray-200 mx-auto mb-3" />
                  <p className="text-gray-500 text-sm">No payment records yet.</p>
                  <p className="text-gray-400 text-xs mt-1">
                    Your first report will appear after your enrollment is active.
                  </p>
                </td>
              </tr>
            ) : (
              payments.map((p) => {
                const Icon = REPORTING_ICON[p.reporting_status] || MinusCircle;
                const iconColor = REPORTING_COLOR[p.reporting_status] || "text-gray-300";
                const period = format(parseISO(p.payment_period_start), "MMMM yyyy");

                return (
                  <tr key={p.id} className="border-b border-gray-50 hover:bg-gray-50/50">
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900 text-sm">{period}</div>
                      {p.is_retroactive && (
                        <span className="badge bg-blue-100 text-blue-700 mt-1">Back-reported</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-gray-600 text-sm">{formatDate(p.due_date)}</td>
                    <td className="px-6 py-4 text-gray-600 text-sm">
                      {p.paid_date ? formatDate(p.paid_date) : "—"}
                    </td>
                    <td className="px-6 py-4 text-gray-900 text-sm font-medium">
                      {formatCents(p.amount_due_cents)}
                    </td>
                    <td className="px-6 py-4">
                      <span className={`badge ${
                        p.payment_status === "on_time"
                          ? "bg-green-100 text-green-700"
                          : "bg-red-100 text-red-700"
                      }`}>
                        {p.payment_status === "on_time" ? "On Time" : "Late"}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <Icon className={`h-4 w-4 ${iconColor}`} />
                        <span className="text-sm text-gray-600">
                          {REPORTING_LABEL[p.reporting_status] || p.reporting_status}
                        </span>
                      </div>
                      {p.reported_at && (
                        <div className="text-xs text-gray-400 mt-0.5">
                          {formatDate(p.reported_at)}
                        </div>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-6 bg-blue-50 rounded-xl p-5 text-sm text-blue-800">
        <strong>Note:</strong> It typically takes 30–40 days for reported payments to appear on your credit report.
        Only on-time payments are reported (positive-only policy). Late payments are never submitted.
        To view your credit score, visit{" "}
        <a href="https://www.annualcreditreport.com" target="_blank" rel="noopener noreferrer" className="underline font-medium">
          annualcreditreport.com
        </a>.
      </div>
    </div>
  );
}
