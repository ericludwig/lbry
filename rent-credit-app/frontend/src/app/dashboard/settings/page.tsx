"use client";
import { useEffect, useState } from "react";
import {
  Building2,
  CreditCard,
  Plug,
  CheckCircle,
  AlertCircle,
  ExternalLink,
  RefreshCw,
} from "lucide-react";
import { paymentsApi, integrationsApi } from "@/lib/api";

const PMS_OPTIONS = [
  { value: "realpage", label: "RealPage", desc: "API Key" },
  { value: "yardi", label: "Yardi", desc: "API Key + Instance URL" },
  { value: "appfolio", label: "AppFolio", desc: "Client ID & Secret (OAuth)" },
  { value: "entrata", label: "Entrata", desc: "API Key" },
  { value: "manual", label: "Manual Entry", desc: "No PMS integration" },
];

export default function SettingsPage() {
  const [stripeStatus, setStripeStatus] = useState<any>(null);
  const [pmsStatus, setPmsStatus] = useState<any>(null);
  const [pmsType, setPmsType] = useState("realpage");
  const [pmsForm, setPmsForm] = useState({ api_key: "", client_id: "", client_secret: "", instance_url: "" });
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<any>(null);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    paymentsApi.getStripeStatus().then((r) => setStripeStatus(r.data));
    integrationsApi.getStatus().then((r) => setPmsStatus(r.data));
  }, []);

  const handleStripeOnboard = async () => {
    const res = await paymentsApi.startStripeOnboarding();
    window.open(res.data.url, "_blank");
  };

  const handleSavePMS = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await integrationsApi.configurePMS({
        pms_type: pmsType,
        pms_api_key: pmsForm.api_key,
        pms_client_id: pmsForm.client_id,
        pms_client_secret: pmsForm.client_secret,
        pms_instance_url: pmsForm.instance_url,
      });
      const r = await integrationsApi.getStatus();
      setPmsStatus(r.data);
    } finally {
      setSaving(false);
    }
  };

  const handleTestPMS = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await integrationsApi.testPMS();
      setTestResult({ ok: true, ...res.data });
    } catch (err: any) {
      setTestResult({ ok: false, message: err?.response?.data?.detail || "Connection failed" });
    } finally {
      setTesting(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      await integrationsApi.triggerSync();
    } finally {
      setSyncing(false);
    }
  };

  const upd = (k: string, v: string) => setPmsForm((f) => ({ ...f, [k]: v }));

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings & Integrations</h1>
        <p className="text-gray-500 mt-1">Connect your PMS and set up payouts</p>
      </div>

      {/* Stripe Connect */}
      <div className="card">
        <div className="flex items-center gap-3 mb-6">
          <div className="bg-purple-50 p-2.5 rounded-lg">
            <CreditCard className="h-5 w-5 text-purple-600" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">Stripe Connect — Revenue Share Payouts</h2>
            <p className="text-sm text-gray-500">Receive your $3.00/month/resident payout via Stripe</p>
          </div>
          {stripeStatus?.onboarded && (
            <span className="badge bg-green-100 text-green-700 ml-auto">
              <CheckCircle className="h-3 w-3 mr-1" />
              Connected
            </span>
          )}
        </div>

        {stripeStatus?.onboarded ? (
          <div className="bg-green-50 rounded-lg p-4 text-sm text-green-800">
            Your Stripe Express account is fully connected. Revenue share payouts will be
            transferred on the 20th of each month.
          </div>
        ) : (
          <div>
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-800 mb-4">
              <AlertCircle className="h-4 w-4 inline mr-2" />
              You need to connect Stripe to receive your monthly revenue share payouts.
            </div>
            <button onClick={handleStripeOnboard} className="btn-primary">
              <ExternalLink className="h-4 w-4 mr-2" />
              Connect Stripe Account
            </button>
          </div>
        )}
      </div>

      {/* PMS Integration */}
      <div className="card">
        <div className="flex items-center gap-3 mb-6">
          <div className="bg-blue-50 p-2.5 rounded-lg">
            <Plug className="h-5 w-5 text-blue-600" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">Property Management Software Integration</h2>
            <p className="text-sm text-gray-500">Automatically sync residents and payment ledger data</p>
          </div>
          {pmsStatus?.is_configured && (
            <span className="badge bg-blue-100 text-blue-700 ml-auto">
              <CheckCircle className="h-3 w-3 mr-1" />
              {pmsStatus.pms_type}
            </span>
          )}
        </div>

        <form onSubmit={handleSavePMS} className="space-y-4">
          <div>
            <label className="label">Select your PMS</label>
            <div className="grid grid-cols-5 gap-3">
              {PMS_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setPmsType(opt.value)}
                  className={`p-3 rounded-lg border text-center transition-colors ${
                    pmsType === opt.value
                      ? "border-brand-500 bg-brand-50 text-brand-700"
                      : "border-gray-200 text-gray-600 hover:border-gray-300"
                  }`}
                >
                  <Building2 className="h-5 w-5 mx-auto mb-1" />
                  <div className="text-xs font-medium">{opt.label}</div>
                </button>
              ))}
            </div>
          </div>

          {pmsType !== "manual" && (
            <>
              {["appfolio"].includes(pmsType) ? (
                <>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="label">Client ID</label>
                      <input className="input" value={pmsForm.client_id} onChange={(e) => upd("client_id", e.target.value)} placeholder="OAuth client ID" />
                    </div>
                    <div>
                      <label className="label">Client Secret</label>
                      <input type="password" className="input" value={pmsForm.client_secret} onChange={(e) => upd("client_secret", e.target.value)} placeholder="OAuth client secret" />
                    </div>
                  </div>
                </>
              ) : (
                <div>
                  <label className="label">API Key</label>
                  <input type="password" className="input" value={pmsForm.api_key} onChange={(e) => upd("api_key", e.target.value)} placeholder="Paste your API key" />
                </div>
              )}
              {pmsType === "yardi" && (
                <div>
                  <label className="label">Yardi Instance URL (optional)</label>
                  <input className="input" value={pmsForm.instance_url} onChange={(e) => upd("instance_url", e.target.value)} placeholder="https://yourcompany.yardipcv.com" />
                </div>
              )}
            </>
          )}

          {testResult && (
            <div className={`rounded-lg p-3 text-sm ${testResult.ok ? "bg-green-50 text-green-800" : "bg-red-50 text-red-800"}`}>
              {testResult.ok
                ? `Connected! Found ${testResult.resident_count ?? "—"} residents.`
                : testResult.message}
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button type="submit" className="btn-primary" disabled={saving}>
              {saving ? "Saving..." : "Save Integration"}
            </button>
            {pmsStatus?.is_configured && (
              <>
                <button type="button" className="btn-secondary" onClick={handleTestPMS} disabled={testing}>
                  {testing ? "Testing..." : "Test Connection"}
                </button>
                <button type="button" className="btn-secondary" onClick={handleSync} disabled={syncing}>
                  <RefreshCw className={`h-4 w-4 mr-2 ${syncing ? "animate-spin" : ""}`} />
                  {syncing ? "Syncing..." : "Sync Now"}
                </button>
              </>
            )}
          </div>
        </form>
      </div>

      {/* Credit Bureau Settings */}
      <div className="card">
        <div className="flex items-center gap-3 mb-6">
          <div className="bg-green-50 p-2.5 rounded-lg">
            <CheckCircle className="h-5 w-5 text-green-600" />
          </div>
          <div>
            <h2 className="font-semibold text-gray-900">Credit Bureau Reporting</h2>
            <p className="text-sm text-gray-500">Select which bureaus to report resident payments to</p>
          </div>
        </div>
        <div className="space-y-3">
          {["Experian", "Equifax", "TransUnion"].map((bureau) => (
            <label key={bureau} className="flex items-center gap-3 p-3 rounded-lg border border-gray-100 hover:bg-gray-50 cursor-pointer">
              <input type="checkbox" defaultChecked className="h-4 w-4 text-brand-600" />
              <div>
                <div className="font-medium text-gray-900 text-sm">{bureau}</div>
                <div className="text-xs text-gray-500">Reports transmitted via SFTP in Metro 2 format on the 18th of each month</div>
              </div>
            </label>
          ))}
        </div>
        <p className="text-xs text-gray-400 mt-4">
          Reporting is positive-only. Late or missed payments are never submitted to credit bureaus.
        </p>
      </div>
    </div>
  );
}
