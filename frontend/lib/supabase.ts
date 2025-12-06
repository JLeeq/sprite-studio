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

// Log configuration in development (without exposing keys)
if (process.env.NODE_ENV === 'development') {
  console.log('[Supabase] Client initialized:', {
    url: supabaseUrl,
    hasAnonKey: !!supabaseAnonKey,
    keyLength: supabaseAnonKey?.length,
  });
}

/**
 * Custom fetch that ensures headers are sent with correct case.
 * Some servers are strict about header case, so we normalize to lowercase.
 */
const customFetch = async (url: string, options: RequestInit = {}) => {
  // Normalize header names to lowercase
  if (options.headers) {
    const headers = new Headers(options.headers);
    const normalizedHeaders = new Headers();
    
    headers.forEach((value, key) => {
      // Ensure 'apikey' is lowercase (Supabase requirement)
      const normalizedKey = key.toLowerCase() === 'apikey' ? 'apikey' : key.toLowerCase();
      normalizedHeaders.set(normalizedKey, value);
    });
    
    return fetch(url, {
      ...options,
      headers: normalizedHeaders,
    });
  }
  
  return fetch(url, options);
};

/**
 * Browser-safe Supabase client using the public anon key.
 * Use this instance for signup/login flows within Next.js.
 */
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
  },
  global: {
    fetch: customFetch,
  },
});



