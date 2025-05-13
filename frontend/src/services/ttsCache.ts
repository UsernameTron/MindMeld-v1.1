// Utility for IndexedDB-based TTS audio caching
// Phase 1: Performance & Cost

const DB_NAME = 'TTSCacheDB';
const STORE_NAME = 'audio';
const DB_VERSION = 1;

export function openTTSCacheDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = () => {
      req.result.createObjectStore(STORE_NAME);
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

export async function cacheAudio(hash: string, audioBlob: Blob) {
  const db = await openTTSCacheDB();
  const tx = db.transaction(STORE_NAME, 'readwrite');
  tx.objectStore(STORE_NAME).put(audioBlob, hash);
  return new Promise((resolve, reject) => {
    tx.oncomplete = resolve;
    tx.onerror = reject;
  });
}

export async function getCachedAudio(hash: string): Promise<Blob | undefined> {
  const db = await openTTSCacheDB();
  const tx = db.transaction(STORE_NAME, 'readonly');
  return new Promise((resolve, reject) => {
    const req = tx.objectStore(STORE_NAME).get(hash);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}
