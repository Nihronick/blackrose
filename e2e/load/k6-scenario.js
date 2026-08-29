import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom failure rate metric
export const errorRate = new Rate('errors');

// 200+ concurrent virtual users load testing scenario
export const options = {
  stages: [
    { duration: '30s', target: 50 },   // Warm-up to 50 users
    { duration: '1m',  target: 150 },  // Ramp up to 150 users
    { duration: '2m',  target: 250 },  // Peak load: 250 concurrent users
    { duration: '1m',  target: 250 },  // Sustained peak load
    { duration: '30s', target: 0 },    // Ramp down to 0
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500', 'p(99)<1000'], // 95% of requests must complete under 500ms
    'errors': ['rate<0.01'],                          // Less than 1% errors
    'http_req_failed': ['rate<0.01'],
  },
};

const BASE_URL = __ENV.API_URL || 'http://localhost:8000';

export default function () {
  // 1. Health check & Categories load (simulates opening app)
  const healthRes = http.get(`${BASE_URL}/api/health`);
  check(healthRes, {
    'health status is 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(0.5);

  const catRes = http.get(`${BASE_URL}/api/categories`);
  const catOk = check(catRes, {
    'categories status is 200': (r) => r.status === 200,
    'categories has items': (r) => {
      try {
        const body = JSON.parse(r.body);
        return Array.isArray(body.categories) || Array.isArray(body);
      } catch (e) {
        return false;
      }
    },
  });
  if (!catOk) errorRate.add(1);

  sleep(1);

  // 2. Search query test (simulates user searching for guides)
  const searchTerms = ['boss', 'skill', 'build', 'spirit', 'promotion'];
  const term = searchTerms[Math.floor(Math.random() * searchTerms.length)];
  const searchRes = http.get(`${BASE_URL}/api/search?q=${term}`);
  check(searchRes, {
    'search status is 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(1.5);

  // 3. Specific guide fetch (simulates reading a guide)
  const guideRes = http.get(`${BASE_URL}/api/guide/beginner-faq`);
  check(guideRes, {
    'guide fetch status is 200 or 404': (r) => r.status === 200 || r.status === 404,
  }) || errorRate.add(1);

  sleep(2);
}
