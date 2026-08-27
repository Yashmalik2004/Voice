import type { VercelRequest, VercelResponse } from '@vercel/node'
import { AccessToken } from 'livekit-server-sdk'

export default async function handler(req: VercelRequest, res: VercelResponse) {
  // Set CORS headers for security and browser compatibility
  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')

  if (req.method === 'OPTIONS') {
    return res.status(200).end()
  }

  const room = (req.query.room as string) || 'voice-room'
  const identity = (req.query.identity as string) || `user-${Math.random().toString(36).slice(2, 8)}`

  const apiKey = process.env.LIVEKIT_API_KEY
  const apiSecret = process.env.LIVEKIT_API_SECRET
  const wsUrl = process.env.LIVEKIT_URL

  if (!apiKey || !apiSecret || !wsUrl) {
    return res.status(500).json({
      error: 'LiveKit environment variables (LIVEKIT_API_KEY, LIVEKIT_API_SECRET, LIVEKIT_URL) are missing in Vercel settings.',
    })
  }

  try {
    const at = new AccessToken(apiKey, apiSecret, {
      identity,
      name: identity,
      ttl: '1h',
    })

    at.addGrant({
      room,
      roomJoin: true,
      canPublish: true,
      canSubscribe: true,
    })

    const token = await at.toJwt()

    return res.status(200).json({
      token,
      url: wsUrl,
    })
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : String(error)
    return res.status(500).json({ error: message })
  }
}
