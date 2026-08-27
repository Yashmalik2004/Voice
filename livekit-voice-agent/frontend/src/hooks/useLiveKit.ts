/**
 * useLiveKit — manages the full LiveKit connection lifecycle for the
 * voice assistant frontend.
 *
 * States:
 *   idle        — not connected, waiting for user action
 *   connecting  — fetching token + joining room
 *   connected   — in room, pipeline active (sub-states: listening/thinking/speaking)
 *   disconnected — cleanly left the room
 *   error       — connection or permission failure
 */

import { useCallback, useEffect, useRef, useState } from 'react'
import {
  Room,
  RoomEvent,
  RemoteTrack,
  Track,
  ConnectionState,
} from 'livekit-client'

export type ConnectionStatus =
  | 'idle'
  | 'connecting'
  | 'listening'
  | 'thinking'
  | 'speaking'
  | 'disconnected'
  | 'error'

interface UseLiveKitReturn {
  status: ConnectionStatus
  connect: () => Promise<void>
  disconnect: () => Promise<void>
  errorMessage: string | null
}

const ROOM_NAME = 'voice-room'
const PARTICIPANT_IDENTITY = `user-${Math.random().toString(36).slice(2, 8)}`

async function fetchToken(room: string, identity: string): Promise<{ token: string; url: string }> {
  const res = await fetch(`/api/token?room=${encodeURIComponent(room)}&identity=${encodeURIComponent(identity)}`)
  if (!res.ok) {
    let errorDetail = `Token fetch failed: ${res.status}`
    try {
      const errJson = await res.json()
      if (errJson.error) {
        errorDetail = `${errorDetail} - ${errJson.error}`
      }
    } catch {
      // Use status if body is not JSON
    }
    throw new Error(errorDetail)
  }
  return res.json()
}

export function useLiveKit(): UseLiveKitReturn {
  const [status, setStatus] = useState<ConnectionStatus>('idle')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const roomRef = useRef<Room | null>(null)

  // Track agent participant's data-channel messages for state inference.
  // LiveKit agents publish their state via participant attributes or metadata.
  const updateAgentState = useCallback((state: string) => {
    switch (state) {
      case 'listening':
        setStatus('listening')
        break
      case 'thinking':
        setStatus('thinking')
        break
      case 'speaking':
        setStatus('speaking')
        break
      default:
        setStatus('connected' as ConnectionStatus)
    }
  }, [])

  const connect = useCallback(async () => {
    if (status !== 'idle' && status !== 'disconnected' && status !== 'error') return

    setStatus('connecting')
    setErrorMessage(null)

    try {
      const { token, url } = await fetchToken(ROOM_NAME, PARTICIPANT_IDENTITY)

      const room = new Room({
        adaptiveStream: true,
        dynacast: true,
        audioCaptureDefaults: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      })
      roomRef.current = room

      // Wire up room lifecycle events
      room.on(RoomEvent.Disconnected, () => {
        setStatus('disconnected')
      })

      room.on(RoomEvent.ConnectionStateChanged, (state: ConnectionState) => {
        if (state === ConnectionState.Connected) {
          setStatus('listening')
        }
      })

      // Subscribe to remote audio tracks (agent TTS output)
      room.on(RoomEvent.TrackSubscribed, (track: RemoteTrack) => {
        if (track.kind === Track.Kind.Audio) {
          const audioEl = track.attach()
          audioEl.autoplay = true
          document.body.appendChild(audioEl)
        }
      })

      room.on(RoomEvent.TrackUnsubscribed, (track: RemoteTrack) => {
        track.detach()
      })

      // Listen for agent state changes published via participant attributes
      room.on(RoomEvent.ParticipantAttributesChanged, (changed: Record<string, string>) => {
        // LiveKit agents set "agent_state" attribute on their participant
        if ('agent_state' in changed) {
          updateAgentState(changed['agent_state'])
        }
      })

      // Also watch for data messages (some agent versions broadcast state this way)
      room.on(RoomEvent.DataReceived, (data: Uint8Array) => {
        try {
          const msg = JSON.parse(new TextDecoder().decode(data))
          if (msg.type === 'agent_state') {
            updateAgentState(msg.state)
          }
        } catch {
          // Ignore non-JSON data messages
        }
      })

      await room.connect(url, token)

      // Enable local microphone
      await room.localParticipant.setMicrophoneEnabled(true)

    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : String(err)
      setErrorMessage(message)
      setStatus('error')
    }
  }, [status, updateAgentState])

  const disconnect = useCallback(async () => {
    if (roomRef.current) {
      await roomRef.current.disconnect()
      roomRef.current = null
    }
    setStatus('disconnected')
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      roomRef.current?.disconnect()
    }
  }, [])

  return { status, connect, disconnect, errorMessage }
}
