# AI-Powered Lead Generation Tool

<div align="center">

# AI-Powered Lead Generation Tool

<p style="font-size: 18px; padding: 10px; margin: 20px 0; background-color: #5271FF; color: white; border-radius: 8px; width: 85%; max-width: 800px;">
An AI-driven platform for lead generation, enrichment, and automated outreach
</p>

[![GitHub Stars](https://img.shields.io/github/stars/skanderbenali/AI-powered-lead-generation-tool?style=for-the-badge)](https://github.com/skanderbenali/AI-powered-lead-generation-tool/stargazers)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

</div>

A full-stack SaaS application for AI-driven lead generation, enrichment, and automated outreach. This project provides a comprehensive solution for businesses to find, score, enrich, and engage with high-quality leads.

## 🚀 Features

- **Lead Discovery**: Search and scrape leads from LinkedIn and company websites
- **AI-Powered Lead Scoring**: Automatically score leads based on quality and fit
- **Email Prediction**: Predict email addresses based on name and company patterns
- **Lead Enrichment**: Enhance lead data with additional information from multiple sources
- **AI Email Generation**: Create personalized outreach emails using GPT models
- **Campaign Management**: Create, track, and optimize email campaigns
- **Analytics Dashboard**: Monitor campaign performance and conversion metrics
- **Team Collaboration**: Manage projects and share leads with team members
- **API Access**: Integrate with existing tools and workflows

## 🏗️ Project Architecture

This project is structured as a monorepo with several interconnected components:

```
/
├── frontend/            # Next.js dashboard UI with Tailwind CSS
├── backend/             # FastAPI backend with Celery for async tasks
├── ml/                  # Machine learning models and AI components
├── scraper/             # Scraping microservice for lead generation
├── shared/              # Shared types, models, and utilities
└── docker-compose.yml   # Docker Compose configuration for all services
```

### Component Overview

| Component | Technology | Purpose |
|-----------|------------|---------|
| Frontend | Next.js, React, Tailwind CSS | User interface for managing leads and campaigns |
| Backend | FastAPI, SQLAlchemy, Celery | API server for business logic and data management |
| ML | Python, XGBoost, OpenAI GPT | Lead scoring, email prediction, and content generation |
| Scraper | Python, BeautifulSoup, Puppeteer | Data acquisition from LinkedIn and company websites |
| Database | PostgreSQL | Persistent storage for user and lead data |
| Cache | Redis | Task queuing and temporary data storage |

## 🛠️ Tech Stack

- **Frontend**: Next.js, React, Tailwind CSS, TypeScript
- **Backend**: FastAPI, SQLAlchemy, Alembic, Celery
- **Database**: PostgreSQL, Redis
- **ML**: XGBoost/RandomForest, OpenAI GPT, scikit-learn
- **Scraping**: BeautifulSoup, Puppeteer, Selenium
- **Deployment**: Docker, Docker Compose
- **Authentication**: JWT, OAuth2 (Google & GitHub)

## ⚙️ Getting Started

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- OpenAI API key (for AI features)
- Google OAuth credentials (for Google authentication)
- GitHub OAuth credentials (for GitHub authentication)

### Installation with Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/skanderbenali/AI-powered-lead-generation-tool.git
   cd AI-powered-lead-generation-tool
   ```

2. Create a `.env` file in the root directory (use `.env.example` as a template):
   ```bash
   cp .env.example .env
   # Edit .env with your configuration, including OAuth credentials
   ```
   
   Key environment variables to configure:
   ```
   # Core Application
   SECRET_KEY=your_secret_key
   DATABASE_URL=postgresql://leadgen:leadgenpass@postgres:5432/leadgen
   REDIS_URL=redis://redis:6379/0
   
   # OAuth Configuration
   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   GITHUB_CLIENT_ID=your_github_client_id
   GITHUB_CLIENT_SECRET=your_github_client_secret
   FRONTEND_URL=http://localhost:3000
   
   # API Configuration
   OPENAI_API_KEY=your_openai_api_key
   ```

3. Start all services with Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. Access the dashboard at `http://localhost:3000`

5. API documentation is available at `http://localhost:8000/docs`

### Local Development Setup

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

#### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Scraper Service

```bash
cd scraper
pip install -r requirements.txt
uvicorn main:app --reload --port 8080
```

#### ML Service

```bash
cd ml
pip install -r requirements.txt
python -m lead_scoring.model  # Train and save the model
```

## 📋 Project Structure Details

### Frontend (`/frontend`)

```
frontend/
├── components/          # Reusable UI components
├── contexts/            # React context providers
├── lib/                 # Utility functions
├── pages/               # Next.js pages and API routes
├── public/              # Static assets
└── styles/              # Global styles and Tailwind config
```

### Backend (`/backend`)

```
backend/
├── alembic/             # Database migrations
├── app/
│   ├── deps/            # Dependency injection
│   ├── models/          # SQLAlchemy models
│   ├── routers/         # API route handlers
│   ├── schemas/         # Pydantic schemas
│   └── services/        # Business logic
│       └── tasks/       # Celery tasks
├── main.py              # Application entry point
└── worker.py            # Celery worker configuration
```

### ML (`/ml`)

```
ml/
├── lead_scoring/        # Lead scoring model
├── email_generation/    # Email generation with GPT
└── email_prediction/    # Email address prediction
```

### Scraper (`/scraper`)

```
scraper/
├── app/
│   ├── linkedin.py      # LinkedIn scraping
│   ├── website.py       # Website scraping
│   └── tasks.py         # Scraping tasks
└── main.py              # Scraper service entry point
```

### Shared (`/shared`)

```
shared/
├── types/               # TypeScript type definitions
└── utils/               # Shared utility functions
```

## 🔄 API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token
- `GET /auth/google` - Initiate Google OAuth authentication
- `GET /auth/google/callback` - Handle Google OAuth callback
- `GET /auth/github` - Initiate GitHub OAuth authentication
- `GET /auth/github/callback` - Handle GitHub OAuth callback
- `GET /auth/me` - Get current user profile

### Leads

- `GET /leads` - List leads
- `POST /leads` - Create a lead
- `GET /leads/{id}` - Get lead details
- `PUT /leads/{id}` - Update lead
- `DELETE /leads/{id}` - Delete lead
- `POST /leads/search` - Search leads
- `POST /leads/{id}/enrich` - Enrich lead data

### Projects

- `GET /projects` - List projects
- `POST /projects` - Create a project
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project
- `GET /projects/{id}/stats` - Get project statistics

### Emails

- `GET /emails/templates` - List email templates
- `POST /emails/templates` - Create a template
- `GET /emails/campaigns` - List email campaigns
- `POST /emails/campaigns` - Create a campaign
- `POST /emails/campaigns/{id}/start` - Start a campaign

### AI

- `POST /ai/generate-email` - Generate an email template
- `POST /ai/predict-email` - Predict an email address
- `POST /ai/score-leads` - Score leads

## 📦 Deployment

This project is designed to be deployed with Docker Compose for simplicity, but can also be deployed to cloud providers like AWS, Azure, or GCP.

### Production Considerations

- Set up proper API keys and secrets
- Configure HTTPS
- Set up monitoring and logging
- Configure backups for PostgreSQL
- Scale services based on load

## 🧪 Testing

- **Frontend**: Jest for unit tests, Cypress for end-to-end tests
- **Backend**: Pytest for unit and integration tests
- **ML**: Validation and test sets for model evaluation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you have any questions or need help, please open an issue on GitHub or contact the team at support@example.com.

## 🔐 OAuth Configuration

### Setting Up OAuth

1. **Google OAuth**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Navigate to APIs & Services > Credentials
   - Create OAuth client ID credentials
   - Set the authorized redirect URI to `http://localhost:8000/auth/google/callback`
   - Add the Client ID and Client Secret to your `.env` file

2. **GitHub OAuth**:
   - Go to your [GitHub Settings](https://github.com/settings/developers)
   - Navigate to Developer Settings > OAuth Apps
   - Create a new OAuth App
   - Set the callback URL to `http://localhost:8000/auth/github/callback`
   - Add the Client ID and Client Secret to your `.env` file

### Using OAuth in the Application

Users can authenticate via:

1. Traditional username/password login
2. "Login with Google" button
3. "Login with GitHub" button

OAuth users are automatically registered in the system during their first login. The system will:

- Create a new user account if needed
- Link the OAuth account to the user's profile
- Store profile information from the OAuth provider (name, email, avatar)

Users can view and manage their profile information, including data obtained through OAuth providers, on the Profile page.
