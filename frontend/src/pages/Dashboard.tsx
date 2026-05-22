import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { Order } from "../types";
import StateBadge from "../components/StateBadge";

export default function Dashboard() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listOrders()
      .then(setOrders)
      .catch((e) => setError((e as Error).message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-gray-500">Loading orders…</p>;
  if (error) return <p className="text-red-600">Error: {error}</p>;

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold text-navy">Orders</h1>
      {orders.length === 0 ? (
        <div className="rounded-xl border border-dashed border-gray-300 p-12 text-center text-gray-500">
          No orders yet.{" "}
          <Link to="/orders/new" className="font-semibold text-brand">
            Create your first order
          </Link>
        </div>
      ) : (
        <div className="overflow-hidden rounded-xl border border-gray-200 bg-white">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-gray-100 bg-gray-50 text-gray-600">
              <tr>
                <th className="px-5 py-3">Order ID</th>
                <th className="px-5 py-3">Products</th>
                <th className="px-5 py-3">Amount</th>
                <th className="px-5 py-3">State</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr
                  key={order.orderId}
                  className="border-b border-gray-50 hover:bg-gray-50"
                >
                  <td className="px-5 py-3">
                    <Link
                      to={`/orders/${order.orderId}`}
                      className="font-mono text-brand hover:underline"
                    >
                      {order.orderId}
                    </Link>
                  </td>
                  <td className="px-5 py-3 text-gray-600">
                    {order.productIds.join(", ")}
                  </td>
                  <td className="px-5 py-3">${order.amount.toFixed(2)}</td>
                  <td className="px-5 py-3">
                    <StateBadge state={order.state} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}