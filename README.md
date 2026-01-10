# SentinelFlow: Automated Power Platform Governance Engine

![Azure](https://img.shields.io/badge/azure-%230072C6.svg?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Power Apps](https://img.shields.io/badge/Power%20Apps-742774?style=for-the-badge&logo=powerapps&logoColor=white)
![Bicep](https://img.shields.io/badge/Bicep-0078D4?style=for-the-badge&logo=azure-devops&logoColor=white)

**SentinelFlow** is a hybrid governance engine that bridges the gap between **Low-Code** velocity and **Pro-Code** security standards. It allows Citizen Developers to audit their Power Apps code in real-time against enterprise security policies (GDPR, Credential Leaks, Performance) using a serverless Azure backend.

---

## Architecture

The solution implements a **Hybrid Fusion Development** architecture:

```mermaid
graph TD
    subgraph "Power Platform (Client)"
        User[Developer] -->|Pastes Code| Canvas[SentinelFlow Dashboard]
        Canvas -->|HTTPS Request| Connector[Custom Connector]
    end

    subgraph "Azure Cloud (Backend)"
        Connector -->|API Call| Func["Azure Function (Python 3.11)"]
        Func -->|Validates| Logic["Governance Engine (Regex/Pydantic)"]
        Logic -- Returns Score --> Func
        Func -- JSON Response --> Canvas
    end

    subgraph "Infrastructure"
        Func -->|Logs| AppInsights[Application Insights]
        Func -->|Storage| Storage[Azure Storage]
    end
```

## Key Features

* **Real-Time Static Analysis:** Scans PowerFx code for hardcoded secrets (API keys, passwords) and PII (Social Security Numbers).
* **Performance Auditing:** Detects heavy operations like unfiltered `ClearCollect`.
* **Hybrid Integration:** Seamlessly connects a Canvas App UI to a Python backend via OpenAPI (Swagger).
* **Infrastructure as Code:** Fully deployable via Azure Bicep for reproducible environments.
* **Strict Typing:** Powered by Pydantic to ensure a rigid API contract.

---

## Project Structure

```text
SentinelFlow/
├── backend/                  # Azure Function (Python 3.11)
│   ├── governance_engine/    # Core Logic (Rules & Models)
│   ├── function_app.py       # API Entry Point
│   └── requirements.txt      # Python Dependencies
├── infra/                    # Infrastructure as Code
│   └── main.bicep            # Azure Resource Definitions
├── integration/              # API Contract
│   └── sentinel_openapi.json # Swagger Definition for Power Platform
├── docs/                     # Documentation & Diagrams
├── tests/                    # Unit Tests (Pytest)
├── Makefile                  # Automation Scripts
└── README.md                 # Project Documentation

```

---

## Deployment Guide

This project uses a `Makefile` to automate the entire lifecycle.

### Prerequisites

* **Azure CLI** (`az login` must be run beforehand)
* **Python 3.11+**
* **Azure Functions Core Tools** (for local debugging)
* **Power Apps Developer Plan**

### 1. Setup Local Environment

Creates a virtual environment and installs Python dependencies.

```bash
make setup

```

### 2. Provision Infrastructure

Deploys the Azure Resources (Function App, Storage, App Insights) using Bicep.

```bash
make infra-create

```

### 3. Deploy Backend Code

Publishes the Python logic to the newly created Azure Function.

```bash
make deploy-code

```

*(Optional) To deploy both infrastructure and code in one go:*

```bash
make deploy-all

```

---

## Connecting Power Apps

Once the backend is live, you must connect the UI:

1. **Get the API URL:**
Run `make get-url` to retrieve your deployed endpoint.

2. **Update OpenAPI Definition:**
Open `integration/sentinel_openapi.json` and replace the `"host"` value with your Azure Function domain.

3. **Import Custom Connector:**
   * Go to [make.powerapps.com](https://www.google.com/search?q=https://make.powerapps.com)
   * **Custom Connectors** > **New** > **Import from OpenAPI file**.
   * Select `integration/sentinel_openapi.json`.

4. **Create Canvas App:**
   * Create a new Blank Canvas App.
   * Add the `SentinelFlowConnector` as a data source.
   * Build the UI to accept text input and call `SentinelFlowConnector.AuditApp()`.

## Build the UI

We treat the UI as code, using global variables for theming and relative formulas for responsive layout.

#### **A. Global Theming (App.OnStart)**
Define a corporate color palette and design system variables to ensure consistency.
```powerfx
// App.OnStart Property
Set(varTheme, {
    Primary: ColorValue("#0072C6"),     // Metso Blue
    Background: ColorValue("#F3F4F6"),  // Light Gray (Tailwind gray-100)
    Surface: ColorValue("#FFFFFF"),     // White
    Critical: ColorValue("#DC2626"),    // Red
    Safe: ColorValue("#16A34A")         // Green
});

```

#### **B. Screen Layout (Responsive)**

1. **Main Screen:** Set `Fill` to `varTheme.Background`.
2. **Header:**
   * **Control:** Label
   * **Width:** `Parent.Width` (Full Span)
   * **Fill:** `varTheme.Primary`
   * **Text:** "SentinelFlow Governance Engine"

3. **Input Area (Left Split):**
   * **Control:** Text Input (`txtCodeInput`)
   * **Mode:** `Multiline`
   * **X/Y:** Anchored to left (`40`, `120`)
   * **Width:** `(Parent.Width / 2) - 60`
   * **Height:** `Parent.Height - 160`

4. **Results Area (Right Split):**
   * **Control:** HTML Text (Background Card)
   * **HtmlText:**
```html
<div style='background: white; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 98%; height: 98%;'></div>

```

* **Logic:** Place the Gallery and Score Labels on top of this card for an elevated UI effect.


#### **C. Core Logic (Audit Button)**

The button triggers the Azure Function and stores the result in a context variable.

```powerfx
// OnSelect Property
UpdateContext({ locIsLoading: true });

// Call Azure Function (Pass arguments as raw strings)
UpdateContext({ 
    locScanResult: SentinelFlowGovernanceAPI.AuditApp(
        "UserScan", 
        txtCodeInput.Text
    ) 
});

UpdateContext({ locIsLoading: false });

```

#### **D. Dynamic Feedback**

* **Score Label:**
```powerfx
"Governance Score: " & locScanResult.governance_score & "/100"

```


* **Color Logic:**
```powerfx
If(locScanResult.governance_score < 70, varTheme.Critical, varTheme.Safe)

```

---

## Demo Scenarios

Use these code snippets to demonstrate the engine's capabilities during a live demo.

### 🟢 Scenario 1: The "Perfect" App

**Goal:** Prove the engine recognizes good code patterns.
**Input:**

```javascript
// A perfectly compliant app
Set(varCurrentUser, User().FullName);
Set(locIsVisible, true);
Set(colMenu, ["Home", "Settings"]);

```

**Expected Result:**

* **Score:** 100/100 (Green)
* **Findings:** None (Empty Gallery)

### 🔴 Scenario 2: The "GDPR Nightmare"

**Goal:** Trigger a Critical Privacy Rule (`PRIV-001`).
**Input:**

```javascript
// Asking for sensitive info
Set(varEmployeeSSN, "123-45-6789");
Label1.Text = "Please enter your Social Security Number";

```

**Expected Result:**

* **Score:** < 80/100 (Red)
* **Findings:**
* `PRIV-001 | Critical` (Red) - "Potential PII exposure..."

### 🟠 Scenario 3: The "Sloppy Developer"

**Goal:** Trigger Warnings (`GOV-001`) and Info (`PERF-001`) without failing security checks.
**Input:**

```javascript
// Bad naming conventions (No 'var' prefix)
Set(userCount, 50); 
Set(tempData, "test");

// Performance risk
ClearCollect(bigList, SharePoint_Data);

```

**Expected Result:**

* **Score:** ~88/100 (Yellow/Orange)
* **Findings:**
* `GOV-001 | Warning` (Orange) - "Variable does not follow naming..."
* `PERF-001 | Info` (Black) - "Heavy operation detected..."

---

## Teardown

To avoid incurring cloud costs, destroy all resources when finished.

```bash
make destroy

```

*Warning: This permanently deletes the 'SentinelFlow-RG' resource group.*

---