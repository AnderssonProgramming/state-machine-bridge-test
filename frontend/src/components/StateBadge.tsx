interface StateBadgeProps {
  state: string;
}

const STATE_COLORS: Record<string, string> = {
  Pending: "bg-gray-100 text-gray-700",
  OnHold: "bg-amber-100 text-amber-700",
  PendingPayment: "bg-blue-100 text-blue-700",
  Confirmed: "bg-indigo-100 text-indigo-700",
  Processing: "bg-purple-100 text-purple-700",
  Shipped: "bg-cyan-100 text-cyan-700",
  Delivered: "bg-green-100 text-green-700",
  Returning: "bg-orange-100 text-orange-700",
  Returned: "bg-orange-100 text-orange-800",
  Refunded: "bg-teal-100 text-teal-700",
  Cancelled: "bg-red-100 text-red-700",
};

export default function StateBadge({ state }: Readonly<StateBadgeProps>) {
  const color = STATE_COLORS[state] ?? "bg-gray-100 text-gray-700";
  return (
    <span
      className={`inline-block rounded-full px-3 py-1 text-xs font-semibold ${color}`}
    >
      {state}
    </span>
  );
}