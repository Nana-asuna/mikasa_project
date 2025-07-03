"use client"

import { useState, useEffect } from "react"
import { useAuth } from "@/hooks/use-auth"
import { Layout } from "@/components/Layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Users, Heart, Package, Calendar, UserPlus, Stethoscope, TrendingUp, Clock } from "lucide-react"
import Link from "next/link"
import type { Enfant, PendingUser } from "@/types"

export default function DashboardPage() {
  const { user } = useAuth()
  const [stats, setStats] = useState({
    enfants: 0,
    dons: 0,
    stock: 0,
    planning: 0,
    pendingUsers: 0,
    mesPatients: 0,
    consultationsAujourdhui: 0,
  })
  const [mesPatients, setMesPatients] = useState<Enfant[]>([])
  const [pendingUsers, setPendingUsers] = useState<PendingUser[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (user && localStorage.getItem("token")) {  
      fetchDashboardData()
    }
  }, [user])

  const fetchDashboardData = async () => {
    try {
      // Récupérer les statistiques générales
      const statsPromises = [
        fetch("/api/enfants", { headers: { Authorization: `Bearer ${tokens?.accessToken}` } }),
        fetch("/api/dons", { headers: { Authorization: `Bearer ${tokens?.accessToken}` } }),
        fetch("/api/stock", { headers: { Authorization: `Bearer ${tokens?.accessToken}` } }),
        fetch("/api/planning", { headers: { Authorization: `Bearer ${tokens?.accessToken}` } }),
      ]

      // Si admin, récupérer les demandes en attente
      if (user?.role === "admin") {
        statsPromises.push(
          fetch("/api/admin/pending-users", { headers: { Authorization: `Bearer ${tokens?.accessToken}` } }),
        )
      }

      // Si médecin, récupérer ses patients
      if (user?.role === "medecin") {
        statsPromises.push(
          fetch(`/api/enfants/medecin/${user.id}`, { headers: { Authorization: `Bearer ${tokens?.accessToken}` } }),
        )
      }

      const responses = await Promise.all(statsPromises)
      const results = await Promise.all(responses.map((r) => r.json()))

      const newStats = {
        enfants: results[0]?.success ? results[0].data.length : 0,
        dons: results[1]?.success ? results[1].data.length : 0,
        stock: results[2]?.success ? results[2].data.length : 0,
        planning: results[3]?.success ? results[3].data.length : 0,
        pendingUsers: user?.role === "admin" && results[4]?.success ? results[4].data.length : 0,
        mesPatients: user?.role === "medecin" && results[4]?.success ? results[4].data.length : 0,
        consultationsAujourdhui: 0, // À implémenter
      }

      setStats(newStats)

      if (user?.role === "admin" && results[4]?.success) {
        setPendingUsers(results[4].data.slice(0, 3)) // Afficher les 3 dernières demandes
      }

      if (user?.role === "medecin" && results[4]?.success) {
        setMesPatients(results[4].data.slice(0, 5)) // Afficher les 5 derniers patients
      }
    } catch (error) {
      console.error("Erreur lors du chargement du dashboard:", error)
    } finally {
      setLoading(false)
    }
  }

  const getWelcomeMessage = () => {
    const hour = new Date().getHours()
    let greeting = "Bonjour"
    if (hour >= 18) greeting = "Bonsoir"
    else if (hour >= 12) greeting = "Bon après-midi"

    return `${greeting}, ${user?.first_name || user?.username} !`
  }

  const getRoleSpecificCards = () => {
    switch (user?.role) {
      case "admin":
        return (
          <>
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Demandes d'inscription</CardTitle>
                <UserPlus className="h-4 w-4 text-orange-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">{stats.pendingUsers}</div>
                <p className="text-xs text-muted-foreground">En attente d'approbation</p>
              </CardContent>
            </Card>
          </>
        )

      case "medecin":
        return (
          <>
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Mes patients</CardTitle>
                <Stethoscope className="h-4 w-4 text-red-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">{stats.mesPatients}</div>
                <p className="text-xs text-muted-foreground">Enfants sous ma responsabilité</p>
              </CardContent>
            </Card>
            <Card className="hover:shadow-lg transition-shadow">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Consultations aujourd'hui</CardTitle>
                <Clock className="h-4 w-4 text-purple-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-purple-600">{stats.consultationsAujourdhui}</div>
                <p className="text-xs text-muted-foreground">Rendez-vous programmés</p>
              </CardContent>
            </Card>
          </>
        )

      default:
        return null
    }
  }

  if (loading) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Chargement du tableau de bord...</p>
          </div>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* En-tête de bienvenue */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">{getWelcomeMessage()}</h1>
          <p className="text-gray-600 mt-2">Voici un aperçu de votre tableau de bord - Organisation Mikasa</p>
        </div>

        {/* Cartes de statistiques */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Enfants</CardTitle>
              <Users className="h-4 w-4 text-blue-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-600">{stats.enfants}</div>
              <p className="text-xs text-muted-foreground">Total des enfants</p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Dons</CardTitle>
              <Heart className="h-4 w-4 text-red-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{stats.dons}</div>
              <p className="text-xs text-muted-foreground">Dons reçus</p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Stock</CardTitle>
              <Package className="h-4 w-4 text-green-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{stats.stock}</div>
              <p className="text-xs text-muted-foreground">Articles en stock</p>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Planning</CardTitle>
              <Calendar className="h-4 w-4 text-purple-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-600">{stats.planning}</div>
              <p className="text-xs text-muted-foreground">Événements planifiés</p>
            </CardContent>
          </Card>

          {/* Cartes spécifiques au rôle */}
          {getRoleSpecificCards()}
        </div>

        {/* Sections spécifiques au rôle */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Section Admin - Demandes en attente */}
          {user?.role === "admin" && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <UserPlus className="w-5 h-5 mr-2 text-orange-600" />
                  Demandes d'inscription récentes
                </CardTitle>
                <CardDescription>Les dernières demandes en attente d'approbation</CardDescription>
              </CardHeader>
              <CardContent>
                {pendingUsers.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">Aucune demande en attente</p>
                ) : (
                  <div className="space-y-3">
                    {pendingUsers.map((pendingUser) => (
                      <div key={pendingUser.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <p className="font-medium">
                            {pendingUser.first_name} {pendingUser.last_name}
                          </p>
                          <p className="text-sm text-gray-600">
                            {pendingUser.role} - {pendingUser.email}
                          </p>
                        </div>
                        <Badge variant="outline" className="text-orange-600 border-orange-300">
                          En attente
                        </Badge>
                      </div>
                    ))}
                    <Link href="/admin/approvals">
                      <Button className="w-full mt-4">Voir toutes les demandes</Button>
                    </Link>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Section Médecin - Mes patients */}
          {user?.role === "medecin" && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Stethoscope className="w-5 h-5 mr-2 text-red-600" />
                  Mes patients récents
                </CardTitle>
                <CardDescription>Les enfants sous votre responsabilité médicale</CardDescription>
              </CardHeader>
              <CardContent>
                {mesPatients.length === 0 ? (
                  <div className="text-center py-4">
                    <p className="text-gray-500 mb-4">Aucun patient assigné</p>
                    <Link href="/enfants/nouveau">
                      <Button>
                        <UserPlus className="w-4 h-4 mr-2" />
                        Créer un dossier enfant
                      </Button>
                    </Link>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {mesPatients.map((enfant) => (
                      <div key={enfant.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <p className="font-medium">
                            {enfant.prenom} {enfant.nom}
                          </p>
                          <p className="text-sm text-gray-600">
                            {enfant.age} ans - {enfant.sexe === "M" ? "Garçon" : "Fille"}
                          </p>
                        </div>
                        <Badge className="bg-green-100 text-green-800">{enfant.statut}</Badge>
                      </div>
                    ))}
                    <div className="flex space-x-2 mt-4">
                      <Link href="/enfants/mes-patients" className="flex-1">
                        <Button variant="outline" className="w-full bg-transparent">
                          Voir tous mes patients
                        </Button>
                      </Link>
                      <Link href="/enfants/nouveau" className="flex-1">
                        <Button className="w-full">
                          <UserPlus className="w-4 h-4 mr-2" />
                          Nouveau dossier
                        </Button>
                      </Link>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Actions rapides */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <TrendingUp className="w-5 h-5 mr-2 text-blue-600" />
                Actions rapides
              </CardTitle>
              <CardDescription>Accès rapide aux fonctionnalités principales</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-3">
                <Link href="/enfants">
                  <Button variant="outline" className="w-full bg-transparent">
                    <Users className="w-4 h-4 mr-2" />
                    Enfants
                  </Button>
                </Link>
                <Link href="/dons">
                  <Button variant="outline" className="w-full bg-transparent">
                    <Heart className="w-4 h-4 mr-2" />
                    Dons
                  </Button>
                </Link>
                <Link href="/stock">
                  <Button variant="outline" className="w-full bg-transparent">
                    <Package className="w-4 h-4 mr-2" />
                    Stock
                  </Button>
                </Link>
                <Link href="/planning">
                  <Button variant="outline" className="w-full bg-transparent">
                    <Calendar className="w-4 h-4 mr-2" />
                    Planning
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  )
}
