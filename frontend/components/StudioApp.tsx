"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";
import { Header } from "@/components/Header";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type TabKey = "character" | "item" | "sprites" | "background" | "animation";

const tabLabels: Record<TabKey, string> = {
  character: "Character",
  item: "Item",
  sprites: "Sprites",
  background: "Background",
  animation: "Sprite Animation",
};

const selectOptions = ["None", "Fantasy", "Sci-Fi", "Pixel", "Retro", "Modern"];
const moodOptions = ["None", "Heroic", "Dark", "Playful", "Epic"];
const colorOptions = ["None", "Warm", "Cool", "Vibrant", "Muted"];
const actionOptions = ["attack", "jump", "walk", "dead"];

type TabOutputs = {
  previewUrl?: string;
  gallery?: string[];
  message?: string;
};

export function StudioApp() {
  const [session, setSession] = useState<Awaited<ReturnType<typeof supabase.auth.getSession>>["data"]["session"] | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authMessage, setAuthMessage] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabKey>("character");
  const [tokens, setTokens] = useState<number | null>(null);
  const [lastImageUrl, setLastImageUrl] = useState<string | null>(null);
  const [tabOutputs, setTabOutputs] = useState<Record<TabKey, TabOutputs>>({
    character: {},
    item: {},
    sprites: {},
    background: {},
    animation: {},
  });
  const [isLoading, setIsLoading] = useState(false);
  const [showSignUpModal, setShowSignUpModal] = useState(false);
  const [signUpEmail, setSignUpEmail] = useState("");
  const [signUpPassword, setSignUpPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const fetchProfile = useCallback(async () => {
    if (!session?.access_token) return;
    try {
      const res = await fetch(`${API_BASE}/profile`, {
        headers: { Authorization: `Bearer ${session.access_token}` },
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setTokens(data.tokens ?? 0);
      setLastImageUrl(data.last_image_url ?? null);
    } catch (error) {
      console.error("[profile]", error);
    }
  }, [session]);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => setSession(data.session));
    const { data: listener } = supabase.auth.onAuthStateChange((_event, newSession) => {
      setSession(newSession);
    });
    return () => {
      listener.subscription.unsubscribe();
    };
  }, []);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  // postMessage로 토큰 업데이트 받기 (iframe에서)
  useEffect(() => {
    const handleTokenUpdate = (event: CustomEvent<number>) => {
      setTokens(event.detail);
    };

    window.addEventListener("token-update", handleTokenUpdate as EventListener);
    return () => window.removeEventListener("token-update", handleTokenUpdate as EventListener);
  }, []);

  const handleSignIn = async (action: "signIn" | "signUp") => {
    console.log("[handleSignIn] Called with action:", action);
    console.log("[handleSignIn] Email value:", email || "(empty)", "| Password length:", password.length);
    console.log("[handleSignIn] Email truthy:", !!email, "| Password truthy:", !!password);
    
    setAuthMessage(null);
    
    if (!email || !password) {
      console.log("[handleSignIn] Validation failed - Missing email or password");
      console.log("[handleSignIn] Email:", email, "| Password:", password ? "***" : "(empty)");
      setAuthMessage("이메일과 비밀번호를 입력해 주세요.");
      return;
    }
    
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      console.log("[handleSignIn] Invalid email format");
      setAuthMessage("올바른 이메일 형식을 입력해 주세요.");
      return;
    }
    
    // Validate password length (Supabase minimum is 6 characters)
    if (password.length < 6) {
      console.log("[handleSignIn] Password too short:", password.length);
      setAuthMessage("비밀번호는 최소 6자 이상이어야 합니다.");
      return;
    }
    
    console.log("[handleSignIn] Validation passed, calling Supabase...");
    
    try {
      if (action === "signUp") {
        console.log("[signUp] Starting sign up process...");
        const { data, error } = await supabase.auth.signUp({ email, password });
        console.log("[signUp] Response received:", { 
          hasData: !!data, 
          hasUser: !!data?.user, 
          hasSession: !!data?.session,
          error: error ? { message: error.message, status: error.status } : null 
        });
        
        if (error) {
          console.error("[signUp] Error details:", error);
          throw error;
        }
        
        // Check if email confirmation is required
        if (data.user && !data.session) {
          console.log("[signUp] User created, email confirmation required");
          setAuthMessage("가입이 완료되었습니다. 이메일을 확인해 주세요.");
        } else if (data.session) {
          console.log("[signUp] User created and logged in automatically");
          setAuthMessage("가입 및 로그인에 성공했습니다.");
          fetchProfile();
        } else {
          console.warn("[signUp] Unexpected response:", data);
        }
      } else {
        console.log("[signIn] Starting sign in process...");
        const { data, error } = await supabase.auth.signInWithPassword({ email, password });
        console.log("[signIn] Response received:", { 
          hasData: !!data, 
          hasSession: !!data?.session,
          error: error ? { message: error.message, status: error.status } : null 
        });
        
        if (error) {
          console.error("[signIn] Error details:", error);
          throw error;
        }
        setAuthMessage("로그인에 성공했습니다.");
        fetchProfile();
      }
    } catch (error: any) {
      console.error("[handleSignIn] Full error:", error);
      // More detailed error messages
      if (error?.status === 400) {
        if (error?.message?.includes("Invalid login credentials")) {
          setAuthMessage("이메일 또는 비밀번호가 올바르지 않습니다.");
        } else if (error?.message?.includes("Email not confirmed")) {
          setAuthMessage("이메일 인증이 완료되지 않았습니다. 이메일을 확인해 주세요.");
        } else {
          setAuthMessage(`로그인 실패: ${error.message ?? "알 수 없는 오류"}`);
        }
      } else {
        setAuthMessage(error.message ?? "로그인 중 오류가 발생했습니다.");
      }
    }
  };

  const handleGoogleSignIn = async () => {
    setAuthMessage(null);
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}`,
        },
      });
      if (error) {
        console.error("[Google Sign In] Error:", error);
        setAuthMessage(`Google 로그인 실패: ${error.message}`);
      }
      // OAuth redirect will happen automatically
    } catch (error: any) {
      console.error("[handleGoogleSignIn] Full error:", error);
      setAuthMessage(error.message ?? "Google 로그인 중 오류가 발생했습니다.");
    }
  };

  const handleSignUp = async () => {
    setAuthMessage(null);
    
    if (!signUpEmail || !signUpPassword || !confirmPassword) {
      setAuthMessage("모든 필드를 입력해 주세요.");
      return;
    }
    
    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(signUpEmail)) {
      setAuthMessage("올바른 이메일 형식을 입력해 주세요.");
      return;
    }
    
    // Validate password length
    if (signUpPassword.length < 6) {
      setAuthMessage("비밀번호는 최소 6자 이상이어야 합니다.");
      return;
    }
    
    // Validate password match
    if (signUpPassword !== confirmPassword) {
      setAuthMessage("비밀번호가 일치하지 않습니다.");
      return;
    }
    
    try {
      console.log("[SignUp Modal] Starting sign up process...");
      const { data, error } = await supabase.auth.signUp({ 
        email: signUpEmail, 
        password: signUpPassword 
      });
      
      console.log("[SignUp Modal] Response:", { 
        hasData: !!data, 
        hasUser: !!data?.user, 
        hasSession: !!data?.session,
        error: error ? { message: error.message, status: error.status } : null 
      });
      
      if (error) {
        console.error("[SignUp Modal] Error details:", error);
        setAuthMessage(`가입 실패: ${error.message}`);
        return;
      }
      
      // Check if email confirmation is required
      if (data.user && !data.session) {
        setAuthMessage("가입이 완료되었습니다. 이메일을 확인해 주세요.");
        setShowSignUpModal(false);
        setSignUpEmail("");
        setSignUpPassword("");
        setConfirmPassword("");
      } else if (data.session) {
        setAuthMessage("가입 및 로그인에 성공했습니다.");
        setShowSignUpModal(false);
        setSignUpEmail("");
        setSignUpPassword("");
        setConfirmPassword("");
        fetchProfile();
      }
    } catch (error: any) {
      console.error("[SignUp Modal] Full error:", error);
      setAuthMessage(error.message ?? "가입 중 오류가 발생했습니다.");
    }
  };

  const router = useRouter();

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    setSession(null);
    setTokens(null);
    setLastImageUrl(null);
    setTabOutputs({
      character: {},
      item: {},
      sprites: {},
      background: {},
      animation: {},
    });
    setAuthMessage("로그아웃되었습니다.");
  };

  const handleOpenStudio = () => {
    router.push("/studio");
  };

  const activeClass = useCallback(
    (tab: TabKey) =>
      `rounded-full px-4 py-2 text-sm font-semibold transition-all ${
        tab === activeTab ? "bg-[var(--enhanced-accent)] text-white" : "bg-white/20 text-white hover:bg-white/30"
      }`,
    [activeTab]
  );

  const saveOutputs = useCallback((tab: TabKey, payload: TabOutputs) => {
    setTabOutputs((prev) => ({ ...prev, [tab]: payload }));
  }, []);

  const onSubmit =
    (tab: TabKey, endpoint: string, buildFormData: (event: FormEvent<HTMLFormElement>) => FormData) =>
    async (event: FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      if (!session?.access_token) {
        setAuthMessage("먼저 로그인해 주세요.");
        return;
      }
      setIsLoading(true);
      try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
          method: "POST",
          headers: { Authorization: `Bearer ${session.access_token}` },
          body: buildFormData(event),
        });
        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.detail || data.message || "생성에 실패했습니다.");
        }
        if (typeof data.tokens === "number") setTokens(data.tokens);
        if (data.last_image_url) setLastImageUrl(data.last_image_url);
        saveOutputs(tab, {
          previewUrl: data.image_url ?? data.preview_url ?? tabOutputs[tab]?.previewUrl,
          gallery: data.image_urls ?? tabOutputs[tab]?.gallery,
          message: data.message ?? "완료되었습니다.",
        });
        setAuthMessage(null);
      } catch (error: any) {
        saveOutputs(tab, { ...tabOutputs[tab], message: error.message ?? "오류가 발생했습니다." });
      } finally {
        setIsLoading(false);
      }
    };

  const renderStatus = (tab: TabKey) => {
    const output = tabOutputs[tab];
    if (!output) return null;
    return (
      <div className="space-y-2 rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-white/80">
        {output.message && <p>{output.message}</p>}
        {output.previewUrl && (
          <div>
            <p className="text-xs uppercase tracking-wide text-white/60">Latest Preview</p>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={output.previewUrl} alt={`${tab} preview`} className="mt-2 w-full rounded-lg border border-white/20" />
          </div>
        )}
        {output.gallery && (
          <div className="grid grid-cols-2 gap-2">
            {output.gallery.map((url) => (
              // eslint-disable-next-line @next/next/no-img-element
              <img key={url} src={url} alt="frame" className="rounded-lg border border-white/20" />
            ))}
          </div>
        )}
      </div>
    );
  };

  const sharedSelect = (name: string, label: string) => (
    <label className="text-sm text-white/70">
      {label}
      <select name={name} defaultValue="None" className="mt-1 w-full rounded-xl border border-white/20 bg-white/10 p-2 text-white">
        {selectOptions.map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
      </select>
    </label>
  );

  const content = useMemo(() => {
    if (!session) {
      return (
        <div className="space-y-16">
          {/* Hero Section */}
          <div className="text-center py-12">
            <h1 className="pixel-font text-5xl font-bold text-black mb-4">Sprite Studio</h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Create stunning 2D game assets with AI-powered generation. 
              Characters, sprites, backgrounds, and more.
            </p>
          </div>

          {/* Login Form */}
          <div className="mx-auto w-full max-w-md space-y-4 rounded-3xl border border-white/10 bg-white/10 p-6 text-white">
            <h2 className="pixel-font text-center text-2xl font-semibold text-black">Sign in to Sprite Studio</h2>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => {
                const newValue = e.target.value;
                console.log("[Email Input] onChange:", newValue);
                setEmail(newValue);
              }}
              className="w-full rounded-2xl border border-white/20 bg-black/30 p-3 text-white"
            />
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => {
                const newValue = e.target.value;
                console.log("[Password Input] onChange, length:", newValue.length);
                setPassword(newValue);
              }}
              className="w-full rounded-2xl border border-white/20 bg-black/30 p-3 text-white"
            />
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => {
                  console.log("[UI] Log In button clicked");
                  handleSignIn("signIn");
                }}
                className="pixel-font flex-1 rounded-2xl bg-[var(--enhanced-accent)] py-3 font-semibold text-black"
              >
                Log In
              </button>
              <button
                type="button"
                onClick={() => {
                  console.log("[UI] Create Account button clicked - opening modal");
                  setShowSignUpModal(true);
                  setAuthMessage(null);
                }}
                className="pixel-font flex-1 rounded-2xl bg-[var(--enhanced-accent)] py-3 font-semibold text-black opacity-80 hover:opacity-100"
              >
                Create Account
              </button>
            </div>
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-white/20"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white/10 text-white/60">or</span>
              </div>
            </div>
            <button
              type="button"
              onClick={handleGoogleSignIn}
              className="w-full rounded-2xl border-2 border-white/40 bg-white/10 py-3 font-semibold text-black hover:bg-white/20 transition-colors flex items-center justify-center gap-3 shadow-lg"
            >
              <svg className="w-6 h-6" viewBox="0 0 24 24">
                <path
                  fill="#4285F4"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="#34A853"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="#FBBC05"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="#EA4335"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
              <span className="pixel-font text-black">Continue with Google</span>
            </button>
            {authMessage && <p className="text-center text-sm text-white/70">{authMessage}</p>}
          </div>

          {/* Features Section */}
          <div className="py-16">
            <h2 className="pixel-font text-3xl font-bold text-center text-black mb-12">
              Powerful Features for Game Developers
            </h2>
            <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3 max-w-6xl mx-auto">
              <div className="rounded-3xl border border-white/10 bg-white/10 p-6 text-center hover:bg-white/20 transition-colors">
                <div className="text-4xl mb-4">🎨</div>
                <h3 className="text-xl font-semibold text-black mb-2">Character Generation</h3>
                <p className="text-gray-600">
                  Create unique characters with customizable styles, moods, and color palettes. Perfect for any game genre.
                </p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/10 p-6 text-center hover:bg-white/20 transition-colors">
                <div className="text-4xl mb-4">🏃</div>
                <h3 className="text-xl font-semibold text-black mb-2">Sprite Animation</h3>
                <p className="text-gray-600">
                  Generate animated sprite sheets for walk, run, jump, attack, and more. Ready-to-use in your game engine.
                </p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/10 p-6 text-center hover:bg-white/20 transition-colors">
                <div className="text-4xl mb-4">🌄</div>
                <h3 className="text-xl font-semibold text-black mb-2">Background Design</h3>
                <p className="text-gray-600">
                  Design immersive game backgrounds with various orientations. From fantasy landscapes to sci-fi cities.
                </p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/10 p-6 text-center hover:bg-white/20 transition-colors">
                <div className="text-4xl mb-4">⚔️</div>
                <h3 className="text-xl font-semibold text-black mb-2">Item Generation</h3>
                <p className="text-gray-600">
                  Create weapons, armor, potions, and other game items with consistent art styles for your inventory.
                </p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/10 p-6 text-center hover:bg-white/20 transition-colors">
                <div className="text-4xl mb-4">🎮</div>
                <h3 className="text-xl font-semibold text-black mb-2">Pixel Art Mode</h3>
                <p className="text-gray-600">
                  Toggle pixel art mode for retro-style games. Perfect for platformers and classic RPGs.
                </p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/10 p-6 text-center hover:bg-white/20 transition-colors">
                <div className="text-4xl mb-4">⚡</div>
                <h3 className="text-xl font-semibold text-black mb-2">AI-Powered</h3>
                <p className="text-gray-600">
                  Powered by Google Gemini AI for high-quality, consistent game asset generation in seconds.
                </p>
              </div>
            </div>
          </div>

          {/* How It Works Section */}
          <div className="py-16 bg-white/5 rounded-3xl">
            <h2 className="pixel-font text-3xl font-bold text-center text-black mb-12">
              How It Works
            </h2>
            <div className="flex flex-col md:flex-row justify-center items-center gap-8 max-w-4xl mx-auto px-6">
              <div className="text-center flex-1">
                <div className="w-16 h-16 rounded-full bg-[var(--enhanced-accent)] text-white text-2xl font-bold flex items-center justify-center mx-auto mb-4">1</div>
                <h3 className="font-semibold text-black mb-2">Describe</h3>
                <p className="text-gray-600">Enter a description of the asset you want to create</p>
              </div>
              <div className="hidden md:block text-3xl text-gray-400">→</div>
              <div className="text-center flex-1">
                <div className="w-16 h-16 rounded-full bg-[var(--enhanced-accent)] text-white text-2xl font-bold flex items-center justify-center mx-auto mb-4">2</div>
                <h3 className="font-semibold text-black mb-2">Generate</h3>
                <p className="text-gray-600">AI creates your asset based on your description</p>
              </div>
              <div className="hidden md:block text-3xl text-gray-400">→</div>
              <div className="text-center flex-1">
                <div className="w-16 h-16 rounded-full bg-[var(--enhanced-accent)] text-white text-2xl font-bold flex items-center justify-center mx-auto mb-4">3</div>
                <h3 className="font-semibold text-black mb-2">Download</h3>
                <p className="text-gray-600">Save your assets and use them in your game</p>
              </div>
            </div>
          </div>

          {/* Game Showcase Section */}
          <div className="py-16 bg-gradient-to-b from-white/5 to-white/10 rounded-3xl">
            <h2 className="pixel-font text-3xl font-bold text-center text-black mb-4">
              Made with Sprite Studio
            </h2>
            <p className="text-center text-gray-600 mb-8 max-w-2xl mx-auto">
              Check out this game created entirely using assets generated by Sprite Studio!
            </p>
            
            {/* Game Preview Images */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto mb-8 px-6">
              <div className="rounded-2xl overflow-hidden border border-white/20 shadow-lg hover:shadow-xl transition-shadow">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img 
                  src="/images/gameref_1.png" 
                  alt="Game Preview 1" 
                  className="w-full h-auto object-cover"
                />
              </div>
              <div className="rounded-2xl overflow-hidden border border-white/20 shadow-lg hover:shadow-xl transition-shadow">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img 
                  src="/images/gameref_2.png" 
                  alt="Game Preview 2" 
                  className="w-full h-auto object-cover"
                />
              </div>
            </div>

            {/* Sprite Actions Showcase */}
            <div className="text-center mb-8">
              <h3 className="text-xl font-semibold text-black mb-4">
                🎮 AI-Generated Sprite Actions
              </h3>
              <p className="text-gray-600 mb-6">
                These character animations were created using our Sprite Animation feature
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto px-6">
                <div className="rounded-2xl overflow-hidden border border-white/20 shadow-lg bg-white/5 p-4">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img 
                    src="/images/gameref_3.png" 
                    alt="Sprite Action 1" 
                    className="w-full h-auto object-contain rounded-lg"
                  />
                  <p className="text-sm text-gray-500 mt-2">Character Action Sprites</p>
                </div>
                <div className="rounded-2xl overflow-hidden border border-white/20 shadow-lg bg-white/5 p-4">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img 
                    src="/images/gameref_4.png" 
                    alt="Sprite Action 2" 
                    className="w-full h-auto object-contain rounded-lg"
                  />
                  <p className="text-sm text-gray-500 mt-2">Animation Frames</p>
                </div>
              </div>
            </div>

            {/* Play Game Button */}
            <div className="text-center">
              <a
                href="https://gd.games/games/feac74c4-ee1a-4858-949b-bea628e5a081"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-3 pixel-font rounded-2xl bg-gradient-to-r from-purple-600 to-indigo-600 px-8 py-4 text-xl font-semibold text-white hover:from-purple-700 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl"
              >
                <span className="text-2xl">🎮</span>
                Play the Game Now
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
              <p className="text-sm text-gray-500 mt-3">
                Play directly in your browser - no download required!
              </p>
            </div>
          </div>

          {/* CTA Section */}
          <div className="text-center py-12">
            <h2 className="pixel-font text-2xl font-bold text-black mb-4">
              Ready to create amazing game assets?
            </h2>
            <p className="text-gray-600 mb-6">Sign up now and get free tokens to start generating!</p>
            <button
              type="button"
              onClick={() => {
                setShowSignUpModal(true);
                setAuthMessage(null);
              }}
              className="pixel-font rounded-2xl bg-[var(--enhanced-accent)] px-8 py-4 text-xl font-semibold text-black hover:opacity-90 transition-opacity"
            >
              Get Started Free
            </button>
          </div>
        </div>
      );
    }

    return (
      <div className="flex min-h-screen flex-col">
        <Header session={session} tokens={tokens} onSignOut={handleSignOut} />
        <div className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-4 py-10">
          <div className="space-y-8">
            {/* Welcome Section */}
            <div className="rounded-3xl border border-white/10 bg-white/10 p-8 text-center text-white">
              <h1 className="pixel-font mb-4 text-3xl font-semibold text-black">Welcome to Sprite Studio</h1>
              <p className="mb-6 text-lg text-gray-700">
                Create amazing 2D game assets with AI-powered generation
              </p>
              {tokens !== null && (
                <div className="mb-8 text-center">
                  <span className="text-gray-500 text-sm">Available Credits</span>
                  <p className="text-3xl font-bold text-[var(--enhanced-accent)]">
                    {tokens} <span className="text-lg font-normal text-gray-600">tokens</span>
                  </p>
                </div>
              )}
              <button
                onClick={handleOpenStudio}
                className="pixel-font rounded-2xl bg-[var(--enhanced-accent)] px-8 py-4 text-xl font-semibold text-black hover:opacity-90 transition-opacity shadow-lg"
              >
                Open Sprite Studio
              </button>
            </div>

            {/* Features Section */}
            <div className="grid gap-6 md:grid-cols-2">
              <div className="rounded-3xl border border-white/10 bg-white/10 p-6 text-white">
                <h3 className="mb-2 text-xl font-semibold text-black">Character Generation</h3>
                <p className="text-sm text-gray-700">
                  Create unique characters with customizable styles, moods, and color palettes
                </p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/10 p-6 text-white">
                <h3 className="mb-2 text-xl font-semibold text-black">Sprite Animation</h3>
                <p className="text-sm text-gray-700">
                  Generate animated sprites for walk, run, jump, attack, and more
                </p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/10 p-6 text-white">
                <h3 className="mb-2 text-xl font-semibold text-black">Background & Items</h3>
                <p className="text-sm text-gray-700">
                  Design immersive backgrounds and game items with AI assistance
                </p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/10 p-6 text-white">
                <h3 className="mb-2 text-xl font-semibold text-black">Token System</h3>
                <p className="text-sm text-gray-700">
                  Each generation consumes one token. Upgrade your plan for more tokens
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }, [session, email, password, authMessage, tokens, lastImageUrl, handleSignOut, handleOpenStudio]);

  return (
    <>
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-4 py-10">{content}</div>
      {showSignUpModal && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          onClick={(e) => {
            if (e.target === e.currentTarget) {
              setShowSignUpModal(false);
              setAuthMessage(null);
            }
          }}
        >
          <div 
            className="bg-white/95 backdrop-blur-md rounded-3xl border border-white/20 shadow-2xl max-w-md w-full p-6 space-y-4"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="pixel-font text-2xl font-semibold text-black">Create Account</h2>
              <button
                type="button"
                onClick={() => {
                  setShowSignUpModal(false);
                  setAuthMessage(null);
                  setSignUpEmail("");
                  setSignUpPassword("");
                  setConfirmPassword("");
                }}
                className="text-gray-500 hover:text-gray-700 text-2xl leading-none"
              >
                ×
              </button>
            </div>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  placeholder="you@example.com"
                  value={signUpEmail}
                  onChange={(e) => setSignUpEmail(e.target.value)}
                  className="w-full rounded-2xl border border-gray-300 bg-white p-3 text-gray-900 focus:outline-none focus:ring-2 focus:ring-[var(--enhanced-accent)]"
                  autoFocus
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Password
                </label>
                <input
                  type="password"
                  placeholder="•••••••• (minimum 6 characters)"
                  value={signUpPassword}
                  onChange={(e) => setSignUpPassword(e.target.value)}
                  className="w-full rounded-2xl border border-gray-300 bg-white p-3 text-gray-900 focus:outline-none focus:ring-2 focus:ring-[var(--enhanced-accent)]"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Confirm Password
                </label>
                <input
                  type="password"
                  placeholder="••••••••"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full rounded-2xl border border-gray-300 bg-white p-3 text-gray-900 focus:outline-none focus:ring-2 focus:ring-[var(--enhanced-accent)]"
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      handleSignUp();
                    }
                  }}
                />
              </div>
              
              {authMessage && (
                <p className={`text-center text-sm ${
                  authMessage.includes("완료") || authMessage.includes("성공") 
                    ? "text-green-600" 
                    : "text-red-600"
                }`}>
                  {authMessage}
                </p>
              )}
              
              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => {
                    setShowSignUpModal(false);
                    setAuthMessage(null);
                    setSignUpEmail("");
                    setSignUpPassword("");
                    setConfirmPassword("");
                  }}
                  className="flex-1 rounded-2xl border-2 border-gray-300 bg-white py-3 font-semibold text-gray-700 hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleSignUp}
                  disabled={isLoading}
                  className="pixel-font flex-1 rounded-2xl bg-[var(--enhanced-accent)] py-3 font-semibold text-black hover:opacity-90 disabled:opacity-50"
                >
                  {isLoading ? "Creating..." : "Create Account"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

