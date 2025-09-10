READ ME LIKE A KID:

1. You got a folder with files.
2. Open Railway, create a new project.
3. Upload all files there (or push to GitHub and connect).
4. Go to Railway -> Variables and add the values from .env.example (fill with real API keys).
5. Deploy.
6. Copy your deployed URL (looks like https://xxx.up.railway.app).
7. In Shopify admin -> Settings -> Notifications -> Webhooks, add a webhook:
   Event: Orders Create (or Paid)
   URL: https://xxx.up.railway.app/webhook/shopify
   Format: JSON
8. Place a test order with an uploaded image.
9. The app will grab the image, run remove_watermark (right now just copies it), and try to "send" via Klaviyo (placeholder).

DONE. 
