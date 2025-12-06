"use client";

import { supabase } from "@/lib/supabase";
import { useEffect, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

interface HeaderProps {
  session: Awaited<ReturnType<typeof supabase.auth.getSession>>["data"]["session"] | null;
  tokens: number | null;
  onSignOut: () => void;
}

export function Header({ session, tokens, onSignOut }: HeaderProps) {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  // Header는 props로 받은 tokens를 표시만 함
  // 실제 토큰 업데이트는 부모 컴포넌트(StudioPage)에서 처리

  if (!session) return null;

  return (
    <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-white/95 backdrop-blur-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
        <div className="flex items-center gap-4">
          <h1 className="pixel-font text-lg font-semibold text-black">Sprite Studio</h1>
          {tokens !== null && (
            <div className="rounded-full bg-[var(--enhanced-accent)] px-4 py-1 text-sm font-semibold text-white">
              Tokens: {tokens}
            </div>
          )}
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-700">{session.user?.email}</span>
          <button
            onClick={onSignOut}
            className="rounded-xl border border-gray-300 bg-white px-4 py-2 text-sm font-semibold text-gray-700 hover:bg-gray-50"
          >
            Sign Out
          </button>
        </div>
      </div>
    </header>
  );
}

