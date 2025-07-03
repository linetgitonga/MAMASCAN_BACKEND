# README for MAMASCAN Payment System

## Overview
The MAMASCAN Payment System is designed to facilitate payment processing through various methods, including integration with the M-Pesa and Daraja API. This system allows users to make payments for services seamlessly and securely.

## Project Structure
The project consists of the following key components:

- **payments/**: The main package containing all payment-related functionalities.
  - **models.py**: Defines the data models for payments, transactions, and services.
  - **serializers.py**: Handles serialization and deserialization of payment data.
  - **urls.py**: Maps URLs to payment-related views.
  - **utils.py**: Contains utility functions for generating payment links and validating responses.
  - **views.py**: Manages incoming requests and responses related to payments.
  - **mpesa/**: Contains modules for M-Pesa integration.
    - **daraja_client.py**: Implements functions for interacting with the Daraja API.
    - **mpesa_services.py**: Defines services for initiating payments and checking payment status.
    - **callbacks.py**: Handles callbacks from the M-Pesa API to update payment statuses.

## Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```
   cd MAMASCAN_BACKEND
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Configure your settings:
   - Update the `settings.py` file with your M-Pesa credentials and other necessary configurations.

## Usage
- To initiate a payment, use the appropriate view function defined in `views.py`.
- For M-Pesa payments, ensure that the Daraja API credentials are correctly set up in `daraja_client.py`.
- The system will handle callbacks from M-Pesa through the `callbacks.py` module.

## API Details
- The API endpoints for payment processing are defined in `urls.py`. Refer to this file for the available routes and their corresponding view functions.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.