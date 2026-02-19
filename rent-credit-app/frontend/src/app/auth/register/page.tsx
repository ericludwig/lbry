"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { TrendingUp } from "lucide-react";
import { authApi } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    email: "",
    password: "",
    company_name: "",
    contact_name: "",
    phone: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await authApi.registerPM(form);
      const res = await authApi.loginPM(form.email, form.password);
      const { access_token, user_type } = res.data;
      localStorage.setItem("access_token", access_token);
      localStorage.setItem("user_type", user_type);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Registration failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const update = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2">
            <TrendingUp className="h-7 w-7 text-brand-600" />
            <span className="text-2xl font-bold text-gray-900">RentReport</span>
          </Link>
          <h1 className="text-2xl font-bold text-gray-900 mt-6">Create your account</h1>
          <p className="text-gray-500 mt-2 text-sm">
            Already have an account?{" "}
            <Link href="/auth/login" className="text-brand-600 font-medium hover:underline">
              Sign in
            </Link>
          </p>
        </div>

        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">
                {error}
              </div>
            )}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">First Name</label>
                <input
                  className="input"
                  value={form.contact_name.split(" ")[0]}
                  onChange={(e) =>
                    update("contact_name", `${e.target.value} ${form.contact_name.split(" ").slice(1).join(" ")}`.trim())
                  }
                  placeholder="Jane"
                  required
                />
              </div>
              <div>
                <label className="label">Last Name</label>
                <input
                  className="input"
                  value={form.contact_name.split(" ").slice(1).join(" ")}
                  onChange={(e) =>
                    update("contact_name", `${form.contact_name.split(" ")[0]} ${e.target.value}`.trim())
                  }
                  placeholder="Smith"
                />
              </div>
            </div>
            <div>
              <label className="label">Company Name</label>
              <input
                className="input"
                value={form.company_name}
                onChange={(e) => update("company_name", e.target.value)}
                placeholder="Smith Property Management LLC"
                required
              />
            </div>
            <div>
              <label className="label">Work Email</label>
              <input
                type="email"
                className="input"
                value={form.email}
                onChange={(e) => update("email", e.target.value)}
                placeholder="jane@smithpm.com"
                required
              />
            </div>
            <div>
              <label className="label">Phone (optional)</label>
              <input
                type="tel"
                className="input"
                value={form.phone}
                onChange={(e) => update("phone", e.target.value)}
                placeholder="(555) 123-4567"
              />
            </div>
            <div>
              <label className="label">Password</label>
              <input
                type="password"
                className="input"
                value={form.password}
                onChange={(e) => update("password", e.target.value)}
                placeholder="Min. 8 characters"
                minLength={8}
                required
              />
            </div>

            <div className="text-xs text-gray-500 bg-brand-50 rounded-lg p-3">
              By creating an account you agree to our{" "}
              <a href="#" className="text-brand-600 underline">Terms of Service</a> and{" "}
              <a href="#" className="text-brand-600 underline">Privacy Policy</a>.
              As a data furnisher, you acknowledge FCRA compliance requirements.
            </div>

            <button type="submit" className="btn-primary w-full justify-center" disabled={loading}>
              {loading ? "Creating account..." : "Create Account — Start Free"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
