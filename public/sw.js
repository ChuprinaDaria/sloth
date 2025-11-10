// Service Worker for PWA
const CACHE_NAME = 'sloth-v2'; // Updated version to clear old cache
const urlsToCache = [
  '/',
  '/index.html',
  '/logo/logo.svg',
  '/manifest.json',
  '/site.webmanifest',
];

// Install event
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        // Use addAll with error handling - only cache files that exist
        return Promise.allSettled(
          urlsToCache.map(url => 
            cache.add(url).catch(err => {
              console.log(`[Service Worker] Failed to cache ${url}:`, err);
              return null; // Continue even if one file fails
            })
          )
        );
      })
      .then(() => {
        console.log('[Service Worker] Cache installed');
      })
      .catch(err => {
        console.error('[Service Worker] Install error:', err);
      })
  );
  self.skipWaiting();
});

// Activate event
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event - Network first, fallback to cache
self.addEventListener('fetch', (event) => {
  // Skip cross-origin requests
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Only cache successful responses
        if (response.status === 200) {
          // Clone the response
          const responseToCache = response.clone();

          // Cache in background (don't block response)
          caches.open(CACHE_NAME)
            .then((cache) => {
              // Only cache if response is ok
              if (responseToCache.ok) {
                cache.put(event.request, responseToCache).catch(err => {
                  console.log(`[Service Worker] Failed to cache ${event.request.url}:`, err);
                });
              }
            })
            .catch(err => {
              console.log(`[Service Worker] Cache open error:`, err);
            });
        }

        return response;
      })
      .catch(() => {
        // Fallback to cache if network fails
        return caches.match(event.request).then(cachedResponse => {
          if (cachedResponse) {
            console.log(`[Service Worker] Serving from cache: ${event.request.url}`);
          }
          return cachedResponse;
        });
      })
  );
});
