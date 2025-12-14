# Connecting Subdomain to Vercel (GoDaddy)

This guide will help you connect your Vercel deployment to a subdomain (e.g., `leads.yourdomain.com`) on GoDaddy.

## Prerequisites

- Your domain is registered with GoDaddy
- Your website is deployed on Vercel
- You have access to both GoDaddy and Vercel accounts

## Step-by-Step Instructions

### Step 1: Add Domain in Vercel

1. Go to your Vercel dashboard: https://vercel.com/dashboard
2. Click on your project: **website-leads**
3. Go to **Settings** → **Domains**
4. Click **Add Domain** or **Add**
5. Enter your subdomain (e.g., `leads.yourdomain.com`)
6. Click **Add**

### Step 2: Get DNS Configuration from Vercel

After adding the domain, Vercel will show you DNS configuration options:

**Option A: CNAME Record (Recommended for subdomains)**
- Type: `CNAME`
- Name/Host: `leads` (or your subdomain prefix)
- Value/Target: `cname.vercel-dns.com`
- TTL: 3600 (or Default)

**Option B: A Record (if CNAME doesn't work)**
- Vercel will provide specific IP addresses

### Step 3: Configure DNS in GoDaddy

1. Log in to your **GoDaddy account**
2. Go to **My Products** → Click on **DNS** next to your domain
3. Scroll down to the **Records** section

#### For CNAME Record (Recommended):

1. Click **Add** to create a new record
2. Select:
   - **Type**: `CNAME`
   - **Name**: `leads` (this is your subdomain prefix)
   - **Value**: `cname.vercel-dns.com`
   - **TTL**: `1 hour` (or default)
3. Click **Save**

#### If CNAME is not available (some restrictions apply):

1. Click **Add** to create a new record
2. Select:
   - **Type**: `A`
   - **Name**: `leads`
   - **Value**: Use the IP address provided by Vercel
   - **TTL**: `1 hour`
3. Click **Save**

**Note:** If you already have other records for your subdomain, you may need to remove them first (A records and CNAME records cannot coexist for the same subdomain).

### Step 4: Verify DNS Propagation

1. After saving the DNS record, it may take **5 minutes to 48 hours** to propagate (usually within 15-30 minutes)
2. Check propagation status:
   - Go back to Vercel → Settings → Domains
   - You'll see the status next to your domain
   - It will show "Valid Configuration" once DNS is propagated
3. You can also check using online tools:
   - https://www.whatsmydns.net/
   - Enter: `leads.yourdomain.com`
   - Check if it resolves to Vercel

### Step 5: SSL Certificate (Automatic)

Vercel automatically provisions SSL certificates for your domain:
- Usually takes 1-5 minutes after DNS propagation
- You'll see "Valid Certificate" in the Vercel dashboard
- Your site will be accessible via `https://leads.yourdomain.com`

## Troubleshooting

### DNS Not Propagating

- Wait at least 15-30 minutes after making changes
- Clear your DNS cache: `sudo dscacheutil -flushcache` (Mac) or restart your router
- Use different DNS servers (e.g., Google DNS: 8.8.8.8, 8.8.4.4)

### Still Showing Old Site

- Clear browser cache or use incognito/private mode
- Try accessing from a different network
- Wait for DNS propagation to complete

### Vercel Shows "Invalid Configuration"

- Double-check the DNS record values in GoDaddy
- Ensure there are no conflicting records
- Make sure you're using the exact values provided by Vercel

### Can't Access Site After Setup

1. Check Vercel deployment status (should be "Ready")
2. Verify DNS records are correct in GoDaddy
3. Check Vercel domain status shows "Valid Configuration"
4. Wait for SSL certificate to be issued

## Example DNS Record

If your main domain is `dreamaxis.com` and you want `leads.dreamaxis.com`:

**In GoDaddy DNS:**
```
Type: CNAME
Name: leads
Value: cname.vercel-dns.com
TTL: 1 hour
```

This will make `leads.dreamaxis.com` point to your Vercel deployment.

## Additional Notes

- **Root Domain vs Subdomain:** If you want to use the root domain (`yourdomain.com`) instead of a subdomain, the process is different and requires changing nameservers. For a subdomain, DNS records are sufficient.
- **Multiple Subdomains:** You can add multiple subdomains (e.g., `leads`, `www`, `app`) by creating separate DNS records.
- **HTTPS:** Vercel automatically enables HTTPS with Let's Encrypt certificates - no additional configuration needed.

## Support

If you encounter issues:
1. Check Vercel's domain documentation: https://vercel.com/docs/concepts/projects/domains
2. Check GoDaddy's DNS help: https://www.godaddy.com/help
3. Verify your DNS records match exactly what Vercel shows

