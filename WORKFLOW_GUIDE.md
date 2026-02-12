# ZKP Scholarship System - Complete Workflow Guide

## 🚀 Step-by-Step Instructions to Run the System

### Prerequisites

Before starting, ensure you have:
- ✅ Python 3.7+ installed
- ✅ All dependencies installed: `pip install -r requirements.txt`
- ✅ Test data initialized: `python init_demo_data.py`

---

## Option 1: Automated Startup (Recommended)

### Single Command to Start Everything

```powershell
.\start_system.ps1
```

**What this does:**
1. Starts the College (Issuer) server on port 5001
2. Starts the Scholarship (Verifier) server on port 5002
3. Opens the home page in your default browser

**You'll see:**
```
Starting Issuer (College) Server...
Starting Verifier (Scholarship) Server...
Opening Student Portal...

All services started!
Issuer Server: http://localhost:5001
Verifier Server: http://localhost:5002
Home Page: Opened in browser
```

---

## Option 2: Manual Startup (Step-by-Step)

If you prefer to start each component manually:

### Step 1: Start the College (Issuer) Server

Open a **new PowerShell terminal** and run:

```powershell
cd d:\ZKP
python issuer/app.py
```

**Expected output:**
```
 * Running on http://127.0.0.1:5001
 * Debug mode: on
```

**Keep this terminal open!**

---

### Step 2: Start the Scholarship (Verifier) Server

Open **another new PowerShell terminal** and run:

```powershell
cd d:\ZKP
python verifier/app.py
```

**Expected output:**
```
 * Running on http://127.0.0.1:5002
 * Debug mode: on
```

**Keep this terminal open too!**

---

### Step 3: Open the Student Portal

Open your web browser and navigate to:

```
file:///d:/ZKP/student/home.html
```

Or simply double-click on `d:\ZKP\student\home.html` in File Explorer.

---

## 📋 Complete User Workflow

Once the system is running, follow this workflow:

### Phase 1: College Portal (Get Credential)

1. **Open College Portal**
   - From home page, click "Enter College Portal →"
   - Or open: `file:///d:/ZKP/student/college_portal.html`

2. **Generate Keys**
   - Click "Generate Keys" button
   - Your private key is created and stored in browser
   - Public key is displayed on screen

3. **Request Credential**
   - Enter Student ID: `STU001`
   - Enter Name: `Alice Johnson`
   - Click "Request Credential from College"
   - Wait for success message

4. **Credential Issued**
   - You'll see: "✅ Success! Your credential has been issued"
   - Student details will be displayed
   - "Go to Scholarship Portal" button appears

---

### Phase 2: Scholarship Portal (Apply Anonymously)

5. **Open Scholarship Portal**
   - Click "🎯 Go to Scholarship Portal →"
   - Or open: `file:///d:/ZKP/student/scholarship_portal.html`

6. **Apply for Scholarship**
   - Enter Student ID: `STU001`
   - Click "🎓 Apply for Scholarship (Anonymous)"
   - System generates Zero-Knowledge Proof
   - Wait for verification

7. **View Result**
   - You'll see eligibility decision
   - Reasons for approval/denial
   - Privacy note confirming your identity was protected

---

## 🧪 Testing Different Scenarios

### ✅ Test Case 1: Successful Application (Eligible Student)

**Student:** STU001 - Alice Johnson
- GPA: 3.8 (meets requirement ≥ 3.5)
- Admission Year: 2020 (meets requirement < 2022)
- **Expected Result:** ✅ GRANT

**Steps:**
1. College Portal: Generate keys
2. College Portal: Request credential (STU001 / Alice Johnson)
3. Scholarship Portal: Apply (STU001)
4. **Result:** Scholarship granted!

---

### ✅ Test Case 2: Successful Application (Another Eligible Student)

**Student:** STU003 - Carol White
- GPA: 3.9
- Admission Year: 2019
- **Expected Result:** ✅ GRANT

**Steps:**
1. Clear browser localStorage (F12 → Application → Local Storage → Clear)
2. College Portal: Generate keys
3. College Portal: Request credential (STU003 / Carol White)
4. Scholarship Portal: Apply (STU003)
5. **Result:** Scholarship granted!

---

### ❌ Test Case 3: Ineligible Student (Low GPA)

**Student:** STU004 - David Brown
- GPA: 3.2 (below requirement)
- Admission Year: 2022
- **Expected Result:** ❌ DENY

**Steps:**
1. Clear browser localStorage
2. College Portal: Generate keys
3. College Portal: Request credential (STU004 / David Brown)
4. Scholarship Portal: Apply (STU004)
5. **Result:** Scholarship denied (GPA too low)

---

### ❌ Test Case 4: Unauthorized Access (No Credential)

**Objective:** Prove ZKP security prevents unauthorized access

**Steps:**
1. Open **new browser** or **incognito window**
2. Go directly to Scholarship Portal (skip College Portal)
3. Try to apply with Student ID: `STU001`
4. **Result:** ❌ "No keys found! Please visit College Portal first"

---

### ❌ Test Case 5: Non-Existent Student

**Objective:** Show system rejects invalid students

**Steps:**
1. Go to Scholarship Portal
2. Enter Student ID: `STU999` (doesn't exist)
3. Click Apply
4. **Result:** ❌ "Unauthorized Access Prevented! Student not registered"

---

## 🔍 Verifying the System is Working

### Check Backend Servers

**College Server (Port 5001):**
```powershell
# In browser, visit:
http://localhost:5001/health
```

**Scholarship Server (Port 5002):**
```powershell
# In browser, visit:
http://localhost:5002/health
```

If servers are running, you'll see a response (or 404 if no health endpoint).

---

### View Database Contents

To see what's stored in the databases:

```powershell
python view_database.py
```

**This shows:**
- All students in college database
- Key bindings
- Issued credentials
- Certified keys in scholarship registry
- Verification sessions

---

## 🛠️ Troubleshooting

### Problem: "Port already in use"

**Solution:**
```powershell
# Find process using port 5001
netstat -ano | findstr :5001

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Repeat for port 5002
netstat -ano | findstr :5002
taskkill /PID <PID> /F
```

---

### Problem: "Module not found"

**Solution:**
```powershell
# Install dependencies
pip install -r requirements.txt
```

---

### Problem: "No students found"

**Solution:**
```powershell
# Initialize demo data
python init_demo_data.py
```

---

### Problem: "Keys not found" in Scholarship Portal

**Solution:**
1. Make sure you completed College Portal workflow first
2. Check browser localStorage (F12 → Application → Local Storage)
3. Look for `zkp_keys` entry
4. If missing, regenerate keys in College Portal

---

### Problem: Browser shows "Cannot convert undefined to BigInt"

**Solution:**
1. Refresh the browser page (Ctrl + F5)
2. Clear browser cache
3. Make sure you're using the latest version of the files

---

## 📊 Files You Need to Run

### Required Files (Must Run):

| File | Purpose | How to Run |
|------|---------|------------|
| `issuer/app.py` | College backend server | `python issuer/app.py` |
| `verifier/app.py` | Scholarship backend server | `python verifier/app.py` |
| `student/home.html` | Landing page | Open in browser |
| `student/college_portal.html` | College interface | Open from home page |
| `student/scholarship_portal.html` | Scholarship interface | Open from home page |

### Supporting Files (Auto-loaded):

| File | Purpose | Loaded By |
|------|---------|-----------|
| `student/crypto.js` | Client-side cryptography | Both portals |
| `crypto/*.py` | Backend cryptography | Both servers |
| `issuer/database.py` | College database | Issuer server |
| `issuer/credentials.py` | Credential signing | Issuer server |
| `verifier/registry.py` | Key registry | Verifier server |
| `verifier/verification.py` | Proof verification | Verifier server |
| `verifier/eligibility.py` | Eligibility logic | Verifier server |

### Optional Files:

| File | Purpose | When to Use |
|------|---------|-------------|
| `init_demo_data.py` | Create test students | Before first run |
| `view_database.py` | Inspect databases | For debugging |
| `tests/test_schnorr.py` | Unit tests | To verify crypto |

---

## 🎯 Quick Reference: Complete Workflow

```
1. START SERVERS
   ├── Run: .\start_system.ps1
   │   OR
   ├── Terminal 1: python issuer/app.py
   └── Terminal 2: python verifier/app.py

2. OPEN BROWSER
   └── Navigate to: file:///d:/ZKP/student/home.html

3. COLLEGE PORTAL
   ├── Click "Enter College Portal"
   ├── Generate Keys
   ├── Enter: STU001 / Alice Johnson
   └── Request Credential

4. SCHOLARSHIP PORTAL
   ├── Click "Go to Scholarship Portal"
   ├── Enter: STU001
   ├── Apply for Scholarship
   └── View Result: ✅ GRANT

5. TEST SECURITY
   ├── New browser/incognito
   ├── Try: STU999 (non-existent)
   └── Result: ❌ Access Denied
```

---

## 📝 Summary

**Minimum steps to see it working:**

1. Run: `.\start_system.ps1`
2. Browser opens automatically
3. College Portal → Generate Keys → Request Credential (STU001 / Alice Johnson)
4. Scholarship Portal → Apply (STU001)
5. See result: ✅ Scholarship Granted!

**That's it!** The system demonstrates privacy-preserving verification using Zero-Knowledge Proofs. 🎓
