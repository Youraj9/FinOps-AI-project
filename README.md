# FinOps AI Enterprise Application
> **Autonomous Invoice Auditing, Multimodal Generative AI Extraction, and Multi-Currency Ledger Synchronization Pipeline**

FinOps AI Enterprise is an automated financial operations lifecycle platform designed to eliminate manual tracking overheads, data processing errors, and ledger synchronization variances in global supply chain billing. 

By merging non-deterministic Multimodal Vision AI with deterministic accounting compilation layers, the application securely processes, hashes, transforms, audits, and archives international vendor receipts into structured, transactionally stable ledgers.

---

## 🏗️ System Architecture & Logic Flow

The core architecture operates via a distinct pipeline pattern consisting of:
1. **The Ingest Gatekeeper:** Cryptographic checksum evaluation utilizing a 32-character binary stream MD5 hash calculation to systematically intercept duplicate invoice submissions before database persistence.
2. **The Multimodal Extraction Layer:** Deep payload analytics via the `gemini-1.5-flash` model parsing noisy, low-resolution visual media inputs into compliant structured JSON.
3. **The Financial Calculation Sanitizer:** Programmatic subtotal mathematical audits cross-checking `Subtotal + Tax == Grand_Total` to enforce structural policy alignment.
4. **The Base Ledger Synchronizer:** Historical value stamping converting global currencies (USD, GBP, EUR, JPY, CNY) into Indian Rupees (INR) at runtime using real-time dynamic converter objects and localized fallback fallbacks, preventing down-stream ledger manipulation due to foreign exchange float values.



---

## 🛠️ Technology Stack

* **Frontend Engine:** Streamlit UI Framework (Dynamic State Tracking, Contextual Navigation Matrix, Multiplex Dashboard Formatting).
* **Backend Runtime:** Python 3.9+ Ecosystem (`hashlib` file hashing, secure `smtplib` mail engines with Transport Layer Security).
* **Machine Intelligence Core:** Google Generative AI Python SDK (`google-generativeai`).
* **Relational Database Management System:** Oracle MySQL relational engines managed via transactional pooling wrappers.
* **Analytical Processing:** Pandas DataFrames, NumPy multi-precision mathematics, and `openpyxl` reporting compilers.

---

## 🔐 Key Configurations & Environment Variables

To instantiate local environments safely, configure your `.env` properties matrix matching the template below:

```env
# Google Generative AI Key Vector
GEMINI_API_KEY="AIzaSyYourActualSecureGeminiKeyLine"

# Relational Storage Access Profiles
DB_HOST="localhost"
DB_USER="root"
DB_PASSWORD="your_secure_mysql_root_password"
DB_NAME="finops_ai_ledger"

# Secure Communication Agent SMTP Overheads
EMAIL_ADDRESS="accounts-disputes@yourdomain.com"
EMAIL_PASSWORD="your_secure_gmail_app_specific_token"
```

🚦 Role-Based Workspaces & Feature Manifest
🧑‍💻 1. Operator Workspace (Document Ingestion & Execution Layer)
Purpose: Streamline daily data entry and handle vendor dispute routing.

📤 Multi-Invoice Uploader: Asynchronous ingestion pipelines interpreting layout trees from uploaded PNG, JPG, or PDF images.

🔍 Discrepancy Validation Hub: Visual inspection dashboards displaying parsed transaction definitions side-by-side with localized calculation assessments.

🔀 Communication Matrix Router: Adaptive communication router that queries vendor contact definitions:

✅ Verified Contact Chains: Dispatches programmatic dispute emails to vendors if calculation variance is present.

⚠️ Broken/Absent String Management: Automatically isolates listings without formatted @ strings into interactive manual exception processing worklogs.

🛡️ 2. Administrator Workspace (Enterprise Governance & Analytics Layer)
Purpose: Ensure compliance, track financial health, and audit system security.

📋 Master Invoice Ledger: Full-scale database view tracking normalized financial entries, tracking native base payments side-by-side with the immutable snapshot record stored within the amount_inr column.

📊 Financial Analytics Dashboard: Aggregated tracking graphs illustrating localized rolling spending sums, transactional load rates, and document variance analytics filtered across historical months.

🕵️ Security Audit Trail Log: Compliance record detailing administrative actions, explicitly filtering out system operations queries to isolate user transaction history.

📥 Data Compiler Engine: Live extraction routines generating formatted CSV and structured Excel reports styled with dynamic cell auto-width expansion matrices.

🏁 Installation & Deployment Matrix
Get the system up and running on your local machine in four simple steps.

Bash
# 1. Clone the master repository system
git clone https://github.com/YOUR_GITHUB_USERNAME/FinOps-AI-Enterprise.git
cd FinOps-AI-Enterprise

# 2. Deploy your application variables file
cp .env.example .env
nano .env # Inject production API and storage credentials 

# 3. Compile structural system requirements
pip install -r requirements.txt

# 4. Initialize Streamlit core servers
streamlit run app.py
📑 Relational Data Schema Model
The persistence layer relies on a secure, structured, and transactional relational model to ensure absolute data integrity.

SQL
-- Core User Identity & RBAC Matrix
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('Admin', 'Operator') NOT NULL
);

-- Master Ledger & Transaction Records
CREATE TABLE invoices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_hash VARCHAR(32) UNIQUE NOT NULL,
    vendor_name VARCHAR(100) NOT NULL,
    vendor_email VARCHAR(100),
    grand_total DECIMAL(15,2) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    amount_inr DECIMAL(15,2) NOT NULL,
    status VARCHAR(30) NOT NULL,
    uploaded_by INT,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
);

-- Enterprise Security Audit Tracker
CREATE TABLE audit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
 
