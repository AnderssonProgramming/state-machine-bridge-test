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
      <div className="mb-4 flex items-center justify-between sm:mb-6">
        <h1 className="text-xl font-bold text-navy sm:text-2xl">Orders</h1>
        <Link
          to="/orders/new"
          className="rounded-lg bg-brand px-3 py-1.5 text-sm font-semibold text-white hover:bg-bright sm:hidden"
        >
          + New
        </Link>
      </div>
      {orders.length === 0 ? (
        <div className="rounded-xl border border-dashed border-gray-300 p-8 text-center text-gray-500 sm:p-12">
          No orders yet.{" "}
          <Link to="/orders/new" className="font-semibold text-brand">
            Create your first order
          </Link>
        </div>
      ) : (
        <>
          {/* Desktop table */}
          <div className="hidden overflow-hidden rounded-xl border border-gray-200 bg-white sm:block">
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

          {/* Mobile card list */}
          <div className="space-y-3 sm:hidden">
            {orders.map((order) => (
              <Link
                key={order.orderId}
                to={`/orders/${order.orderId}`}
                className="block rounded-xl border border-gray-200 bg-white p-4 hover:border-brand"
              >
                <div className="mb-2 flex items-center justify-between">
                  <span className="font-mono text-sm font-semibold text-brand">
                    {order.orderId}
                  </span>
                  <StateBadge state={order.state} />
                </div>
                <div className="flex items-center justify-between text-sm text-gray-500">
                  <span>{order.productIds.join(", ")}</span>
                  <span className="font-medium text-gray-700">${order.amount.toFixed(2)}</span>
                </div>
              </Link>
            ))}
          </div>
        </>
      )}
    </div>
  );
}