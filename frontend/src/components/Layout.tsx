import { ReactNode } from "react";
import { Link } from "react-router-dom";

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: Readonly<LayoutProps>) {
  return (
    <div className="min-h-screen">
      <header className="bg-gradient-to-r from-navy via-brand to-bright text-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3 sm:px-6 sm:py-4">
          <Link to="/" className="flex items-center gap-2">
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-white/15 font-extrabold sm:h-9 sm:w-9">
              O
            </span>
            <div>
              <div className="text-sm font-bold leading-tight sm:text-base">Order State Machine</div>
              <div className="text-xs text-white/60">
                Sainapsis · Technical Test
              </div>
            </div>
          </Link>
          <nav className="flex items-center gap-2 text-sm sm:gap-4">
            <Link to="/" className="hover:text-lila hidden sm:inline">
              Dashboard
            </Link>
            <Link
              to="/orders/new"
              className="rounded-lg bg-white/15 px-2.5 py-1.5 text-xs hover:bg-white/25 sm:px-3 sm:text-sm"
            >
              + New Order
            </Link>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6 sm:px-6 sm:py-8">{children}</main>
    </div>
  );
}