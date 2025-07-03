"use client"

import type React from "react"

import { useAuth } from "@/hooks/use-auth"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { useRouter } from "next/navigation"

interface LayoutProps {
  children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
  const { user, logout } = useAuth()
  const router = useRouter()

  const handleLogout = async () => {
    await logout()
    router.push("/login")
  }

  if (!user) {
    return <>{children}</>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link href="/dashboard" className="text-xl font-bold text-blue-600">
                Orphelinat Mikasa
              </Link>
            </div>

            <nav className="hidden md:flex space-x-8">
              <Link href="/dashboard" className="text-gray-700 hover:text-blue-600">
                Tableau de bord
              </Link>
              {user.role === "admin" && (
                <Link href="/admin" className="text-gray-700 hover:text-blue-600">
                  Administration
                </Link>
              )}
              {(user.role === "medecin" || user.role === "soignant" || user.role === "assistant_social") && (
                <Link href="/enfants" className="text-gray-700 hover:text-blue-600">
                  Enfants
                </Link>
              )}
              {user.role === "logisticien" && (
                <Link href="/stock" className="text-gray-700 hover:text-blue-600">
                  Inventaire
                </Link>
              )}
              <Link href="/planning" className="text-gray-700 hover:text-blue-600">
                Planning
              </Link>
            </nav>

            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Dr {user.firstName} {user.lastName}
              </span>
              <Button onClick={handleLogout} variant="outline" size="sm">
                Déconnexion
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">{children}</main>
    </div>
  )
}
