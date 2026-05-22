import { ReactNode } from "react";
import { Link } from "react-router-dom";

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen">
      <header className="bg-gradient-to-r from-navy via-brand to-bright text-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link to="/" className="flex items-center gap-2">
            <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-white/15 font-extrabold">
              O
            </span>
            <div>
              <div className="font-bold leading-tight">Order State Machine</div>
              <div className="text-xs text-white/60">
                Sainapsis · Technical Test
              </div>
            </div>
          </Link>
          <nav className="flex items-center gap-4 text-sm">
            <Link to="/" className="hover:text-lila">
              Dashboard
            </Link>
            <Link
              to="/orders/new"
              className="rounded-lg bg-white/15 px-3 py-1.5 hover:bg-white/25"
            >
              + New Order
            </Link>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-8">{children}</main>
    </div>
  );
}