# Padashetty Coaching Class Deployment Guide

This guide walks you through deploying your application for free while preserving all your data.

## Backend Deployment (Render.com)

1. **Create a Render.com account**
   - Go to [Render.com](https://render.com) and sign up for a free account

2. **Deploy the backend**
   - Log in to your Render account
   - Click "New +" and select "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file
   - Click "Apply Blueprint"
   - Render will create a web service with a 1GB persistent disk to store your data

3. **Note the backend URL**
   - Once deployment is complete, note the URL of your backend service
   - It will look like `https://padashetty-backend.onrender.com`
   - You'll need this URL for the frontend deployment

## Frontend Deployment (Vercel)

1. **Create a Vercel account**
   - Go to [Vercel.com](https://vercel.com) and sign up for a free account

2. **Update the frontend environment file**
   - Open `frontend/.env.production`
   - Replace the placeholder API URL with your actual Render.com backend URL

3. **Deploy the frontend**
   - Log in to your Vercel account
   - Click "Add New" → "Project"
   - Connect your GitHub repository
   - Specify the following settings:
     - Framework Preset: `Vite`
     - Root Directory: `frontend`
     - Build Command: `npm run build`
     - Output Directory: `dist`
   - Click "Deploy"

4. **Update backend CORS settings**
   - Go back to your Render.com dashboard
   - Open the environment variables for your backend service
   - Update the `FRONTEND_URL` and `CORS_ORIGINS` variables with your Vercel URL
   - Click "Save Changes" and wait for the backend to redeploy

## Backup and Data Management

Your data will be stored on Render.com's persistent disk. However, for added safety:

1. **Regular Backups**
   - Download your SQLite database file periodically
   - You can create a "Backup" endpoint in your backend or use Render.com's shell access

2. **File Management**
   - Render provides 1GB of free persistent storage
   - Be mindful of PDF sizes and other uploaded files
   - Consider implementing a file cleanup system for older files

## Accessing Your Application

1. **Admin Login**
   - Go to your Vercel URL
   - Log in with the default admin credentials:
     - Username: `pcc`
     - Password: `pcc@8618`

2. **Student Access**
   - Students can access the application using the same Vercel URL
   - They will use the credentials you've set up for them

## Troubleshooting

- **CORS Issues**: Ensure the Vercel domain is added to the CORS_ORIGINS in Render.com
- **Database Issues**: Run the setup script manually via Render shell: `python backend/cloud_db_setup.py`
- **Storage Issues**: Free tier has 1GB limit - monitor your usage in the Render dashboard

## Free Tier Limitations

- **Render.com**: The free tier "spins down" after 15 minutes of inactivity. The first request after inactivity may take a few seconds.
- **Vercel**: No significant limitations for your use case.

## Production Security Considerations

For enhanced security in production:
- Change the default admin password
- Consider implementing proper password hashing
- Set up regular database backups 