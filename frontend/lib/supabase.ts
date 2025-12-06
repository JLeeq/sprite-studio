import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  const missing = [];
  if (!supabaseUrl) missing.push('NEXT_PUBLIC_SUPABASE_URL');
  if (!supabaseAnonKey) missing.push('NEXT_PUBLIC_SUPABASE_ANON_KEY');
  throw new Error(
    `Missing required environment variables: ${missing.join(', ')}. ` +
      'Add them to your Next.js environment (.env.local) and restart the dev server.'
  );
}

if (process.env.NODE_ENV === 'development') {
  console.log('[Supabase] Client initialized:', {
    url: supabaseUrl,
    hasAnonKey: !!supabaseAnonKey,
    keyLength: supabaseAnonKey?.length,
  });
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
  },
});
