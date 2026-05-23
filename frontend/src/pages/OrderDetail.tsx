import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api/client";
import { AvailableEvents, Order } from "../types";
import StateBadge from "../components/StateBadge";
import StateMachineDiagram from "../components/StateMachineDiagram";

export default function OrderDetail() {
  const { id } = useParams<{ id: string }>();
  const [order, setOrder] = useState<Order | null>(null);
  const [available, setAvailable] = useState<AvailableEvents | null>(null);
  const [selectedEvent, setSelectedEvent] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    if (!id) return;
    try {
      const [orderData, availableData] = await Promise.all([
        api.getOrder(id),
        api.availableEvents(id),
      ]);
      setOrder(orderData);
      setAvailable(availableData);
      setSelectedEvent("");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  async function triggerEvent() {
    if (!id || !selectedEvent) return;
    setError(null);
    try {
      await api.applyEvent(id, selectedEvent);
      await load();
    } catch (e) {
      setError((e as Error).message);
    }
  }

  if (loading) return <p className="text-gray-500">Loading…</p>;
  if (!order) return <p className="text-red-600">Order not found.</p>;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-mono text-xl font-bold text-navy">
            {order.orderId}
          </h1>
          <p className="text-sm text-gray-500">
            {order.productIds.join(", ")} · ${order.amount.toFixed(2)}
          </p>
        </div>
        <StateBadge state={order.state} />
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-4">
        <h2 className="mb-3 text-sm font-semibold text-gray-700">
          State Machine
        </h2>
        <StateMachineDiagram currentState={order.state} />
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="mb-3 text-sm font-semibold text-gray-700">
          Trigger Event
        </h2>
        {available && available.availableEvents.length > 0 ? (
          <div className="flex gap-3">
            <select
              value={selectedEvent}
              onChange={(e) => setSelectedEvent(e.target.value)}
              className="flex-1 rounded-lg border border-gray-300 px-3 py-2"
            >
              <option value="">Select an event…</option>
              {available.availableEvents.map((event) => (
                <option key={event} value={event}>
                  {event}
                </option>
              ))}
            </select>
            <button
              onClick={triggerEvent}
              disabled={!selectedEvent}
              className="rounded-lg bg-brand px-5 py-2 font-semibold text-white hover:bg-bright disabled:opacity-50"
            >
              Apply
            </button>
          </div>
        ) : (
          <p className="text-sm text-gray-500">
            No further transitions available (terminal state).
          </p>
        )}
        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-6">
        <h2 className="mb-3 text-sm font-semibold text-gray-700">History</h2>
        <ol className="space-y-2">
          {order.history.map((entry) => (
            <li key={`${entry.timestamp}-${entry.toState}`} className="flex flex-wrap items-center gap-3 text-sm">
              <span className="font-mono text-xs text-gray-400">
                {new Date(entry.timestamp).toLocaleString()}
              </span>
              <span className="text-gray-600">
                {entry.fromState ?? "∅"} →{" "}
                <span className="font-semibold">{entry.toState}</span>
              </span>
              <span className="rounded bg-gray-100 px-2 py-0.5 text-xs text-gray-500">
                {entry.eventType}
              </span>
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}