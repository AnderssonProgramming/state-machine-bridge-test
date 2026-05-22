import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";

export default function CreateOrder() {
  const navigate = useNavigate();
  const [productInput, setProductInput] = useState("");
  const [amount, setAmount] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit() {
    setError(null);
    const productIds = productInput
      .split(",")
      .map((p) => p.trim())
      .filter(Boolean);
    const amountValue = parseFloat(amount);

    if (productIds.length === 0) {
      setError("Add at least one product ID.");
      return;
    }
    if (Number.isNaN(amountValue) || amountValue <= 0) {
      setError("Amount must be a positive number.");
      return;
    }

    setSubmitting(true);
    try {
      const order = await api.createOrder(productIds, amountValue);
      navigate(`/orders/${order.orderId}`);
    } catch (e) {
      setError((e as Error).message);
      setSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="mb-6 text-2xl font-bold text-navy">Create Order</h1>
      <div className="space-y-5 rounded-xl border border-gray-200 bg-white p-6">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Product IDs <span className="text-gray-400">(comma-separated)</span>
          </label>
          <input
            type="text"
            value={productInput}
            onChange={(e) => setProductInput(e.target.value)}
            placeholder="prod-001, prod-002"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-brand focus:outline-none"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Amount (USD)
          </label>
          <input
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            placeholder="249.99"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-brand focus:outline-none"
          />
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          onClick={handleSubmit}
          disabled={submitting}
          className="w-full rounded-lg bg-brand py-2.5 font-semibold text-white hover:bg-bright disabled:opacity-50"
        >
          {submitting ? "Creating…" : "Create Order"}
        </button>
      </div>
    </div>
  );
}