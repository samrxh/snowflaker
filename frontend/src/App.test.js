import { render, screen } from '@testing-library/react';
import App from './App';

beforeEach(() => {
  global.fetch = jest.fn().mockResolvedValue({
    ok: true,
    json: async () => ({ grid: [[0]] }),
  });
});

afterEach(() => {
  jest.resetAllMocks();
});

test('renders app title and board size controls', async () => {
  render(<App />);
  expect(await screen.findByRole('heading', { name: /snowflaker/i })).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /small board/i })).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /big board/i })).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /clear board/i })).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /solve board/i })).toBeInTheDocument();
});
