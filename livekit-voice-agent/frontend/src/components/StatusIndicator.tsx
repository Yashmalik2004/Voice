/**
 * StatusIndicator — displays the current agent/connection state with
 * an animated orb and a text label.
 */

import type { ConnectionStatus } from '../hooks/useLiveKit'
import './StatusIndicator.css'

interface Props {
  status: ConnectionStatus
  errorMessage?: string | null
}

const STATUS_CONFIG: Record<ConnectionStatus, { label: string; className: string }> = {
  idle: { label: 'Ready', className: 'status-idle' },
  connecting: { label: 'Connecting…', className: 'status-connecting' },
  listening: { label: 'Listening…', className: 'status-listening' },
  thinking: { label: 'Thinking…', className: 'status-thinking' },
  speaking: { label: 'Speaking…', className: 'status-speaking' },
  disconnected: { label: 'Disconnected', className: 'status-disconnected' },
  error: { label: 'Error', className: 'status-error' },
}

export function StatusIndicator({ status, errorMessage }: Props) {
  const config = STATUS_CONFIG[status]

  return (
    <div className="status-container" aria-live="polite" aria-label={`Status: ${config.label}`}>
      <div className={`status-orb ${config.className}`} />
      <span className="status-label">{config.label}</span>
      {status === 'error' && errorMessage && (
        <p className="status-error-detail">{errorMessage}</p>
      )}
    </div>
  )
}
