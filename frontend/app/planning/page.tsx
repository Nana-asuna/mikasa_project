"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { useAuth } from "@/hooks/use-auth"
import { Layout } from "@/components/Layout"
import { useRouter } from "next/navigation"
import type { Planning, Enfant } from "@/types"

export default function PlanningPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [planning, setPlanning] = useState<Planning[]>([])
  const [enfants, setEnfants] = useState<Enfant[]>([])
  const [dataLoading, setDataLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    type: "visite_medicale",
    enfantId: "",
    date: "",
    commentaire: "",
  })

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login")
    }
  }, [user, loading, router])

  useEffect(() => {
    if (user && localStorage.getItem("token")) {
      fetchData()
    }
  }, [user])

  const fetchData = async () => {
    try {
      const [planningRes, enfantsRes] = await Promise.all([
        fetch("/api/planning", {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }),
        fetch("/api/enfants", {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }),
      ])

      const planningData = await planningRes.json()
      const enfantsData = await enfantsRes.json()

      if (planningData.success) setPlanning(planningData.data)
      if (enfantsData.success) setEnfants(enfantsData.data)
    } catch (error) {
      console.error("Erreur:", error)
    } finally {
      setDataLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await fetch("/api/planning", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify(formData),
      })

      const result = await response.json()
      if (result.success) {
        setPlanning([...planning, result.data])
        setShowForm(false)
        setFormData({
          type: "visite_medicale",
          enfantId: "",
          date: "",
          commentaire: "",
        })
      }
    } catch (error) {
      console.error("Erreur:", error)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  if (loading || !user) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <div className="text-lg">Chargement...</div>
        </div>
      </Layout>
    )
  }

  const canManagePlanning = user.role === "admin" || user.role === "soignant" || user.role === "assistant_social"

  if (!canManagePlanning) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Accès non autorisé</h1>
            <p className="text-gray-600">Vous n'avez pas les permissions pour accéder à cette page.</p>
          </div>
        </div>
      </Layout>
    )
  }

  const getEnfant = (enfantId: string) => {
    return enfants.find((e) => e.id === enfantId)
  }

  const getTypeColor = (type: string) => {
    const colors = {
      visite_medicale: "bg-red-100 text-red-800",
      activite: "bg-blue-100 text-blue-800",
      education: "bg-green-100 text-green-800",
      recreation: "bg-yellow-100 text-yellow-800",
      autre: "bg-gray-100 text-gray-800",
    }
    return colors[type as keyof typeof colors] || "bg-gray-100 text-gray-800"
  }

  const getTypeName = (type: string) => {
    const types = {
      visite_medicale: "Visite Médicale",
      activite: "Activité",
      education: "Éducation",
      recreation: "Récréation",
      autre: "Autre",
    }
    return types[type as keyof typeof types] || type
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Planning</h1>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            {showForm ? "Annuler" : "Ajouter un Événement"}
          </button>
        </div>

        {/* Formulaire d'ajout */}
        {showForm && (
          <div className="bg-white p-6 rounded-lg shadow-md mb-8">
            <h2 className="text-xl font-semibold mb-4">Ajouter un Événement</h2>
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Type d'événement</label>
                <select
                  name="type"
                  value={formData.type}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="visite_medicale">Visite Médicale</option>
                  <option value="activite">Activité</option>
                  <option value="education">Éducation</option>
                  <option value="recreation">Récréation</option>
                  <option value="autre">Autre</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Enfant</label>
                <select
                  name="enfantId"
                  value={formData.enfantId}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                >
                  <option value="">Sélectionner un enfant</option>
                  {enfants.map((enfant) => (
                    <option key={enfant.id} value={enfant.id}>
                      {enfant.prenom} {enfant.nom}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Date et heure</label>
                <input
                  type="datetime-local"
                  name="date"
                  value={formData.date}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">Commentaire</label>
                <textarea
                  name="commentaire"
                  value={formData.commentaire}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Détails de l'événement..."
                />
              </div>

              <div className="md:col-span-2">
                <button type="submit" className="bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600">
                  Ajouter l'Événement
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Liste du planning */}
        {dataLoading ? (
          <div className="text-center py-8">Chargement du planning...</div>
        ) : (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Enfant
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Commentaire
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {planning.map((event) => {
                    return (
                      <tr key={event.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {new Date(event.date_debut).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span
                            className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getTypeColor(event.type)}`}
                          >
                            {getTypeName(event.type)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {event.responsable}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                          {event.description || "-"}
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {planning.length === 0 && !dataLoading && (
          <div className="text-center py-8 text-gray-500">Aucun événement planifié</div>
        )}
      </div>
    </Layout>
  )
}
