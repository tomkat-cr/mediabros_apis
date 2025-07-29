# Product Context: mediabros_apis

## 1. Why This Project Exists

`mediabros_apis` was created to centralize and simplify access to frequently needed data and services through a unified API layer. Developers often need to integrate with multiple external services for tasks like currency conversion, cryptocurrency price tracking, or interacting with AI models. This project abstracts away the complexity of individual integrations, providing a single, consistent, and easy-to-use set of endpoints.

## 2. Problem It Solves

The project addresses several key problems for developers:

- **Reduces Boilerplate:** Eliminates the need to write and maintain separate integration code for each external service (e.g., different currency exchanges, crypto data providers, OpenAI).
- **Simplifies Data Access:** Provides clean, predictable JSON responses for complex data, saving developers from parsing messy or inconsistent data formats from various sources.
- **Centralizes API Keys:** Manages and secures API keys and credentials for external services on the backend, so client-side applications don't need to handle them.
- **Provides Essential Tools:** Offers ready-to-use endpoints for common financial data relevant to specific regions (Colombia and Venezuela), which are not always available in mainstream financial APIs.
- **Adds Value-Added Services:** Includes features like Telegram notifications for error monitoring, which helps in maintaining application health.

## 3. How It Should Work

A developer interacts with `mediabros_apis` by making simple HTTP requests to its public endpoints. The system is designed to be straightforward:

1.  **Request:** A user (typically another application or service) sends a GET or POST request to a specific URL (e.g., `.../usdcop` or `.../ai`).
2.  **Processing:** The serverless function receives the request, identifies the required service, fetches data from the appropriate external source (or its own database), processes it, and formats it.
3.  **Response:** The API returns a clean, standardized JSON object containing the requested information.

Authentication is handled via JWT or Auth0 for protected endpoints, ensuring that access to sensitive or rate-limited services is secure.

## 4. User Experience Goals

The primary users of this API are developers. The key UX goals are:

- **Simplicity:** Endpoints should be intuitive and easy to remember (e.g., `/btc` for Bitcoin price).
- **Speed:** Responses should be fast, leveraging the performance of AWS Lambda.
- **Reliability:** The API should have high uptime and provide accurate, up-to-date information.
- **Clear Documentation:** The purpose, parameters, and response format of each endpoint should be clearly documented.
- **Helpful Error Messages:** When something goes wrong, the API should return meaningful error messages that help developers debug the issue quickly.
