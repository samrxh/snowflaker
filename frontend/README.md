# Snowflaker Frontend

React client for the Snowflaker puzzle board.

## Requirements

- Node.js 18+ (recommended)
- npm
- Snowflaker backend running (default: `http://localhost:8000`)

## Environment

The app can connect to the backend using:

- `REACT_APP_API_BASE_URL` (optional)

If not set, it defaults to `http://localhost:8000`.

## Run locally

```bash
npm install
npm start
```

The app runs at `http://localhost:3000`.

## Available scripts

- `npm start` - start dev server
- `npm test` - run tests
- `npm run build` - create production build

## Notes

- Board data is loaded from `GET /board?size=small|big`
- Cell updates are sent to `POST /update?row=<r>&col=<c>&value=<1-6>&size=small|big`
