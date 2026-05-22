import { useMemo } from "react";
import ReactFlow, { Background, Controls, Edge, Node } from "reactflow";
import "reactflow/dist/style.css";

interface StateMachineDiagramProps {
  currentState: string;
}

const NODE_POSITIONS: Record<string, { x: number; y: number }> = {
  Pending: { x: 0, y: 150 },
  OnHold: { x: 180, y: 20 },
  PendingPayment: { x: 230, y: 150 },
  Confirmed: { x: 410, y: 150 },
  Processing: { x: 560, y: 150 },
  Shipped: { x: 710, y: 150 },
  Delivered: { x: 880, y: 150 },
  Returning: { x: 1040, y: 150 },
  Returned: { x: 1040, y: 280 },
  Refunded: { x: 880, y: 280 },
  Cancelled: { x: 230, y: 300 },
};

const TRANSITIONS: Array<[string, string, string]> = [
  ["Pending", "OnHold", "pendingBiometricalVerification"],
  ["Pending", "PendingPayment", "noVerificationNeeded"],
  ["Pending", "Cancelled", "paymentFailed"],
  ["OnHold", "PendingPayment", "biometricalVerificationSuccessful"],
  ["OnHold", "Cancelled", "verificationFailed"],
  ["PendingPayment", "Confirmed", "paymentSuccessful"],
  ["Confirmed", "Processing", "preparingShipment"],
  ["Processing", "Shipped", "itemDispatched"],
  ["Shipped", "Delivered", "itemReceivedByCustomer"],
  ["Shipped", "OnHold", "deliveryIssue"],
  ["Delivered", "Returning", "returnInitiatedByCustomer"],
  ["Returning", "Returned", "itemReceivedBack"],
  ["Returned", "Refunded", "refundProcessed"],
];

export default function StateMachineDiagram({
  currentState,
}: StateMachineDiagramProps) {
  const nodes: Node[] = useMemo(
    () =>
      Object.entries(NODE_POSITIONS).map(([state, position]) => {
        const isActive = state === currentState;
        return {
          id: state,
          position,
          data: { label: state },
          style: {
            background: isActive ? "#3556AC" : "#ffffff",
            color: isActive ? "#ffffff" : "#2A3759",
            border: `2px solid ${isActive ? "#A9FF62" : "#e2e6f0"}`,
            borderRadius: 8,
            fontSize: 12,
            fontWeight: 600,
            width: 130,
            padding: 6,
          },
        };
      }),
    [currentState]
  );

  const edges: Edge[] = useMemo(
    () =>
      TRANSITIONS.map(([from, to, label], index) => ({
        id: `edge-${index}`,
        source: from,
        target: to,
        label,
        labelStyle: { fontSize: 9, fill: "#6b7280" },
        style: { stroke: "#A0AAF9" },
        animated: from === currentState,
      })),
    [currentState]
  );

  return (
    <div style={{ height: 380 }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        proOptions={{ hideAttribution: true }}
      >
        <Background color="#f0f2f8" />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}