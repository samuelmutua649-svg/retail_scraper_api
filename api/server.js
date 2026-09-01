import Fastify from 'fastify';
import cors from '@fastify/cors';
import { exec } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';
import Database from 'better-sqlite3';
import stringSimilarity from 'string-similarity';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const fastify = Fastify({ logger: true });
await fastify.register(cors, { origin: '*' });

// SQLite Database Setup
const dbPath = path.join(__dirname, '..', 'retail_data.db');
const db = new Database(dbPath);

function fetchHistoryFromDb(query) {
  const terms = query.trim().toLowerCase().split(/\s+/).filter(Boolean).map(t => `%${t}%`);
  if (terms.length === 0) return [];

  let sql = `
    SELECT p.id as product_id, p.store, p.title, p.product_url, ph.price, ph.scraped_at
    FROM products p
    JOIN price_history ph ON p.id = ph.product_id
    WHERE 1=1
  `;
  
  terms.forEach(() => {
    sql += ` AND LOWER(p.title) LIKE ?`;
  });
  sql += ` ORDER BY ph.scraped_at ASC`;

  const stmt = db.prepare(sql);
  const rows = stmt.all(...terms);

  const history = {};
  
  rows.forEach(row => {
    if (!history[row.store]) history[row.store] = {};
    
    if (!history[row.store][row.product_url]) {
      history[row.store][row.product_url] = {
        title: row.title,
        url: row.product_url,
        store: row.store,
        current_price: row.price,
        min_price: row.price,
        max_price: row.price,
        history: []
      };
    }

    const item = history[row.store][row.product_url];
    item.current_price = row.price;
    item.min_price = Math.min(item.min_price, row.price);
    item.max_price = Math.max(item.max_price, row.price);
    item.history.push({ price: row.price, date: row.scraped_at });
  });

  // Flatten into list for clustering
  const allProducts = [];
  for (const store of Object.keys(history)) {
    for (const url of Object.keys(history[store])) {
      allProducts.push(history[store][url]);
    }
  }

  return allProducts;
}

function groupSimilarProducts(products) {
  const clusters = [];
  const SIMILARITY_THRESHOLD = 0.55;

  products.forEach(prod => {
    let matchedCluster = null;

    for (const cluster of clusters) {
      const score = stringSimilarity.compareTwoStrings(
        prod.title.toLowerCase(),
        cluster.representativeTitle.toLowerCase()
      );

      if (score >= SIMILARITY_THRESHOLD) {
        matchedCluster = cluster;
        break;
      }
    }

    if (matchedCluster) {
      matchedCluster.listings.push(prod);
    } else {
      clusters.push({
        representativeTitle: prod.title,
        listings: [prod]
      });
    }
  });

  return clusters;
}

// Scrape API Endpoint
fastify.post('/api/scrape', async (request, reply) => {
  console.log('RECEIVED SCRAPE REQUEST:', request.body);
  const { query } = request.body || {};
  const searchQuery = query || 'laptop';
  const scraperPath = path.join(__dirname,'scraper.py');
  // 1. Log the exact directory and resolved path to the console
console.log('__dirname is:', __dirname);
console.log('scraperPath is:', scraperPath);

  return new Promise((resolve) => {
    exec(`python3 "${scraperPath}" "${searchQuery}"`, (error, stdout, stderr) => {
      if (error) {
        console.error(`Scraper error: ${error.message}`);
        resolve(reply.status(500).send({ success: false, error: error.message }));
        return;
      }
      try {
        const results = JSON.parse(stdout);
        resolve({ success: true, count: results.length, data: results });
      } catch (parseErr) {
        resolve({ success: true, count: 0, raw: stdout });
      }
    });
  });
});
fastify.get('/', async (request, reply) => {
  return { status: 'ok', service: 'Retail Scraper API' };
});

// History & Cross-Store Clustering API Endpoint
fastify.get('/api/products/history', async (request, reply) => {
  const { query } = request.query || {};
  if (!query) return { success: false, message: 'Query parameter is required' };

  const products = fetchHistoryFromDb(query);
  const clusters = groupSimilarProducts(products);

  return { success: true, count: clusters.length, clusters };
});

// Start Fastify Server
const start = async () => {
  try {
    // 1. Read Render's assigned PORT dynamically, fallback to 3000 locally
    const port = process.env.PORT || 3000;
    
    await fastify.listen({ port: Number(port), host: '0.0.0.0' });
    
    // 2. Log the actual dynamic port instead of hardcoded localhost
    console.log(`🚀 Fastify server listening on port ${port}`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();