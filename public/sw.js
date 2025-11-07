// Service Worker for Sloth AI PWA
// Version 1.0.1

const CACHE_NAME = 'sloth-ai-v1.0.1';
const urlsToCache = [
  '/',
  '/index.html',
  '/logo/logo.svg',
  '/og-image.jpg',
  '/manifest.json'
];

// Install event - cache resources
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');

  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Caching app shell');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        console.log('[Service Worker] Installed successfully');
        return self.skipWaiting(); // Activate immediately
      })
      .catch((error) => {
        console.error('[Service Worker] Installation failed:', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');

  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('[Service Worker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
    .then(() => {
      console.log('[Service Worker] Activated successfully');
      return self.clients.claim(); // Take control immediately
    })
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // Only handle http/https requests
  const url = new URL(event.request.url);
  if (!url.protocol.startsWith('http')) {
    return;
  }

  // Skip API calls and webhooks
  if (event.request.url.includes('/api/') ||
      event.request.url.includes('/admin/') ||
      event.request.url.includes('/webhooks/') ||
      event.request.url.includes('/@react-refresh') ||
      event.request.url.includes('/node_modules/') ||
      event.request.url.includes('/@vite/') ||
      event.request.url.includes('/src/')) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Cache hit - return response
        if (response) {
          console.log('[Service Worker] Serving from cache:', event.request.url);
          return response;
        }

        // Clone the request
        const fetchRequest = event.request.clone();

        return fetch(fetchRequest).then((response) => {
          // Check if valid response
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }

          // Clone the response
          const responseToCache = response.clone();

          // Cache the new response
          caches.open(CACHE_NAME)
            .then((cache) => {
              cache.put(event.request, responseToCache);
            })
            .catch((err) => {
              console.warn('[Service Worker] Failed to cache:', err);
            });

          return response;
        });
      })
      .catch((error) => {
        console.error('[Service Worker] Fetch failed:', error);

        // Return offline page if available
        return caches.match('/index.html');
      })
  );
});

// Background sync (for future use)
self.addEventListener('sync', (event) => {
  console.log('[Service Worker] Background sync:', event.tag);

  if (event.tag === 'sync-data') {
    event.waitUntil(syncData());
  }
});

async function syncData() {
  // Implement background sync logic here
  console.log('[Service Worker] Syncing data...');
}

// Push notifications (for future use)
self.addEventListener('push', (event) => {
  console.log('[Service Worker] Push received:', event);

  const options = {
    body: event.data ? event.data.text() : 'New notification',
    icon: '/logo/logo.svg',
    badge: '/logo/logo.svg',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    }
  };

  event.waitUntil(
    self.registration.showNotification('Sloth AI', options)
  );
});

// Notification click
self.addEventListener('notificationclick', (event) => {
  console.log('[Service Worker] Notification clicked:', event);

  event.notification.close();

  event.waitUntil(
    clients.openWindow('/')
  );
});
