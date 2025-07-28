# Tech Context: mediabros_apis

## 1. Technologies Used

-   **Backend Language:** Python 3.11
-   **Core Frameworks:**
    -   **AWS Chalice:** For routing, request/response handling, and rapid serverless development.
    -   **FastAPI (components):** Pydantic models are used for data validation and serialization, bringing type safety and structure to the application.
-   **Deployment & Infrastructure:**
    -   **AWS Lambda:** The serverless compute service running the application code.
    -   **Amazon API Gateway:** Manages all HTTP endpoints and triggers the Lambda function.
    -   **Serverless Framework:** Orchestrates the deployment of all AWS resources as defined in `serverless.yml`.
    -   **Docker:** The application is packaged and deployed as a container image to AWS Lambda.
    -   **AWS ECR:** Stores the Docker images used for Lambda deployments.
-   **Database:**
    -   **MongoDB:** Used for data persistence, connected via a `DB_URI` environment variable.
-   **Web Scraping & Automation:**
    -   **Selenium:** Used for browser automation to scrape data from websites that require JavaScript rendering.
    -   **BeautifulSoup4 & Cloudscraper:** For parsing HTML and bypassing cloud-based bot detection.

## 2. Development Setup

-   **Python Environment:** `pipenv` is used to manage Python packages and create a virtual environment, ensuring dependency isolation and reproducible builds.
-   **Task Automation:** A `Makefile` provides a set of simple, high-level commands (`make install`, `make run`, `make deploy`) that abstract away the underlying shell scripts and commands.
-   **Configuration:** All environment-specific settings (API keys, database connections, etc.) are managed through a `.env` file, with `.env-example` serving as a template.
-   **Local Execution:** The application can be run locally for development and testing using the `make run` command, which executes the `run_aws.sh` script.

## 3. Technical Constraints

-   **Serverless Limitations:** The application operates within the constraints of AWS Lambda, such as a maximum execution timeout (set to 29 seconds) and memory limits (configured to 2048 MB). These constraints influence the design of long-running tasks.
-   **Deployment Package Size:** The use of Selenium and a headless browser (Chrome) introduces large binaries. This has necessitated a move from traditional ZIP deployments to **Docker image-based deployments** to overcome Lambda's package size limitations.
-   **Dependency on External Services:** The application's core functionality is tightly coupled to the availability and performance of third-party APIs (OpenAI, currency exchanges). Proper error handling and timeouts are critical.

## 4. Dependencies

-   **Python Packages (`Pipfile`):**
    -   **Web & API:** `chalice`, `fastapi`, `requests`, `boto3`, `python-multipart`.
    -   **Authentication:** `python-jose[cryptography]` (for JWTs), `passlib[bcrypt]` (for hashing).
    -   **Data:** `pymongo`, `beautifulsoup4`, `cloudscraper`, `selenium`.
    -   **Utilities:** `python-dotenv`, `wheel`.
    -   **Custom Libraries:** The project depends on several custom libraries hosted on GitHub for fetching exchange rates (`monitor-exchange-rates`, `bcv-exchange-rates`, `cop-exchange-rates`).
-   **Development Dependencies (`Pipfile`):**
    -   `pytest` and `pytest-chalice` for the testing suite.
-   **Node.js Tooling (`package.json`):**
    -   `npm` is used as a script runner to orchestrate various deployment and maintenance tasks via shell scripts.
-   **System-Level (`Dockerfile`):**
    -   The Docker image includes various `yum` packages (`unzip`, `git`, and X11/GTK libraries) required to run headless Chrome on the Amazon Linux 2 base image.

## 5. Tool Usage Patterns

-   **`make`:** The primary interface for developers. It simplifies complex workflows into single commands.
-   **`pipenv`:** The standard for managing the Python development environment. `Pipfile` and `Pipfile.lock` ensure deterministic builds.
-   **`serverless` CLI:** The core engine for infrastructure-as-code. It interprets `serverless.yml` to create and manage all AWS resources.
-   **`docker` CLI:** Used during the deployment process (invoked by the Serverless Framework) to build the application container image.
-   **Shell Scripts (`run_*.sh`):** Contain the detailed logic for different deployment targets (AWS, Vercel, Fly.io), providing a layer of abstraction between the `Makefile`/`package.json` and the specific CLI commands.
