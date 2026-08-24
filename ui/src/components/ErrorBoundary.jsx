/**
 * ==================================================
 * REETA — ui/src/components/ErrorBoundary.jsx
 * ==================================================
 * PURPOSE:
 *   Catches JavaScript errors anywhere in the child component
 *   tree and displays a fallback UI instead of crashing
 *   the entire dashboard (the "white screen of death").
 *
 *   React Error Boundaries MUST be class components —
 *   there is no hook equivalent for componentDidCatch.
 * ==================================================
 */

import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render shows the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log the error for debugging
    console.error('[REETA ErrorBoundary] Caught error:', error, errorInfo);
    this.setState({ errorInfo });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center h-full bg-gray-900 rounded-xl border border-red-900/50 p-8 text-center">
          <div className="w-16 h-16 rounded-full bg-red-900/30 flex items-center justify-center mb-4">
            <AlertTriangle className="w-8 h-8 text-red-400" />
          </div>
          <h2 className="text-lg font-semibold text-red-300 mb-2">
            {this.props.panelName || 'Component'} encountered an error
          </h2>
          <p className="text-sm text-gray-400 mb-1 max-w-md">
            {this.state.error?.message || 'An unexpected error occurred.'}
          </p>
          <p className="text-xs text-gray-600 mb-6">
            The rest of REETA is still running. Only this panel crashed.
          </p>
          <button
            onClick={this.handleReset}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg transition-colors text-sm"
          >
            <RefreshCw className="w-4 h-4" />
            Retry
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
