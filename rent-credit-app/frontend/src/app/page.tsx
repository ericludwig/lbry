"use client";
import Link from "next/link";
import {
  CheckCircle,
  TrendingUp,
  Shield,
  Building2,
  ArrowRight,
  Star,
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-7 w-7 text-brand-600" />
              <span className="text-xl font-bold text-gray-900">RentReport</span>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <Link href="#how-it-works" className="text-gray-600 hover:text-gray-900 text-sm font-medium">
                How It Works
              </Link>
              <Link href="#pricing" className="text-gray-600 hover:text-gray-900 text-sm font-medium">
                Pricing
              </Link>
              <Link href="#for-managers" className="text-gray-600 hover:text-gray-900 text-sm font-medium">
                For Managers
              </Link>
            </div>
            <div className="flex items-center gap-3">
              <Link href="/auth/login" className="btn-secondary text-sm px-4 py-2">
                Sign In
              </Link>
              <Link href="/auth/register" className="btn-primary text-sm px-4 py-2">
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-28 pb-20 bg-gradient-to-br from-brand-50 to-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 bg-brand-100 text-brand-700 rounded-full px-4 py-1.5 text-sm font-medium mb-6">
            <Star className="h-4 w-4" />
            82% resident participation rate at enrolled properties
          </div>
          <h1 className="text-5xl md:text-6xl font-extrabold text-gray-900 leading-tight mb-6">
            Your rent payment is<br />
            <span className="text-brand-600">building your future</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-10">
            RentReport automatically reports your on-time rent payments to Experian, Equifax,
            and TransUnion — helping you build credit while you sleep.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/auth/register" className="btn-primary text-base px-8 py-4">
              Start Free Trial <ArrowRight className="ml-2 h-5 w-5" />
            </Link>
            <Link href="#how-it-works" className="btn-secondary text-base px-8 py-4">
              Learn More
            </Link>
          </div>

          {/* Stats */}
          <div className="mt-16 grid grid-cols-3 gap-8 max-w-2xl mx-auto">
            {[
              { value: "26pts", label: "avg credit score boost, year 1" },
              { value: "3", label: "credit bureaus reported to" },
              { value: "24mo", label: "retroactive back-reporting" },
            ].map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-3xl font-bold text-brand-600">{stat.value}</div>
                <div className="text-sm text-gray-500 mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-gray-900">How RentReport Works</h2>
            <p className="text-gray-600 mt-3 max-w-xl mx-auto">
              Fully automated. No extra work for you or your property manager.
            </p>
          </div>
          <div className="grid md:grid-cols-4 gap-8">
            {[
              {
                step: "1",
                title: "Auto-Enrolled",
                desc: "Your property manager enrolls the building. You're automatically added when your lease starts.",
                icon: Building2,
              },
              {
                step: "2",
                title: "Free Trial Starts",
                desc: "Your first month is completely free. No payment method required during the trial.",
                icon: Star,
              },
              {
                step: "3",
                title: "Payments Verified",
                desc: "We pull on-time payment data directly from your property's software — nothing for you to submit.",
                icon: CheckCircle,
              },
              {
                step: "4",
                title: "Credit Score Rises",
                desc: "Monthly on-time payments are reported to all 3 bureaus. Your score builds automatically.",
                icon: TrendingUp,
              },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div className="w-14 h-14 bg-brand-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <item.icon className="h-7 w-7 text-brand-600" />
                </div>
                <div className="text-xs font-bold text-brand-600 uppercase tracking-wide mb-2">
                  Step {item.step}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-gray-600 text-sm">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">
                Everything you need to build credit through rent
              </h2>
              <div className="space-y-5">
                {[
                  {
                    title: "All 3 Credit Bureaus",
                    desc: "Payments reported to Experian, Equifax, and TransUnion every month.",
                  },
                  {
                    title: "Retroactive Reporting",
                    desc: "Claim up to 24 months of past on-time rent payments at no extra charge.",
                  },
                  {
                    title: "Positive-Only Policy",
                    desc: "Only on-time payments are ever reported. Late payments are never submitted.",
                  },
                  {
                    title: "Real-Time Dashboard",
                    desc: "Track every payment reported, view your full reporting history, and monitor enrollment status.",
                  },
                  {
                    title: "Identity Protection",
                    desc: "Real-time credit monitoring with $1M identity theft protection policy.",
                  },
                ].map((f) => (
                  <div key={f.title} className="flex gap-4">
                    <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <div>
                      <div className="font-semibold text-gray-900">{f.title}</div>
                      <div className="text-gray-600 text-sm">{f.desc}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
              <div className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
                Payment Reporting History
              </div>
              {[
                { month: "June 2024", status: "Reported", bureaus: "EXP · EFX · TU", ok: true },
                { month: "May 2024", status: "Reported", bureaus: "EXP · EFX · TU", ok: true },
                { month: "April 2024", status: "Reported", bureaus: "EXP · EFX · TU", ok: true },
                { month: "March 2024", status: "Reported", bureaus: "EXP · EFX · TU", ok: true },
                { month: "February 2024", status: "Trial", bureaus: "Free month", ok: true },
              ].map((row) => (
                <div key={row.month} className="flex items-center justify-between py-3 border-b border-gray-50 last:border-0">
                  <div>
                    <div className="font-medium text-gray-900 text-sm">{row.month}</div>
                    <div className="text-xs text-gray-400">{row.bureaus}</div>
                  </div>
                  <span className={`badge ${row.ok ? "bg-green-100 text-green-700" : "bg-orange-100 text-orange-700"}`}>
                    {row.ok ? <CheckCircle className="h-3 w-3 mr-1" /> : null}
                    {row.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Simple, Transparent Pricing</h2>
          <p className="text-gray-600 mb-12 max-w-lg mx-auto">
            Added as a line item on your monthly rent ledger — no separate billing.
          </p>
          <div className="max-w-sm mx-auto">
            <div className="card border-2 border-brand-600 relative">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-brand-600 text-white text-xs font-bold px-4 py-1 rounded-full">
                FIRST MONTH FREE
              </div>
              <div className="text-4xl font-extrabold text-gray-900 mt-2">$8.95
                <span className="text-lg font-medium text-gray-500">/mo</span>
              </div>
              <p className="text-gray-500 text-sm mt-1 mb-6">Per enrolled resident</p>
              <ul className="space-y-3 text-sm text-left">
                {[
                  "All 3 credit bureaus",
                  "24-month retroactive reporting",
                  "Monthly payment reporting",
                  "Resident dashboard",
                  "Credit monitoring & ID protection",
                  "Cancel anytime",
                ].map((f) => (
                  <li key={f} className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-500" />
                    <span className="text-gray-700">{f}</span>
                  </li>
                ))}
              </ul>
              <Link href="/auth/register" className="btn-primary w-full mt-8 justify-center">
                Start Free Trial
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* For Property Managers */}
      <section id="for-managers" className="py-20 bg-brand-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="text-brand-300 text-sm font-bold uppercase tracking-wide mb-4">
                For Property Managers
              </div>
              <h2 className="text-3xl font-bold mb-6">
                Turn a resident amenity into<br />
                <span className="text-brand-300">$3/month per door</span>
              </h2>
              <p className="text-brand-100 mb-6">
                Offer RentReport as a premium amenity that residents love — and earn
                $3.00/month for every enrolled resident. A 200-unit property earns
                $7,200/year in additional NOI.
              </p>
              <div className="grid grid-cols-2 gap-4 mb-8">
                {[
                  { value: "$3.00", label: "per enrolled resident/month" },
                  { value: "82%", label: "average enrollment rate" },
                  { value: "~$4.5M", label: "added property value at 15k units" },
                  { value: "0", label: "extra staff work required" },
                ].map((s) => (
                  <div key={s.label} className="bg-brand-800 rounded-xl p-4">
                    <div className="text-2xl font-bold text-white">{s.value}</div>
                    <div className="text-brand-300 text-xs mt-1">{s.label}</div>
                  </div>
                ))}
              </div>
              <Link href="/auth/register" className="inline-flex items-center gap-2 bg-white text-brand-900 font-bold px-6 py-3 rounded-lg hover:bg-brand-50 transition-colors">
                Get Started Free <ArrowRight className="h-5 w-5" />
              </Link>
            </div>
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-brand-200 mb-4">Integrates with your PMS</h3>
              {["RealPage", "Yardi", "AppFolio", "Entrata"].map((pms) => (
                <div key={pms} className="flex items-center gap-3 bg-brand-800 rounded-xl p-4">
                  <Building2 className="h-5 w-5 text-brand-300" />
                  <span className="font-medium">{pms}</span>
                  <Shield className="h-4 w-4 text-green-400 ml-auto" />
                </div>
              ))}
              <p className="text-brand-300 text-sm mt-2">
                No manual data entry. Resident data and payment ledgers sync automatically.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-2 text-white mb-3">
                <TrendingUp className="h-5 w-5 text-brand-400" />
                <span className="font-bold">RentReport</span>
              </div>
              <p className="text-sm">Building credit through rent, automatically.</p>
            </div>
            {[
              { title: "Product", links: ["How It Works", "Pricing", "Security"] },
              { title: "Property Managers", links: ["Integrations", "Revenue Share", "Onboarding"] },
              { title: "Company", links: ["About", "Privacy Policy", "Terms of Service", "Contact"] },
            ].map((col) => (
              <div key={col.title}>
                <h4 className="text-white font-semibold text-sm mb-3">{col.title}</h4>
                <ul className="space-y-2">
                  {col.links.map((link) => (
                    <li key={link}>
                      <a href="#" className="text-sm hover:text-white transition-colors">{link}</a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <div className="border-t border-gray-800 pt-6 flex flex-col md:flex-row justify-between items-center text-xs">
            <p>&copy; 2024 RentReport LLC. All rights reserved.</p>
            <p className="mt-2 md:mt-0">
              FCRA compliant data furnisher. SOC 2 certified.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
