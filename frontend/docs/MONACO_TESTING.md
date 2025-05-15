# Monaco Editor Testing Guide

This document outlines the testing patterns and best practices for components that use Monaco Editor in the MindMeld application.

## Table of Contents

1. [Introduction](#introduction)
2. [Monaco Editor Test Utilities](#monaco-editor-test-utilities)
3. [Testing Patterns](#testing-patterns)
4. [Best Practices](#best-practices)
5. [Examples](#examples)
6. [Troubleshooting](#troubleshooting)

## Introduction

Monaco Editor is a powerful code editor that we use in various components across the MindMeld application, particularly for code analysis and editing. Testing components that use Monaco Editor presents some challenges:

- Monaco is loaded dynamically and relies on browser APIs
- It has a complex API surface with many methods
- It has side effects that can be difficult to mock
- It relies on DOM measurements and positioning

To address these challenges, we've created a set of test utilities that make it easier to test components that use Monaco Editor.

## Monaco Editor Test Utilities

We've created a set of utilities in `/frontend/test-utils/monaco/` that provide:

1. A mock implementation of Monaco Editor that works in tests
2. Helper functions for common testing patterns
3. Type-compatible mocks of Monaco APIs

### Available Utilities

- `MockMonacoEditor`: A React component that mimics Monaco's behavior
- `createMockEditor`: Creates a mock editor instance with common methods
- `mockDynamicMonacoImport`: For mocking Next.js dynamic imports
- `MockMonaco`: Mock implementation of the Monaco namespace
- `mockMonaco`: Helper function to set up common mocks
- `resetMonacoMocks`: Helper to reset all Monaco mocks between tests

## Testing Patterns

### Basic Component Testing

For basic component tests that don't need to interact with Monaco's specific APIs:

```tsx
import { mockMonaco } from '@test-utils/monaco';

// Set up Monaco mocks
mockMonaco();

describe('MyEditorComponent', () => {
  test('renders correctly', () => {
    render(<MyEditorComponent />);
    expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
  });
});
```

### Testing Editor Interactions

For tests that need to interact with the editor:

```tsx
import { mockMonaco, mockEditorInstances } from '@test-utils/monaco';

mockMonaco();

describe('MyEditorComponent', () => {
  test('updates content when typing', async () => {
    const { container } = render(<MyEditorComponent />);
    
    // Get the mock editor element
    const editorTextarea = screen.getByTestId('mock-editor-textarea');
    
    // Simulate typing
    fireEvent.change(editorTextarea, { target: { value: 'new content' } });
    
    // Check if the component reacted to the change
    await waitFor(() => {
      expect(screen.getByText('Content updated')).toBeInTheDocument();
    });
  });
});
```

### Testing Editor API Calls

For testing components that call Monaco editor methods:

```tsx
import { mockMonaco, createMockEditor } from '@test-utils/monaco';
import { vi } from 'vitest';

mockMonaco();

describe('CodeNavigation', () => {
  test('navigates to specific line when requested', () => {
    // Create a mock editor with spied methods
    const mockEditor = createMockEditor('test-editor');
    mockEditor.revealLineInCenter = vi.fn();
    
    // Render component with this editor
    const { result } = renderHook(() => useCodeNavigation(mockEditor));
    
    // Call the navigation function
    result.current.goToLine(10);
    
    // Check if the editor method was called
    expect(mockEditor.revealLineInCenter).toHaveBeenCalledWith(10);
  });
});
```

## Best Practices

1. **Always reset mocks between tests**:
   ```tsx
   import { resetMonacoMocks } from '@test-utils/monaco';
   
   beforeEach(() => {
     resetMonacoMocks();
   });
   ```

2. **Test component behavior, not Monaco implementation**:
   Focus on testing how your component interacts with Monaco, not the internal implementation of Monaco itself.

3. **Use data-testid attributes**:
   Add data-testid attributes to key elements in your components to make them easier to select in tests.

4. **Mock minimal functionality**:
   Only mock the Monaco functionality that your component actually uses.

5. **Test in isolation**:
   Test Monaco-based components in isolation before testing their integration with other components.

6. **Handle async behavior**:
   Monaco operations are often asynchronous, so use `waitFor` and `async/await` in your tests.

7. **Test with different editor configurations**:
   Test your components with different Monaco configurations (language, theme, etc.).

## Examples

### Testing the CodeEditor Component

```tsx
import { mockMonaco } from '@test-utils/monaco';
import { render, screen, fireEvent } from '@testing-library/react';
import CodeEditor from '../components/CodeEditor';

mockMonaco();

describe('CodeEditor', () => {
  test('applies language settings', () => {
    render(<CodeEditor language="python" />);
    const editorContainer = screen.getByTestId('monaco-editor');
    expect(editorContainer).toHaveAttribute('data-language', 'python');
  });

  test('calls onChange when content changes', () => {
    const handleChange = vi.fn();
    render(<CodeEditor onChange={handleChange} />);
    
    const textarea = screen.getByTestId('mock-editor-textarea');
    fireEvent.change(textarea, { target: { value: 'new code' } });
    
    expect(handleChange).toHaveBeenCalledWith('new code');
  });
});
```

### Testing the CodeAnalyzer Component

```tsx
import { mockMonaco } from '@test-utils/monaco';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import CodeAnalyzer from '../components/CodeAnalyzer';

mockMonaco();

describe('CodeAnalyzer', () => {
  test('analyzes code and shows feedback', async () => {
    render(<CodeAnalyzer />);
    
    // Type some code with errors
    const editor = screen.getByTestId('mock-editor-textarea');
    fireEvent.change(editor, { 
      target: { value: 'function test() {\n  const x = 5\n}' } 
    });
    
    // Trigger analysis
    fireEvent.click(screen.getByRole('button', { name: /analyze/i }));
    
    // Check for feedback
    await waitFor(() => {
      expect(screen.getByText(/missing semicolon/i)).toBeInTheDocument();
    });
  });
});
```

## Troubleshooting

### Common Issues

1. **Editor not found in tests**:
   - Check that you're using the right testid (`mock-editor-textarea`)
   - Ensure Monaco mocks are set up before rendering

2. **"Not implemented" errors**:
   - You might be trying to use a Monaco method that isn't implemented in our mocks
   - Add the method to the mock implementation or use a different approach

3. **Event handlers not firing**:
   - Make sure you're using `fireEvent` correctly
   - Check that the event is being applied to the textarea, not the container

4. **Test timeouts**:
   - Monaco operations can be async, use `waitFor` with reasonable timeouts

5. **Inconsistent test results**:
   - Make sure to reset mocks between tests

### Getting Help

If you encounter issues with Monaco editor testing that aren't covered here:

1. Check the test utilities implementation in `/frontend/test-utils/monaco/`
2. Review the Monaco Editor API documentation
3. Look at existing test examples in the codebase
4. Ask for help in the development chat

---

This guide should help you effectively test components that use Monaco Editor. Remember that the goal is to test your component's behavior, not Monaco's internal implementation.