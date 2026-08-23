# DECODE: Comprehensive Platform Setup & Architecture Guide

This document explains **everything** you need to know about the DECODE platform. It covers exactly what each piece does, *why* it is required, and provides a click-by-click guide to configuring your database (Firebase) and deploying the system.

---

## Part 1: Why is the System Split into Two Parts?

DECODE is a complex scientific infrastructure platform. It cannot run in a single codebase because the frontend and backend have entirely different jobs:

1. **The Frontend (`decode-frontend`)**: Built with **Next.js (React)** and **Tailwind CSS**. Its only job is to look beautiful, handle user interactions, upload PDFs, and display the final intelligent results. It runs in the user's browser.
2. **The Backend (`DECODE_backend`)**: Built with **Python** and **Flask**. Its job is heavy Machine Learning. It runs **OpenCV** (for image processing), **EasyOCR** (for reading text in charts), and deep classification algorithms. *Browsers cannot run these heavy ML models efficiently*, so they must live on a dedicated Python server.

**How they talk:** The Frontend sends a PDF to the Backend. The Backend grinds through the ML classification and sends the JSON results back to the Frontend to be displayed.

---

## Part 2: Firebase Configuration (Step-by-Step)

DECODE uses **Firebase** as its database (Firestore) to store the extracted chart intelligence, and for user authentication.

### Why is Firebase Required?
Without Firebase, the backend has nowhere to save the results of its hard work. If a user uploads a 100-page PDF, it takes time to process. Firebase stores the results permanently so the user can log in later and see their dashboard without reprocessing the file.

### Step-by-Step Setup Guide

**1. Create the Firebase Project**
1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Click **Add project**.
3. Name it `DECODE-Platform` (or similar).
4. You can disable Google Analytics for now. Click **Create Project**.

**2. Enable Firestore (The Database)**
1. On the left sidebar, click **Build** > **Firestore Database**.
2. Click **Create database**.
3. Choose **Start in Test Mode** (this allows you to read/write data easily during development. You can secure it later).
4. Choose a location closest to you and click **Enable**.

**3. Generate the Backend Credentials (CRITICAL)**
Your Python backend needs special "Admin" permissions to write data directly to the database.
1. Click the **Gear Icon** (Project Overview) in the top left and select **Project settings**.
2. Go to the **Service accounts** tab.
3. Make sure "Node.js" or "Python" is selected, and click the blue **Generate new private key** button.
4. A `.json` file will download to your computer.
5. **Move this file** into your `DECODE_backend/backend` folder and rename it to `firebase-adminsdk.json`.
6. **Important:** Never upload this file to GitHub! Keep it secret.

---

## Part 3: Running the Platform Locally

To develop or test the application on your computer, you must run **both** the frontend and the backend simultaneously in two different terminal windows.

### 1. Start the Backend (The ML Engine)
*Why? So the frontend has an API to send PDFs to.*
1. Open a terminal.
2. Navigate to the backend folder: `cd DECODE_backend/backend`
3. Make sure you have installed the requirements: `pip install -r requirements.txt`
4. Run the server: `py -3.12 app.py` (or `python app.py`)
5. You should see it running on `http://localhost:8000`.

### 2. Start the Frontend (The UI)
*Why? This is the actual website the user sees.*
1. Open a second terminal.
2. Navigate to the frontend folder: `cd decode-frontend`
3. Run the development server: `npm run dev`
4. Open your browser to `http://localhost:3000`.

---

## Part 4: Production Deployment

When you are ready to show DECODE to the world, you cannot run it on your laptop. You must put it on the cloud.

### Step 1: Deploying the Backend (Render or AWS)
Because the backend uses heavy system libraries (like `poppler-utils` for PDF reading and `libGL` for OpenCV), you must deploy it using **Docker**.
1. Create an account on [Render.com](https://render.com).
2. Connect your GitHub repository.
3. Create a **New Web Service** and select your repository.
4. Render will automatically detect the `Dockerfile` inside `DECODE_backend` and build your server.
5. In Render's settings, add an Environment Variable containing the exact contents of your `firebase-adminsdk.json` file so the cloud server can talk to Firebase.

### Step 2: Deploying the Frontend (Vercel)
Vercel is the company that created Next.js, so it is the perfect place to host your frontend.
1. Go to [Vercel.com](https://vercel.com) and create an account.
2. Click **Add New Project** and connect your GitHub repo.
3. Set the "Root Directory" to `decode-frontend`.
4. In the Environment Variables section, add:
   - Name: `NEXT_PUBLIC_API_URL`
   - Value: `https://your-render-backend-url.onrender.com` (this tells the cloud frontend where to find the cloud backend).
5. Click **Deploy**.

> [!TIP]
> **Performance Note:** EasyOCR is heavily optimized for GPUs. If your cloud backend is running on a standard CPU server, chart detection will be slow (10-30 seconds per page). For lightning-fast production performance, you will eventually want to host the Docker backend on a GPU-enabled instance (like AWS EC2 g4dn).
