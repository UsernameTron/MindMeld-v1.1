import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import CodeAnalyzer from './CodeAnalyzer';

const queryClient = new QueryClient();

describe('CodeAnalyzer', () => {
  it('renders the code editor and analyze button', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <CodeAnalyzer />
      </QueryClientProvider>
    );
    expect(screen.getByLabelText(/code editor/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /analyze code/i })).toBeInTheDocument();
  });

  it('shows error if code input is empty and analyze is clicked', async () => {
    render(
      <QueryClientProvider client={queryClient}>
        <CodeAnalyzer />
      </QueryClientProvider>
    );
    const codeInput = screen.getByLabelText(/code editor/i);
    fireEvent.change(codeInput, { target: { value: '' } });
    fireEvent.click(screen.getByRole('button', { name: /analyze code/i }));
    expect(await screen.findByText(/code input cannot be empty/i)).toBeInTheDocument();
  });

  it('disables analyze button when code is empty', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <CodeAnalyzer />
      </QueryClientProvider>
    );
    const codeInput = screen.getByLabelText(/code editor/i);
    fireEvent.change(codeInput, { target: { value: '' } });
    expect(screen.getByRole('button', { name: /analyze code/i })).toBeDisabled();
  });

  it('shows loading state when analyzing', async () => {
    // Mock analyzeCode to delay
    jest.mock('../../../services/codeService', () => ({
      analyzeCode: () => new Promise(resolve => setTimeout(() => resolve({
        summary: { score: 90, grade: 'A', description: 'Great code!' },
        complexity: { cyclomatic: 2, linesOfCode: 10, functions: 1, maintainability: 95 },
        issues: [],
        suggestions: [],
      }), 100)),
    }));
    render(
      <QueryClientProvider client={queryClient}>
        <CodeAnalyzer />
      </QueryClientProvider>
    );
    fireEvent.click(screen.getByRole('button', { name: /analyze code/i }));
    expect(await screen.findByText(/analyzing/i)).toBeInTheDocument();
  });
});
