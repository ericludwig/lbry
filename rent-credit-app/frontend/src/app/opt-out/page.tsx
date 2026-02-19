"use client";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { CheckCircle, TrendingUp } from "lucide-react";
import Link from "next/link";
import { residentsApi } from "@/lib/api";

export default function OptOutPage() {
  const params = useSearchParams();
  const token = params.get("token");
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      return;
    }
    residentsApi.optOutViaToken(token)
      .then(() => setStatus("success"))
      .catch(() => setStatus("error"));
  }, [token]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full text-center">
        <div className="flex items-center justify-center gap-2 mb-8">
          <TrendingUp className="h-7 w-7 text-brand-600" />
          <span className="text-2xl font-bold text-gray-900">RentReport</span>
        </div>

        {status === "loading" && (
          <div className="card">
            <p className="text-gray-500">Processing your request...</p>
          </div>
        )}

        {status === "success" && (
          <div className="card">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-3">Successfully Unenrolled</h1>
            <p className="text-gray-600 mb-6">
              You have been unenrolled from RentReport. No further charges will apply.
              Your rent payments will no longer be reported to the credit bureaus.
            </p>
            <p className="text-gray-500 text-sm mb-6">
              Changed your mind? You can re-enroll any time through your resident portal.
            </p>
            <Link href="/resident" className="btn-primary w-full justify-center">
              Go to Resident Portal
            </Link>
          </div>
        )}

        {status === "error" && (
          <div className="card">
            <h1 className="text-xl font-bold text-gray-900 mb-3">Invalid or Expired Link</h1>
            <p className="text-gray-600 mb-6">
              This opt-out link is invalid or has already been used.
              To manage your enrollment, please sign in to your resident portal.
            </p>
            <Link href="/auth/login" className="btn-primary w-full justify-center">
              Sign In
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
