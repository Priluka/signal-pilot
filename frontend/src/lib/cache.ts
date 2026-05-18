/** Tiny in-memory cache for fetch results that don't change during a session.
 *
 * Wraps an async loader: the first call hits the network, subsequent calls
 * for the same key return the cached value immediately. In-flight requests
 * are deduped so simultaneous mounts don't fire N parallel copies.
 *
 * Use only for stable data (the playbook corpus, ticket sample, category
 * counts). Anything that mutates during a session — agent sessions,
 * metrics, chat sessions, batch status — should keep using a plain fetch.
 */
const cache = new Map<string, unknown>();
const inflight = new Map<string, Promise<unknown>>();


export async function cachedFetch<T>(key: string, loader: () => Promise<T>): Promise<T> {
  const hit = cache.get(key);
  if (hit !== undefined) return hit as T;
  const pending = inflight.get(key);
  if (pending) return pending as Promise<T>;
  const promise = (async () => {
    try {
      const value = await loader();
      cache.set(key, value);
      return value;
    } finally {
      inflight.delete(key);
    }
  })();
  inflight.set(key, promise);
  return promise;
}


export function invalidate(key: string): void {
  cache.delete(key);
}


export function invalidateAll(): void {
  cache.clear();
  inflight.clear();
}
