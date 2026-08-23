# DECODE Deployment Guide

This document outlines the professional deployment strategy for the DECODE platform, which consists of a **Next.js Frontend** and a **Python Flask Backend**.

Because the backend performs heavy ML tasks (OCR, Image Processing, Chart Detection), it requires specific system-level dependencies (like Poppler) and is best deployed using Docker.

---

## 1. Backend Deployment (Python / Flask)

The backend handles heavy computer vision and OCR workloads (OpenCV, EasyOCR, pdf2image). It is highly recommended to deploy this via **Docker** to a container hosting service like **Render**, **AWS ECS**, or **Google Cloud Run**.

### System Dependencies
If you are deploying on a bare-metal Linux server (like an Ubuntu EC2 instance) without Docker, you *must* install these system libraries first:
```bash
sudo apt-get update
sudo apt-get install -y poppler-utils tesseract-ocr libgl1-mesa-glx
```

### Environment Variables (`.env`)
Create a `.env` file in your backend environment with the following keys:
```ini
# Firebase Credentials (Required for auth/db)
FIREBASE_CREDENTIALS_PATH=/path/to/firebase-adminsdk.json

# CORS (Allow your frontend URL to access the backend)
CORS_ORIGIN=https://decode.yourdomain.com

# Server Config
PORT=8000
HOST=0.0.0.0
```

### Docker Deployment (Recommended)
Using a `Dockerfile` ensures all ML dependencies are bundled correctly.

**Example `Dockerfile` (Place in `/DECODE_backend`):**
```dockerfile
FROM python:3.12-slim

# Install system dependencies for OpenCV and pdf2image
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download EasyOCR models (optional but recommended for faster boot)
# RUN python -c "import easyocr; easyocr.Reader(['en'])"

COPY backend /app

EXPOSE 8000

# Run with Gunicorn for production
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8000", "app:app"]
```

**Build and Run Locally:**
```bash
docker build -t decode-backend .
docker run -p 8000:8000 --env-file .env decode-backend
```

---

## 2. Frontend Deployment (Next.js)

The frontend is a standard Next.js application. The easiest and most performant way to deploy it is via **Vercel**.

### Environment Variables (`.env.local`)
The frontend needs to know where the backend API is hosted. Set this in Vercel's environment variable settings:
```ini
NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
```

### Deploying to Vercel
1. Push your code to a GitHub repository.
2. Go to [Vercel](https://vercel.com/) and click **Add New Project**.
3. Import your GitHub repository.
4. Set the **Root Directory** to `decode-frontend` (if it's not at the root of the repo).
5. Add the `NEXT_PUBLIC_API_URL` environment variable.
6. Click **Deploy**.

Vercel will automatically build the Next.js app (`npm run build`) and host it on a global CDN.

---

## 3. Production Checklist

> [!WARNING]
> Before going live, ensure you check the following items.

- [ ] **CORS Settings:** Ensure your Flask backend is configured to accept requests *only* from your Vercel frontend domain.
- [ ] **Firebase Rules:** Ensure your Firestore database rules are secure and only allow authenticated users to read/write data.
- [ ] **GPU Acceleration:** EasyOCR is very slow on CPUs. If you deploy the backend to a cloud provider, consider using an instance with a basic GPU (like AWS g4dn or GCP instances with NVIDIA T4) to speed up chart classification by 10x.
- [ ] **Storage:** If you are handling large PDF uploads, configure Firebase Storage (or AWS S3) rather than storing files directly on the backend server.
