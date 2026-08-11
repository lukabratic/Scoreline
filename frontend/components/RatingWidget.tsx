"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import type { Session } from "@supabase/supabase-js";
import { getMyRating, getRatingSummary, submitRating } from "@/lib/api";
import type { RatingSummary } from "@/lib/types";
import { supabase } from "@/lib/supabaseClient";

const SCORES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

export function RatingWidget({ gameId }: { gameId: number }) {
  const [session, setSession] = useState<Session | null>(null);
  const [summary, setSummary] = useState<RatingSummary | null>(null);
  const [myScore, setMyScore] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getRatingSummary(gameId).then(setSummary).catch(() => setSummary(null));
  }, [gameId]);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => setSession(data.session));
    const { data: subscription } = supabase.auth.onAuthStateChange((_event, newSession) => {
      setSession(newSession);
    });
    return () => subscription.subscription.unsubscribe();
  }, []);

  useEffect(() => {
    if (!session) {
      setMyScore(null);
      return;
    }
    getMyRating(gameId, session.access_token)
      .then((rating) => setMyScore(rating?.score ?? null))
      .catch(() => setMyScore(null));
  }, [gameId, session]);

  async function handleRate(score: number) {
    if (!session) return;
    setSubmitting(true);
    setError(null);
    try {
      await submitRating(gameId, score, session.access_token);
      setMyScore(score);
      const freshSummary = await getRatingSummary(gameId);
      setSummary(freshSummary);
    } catch {
      setError("Couldn't submit your rating. Try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex flex-col items-center gap-3 rounded-xl border border-border bg-surface p-6">
      <div className="text-sm text-muted-foreground">
        {summary && summary.count > 0
          ? `Community score: ${summary.average?.toFixed(1)} (${summary.count} rating${summary.count === 1 ? "" : "s"})`
          : "No community ratings yet"}
      </div>

      {session ? (
        <>
          <div className="flex gap-1">
            {SCORES.map((score) => (
              <button
                key={score}
                onClick={() => handleRate(score)}
                disabled={submitting}
                className={`flex h-8 w-8 items-center justify-center rounded-md text-sm font-medium transition-colors disabled:opacity-50 ${
                  myScore === score
                    ? "bg-accent text-white"
                    : "border border-border text-muted-foreground hover:border-accent hover:text-accent"
                }`}
              >
                {score}
              </button>
            ))}
          </div>
          {myScore !== null && (
            <p className="text-xs text-muted-foreground">Your rating: {myScore}</p>
          )}
          {error && <p className="text-xs text-red-400">{error}</p>}
        </>
      ) : (
        <Link href="/sign-in" className="text-sm text-accent hover:underline">
          Sign in to rate this game
        </Link>
      )}
    </div>
  );
}
