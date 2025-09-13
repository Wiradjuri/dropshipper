# Deploying Dropshipper to Vercel (Frontend)

## 1. Create a New Vercel Project
- Go to https://vercel.com/new
- Import your GitHub repo (select `dropshipper`)
- Set **Root Directory**: `frontend`
- Set **Framework Preset**: Next.js
- Set **Node Version**: 20.x

## 2. Set Environment Variables
- Add the following env var:
  - `NEXT_PUBLIC_API_BASE_URL=https://<your-backend-domain>`
    - (Replace with your deployed backend URL after backend is live)

## 3. (Optional) Configure Image Domains
- If you use remote images, add a `vercel.json` with `images.remotePatterns` as needed.

## 4. Deploy
- Click **Deploy**. Wait for build to complete.
- Visit your Vercel URL (e.g., `https://dropshipper-<hash>.vercel.app`)

## 5. Update API URL for Production
- After backend is deployed, update `NEXT_PUBLIC_API_BASE_URL` in Vercel Project Settings to point to your backend.
- Redeploy frontend if needed.

---

## Quick Reference
- **Root Directory**: `frontend`
- **Framework Preset**: Next.js
- **Node Version**: 20.x
- **Env**: `NEXT_PUBLIC_API_BASE_URL=https://<your-backend-domain>`
