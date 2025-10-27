# UrbanThread Loyalty Program - BA Design & Streamlit Prototype

## 1. Project Goal & Business Problem

This project prototypes a Customer Loyalty Program for UrbanThread, an e-commerce apparel company. The core business problems addressed are:

* **Low Customer Retention:** Only a 15% repeat-purchase rate.
* **High Customer Acquisition Cost (CAC):** Making single-purchase customers unprofitable.

The strategic goal is to support a 20% increase in repeat-customer sales within 18 months by providing a foundation for a full loyalty program implementation. This repository contains the **Streamlit web application prototype** code.

## 2. Project Approach: BA Design Meets Prototype Build

This project uniquely combined the roles of Business Analyst and Developer:

* **Phase 1: Business Analysis & Design:**
    * Conducted stakeholder analysis (Marketing, Finance, IT, Customer Service).
    * Developed core BA documents:
        * **Business Requirements Document (BRD):** Defined project vision, scope (points, tiers, redemption, expiration, manual override), and key business rules.
        * **Functional Requirements Document (FRD):** Detailed system behavior using User Stories and Acceptance Criteria.
        * **BPMN Process Flows:** Modeled 'As-Is' and 'To-Be' checkout processes visually.
* **Phase 2: Prototype Development:**
    * **Database:** Created an SQLite database (`loyalty.db` - *not included in repo*) via Python (`create_database.py`).
    * **Web Application:** Built an interactive prototype using Python and Streamlit (`app.py`).
    * **Deployment:** Utilized Git/GitHub for version control and deployed via Streamlit Community Cloud.

## 3. Prototype Features (`app.py`)

The deployed Streamlit application demonstrates the core functionalities defined in the FRD:

* **Customer Lookup:** View point balance, current tier (Standard/Gold), and transaction history by email.
* **Simulate Purchase:** Add 'earn' points based on a dollar amount, triggering tier check logic.
* **Reward Redemption:** Browse available rewards and redeem points (updates balance and logs 'redeem' transaction).
* **Manual Adjustment:** Allow CS agents (simulated) to add/subtract points with a reason (logs 'manual_adjust' transaction).
* **Database Initialization:** Automatically creates necessary tables if the database is empty (for deployment).

## 4. Technology Stack

* **Language:** Python 3
* **Web Framework:** Streamlit
* **Database:** SQLite 3 (using Python's `sqlite3` module)
* **Data Handling (Display):** Pandas
* **Version Control:** Git
* **Repository:** GitHub (`https://github.com/RBhardwaj2080/loyalty-app`)
* **Deployment:** Streamlit Community Cloud



## 5. Live Deployment

A live version of this prototype is hosted on Streamlit Community Cloud:

➡️ **(https://loyalty-app-jsbrvjuweapappenfpf2c4.streamlit.app/)**

some data for testing - Customer View , Add Points (Purchase) , Redeem Reward , Customer Service.
Emails:-* **john.doe@gmail.com**
        * **john.wick@gmail.com**
        * **john.wick@gmail.com**
Note:- Enter Any  Order ID/Number it will work.

## 6. Project Documentation

The detailed BA design documents (BRD, FRD, BPMN Diagrams) guided this prototype's development and are summarized in the `Report_Urban Thread Loyalty Program (v1.0) - Prototype Build` file included in this repository 
