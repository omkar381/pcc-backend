# Padashetty Coaching Class - Deployment Guide

This guide provides instructions on how to deploy the Padashetty Coaching Class application to Vercel (frontend) and Railway.app (backend).

## Backend Deployment (Railway.app)

1. Create a Railway.app account at https://railway.app
2. Install the Railway CLI:
   ```
   npm i -g @railway/cli
   ```
3. Login to Railway:
   ```
   railway login
   ```
4. Navigate to the backend directory:
   ```
   cd backend
   ```
5. Create a new Railway project:
   ```
   railway init
   ```
6. Add environment variables in Railway dashboard or using CLI:
   ```
   railway vars set SECRET_KEY=your_secret_key
   railway vars set FRONTEND_URL=https://your-vercel-app-url.vercel.app
   railway vars set CORS_ORIGINS=https://your-vercel-app-url.vercel.app
   railway vars set WHATSAPP_GROUP_LINK=https://chat.whatsapp.com/your-group-link
   ```
7. Deploy the backend:
   ```
   railway up
   ```
8. Get the backend URL from the Railway dashboard and copy it for the frontend deployment.

## Frontend Deployment (Vercel)

1. Create a Vercel account at https://vercel.com
2. Install the Vercel CLI:
   ```
   npm i -g vercel
   ```
3. Login to Vercel:
   ```
   vercel login
   ```
4. Navigate to the frontend directory:
   ```
   cd frontend
   ```
5. Create a production build:
   ```
   npm run build
   ```
6. Deploy to Vercel with the backend URL:
   ```
   vercel --env VITE_API_URL=https://your-railway-app-url.railway.app
   ```
7. Finalize the deployment:
   ```
   vercel --prod
   ```

## Testing the Deployment

1. Open your Vercel deployment URL in a browser
2. Login with the admin credentials:
   - Username: pcc
   - Password: pcc@8618
3. Verify that all features are working:
   - Student management
   - Attendance tracking
   - Notes management
   - Test management and PDF generation
   - WhatsApp sharing

## Troubleshooting

- **PDF Generation Issues**: Make sure the `uploads` directory is properly set up and has write permissions on Railway.app.
- **CORS Errors**: Verify that the `CORS_ORIGINS` environment variable contains your frontend URL.
- **API Connection Issues**: Check that the `VITE_API_URL` environment variable is correctly set in Vercel.

For additional help, refer to the [Railway.app Documentation](https://docs.railway.app/) and [Vercel Documentation](https://vercel.com/docs). 