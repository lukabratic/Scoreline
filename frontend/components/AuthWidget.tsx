"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import type { Session } from "@supabase/supabase-js";
import { supabase } from "@/lib/supabaseClient";

export function AuthWidget() {
  const [session, setSession] = useState<Session | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      setLoaded(true);
    });
    const { data: subscription } = supabase.auth.onAuthStateChange((_event, newSession) => {
      setSession(newSession);
    });
    return () => subscription.subscription.unsubscribe();
  }, []);

  if (!loaded) return null;

  if (!session) {
    return (
      <Link
        href="/sign-in"
        className="rounded-full border border-border px-3 py-1 text-sm font-medium text-foreground hover:border-accent hover:text-accent"
      >
        Sign in
      </Link>
    );
  }

  return (
    <div className="flex items-center gap-2 text-sm">
      <span className="text-muted-foreground">{session.user.email}</span>
      <button
        onClick={() => supabase.auth.signOut()}
        className="rounded-full border border-border px-3 py-1 font-medium text-foreground hover:border-accent hover:text-accent"
      >
        Sign out
      </button>
    </div>
  );
}
