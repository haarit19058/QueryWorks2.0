# QueryWorks 2.0

## Setup Instructions

### 1. Environment Variables

Add a `.env` file in the following directories:

* `ModuleB/cab_sharing_app/backend/app`
* `ModuleB/cab_sharing_app/frontend/app`

---

## Backend Setup

1. Navigate to the backend directory:

   ```bash
   cd ModuleB/cab_sharing_app/backend/app
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the backend server:

   ```bash
   uvicorn main:app --reload
   ```

---

## Frontend Setup

> **Prerequisite:** Make sure Node.js is installed on your system.

1. Navigate to the frontend directory:

   ```bash
   cd ModuleB/cab_sharing_app/frontend/app
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the development server:

   ```bash
   npm run dev
   ```