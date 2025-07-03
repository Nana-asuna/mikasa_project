import jwt from "jsonwebtoken"
import bcrypt from "bcryptjs"

const JWT_SECRET = process.env.JWT_SECRET || "your-secret-key"
const JWT_REFRESH_SECRET = process.env.JWT_REFRESH_SECRET || "your-refresh-secret-key"

export interface TokenPayload {
  userId: string
  email: string
  role: string
}

export function hasPermission(userRole: string, allowedRoles: string[]): boolean {
  return allowedRoles.includes(userRole)
}

export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 12)
}

export async function verifyPassword(password: string, hashedPassword: string): Promise<boolean> {
  return bcrypt.compare(password, hashedPassword)
}

export async function generateTokens(user: { id: string; email: string; role: string }) {
  const payload: TokenPayload = {
    userId: user.id,
    email: user.email,
    role: user.role,
  }

  const accessToken = jwt.sign(payload, JWT_SECRET, { expiresIn: "1h" })
  const refreshToken = jwt.sign(payload, JWT_REFRESH_SECRET, { expiresIn: "7d" })

  return {
    accessToken,
    refreshToken,
  }
}

export async function verifyAccessToken(token: string): Promise<TokenPayload | null> {
  try {
    return jwt.verify(token, JWT_SECRET) as TokenPayload
  } catch (error) {
    return null
  }
}

export async function verifyRefreshToken(token: string): Promise<TokenPayload | null> {
  try {
    return jwt.verify(token, JWT_REFRESH_SECRET) as TokenPayload
  } catch (error) {
    return null
  }
}
