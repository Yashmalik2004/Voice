/**
 * App — root component.
 *
 * Manages the single-page voice assistant UI:
 *   - Idle: show Talk button, prompt user to start
 *   - Connecting/Active: show status + animated button
 *   - Disconnected/Error: show reconnect option
 */

import { useLiveKit } from './hooks/useLiveKit'
import { TalkButton } from './components/TalkButton'
import { StatusIndicator } from './components/StatusIndicator'
import './index.css'

export default function App() {
  const { status, connect, disconnect, errorMessage } = useLiveKit()

  const isFinished = status === 'disconnected' || status === 'error'

  return (
    <main className="app" role="main">
      <div className="app-card">
        {/* Header */}
        <header className="app-header">
          <h1 className="app-title">Voice Assistant</h1>
          <p className="app-subtitle">
            {status === 'idle'
              ? 'Press Talk to start a conversation'
              : status === 'disconnected'
              ? 'Conversation ended'
              : status === 'error'
              ? 'Something went wrong'
              : 'Speak naturally — I\'m listening'}
          </p>
        </header>

        {/* Central interaction area */}
        <div className="app-center">
          <TalkButton
            status={status}
            onTalk={connect}
            onEnd={disconnect}
          />
          <StatusIndicator status={status} errorMessage={errorMessage} />
        </div>

        {/* Footer / reconnect */}
        <footer className="app-footer">
          {isFinished ? (
            <button
              id="reconnect-button"
              className="reconnect-btn"
              onClick={connect}
              aria-label="Start a new conversation"
            >
              Start new conversation
            </button>
          ) : (
            <p>Powered by LiveKit · GPT-4.1 · Cartesia</p>
          )}
        </footer>
      </div>
    </main>
  )
}
