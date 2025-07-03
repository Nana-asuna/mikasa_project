"use client"

import { createContext, useContext, useState, useEffect, type ReactNode } from "react"

interface User {
  id: string
  email: string
  firstName: string
  lastName: string
  role: string
  status: string
  isVerified: boolean
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>
  logout: () => Promise<void>
  checkAuth: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem("token")
      if (!token) {
        setLoading(false)
        return
      }

      // Timeout pour éviter les requêtes trop lentes
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 5000) // 5 secondes max

      const response = await fetch("/api/auth/me", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else {
        localStorage.removeItem("token")
        setUser(null)
      }
    } catch (error) {
      console.error("Auth check failed:", error)
      localStorage.removeItem("token")
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    try {
      // Timeout pour éviter les requêtes trop lentes
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 10000) // 10 secondes max

      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      // Vérifier si la réponse est du JSON valide
      const contentType = response.headers.get("content-type")
      if (!contentType || !contentType.includes("application/json")) {
        return {
          success: false,
          error: "Erreur serveur. Veuillez réessayer plus tard.",
        }
      }

      const data = await response.json()

      if (response.ok) {
        localStorage.setItem("token", data.token)
        setUser(data.user)
        return { success: true }
      } else {
        return {
          success: false,
          error: data.error || "Erreur de connexion",
        }
      }
    } catch (error) {
      console.error("Login error:", error)
      return {
        success: false,
        error: "Erreur de connexion. Veuillez vérifier votre connexion internet.",
      }
    }
  }

  const logout = async () => {
    try {
      await fetch("/api/auth/logout", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      })
    } catch (error) {
      console.error("Logout error:", error)
    } finally {
      localStorage.removeItem("token")
      setUser(null)
    }
  }

  useEffect(() => {
    checkAuth()
  }, [])

  const value = {
    user,
    loading,
    login,
    logout,
    checkAuth,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

// Export par défaut pour la compatibilité
export default AuthProvider
