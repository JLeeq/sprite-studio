"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { supabase } from "@/lib/supabase";

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
  const [tabOutputs, setTabOutputs] = useState<Record<TabKey, TabOutputs>>({});
  const [isLoading, setIsLoading] = useState(false);

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

  const handleSignIn = async (action: "signIn" | "signUp") => {
    setAuthMessage(null);
    if (!email || !password) {
      setAuthMessage("이메일과 비밀번호를 입력해 주세요.");
      return;
    }
    try {
      if (action === "signUp") {
        const { error } = await supabase.auth.signUp({ email, password });
        if (error) throw error;
        setAuthMessage("가입이 완료되었습니다. 이메일을 확인해 주세요.");
      } else {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
        setAuthMessage("로그인에 성공했습니다.");
        fetchProfile();
      }
    } catch (error: any) {
      setAuthMessage(error.message ?? "로그인 중 오류가 발생했습니다.");
    }
  };

  const handleSignOut = async () => {
    await supabase.auth.signOut();
    setSession(null);
    setTokens(null);
    setLastImageUrl(null);
    setTabOutputs({});
    setAuthMessage("로그아웃되었습니다.");
  };

  const activeClass = useCallback(
    (tab: TabKey) =>
      `rounded-full px-4 py-2 text-sm font-semibold transition-all ${
        tab === activeTab ? "bg-[var(--enhanced-accent)] text-white" : "bg-white/20 text-white hover:bg-white/30"
      }`,
    [activeTab]
  );

  const saveOutputs = (tab: TabKey, payload: TabOutputs) => {
    setTabOutputs((prev) => ({ ...prev, [tab]: payload }));
  };

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
        <div className="mx-auto w-full max-w-md space-y-4 rounded-3xl border border-white/10 bg-white/10 p-6 text-white">
          <h2 className="pixel-font text-center text-2xl font-semibold text-black">Sign in to Sprite Studio</h2>
          <input
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-2xl border border-white/20 bg-black/30 p-3 text-white"
          />
          <input
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-2xl border border-white/20 bg-black/30 p-3 text-white"
          />
          <div className="flex gap-3">
            <button
              onClick={() => handleSignIn("signIn")}
              className="pixel-font flex-1 rounded-2xl bg-[var(--enhanced-accent)] py-3 font-semibold text-black"
            >
              Sign In
            </button>
            <button
              onClick={() => handleSignIn("signUp")}
              className="pixel-font flex-1 rounded-2xl border border-white/30 py-3 font-semibold text-black"
            >
              Create Account
            </button>
          </div>
          {authMessage && <p className="text-center text-sm text-white/70">{authMessage}</p>}
        </div>
      );
    }

    return (
      <div className="space-y-8">
        <div className="flex flex-col gap-4 rounded-3xl border border-white/10 bg-white/10 p-6 text-white md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm uppercase tracking-wide text-white/60">Logged in</p>
            <p className="text-lg font-semibold">{session.user?.email}</p>
            <p className="text-sm text-white/70 mt-1">{tokens !== null ? `Tokens: ${tokens}` : "토큰 정보를 불러오는 중..."}</p>
          </div>
          <button onClick={handleSignOut} className="rounded-2xl border border-white/30 px-4 py-2 text-sm font-semibold">
            Sign Out
          </button>
        </div>

        {lastImageUrl && (
          <div className="space-y-2 rounded-3xl border border-white/10 bg-white/5 p-4 text-white">
            <p className="text-sm uppercase tracking-wide text-white/60">Last generated</p>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={lastImageUrl} alt="Last generated asset" className="w-full rounded-2xl border border-white/20" />
          </div>
        )}

        <div className="flex flex-wrap gap-3">
          {(Object.keys(tabLabels) as TabKey[]).map((tab) => (
            <button key={tab} className={activeClass(tab)} onClick={() => setActiveTab(tab)}>
              {tabLabels[tab]}
            </button>
          ))}
        </div>

        <div className="rounded-3xl border border-white/10 bg-white/5 p-6 text-white">
          {activeTab === "character" && (
            <form className="space-y-4" onSubmit={onSubmit("character", "/generate/character", (ev) => new FormData(ev.currentTarget))}>
              <textarea
                name="character_description"
                required
                placeholder="Describe your hero..."
                className="w-full rounded-2xl border border-white/20 bg-black/30 p-3"
              />
              <div className="grid gap-4 md:grid-cols-2">
                {sharedSelect("art_style", "Art Style")}
                {sharedSelect("mood", "Mood")}
                {sharedSelect("color_palette", "Color Palette")}
                {sharedSelect("character_style", "Character Style")}
              </div>
              <textarea name="additional_notes" placeholder="Additional notes" className="w-full rounded-2xl border border-white/20 bg-black/30 p-3" />
              <label className="flex items-center gap-2 text-sm text-white/70">
                <input type="checkbox" name="pixel_mode" className="h-4 w-4 rounded border-white/30" />
                Pixel mode
              </label>
              <div className="grid gap-4 md:grid-cols-2">
                <label className="text-sm text-white/70">
                  Character Reference
                  <input type="file" name="character_reference_image" accept="image/*" className="mt-1 w-full rounded-2xl border border-dashed border-white/30 p-3" />
                </label>
                <label className="text-sm text-white/70">
                  Item Reference
                  <input type="file" name="item_reference_image" accept="image/*" className="mt-1 w-full rounded-2xl border border-dashed border-white/30 p-3" />
                </label>
              </div>
              <button type="submit" disabled={isLoading} className="w-full rounded-2xl bg-[var(--enhanced-accent)] py-3 text-center font-semibold text-white">
                {isLoading ? "Generating..." : "Generate"}
              </button>
            </form>
          )}

          {activeTab === "item" && (
            <form className="space-y-4" onSubmit={onSubmit("item", "/generate/item", (ev) => new FormData(ev.currentTarget))}>
              <textarea
                name="item_description"
                required
                placeholder="Describe your item..."
                className="w-full rounded-2xl border border-white/20 bg-black/30 p-3"
              />
              <div className="grid gap-4 md:grid-cols-2">
                {sharedSelect("art_style", "Art Style")}
                {sharedSelect("mood", "Mood")}
                {sharedSelect("color_palette", "Color Palette")}
              </div>
              <textarea name="additional_notes" placeholder="Additional notes" className="w-full rounded-2xl border border-white/20 bg-black/30 p-3" />
              <label className="text-sm text-white/70">
                Reference
                <input type="file" name="reference_image" accept="image/*" className="mt-1 w-full rounded-2xl border border-dashed border-white/30 p-3" />
              </label>
              <button type="submit" disabled={isLoading} className="w-full rounded-2xl bg-[var(--enhanced-accent)] py-3 font-semibold text-white">
                {isLoading ? "Generating..." : "Generate"}
              </button>
            </form>
          )}

          {activeTab === "sprites" && (
            <form className="space-y-4" onSubmit={onSubmit("sprites", "/generate/sprites", (ev) => new FormData(ev.currentTarget))}>
              <textarea
                name="character_description"
                required
                placeholder="Describe your character..."
                className="w-full rounded-2xl border border-white/20 bg-black/30 p-3"
              />
              <input
                name="actions_text"
                required
                placeholder="idle, run, jump..."
                className="w-full rounded-2xl border border-white/20 bg-black/30 p-3"
              />
              <label className="text-sm text-white/70">
                Character Reference
                <input type="file" name="reference_image" accept="image/*" className="mt-1 w-full rounded-2xl border border-dashed border-white/30 p-3" />
              </label>
              <button type="submit" disabled={isLoading} className="w-full rounded-2xl bg-[var(--enhanced-accent)] py-3 font-semibold text-white">
                {isLoading ? "Generating..." : "Generate"}
              </button>
            </form>
          )}

          {activeTab === "background" && (
            <form className="space-y-4" onSubmit={onSubmit("background", "/generate/background", (ev) => new FormData(ev.currentTarget))}>
              <textarea
                name="background_description"
                required
                placeholder="Describe your scene..."
                className="w-full rounded-2xl border border-white/20 bg-black/30 p-3"
              />
              <label className="text-sm text-white/70">
                Orientation
                <select name="orientation" className="mt-1 w-full rounded-2xl border border-white/20 bg-white/10 p-2 text-white">
                  <option value="landscape">Landscape</option>
                  <option value="portrait">Portrait</option>
                </select>
              </label>
              <div className="grid gap-4 md:grid-cols-2">
                {sharedSelect("art_style", "Art Style")}
                {sharedSelect("mood", "Mood")}
              </div>
              <textarea name="additional_notes" placeholder="Additional notes" className="w-full rounded-2xl border border-white/20 bg-black/30 p-3" />
              <button type="submit" disabled={isLoading} className="w-full rounded-2xl bg-[var(--enhanced-accent)] py-3 font-semibold text-white">
                {isLoading ? "Generating..." : "Generate"}
              </button>
            </form>
          )}

          {activeTab === "animation" && (
            <form className="space-y-4" onSubmit={onSubmit("animation", "/generate/animation", (ev) => new FormData(ev.currentTarget))}>
              <label className="text-sm text-white/70">
                Character Reference (PNG)
                <input type="file" name="reference_image" accept="image/*" required className="mt-1 w-full rounded-2xl border border-dashed border-white/30 p-3" />
              </label>
              <label className="text-sm text-white/70">
                Action Type
                <select name="action_type" className="mt-1 w-full rounded-2xl border border-white/20 bg-white/10 p-2 text-white">
                  {actionOptions.map((action) => (
                    <option key={action} value={action}>
                      {action}
                    </option>
                  ))}
                </select>
              </label>
              <button type="submit" disabled={isLoading} className="w-full rounded-2xl bg-[var(--enhanced-accent)] py-3 font-semibold text-white">
                {isLoading ? "Generating..." : "Generate"}
              </button>
            </form>
          )}
        </div>

        {renderStatus(activeTab)}
      </div>
    );
  }, [session, email, password, authMessage, activeTab, tokens, lastImageUrl, isLoading, tabOutputs, activeClass, fetchProfile]);

  return <div className="mx-auto flex w-full max-w-5xl flex-col gap-8 px-4 py-10">{content}</div>;
}

