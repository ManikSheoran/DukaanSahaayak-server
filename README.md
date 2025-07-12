# Dukaan Sahaayak Backend

This is the backend for Dukaan Sahaayak, a smart inventory management system. It provides a robust API to manage products, sales, purchases, customers, vendors, and credit tracking. The application is built with FastAPI and uses a PostgreSQL database. It also integrates with Twilio for sending SMS notifications and Google's Gemini AI for intelligent product extraction from images.

## Features

- **Product Management**: Full CRUD operations for inventory products.
- **Transaction Handling**: Record and manage sales and purchase transactions.
- **User Management**: Automatic customer and vendor creation and lookup by phone number.
- **Credit Tracking**: `Udhaar` (credit) management for both sales and purchases.
- **Financials**: Automatic profit and loss calculation for each sale.
- **Notifications**: Automated SMS bill generation and sending via Twilio.
- **AI-Powered Extraction**: Intelligent product extraction from bill images using Google Gemini AI.
- **API Documentation**: Interactive API documentation via Swagger UI.

## Technologies Used

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Data Validation**: Pydantic
- **SMS Service**: Twilio
- **AI/ML**: Google Gemini
- **Server**: Uvicorn

## Setup and Installation

Follow these steps to get the development environment running.

### 1. Prerequisites

- Python 3.8+
- PostgreSQL server running.

### 2. Clone the Repository

```bash
git clone <your-repository-url>
cd DukaanSahaayak-server
```

### 3. Create and Activate a Virtual Environment

```bash
# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate
```

### 4. Install Dependencies

First, ensure you have a `requirements.txt` file. If not, you can create one from your virtual environment once dependencies are installed:

```bash
pip freeze > requirements.txt
```

Then, install the required packages:

```bash
pip install -r requirements.txt
```

### 5. Set Up Environment Variables

Create a `.env` file in the root directory of the project and add the following configuration. Replace the placeholder values with your actual credentials.

```env
DATABASE_URL="postgresql://postgres:******@localhost:5432/smartinventory"
TWILIO_ACCOUNT_SID="your_twilio_account_sid"
TWILIO_AUTH_TOKEN="your_twilio_auth_token"
GEMINI_API_KEY="your_gemini_api_key"
```

### 6. Run the Application

Start the development server using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

The API is structured with the following tags. You can access the interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.

- `/api/products/`: Manage inventory products.
- `/api/sales/`: Record and retrieve sales data.
- `/api/purchases/`: Record and retrieve purchase data.
- `/api/customers/`: Manage customer information.
- `/api/vendors/`: Manage vendor information.
- `/api/udhaar/`: Track credit for sales and purchases.
- `/api/profit-loss/`: View profit and loss records.
- `/api/extract-products/`: Extract products from an uploaded image.

## Database Schema

The application uses SQLAlchemy to define the database models. The main tables are:

- **customers**: Stores customer details (`cust_id`, `customer_name`, `phone_no`).
- **vendors**: Stores vendor details (`vend_id`, `vendor_name`, `phone_no`).
- **products**: Stores product inventory information (`product_id`, `product_name`, `price_purchase`, `price_sale`, `quantity`).
- **sales_data**: Records sales transactions.
- **purchase_data**: Records purchase transactions.
- **profit_loss**: Tracks profit or loss for each sale.
- **udhar_sales**: Manages credit given to customers.
- **udhar_purchase**: Manages credit received from vendors.
- **sale_product** & **purchase_product**: Association tables linking transactions to products.
