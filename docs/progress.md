# Progress & Status: mediabros_apis

## 1. What Works

-   **Core API Functionality:** All primary endpoints listed in the `README.md` and `serverless.yml` are implemented and functional. This includes:
    -   Currency exchange (USD, COP, VEB).
    -   Cryptocurrency price lookups (BTC, ETH, and any symbol).
    -   OpenAI integration for AI queries.
-   **Deployment Pipeline:** The application can be successfully deployed to AWS Lambda using the `make deploy` command. The container-based deployment via the Serverless Framework and ECR is operational.
-   **Authentication:** Both JWT and Auth0 authentication mechanisms are implemented. The `@requires_auth` decorator correctly protects endpoints.
-   **Local Development:** The development environment can be set up and run locally using `make install` and `make run`.
-   **Unit Testing:** A solid foundation of unit tests exists for critical utility and authentication functions in `tests/test_app_functions.py`, ensuring the correctness of these core components.

## 2. What's Left to Build

-   **Comprehensive Integration Tests:** While the setup for integration testing is in place (`pytest-chalice`, `conftest.py`), the actual tests for the API endpoints need to be written. This is the highest-priority development task to ensure end-to-end functionality and prevent regressions.
-   **API Documentation (Swagger/OpenAPI):** There is no automated API documentation generation. Integrating a tool like Swagger UI would make the API much easier for new developers to explore and use.
-   **CI/CD Pipeline:** The deployment process is currently manual (run from a developer's machine). Implementing a CI/CD pipeline (e.g., with GitHub Actions) would automate testing and deployment, improving consistency and safety.

## 3. Current Status

-   **Phase:** The project is in a **maintenance and enhancement phase**. The core features are complete, and the focus has shifted to improving its robustness, reliability, and maintainability.
-   **Immediate Priority:** The current active task is to complete the initial documentation of the project and then proceed with writing integration tests.

## 4. Known Issues

-   **Dependency Installation:** The `pytest` and `pytest-chalice` dependencies have been added to the `Pipfile` but must be installed by running `pipenv install --dev` before the test suite can be run.
-   **Potential for Configuration Drift:** The project has deployment scripts for AWS, Vercel, and Fly.io (`run_aws.sh`, `run_vercel.sh`, `run_fly_io.sh`). While the primary focus is AWS, the presence of other scripts could lead to confusion or outdated deployment methods if not properly maintained or documented.

## 5. Evolution of Project Decisions

-   **Deployment Strategy:** The project initially used a standard Chalice deployment but hit the AWS Lambda package size limit due to large dependencies like Selenium and Chrome. This forced a strategic pivot to a more robust **Docker container-based deployment model**, managed by the Serverless Framework. This was a critical adaptation to support the project's functional requirements.
-   **Testing:** The project is evolving from relying on manual endpoint testing (as suggested by the test URLs in the `README`) to a formal, automated testing culture. The recent addition of unit tests and the setup for integration tests mark a significant step towards improving code quality.
-   **Framework Choice:** The decision to blend Chalice with Serverless Framework and FastAPI components reflects a pragmatic approach, taking the best features from each tool to build a powerful and flexible application. It started as a pure Chalice app and incorporated other tools as needs grew more complex.
