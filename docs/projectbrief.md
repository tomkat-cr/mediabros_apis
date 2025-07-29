# Project Brief: mediabros_apis

## 1. Foundation

This document outlines the core requirements, goals, and scope for the `mediabros_apis` project. It serves as the source of truth for the project's direction and priorities.

## 2. Core Requirements & Goals

The primary goal of `mediabros_apis` is to provide a reliable and scalable set of serverless APIs for various services, including:

- **Currency Exchange:** Real-time exchange rates between USD, Colombian Pesos (COP), and Venezuelan Bolívares (VEB).
- **Cryptocurrency Prices:** Real-time prices for major cryptocurrencies like Bitcoin (BTC) and Ethereum (ETH), with the flexibility to query any crypto symbol.
- **Artificial Intelligence:** An interface to interact with OpenAI's ChatGPT.
- **System Monitoring:** Integration with Telegram for real-time error reporting and notifications.

The project aims to be deployed as a serverless application on AWS Lambda, ensuring high availability and cost-efficiency.

It doesn't have a dedicated user-facing web interface because it's mainly used as a backend service for other applications like the [Market Alert Telegram Bot](https://github.com/tomkat-cr/market_alert_bot).

## 3. Project Scope

### In-Scope

- **API Endpoints:**
  - Currency: `/usdcop`, `/usdveb`, `/usdveb_monitor`, `/usdveb_full`, `/copveb`, `/vebcop`.
  - Crypto: `/btc`, `/eth`, `/crypto/{symbol}`.
  - AI: `/ai` (POST and GET for queries).
  - Authentication: `/login`, `/token` (supporting both JWT and Auth0).
- **Technology Stack:**
  - Backend Frameworks: Python with Chalice and FastAPI components.
  - Deployment: AWS Lambda, API Gateway, managed by the Serverless Framework.
  - Database: MongoDB for data persistence (if required by features).
- **Development & Deployment:**
  - Environment management with `pipenv`.
  - Automated tasks using `make`.
  - Containerization with Docker for consistent build environments.

### Out-of-Scope (for now)

- Support for cloud providers other than AWS, e.g. GCP and Azure. Initially it was deployed to Vercel and Fly.io, but give the free layeer restrictions over the time, it was moved to AWS.
- Advanced user management features beyond basic authentication: it can be implemented using [GenericSuite](https://genericsuite.carlosjramirez.com/). 
- Caching layers for API responses (can be considered for future optimization).
