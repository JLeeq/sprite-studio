"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";
import { useRouter } from "next/navigation";
import { Header } from "@/components/Header";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const GRADIO_URL = process.env.NEXT_PUBLIC_GRADIO_URL ?? "http://localhost:7861";

export default function StudioPage() {
  const [session, setSession] = useState<Awaited<ReturnType<typeof supabase.auth.getSession>>["data"]["session"] | null>(null);
  const [tokens, setTokens] = useState<number | null>(null); // Supabase에서 가져올 때까지 null
  const [isLoading, setIsLoading] = useState(true);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const router = useRouter();

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      if (!data.session) {
        router.push("/");
      } else {
        fetchProfile(data.session.access_token);
      }
      setIsLoading(false);
    });

    const { data: listener } = supabase.auth.onAuthStateChange((_event, newSession) => {
      setSession(newSession);
      if (!newSession) {
        router.push("/");
      } else {
        fetchProfile(newSession.access_token);
      }
    });

    return () => {
      listener.subscription.unsubscribe();
    };
  }, [router]);

  // postMessage로 토큰 업데이트 받기 (iframe에서)
  useEffect(() => {
    const handleMessage = (event: MessageEvent) => {
      // 보안: 프로덕션에서는 origin 체크 필요
      // if (event.origin !== "https://studio.yourdomain.com") return;
      
      if (event.data?.type === "token-updated") {
        console.log("[token-updated] Received tokens:", event.data.tokens);
        if (event.data.tokens !== undefined && event.data.tokens !== null) {
          setTokens(event.data.tokens);
        }
      }
    };

    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, []);

  // 토큰이 10개 이하일 때 자동으로 업그레이드 모달 표시
  useEffect(() => {
    if (tokens !== null && tokens <= 10 && tokens > 0) {
      setShowUpgradeModal(true);
    }
  }, [tokens]);

  const fetchProfile = async (accessToken: string) => {
    try {
      const res = await fetch(`${API_BASE}/profile`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (res.ok) {
        const data = await res.json();
        // Supabase에서 가져온 실제 토큰 값 설정
        setTokens(data.tokens ?? null);
      } else {
        console.error("[profile] Failed to fetch:", res.status);
        // 실패해도 null 유지 (재시도 가능)
      }
    } catch (error) {
      console.error("[profile]", error);
      // 에러 발생 시에도 null 유지 (재시도 가능)
    }
  };

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

