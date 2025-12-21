"use client";

import { useEffect, useState, useCallback } from "react";
import { supabase } from "@/lib/supabase";
import { useRouter } from "next/navigation";
import { Header } from "@/components/Header";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const GRADIO_URL = process.env.NEXT_PUBLIC_GRADIO_URL ?? "http://localhost:7861";

export default function StudioPage() {
  const [session, setSession] = useState<Awaited<ReturnType<typeof supabase.auth.getSession>>["data"]["session"] | null>(null);
  const [tokens, setTokens] = useState<number | null>(null); // API에서 가져옴
  const [isLoading, setIsLoading] = useState(true);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const router = useRouter();

  // fetchProfile: API에서 토큰 가져오기
  const fetchProfile = useCallback(async (accessToken: string) => {
    try {
      const res = await fetch(`${API_BASE}/profile`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (res.ok) {
        const data = await res.json();
        setTokens(data.tokens ?? null);
      } else {
        console.error("[profile] Failed to fetch:", res.status);
      }
    } catch (error) {
      console.error("[profile]", error);
    }
  }, []);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      if (!data.session) {
        router.push("/");
      } else {
        // 세션 확인 후 즉시 토큰 가져오기
        fetchProfile(data.session.access_token);
      }
      setIsLoading(false);
    });

    const { data: listener } = supabase.auth.onAuthStateChange((_event, newSession) => {
      setSession(newSession);
      if (!newSession) {
        router.push("/");
      } else {
        // 세션 변경 시 토큰 가져오기
        fetchProfile(newSession.access_token);
      }
    });

    return () => {
      listener.subscription.unsubscribe();
    };
  }, [router, fetchProfile]);

  // Gradio에서 postMessage로 토큰 업데이트 받기 (로컬 환경 대비)
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      if (event.data?.type === "token-updated") {
        console.log("[token-updated] Received tokens from Gradio:", event.data.tokens);
        if (event.data.tokens !== undefined && event.data.tokens !== null) {
          setTokens(event.data.tokens);
        }
      }
    };

    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, []);

  // 이미지 생성 후 토큰 업데이트를 위해 5초마다 확인
  useEffect(() => {
    if (!session?.access_token) return;

    // 5초마다 토큰 확인 (이미지 생성 후 업데이트)
    const interval = setInterval(() => {
      fetchProfile(session.access_token);
    }, 5000);

    return () => clearInterval(interval);
  }, [session, fetchProfile]);

  // 토큰이 10개 이하일 때 자동으로 업그레이드 모달 표시
  useEffect(() => {
    if (tokens !== null && tokens <= 10 && tokens > 0) {
      setShowUpgradeModal(true);
    }
  }, [tokens]);


  const handleSignOut = async () => {
    await supabase.auth.signOut();
    router.push("/");
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-gray-600">Loading...</p>
      </div>
    );
  }

  if (!session) {
    return null;
  }

  // Gradio URL에 토큰 전달
  const gradioUrl = `${GRADIO_URL}?token=${encodeURIComponent(session.access_token)}`;

  return (
    <div className="flex min-h-screen flex-col">
      <Header 
        session={session} 
        tokens={tokens} 
        onSignOut={handleSignOut}
        showUpgradeModal={showUpgradeModal}
        onUpgradeModalChange={setShowUpgradeModal}
      />
      <div className="flex-1">
        <iframe
          src={gradioUrl}
          className="h-[calc(100vh-64px)] w-full border-0"
          title="Sprite Studio"
          allow="camera; microphone"
        />
      </div>
    </div>
  );
}

