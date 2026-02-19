"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { LayoutDashboard, History, Settings, TrendingUp, LogOut } from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/resident", icon: LayoutDashboard, label: "My Dashboard" },
  { href: "/resident/history", icon: History, label: "Payment History" },
];

export default function ResidentLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Nav */}
      <nav className="bg-white border-b border-gray-100 sticky top-0 z-40">
        <div className="max-w-4xl mx-auto px-4 sm:px-6">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-6 w-6 text-brand-600" />
              <span className="font-bold text-gray-900">RentReport</span>
              <span className="text-xs text-gray-400 font-medium ml-2">Resident Portal</span>
            </div>
            <div className="flex items-center gap-6">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "flex items-center gap-2 text-sm font-medium transition-colors",
                    pathname === item.href
                      ? "text-brand-600"
                      : "text-gray-500 hover:text-gray-900"
                  )}
                >
                  <item.icon className="h-4 w-4" />
                  {item.label}
                </Link>
              ))}
              <button
                onClick={() => {
                  localStorage.removeItem("access_token");
                  router.push("/auth/login");
                }}
                className="flex items-center gap-2 text-sm text-gray-400 hover:text-gray-700"
              >
                <LogOut className="h-4 w-4" />
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
        {children}
      </main>
    </div>
  );
}
