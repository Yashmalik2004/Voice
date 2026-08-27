/**
 * TalkButton — large central call-to-action button.
 * Animates during listening and speaking states.
 */

import type { ConnectionStatus } from '../hooks/useLiveKit'
import './TalkButton.css'

interface Props {
  status: ConnectionStatus
  onTalk: () => void
  onEnd: () => void
}

function getMicIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className="talk-icon" aria-hidden="true">
      <path d="M12 1a4 4 0 0 1 4 4v7a4 4 0 0 1-8 0V5a4 4 0 0 1 4-4zm0 2a2 2 0 0 0-2 2v7a2 2 0 0 0 4 0V5a2 2 0 0 0-2-2z"/>
      <path d="M5 10a1 1 0 0 1 2 0 5 5 0 0 0 10 0 1 1 0 0 1 2 0 7 7 0 0 1-6 6.92V19h3a1 1 0 0 1 0 2H8a1 1 0 0 1 0-2h3v-2.08A7 7 0 0 1 5 10z"/>
    </svg>
  )
}

function getEndIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className="talk-icon" aria-hidden="true">
      <path d="M19.59 7l-7.6 7.6-3.54-3.54-1.41 1.42 4.95 4.95 9.01-9-1.41-1.43z"/>
      <path d="M.41 0L0 .41l6.59 6.59C4.35 8.87 3 11.28 3 14a9 9 0 0 0 9 9c2.72 0 5.13-1.35 6.59-3.41L22 23.59 23.59 22 .41 0z" opacity=".3"/>
      <path d="M12 5a9 9 0 0 1 7.03 14.61l-1.43-1.43A7 7 0 0 0 12 5z" opacity=".3"/>
    </svg>
  )
}

export function TalkButton({ status, onTalk, onEnd }: Props) {
  const isActive = status === 'listening' || status === 'thinking' || status === 'speaking'
  const isConnecting = status === 'connecting'

  return (
    <div className="talk-button-wrapper">
      {/* Ripple rings shown during listening/speaking */}
      {isActive && (
        <>
          <div className={`ripple ripple-1 ${status}`} />
          <div className={`ripple ripple-2 ${status}`} />
          <div className={`ripple ripple-3 ${status}`} />
        </>
      )}

      <button
        id="talk-button"
        className={`talk-button ${isActive ? 'talk-button--active' : ''} ${isConnecting ? 'talk-button--connecting' : ''}`}
        onClick={isActive ? onEnd : onTalk}
        disabled={isConnecting || status === 'disconnected'}
        aria-label={isActive ? 'End conversation' : 'Start conversation'}
        aria-pressed={isActive}
      >
        {isActive ? getEndIcon() : getMicIcon()}
        <span className="talk-button-label">
          {isConnecting ? 'Connecting…' : isActive ? 'End' : 'Talk'}
        </span>
      </button>
    </div>
  )
}
