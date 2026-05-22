import {
  AvailableEvents,
  ChatMessage,
  Order,
  TransitionResult,
} from "../types";

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const body = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(body.detail ?? "Request failed");
  }

  return response.json() as Promise<T>;
}

export const api = {
  createOrder: (productIds: string[], amount: number) =>
    request<Order>("/orders", {
      method: "POST",
      body: JSON.stringify({ productIds, amount }),
    }),

  listOrders: () => request<Order[]>("/orders"),

  getOrder: (id: string) => request<Order>(`/orders/${id}`),

  applyEvent: (id: string, eventType: string, metadata: object = {}) =>
    request<TransitionResult>(`/orders/${id}/events`, {
      method: "POST",
      body: JSON.stringify({ eventType, metadata }),
    }),

  availableEvents: (id: string) =>
    request<AvailableEvents>(`/orders/${id}/available-events`),

  chat: (message: string, conversationHistory: ChatMessage[]) =>
    request<{ reply: string }>("/chat", {
      method: "POST",
      body: JSON.stringify({ message, conversationHistory }),
    }),
};