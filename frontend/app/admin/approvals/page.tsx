"use client"

import { useState, useEffect } from "react"
import { Layout } from "@/components/Layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { useAuth } from "@/hooks/use-auth"
import { CheckCircle, XCircle, Clock, User, Mail, Phone, Briefcase } from "lucide-react"
import type { PendingUser } from "@/types"

export default function ApprovalsPage() {
  const [pendingUsers, setPendingUsers] = useState<PendingUser[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [processingId, setProcessingId] = useState<string | null>(null)
  const { user } = useAuth()

  useEffect(() => {
    if (user?.role === "admin") {
      fetchPendingUsers()
    }
  }, [user])

  const fetchPendingUsers = async () => {
    try {
      const response = await fetch("/api/admin/pending-users", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      })

      const result = await response.json()
      if (result.success) {
        setPendingUsers(result.data)
      } else {
        setError(result.error || "Erreur lors du chargement")
      }
    } catch (error) {
      setError("Erreur de connexion")
    } finally {
      setLoading(false)
    }
  }

  const handleUserAction = async (userId: string, action: "approve" | "reject") => {
    setProcessingId(userId)
    try {
      const response = await fetch(`/api/admin/approve-user/${userId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({ action }),
      })

      const result = await response.json()
      if (result.success) {
        // Retirer l'utilisateur de la liste
        setPendingUsers((prev) => prev.filter((u) => u.id !== userId))
      } else {
        setError(result.error || "Erreur lors du traitement")
      }
    } catch (error) {
      setError("Erreur de connexion")
    } finally {
      setProcessingId(null)
    }
  }

  const getRoleBadgeColor = (role: string) => {
    const colors = {
      medecin: "bg-red-100 text-red-800",
      soignant: "bg-blue-100 text-blue-800",
      assistant_social: "bg-green-100 text-green-800",
      logisticien: "bg-yellow-100 text-yellow-800",
      parrain: "bg-purple-100 text-purple-800",
      donateur: "bg-orange-100 text-orange-800",
      visiteur: "bg-gray-100 text-gray-800",
    }
    return colors[role as keyof typeof colors] || "bg-gray-100 text-gray-800"
  }

  if (user?.role !== "admin") {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Alert variant="destructive">
            <AlertDescription>Accès non autorisé. Cette page est réservée aux administrateurs.</AlertDescription>
          </Alert>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Gestion des Demandes d'Inscription</h1>
          <p className="text-gray-600 mt-2">Examinez et approuvez les demandes d'inscription en attente</p>
        </div>

        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {loading ? (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Chargement des demandes...</p>
          </div>
        ) : pendingUsers.length === 0 ? (
          <Card>
            <CardContent className="text-center py-8">
              <Clock className="mx-auto h-12 w-12 text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">Aucune demande en attente</h3>
              <p className="text-gray-600">Toutes les demandes d'inscription ont été traitées.</p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-6">
            {pendingUsers.map((pendingUser) => (
              <Card key={pendingUser.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                        <User className="w-6 h-6 text-blue-600" />
                      </div>
                      <div>
                        <CardTitle className="text-xl">
                          {pendingUser.first_name} {pendingUser.last_name}
                        </CardTitle>
                        <CardDescription>@{pendingUser.username}</CardDescription>
                      </div>
                    </div>
                    <Badge className={getRoleBadgeColor(pendingUser.role)}>{pendingUser.role}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Informations de contact */}
                    <div className="space-y-3">
                      <h4 className="font-semibold text-gray-900">Informations de contact</h4>
                      <div className="flex items-center space-x-2 text-sm text-gray-600">
                        <Mail className="w-4 h-4" />
                        <span>{pendingUser.email}</span>
                      </div>
                      {pendingUser.phone_number && (
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <Phone className="w-4 h-4" />
                          <span>{pendingUser.phone_number}</span>
                        </div>
                      )}
                      {pendingUser.specialization && (
                        <div className="flex items-center space-x-2 text-sm text-gray-600">
                          <Briefcase className="w-4 h-4" />
                          <span>Spécialisation: {pendingUser.specialization}</span>
                        </div>
                      )}
                      <div className="text-sm text-gray-500">
                        Demande soumise le {new Date(pendingUser.created_at).toLocaleDateString("fr-FR")}
                      </div>
                    </div>

                    {/* Motivation et expérience */}
                    <div className="space-y-3">
                      <h4 className="font-semibold text-gray-900">Motivation</h4>
                      <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">{pendingUser.motivation}</p>
                      {pendingUser.experience && (
                        <>
                          <h4 className="font-semibold text-gray-900">Expérience</h4>
                          <p className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">{pendingUser.experience}</p>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex justify-end space-x-3 mt-6 pt-6 border-t">
                    <Button
                      variant="outline"
                      onClick={() => handleUserAction(pendingUser.id, "reject")}
                      disabled={processingId === pendingUser.id}
                      className="text-red-600 border-red-300 hover:bg-red-50"
                    >
                      <XCircle className="w-4 h-4 mr-2" />
                      Rejeter
                    </Button>
                    <Button
                      onClick={() => handleUserAction(pendingUser.id, "approve")}
                      disabled={processingId === pendingUser.id}
                      className="bg-green-600 hover:bg-green-700"
                    >
                      <CheckCircle className="w-4 h-4 mr-2" />
                      {processingId === pendingUser.id ? "Traitement..." : "Approuver"}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </Layout>
  )
}
