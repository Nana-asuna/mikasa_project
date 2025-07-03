"use client"

import type React from "react"

import { useEffect } from "react"
import { useAuth } from "@/hooks/use-auth"
import { useRouter } from "next/navigation"

interface ProtectedRouteProps {
  children: React.ReactNode
  allowedRoles?: string[]
  redirectTo?: string
}

export function ProtectedRoute({ children, allowedRoles = [], redirectTo = "/login" }: ProtectedRouteProps) {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading) {
      if (!user) {
        router.push(redirectTo)
        return
      }

      if (allowedRoles.length > 0 && !allowedRoles.includes(user.role) && user.role !== "admin") {
        router.push("/dashboard")
        return
      }
    }
  }, [user, loading, router, allowedRoles, redirectTo])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-lg">Chargement...</div>
      </div>
    )
  }

  if (!user) {
    return null
  }

  if (allowedRoles.length > 0 && !allowedRoles.includes(user.role) && user.role !== "admin") {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Accès non autorisé</h1>
          <p className="text-gray-600">Vous n'avez pas les permissions pour accéder à cette page.</p>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
