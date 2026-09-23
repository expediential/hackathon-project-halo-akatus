# Emergency Response Intelligence frontend

Next.js App Router implementation for the Emergency Response Intelligence Center.

Run from this directory:

```bash
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL` to the backend origin when available. API calls fall back to the local mock adapter when the development backend is unavailable, allowing all screens to be demonstrated without a backend.

Backend contract assumptions: REST endpoints from the project brief return JSON objects/arrays using the `src/types/index.ts` shapes. The report-submission and demo endpoints should return `{ "accepted": true }` after accepting the requested operation.
