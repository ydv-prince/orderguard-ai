# Security Considerations

## Authentication
- OrderGuard uses JSON Web Tokens (JWT) for authenticating users.
- Google OAuth is integrated for secure third-party login. Validate the audience claims carefully on the backend to prevent token substitution attacks.

## Data Isolation
- E-commerce merchants must only view and interact with their own data.
- The backend API enforces tenant isolation by linking every created order to the currently authenticated `user_id`.

## Secrets Management
- Sensitive tokens and secrets are stored in `.env`.
- `.env` is ignored via `.gitignore` and must NEVER be committed to the repository.
- Ensure production environments inject these variables securely.

## Current Limitations
- OAuth audience validation might require stricter bounds in production environments.
- API Rate Limiting is not currently enforced. Consider adding `slowapi` or similar to protect endpoints against brute force or DoS attacks.
