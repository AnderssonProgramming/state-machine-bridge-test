export type OrderState =
  | "Pending"
  | "OnHold"
  | "PendingPayment"
  | "Confirmed"
  | "Processing"
  | "Shipped"
  | "Delivered"
  | "Returning"
  | "Returned"
  | "Refunded"
  | "Cancelled";

export interface TransitionLog {
  fromState: string | null;
  toState: string;
  eventType: string;
  timestamp: string;
  metadata: Record<string, unknown>;
}

export interface Order {
  orderId: string;
  productIds: string[];
  amount: number;
  state: OrderState;
  createdAt: string;
  updatedAt: string;
  history: TransitionLog[];
}

export interface TransitionResult {
  orderId: string;
  previousState: string;
  currentState: string;
  eventType: string;
  timestamp: string;
}

export interface AvailableEvents {
  orderId: string;
  state: OrderState;
  availableEvents: string[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}