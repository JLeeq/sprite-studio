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
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  // Header는 props로 받은 tokens를 표시만 함
  // 실제 토큰 업데이트는 부모 컴포넌트(StudioPage)에서 처리

  if (!session) return null;

  return (
    <>
      <header className="sticky top-0 z-50 w-full border-b border-white/10 bg-white/95 backdrop-blur-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <div className="flex items-center gap-4">
            <h1 className="pixel-font text-lg font-semibold text-black">Sprite Studio</h1>
            {tokens !== null && (
              <div className="flex items-center gap-2">
                <div className="rounded-full bg-[var(--enhanced-accent)] px-4 py-1 text-sm font-semibold text-white">
                  Tokens: {tokens}
                </div>
                <button
                  onClick={() => setShowUpgradeModal(true)}
                  className="rounded-full bg-gradient-to-r from-purple-600 to-indigo-600 px-4 py-1 text-sm font-semibold text-white hover:from-purple-700 hover:to-indigo-700 transition-all"
                >
                  Upgrade
                </button>
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

      {/* Upgrade Modal */}
      {showUpgradeModal && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[100] p-4"
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              setShowUpgradeModal(false);
            }
          }}
        >
          <div 
            className="bg-white rounded-3xl border border-gray-200 shadow-2xl max-w-md w-full p-6 space-y-6"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between">
              <h2 className="pixel-font text-2xl font-bold text-black">Get More Tokens</h2>
              <button
                onClick={() => setShowUpgradeModal(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
              >
                ×
              </button>
            </div>

            <p className="text-gray-600">
              Choose a token package to continue creating amazing game assets!
            </p>

            <div className="space-y-4">
              {/* 50 Tokens Package */}
              <div className="border-2 border-gray-200 rounded-2xl p-4 hover:border-purple-400 transition-colors cursor-pointer group">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-black">50 Tokens</h3>
                    <p className="text-sm text-gray-500">Best for small projects</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-purple-600">$9.99</p>
                    <p className="text-xs text-gray-400">$0.20 per token</p>
                  </div>
                </div>
              </div>

              {/* 100 Tokens Package - Popular */}
              <div className="border-2 border-purple-400 rounded-2xl p-4 bg-purple-50 relative cursor-pointer">
                <div className="absolute -top-3 left-4 bg-purple-600 text-white text-xs font-semibold px-3 py-1 rounded-full">
                  POPULAR
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-black">100 Tokens</h3>
                    <p className="text-sm text-gray-500">Best value!</p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-purple-600">$16.99</p>
                    <p className="text-xs text-gray-400">$0.17 per token</p>
                  </div>
                </div>
              </div>
            </div>

            <p className="text-xs text-center text-gray-400">
              Payment processing coming soon. Contact support for bulk purchases.
            </p>

            <button
              onClick={() => setShowUpgradeModal(false)}
              className="w-full rounded-2xl border-2 border-gray-300 bg-white py-3 font-semibold text-gray-700 hover:bg-gray-50"
            >
              Maybe Later
            </button>
          </div>
        </div>
      )}
    </>
  );
}

