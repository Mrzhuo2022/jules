# SubTracker Backend Plan

This document outlines the complete technical plan for the backend of the SubTracker application, a personal subscription management and reminder tool.

## 1. Technology Stack Recommendation

| Component           | Technology      | Why?                                                                                                                                                             |
| ------------------- | --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Backend Framework** | **Python/FastAPI**  | **Developer Velocity & Performance:** FastAPI's modern Python features, type hints, and automatic documentation generation lead to extremely fast development cycles. It's one of the fastest Python frameworks, ensuring a responsive API. The ecosystem (Pydantic, Starlette) is mature and robust. |
| **Database**        | **PostgreSQL**      | **Reliability & Scalability:** PostgreSQL is a powerful, open-source object-relational database with a strong reputation for reliability, data integrity, and feature richness. It handles date/time and currency data types excellently. It's more than enough for the MVP and can scale effortlessly for millions of users. |
| **Scheduled Jobs**  | **APScheduler**     | **Simplicity & Integration:** `APScheduler` is a well-established Python library that can run in-process with the FastAPI application. This simplifies the MVP architecture by avoiding the need for a separate worker process or external services like Celery/Redis or system cron, reducing complexity and cost. |

## 2. System Architecture Design

The architecture is designed for simplicity, low cost, and reliability, focusing on the core MVP features.

```mermaid
graph TD
    A[User] -- HTTPS --> B[Web App (React/Vue/etc.)];
    B -- REST API Call --> C{Backend API (FastAPI)};
    C -- CRUD Ops --> D[(PostgreSQL DB)];

    subgraph "Scheduled Job Runner (In-Process)"
        E[APScheduler]
    end

    C -- Triggers Job --> E;
    E -- Reads Subscriptions --> D;
    E -- Sends Reminders --> F((Email Service));
    F -- Sends Email --> A;

    style C fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#bbf,stroke:#333,stroke-width:2px
```

## 3. Core Database Schema Design

The schema consists of two core tables: `users` for authentication and `subscriptions` to track user-entered data.

```sql
-- Enable the pgcrypto extension to generate UUIDs
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create the users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create the subscriptions table
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    service_name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    billing_cycle VARCHAR(50) NOT NULL CHECK (billing_cycle IN ('monthly', 'yearly')),
    next_renewal_date DATE NOT NULL,
    last_reminder_sent_at TIMESTAMPTZ, -- To track when the last reminder was sent
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Add indexes for performance
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_next_renewal_date ON subscriptions(next_renewal_date);
```

## 4. API Endpoint Design (RESTful)

The V1 API is designed to be clean, predictable, and easy for a frontend client to consume.

| HTTP Method | Endpoint Path                 | Description                                                                 |
| :---------- | :---------------------------- | :-------------------------------------------------------------------------- |
| `POST`      | `/api/v1/auth/register`       | Register a new user account.                                                |
| `POST`      | `/api/v1/auth/login`          | Authenticate a user and receive a JWT access token.                         |
| `POST`      | `/api/v1/subscriptions`       | Create a new subscription for the authenticated user.                       |
| `GET`       | `/api/v1/subscriptions`       | Get a list of all subscriptions for the authenticated user.                 |
| `GET`       | `/api/v1/subscriptions/{id}`  | Get the details of a single subscription by its ID.                         |
| `PUT`       | `/api/v1/subscriptions/{id}`  | Update the details of an existing subscription.                             |
| `DELETE`    | `/api/v1/subscriptions/{id}`  | Delete a subscription.                                                      |

## 5. Renewal Reminder Logic

The renewal reminder logic is encapsulated in a daily scheduled job.

1.  **Trigger:** The job is triggered once every 24 hours by `APScheduler`.
2.  **Query:** The job executes a query to find all subscriptions that meet two conditions:
    -   The `next_renewal_date` is between today and 7 days from now (`WHERE next_renewal_date BETWEEN NOW() AND NOW() + INTERVAL '7 days'`).
    -   A reminder has not been sent recently. This is checked using the `last_reminder_sent_at` timestamp. A reminder is considered "recent" if it was sent within the last 7 days (`AND (last_reminder_sent_at IS NULL OR last_reminder_sent_at < NOW() - INTERVAL '7 days')`). This prevents sending duplicate emails if the job runs more than once or if a renewal date is changed.
3.  **Action:** For each subscription found, the system will:
    -   Queue an email to be sent to the user associated with the `user_id`. The email will contain the service name, price, and renewal date.
    -   Update the `last_reminder_sent_at` field for that subscription record to the current timestamp (`NOW()`). This marks the reminder as sent and prevents it from being picked up in the next run.

## 6. Frontend Support Considerations

This backend design is tailored to support a modern, minimalist, and intuitive frontend application with the following features:

-   **Stateless Authentication:** The use of **JWT (JSON Web Tokens)** for authentication means the API is stateless. The frontend client simply needs to acquire a token upon login and include it in the `Authorization: Bearer <token>` header for all subsequent requests to protected endpoints.
-   **Predictable JSON Responses:** By leveraging FastAPI and Pydantic models, all API responses are guaranteed to have a consistent and well-defined JSON structure. This eliminates guesswork for the frontend developer and allows for easy parsing of data.
-   **Standard HTTP for State Management:** The API uses standard HTTP methods (`POST`, `GET`, `PUT`, `DELETE`) and status codes (`200`, `201`, `400`, `401`, `404`) to communicate the outcome of an operation. This makes state management on the frontend (e.g., handling loading, success, and error states) straightforward and conventional.
-   **Clear Data Contracts:** The auto-generated OpenAPI documentation (`/docs`) from FastAPI provides a live, interactive "contract" that frontend developers can use to understand and test every endpoint, including its parameters and response models, without needing to read the backend source code.
