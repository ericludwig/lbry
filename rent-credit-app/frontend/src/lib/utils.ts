import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCents(cents: number): string {
  return `$${(cents / 100).toFixed(2)}`;
}

export function formatDate(dateStr: string): string {
  if (!dateStr) return "-";
  return new Date(dateStr).toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  });
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    active: "bg-green-100 text-green-800",
    trial: "bg-blue-100 text-blue-800",
    pending: "bg-yellow-100 text-yellow-800",
    opted_out: "bg-gray-100 text-gray-800",
    payment_failed: "bg-red-100 text-red-800",
    reported: "bg-green-100 text-green-800",
    skipped: "bg-orange-100 text-orange-800",
    on_time: "bg-green-100 text-green-800",
    late: "bg-red-100 text-red-800",
  };
  return colors[status] || "bg-gray-100 text-gray-800";
}
