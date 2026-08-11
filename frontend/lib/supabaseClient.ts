import { createClient } from "@supabase/supabase-js";

// Falls back to a placeholder so the app still builds/renders before real Supabase
// credentials are configured in .env.local — auth calls will simply fail until then.
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || "https://placeholder.supabase.co";
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "placeholder-anon-key";

export const supabase = createClient(supabaseUrl, supabaseAnonKey);
