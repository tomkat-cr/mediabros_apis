# System Patterns: mediabros_apis

## 1. System Architecture

`mediabros_apis` is a serverless application built on a microservices-oriented architecture, hosted entirely on AWS. The core components are:

-   **AWS Lambda:** The compute layer where the Python application code runs. The entire application is packaged and deployed as a single Lambda function, invoked by API Gateway.
-   **Amazon API Gateway:** Serves as the front door for all incoming HTTP requests. It routes requests to the appropriate endpoint handler within the Chalice application running on Lambda.
-   **Serverless Framework:** Used for defining and deploying the AWS infrastructure, including the Lambda function, API Gateway configuration, IAM roles, and environment variables, as specified in `serverless.yml`.
-   **AWS ECR (Elastic Container Registry):** The application is built and packaged as a Docker container image, which is stored in ECR and used by AWS Lambda for execution.
-   **External Integrations:** The system communicates with several third-party APIs for its core functionality:
    -   OpenAI API for AI-powered responses.
    -   Telegram API for system notifications and error reporting.
    -   Various financial data providers for currency and cryptocurrency exchange rates.

## 2. Key Technical Decisions

-   **Hybrid Framework Approach:** The project leverages both **AWS Chalice** and the **Serverless Framework**. Chalice is used for its strengths in rapidly developing Python-based serverless applications, while the Serverless Framework is used for more granular control over the AWS infrastructure, particularly for defining the ECR-based deployment.
-   **Containerized Lambda:** Instead of a traditional ZIP package, the Lambda function is deployed as a Docker container image. This approach provides a more consistent and controlled execution environment, simplifying dependency management, especially for binaries or libraries that need to be compiled.
-   **Dual Authentication Strategy:** The system is designed to support two distinct authentication mechanisms:
    1.  **JWT (JSON Web Tokens):** For internal services or users, managed directly by the application.
    2.  **Auth0:** For integrating with a third-party identity provider, allowing for more robust user management and security features like social logins.
-   **Centralized Configuration:** All configuration values (API keys, database URIs, feature flags) are managed via environment variables, following the principles of a 12-factor app. This makes the application portable across different environments (local, staging, production).

## 3. Design Patterns in Use

-   **Decorator Pattern:** The `@requires_auth` decorator is a prime example. It wraps endpoint functions to provide authentication and authorization logic in a clean, reusable, and non-invasive way. It elegantly handles the complexity of checking for JWT or Auth0 tokens before executing the core business logic.
-   **Modular Design (Separation of Concerns):** The `chalicelib` directory enforces a modular structure. Business logic is separated into distinct modules based on functionality (e.g., `api_openai.py`, `api_currency_exchange.py`, `utility_jwt.py`), making the codebase easier to navigate, maintain, and test.
-   **Facade Pattern (implied):** The API endpoints in `app.py` act as a facade. They provide a simple, unified interface to more complex underlying logic. For example, a single call to `/usdcop` hides the details of fetching, parsing, and calculating the exchange rate from an external source.

## 4. Component Relationships

1.  A `make deploy` command initiates the deployment process via the **Serverless Framework**.
2.  The Serverless Framework reads `serverless.yml`, builds the **Docker image** using the `Dockerfile`, and pushes it to **AWS ECR**.
3.  It then provisions or updates the **AWS Lambda** function to use the new container image and configures the **API Gateway** with the HTTP endpoints defined in `serverless.yml`.
4.  When a user makes an HTTP request to an endpoint, **API Gateway** triggers the **Lambda function**.
5.  The `lambda_handler.py` likely acts as the entry point, passing the request to the **Chalice application** (`app.py`).
6.  **Chalice** routes the request to the correct view function, which then calls the necessary modules in `chalicelib` to execute the business logic.

## 5. Critical Implementation Paths

-   **Authentication Flow:** The `requires_auth` decorator is the most critical security path. Its logic for parsing headers, validating tokens against JWKS (for Auth0) or a secret key (for JWT), and handling various error conditions is fundamental to the application's security.
-   **Deployment Pipeline:** The path from source code to a running application (`make deploy` -> `serverless deploy` -> ECR -> Lambda) is critical. Any failure in this chain prevents new features or fixes from reaching production.
-   **External API Interaction:** The functions within `chalicelib` that call out to external services (OpenAI, currency exchanges) are critical paths for functionality. Their error handling, retry logic (if any), and data parsing are essential for the application's reliability.
