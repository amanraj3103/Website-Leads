# Vercel Deployment Guide

This guide will help you deploy the Dream Axis Lead Collection Website to Vercel.

## Prerequisites

1. A Vercel account (sign up at [vercel.com](https://vercel.com))
2. Google Sheets credentials file (`google_credentials.json`)
3. Google Spreadsheet ID

## Deployment Steps

### 1. Install Vercel CLI (Optional but Recommended)

```bash
npm install -g vercel
```

### 2. Prepare Your Project

Make sure you have:
- ✅ `google_credentials.json` file in the root directory
- ✅ `.env` file with `GOOGLE_SPREADSHEET_ID` (or you'll set it in Vercel dashboard)

### 3. Deploy via Vercel CLI

```bash
cd Website_assistant
vercel login
vercel
```

Follow the prompts:
- Set up and deploy? **Yes**
- Which scope? (Select your account)
- Link to existing project? **No**
- Project name? (Press Enter for default or enter a name)
- Directory? (Press Enter for current directory)
- Override settings? **No**

### 4. Set Environment Variables

After initial deployment, set your environment variables:

**Option A: Via Vercel CLI**
```bash
vercel env add GOOGLE_SPREADSHEET_ID
# Enter your spreadsheet ID when prompted
```

**Option B: Via Vercel Dashboard**
1. Go to your project on [vercel.com](https://vercel.com)
2. Navigate to **Settings** → **Environment Variables**
3. Add:
   - Name: `GOOGLE_SPREADSHEET_ID`
   - Value: Your Google Spreadsheet ID
   - Environment: Production, Preview, Development (select all)

### 5. Add Google Credentials File

**Important:** Use environment variables (more secure, no credentials file committed).

**Recommended: Base64 env var**
1. Convert `google_credentials.json` to base64:
   ```bash
   cat google_credentials.json | base64
   ```
2. Add to Vercel env vars:
   - `GOOGLE_SPREADSHEET_ID` = your sheet ID
   - `GOOGLE_CREDENTIALS_JSON_B64` = (paste base64)
3. Deploy. The app decodes this at runtime; no file commit needed.

### 6. Redeploy

After setting environment variables, redeploy:

```bash
vercel --prod
```

Or trigger a new deployment from the Vercel dashboard.

## Important Notes

### File Storage Limitation

⚠️ **Vercel serverless functions are stateless** - they don't have persistent file storage. 

- The `daily_leads.json` file writing has been removed in the Vercel deployment
- **All data is saved only to Google Sheets**
- Make sure Google Sheets integration is properly configured

### API Endpoints

- `POST /api/submit-lead` - Submit lead form data
- `GET /api/health` - Health check endpoint

### Static Files

All static files (HTML, CSS, JS, images) are served automatically by Vercel.

## Troubleshooting

### Google Sheets Not Working

1. Verify `GOOGLE_SPREADSHEET_ID` is set in environment variables
2. Check that `google_credentials.json` is in the root directory
3. Ensure the service account has access to the spreadsheet
4. Check Vercel function logs for errors

### View Logs

```bash
vercel logs
```

Or view in the Vercel dashboard under **Deployments** → **Functions** → **View Function Logs**

### Test Locally with Vercel

```bash
vercel dev
```

This will run your project locally with Vercel's serverless functions.

## Custom Domain

1. Go to your project settings in Vercel
2. Navigate to **Domains**
3. Add your custom domain
4. Follow DNS configuration instructions

## Continuous Deployment

If you connect a Git repository:
- Every push to `main` branch = Production deployment
- Every push to other branches = Preview deployment
- Pull requests = Preview deployment with unique URL

## Support

For Vercel-specific issues, check:
- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Community](https://github.com/vercel/vercel/discussions)

