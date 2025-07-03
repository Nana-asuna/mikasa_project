"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { useAuth } from "@/hooks/use-auth"
import { Layout } from "@/components/Layout"
import { useRouter } from "next/navigation"
import type { Enfant } from "@/types"

export default function EnfantsPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [enfants, setEnfants] = useState<Enfant[]>([])
  const [dataLoading, setDataLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    nom: "",
    prenom: "",
    sexe: "M",
    dateNaissance: "",
    dateArrivee: "",
    statut: "a_parrainer",
    sante: "",
  })

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login")
    }
  }, [user, loading, router])

  useEffect(() => {
    if (user) {
      fetchEnfants()
    }
  }, [user])

  const fetchEnfants = async () => {
    try {
      const response = await fetch("/api/enfants", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`, 
        },
      })
      const result = await response.json()
      if (result.success) {
        setEnfants(result.data)
      }
    } catch (error) {
      console.error("Erreur:", error)
    } finally {
      setDataLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await fetch("/api/enfants", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify(formData),
      })

      const result = await response.json()
      if (result.success) {
        setEnfants([...enfants, result.data])
        setShowForm(false)
        setFormData({
          nom: "",
          prenom: "",
          sexe: "M",
          dateNaissance: "",
          dateArrivee: "",
          statut: "a_parrainer",
          sante: "",
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

  const canManageEnfants = user.role === "admin" || user.role === "assistant_social"

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Gestion des Enfants</h1>
          {canManageEnfants && (
            <button
              onClick={() => setShowForm(!showForm)}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              {showForm ? "Annuler" : "Ajouter un Enfant"}
            </button>
          )}
        </div>

        {/* Formulaire d'ajout */}
        {showForm && canManageEnfants && (
          <div className="bg-white p-6 rounded-lg shadow-md mb-8">
            <h2 className="text-xl font-semibold mb-4">Ajouter un Enfant</h2>
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Nom</label>
                <input
                  type="text"
                  name="nom"
                  value={formData.nom}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Prénom</label>
                <input
                  type="text"
                  name="prenom"
                  value={formData.prenom}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Sexe</label>
                <select
                  name="sexe"
                  value={formData.sexe}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="M">Masculin</option>
                  <option value="F">Féminin</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Date de naissance</label>
                <input
                  type="date"
                  name="dateNaissance"
                  value={formData.dateNaissance}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Date d'arrivée</label>
                <input
                  type="date"
                  name="dateArrivee"
                  value={formData.dateArrivee}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Statut</label>
                <select
                  name="statut"
                  value={formData.statut}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="a_parrainer">À parrainer</option>
                  <option value="parraine">Parrainé</option>
                  <option value="adopte">Adopté</option>
                  <option value="en_attente">En attente</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">Informations de santé</label>
                <textarea
                  name="sante"
                  value={formData.sante}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Informations médicales, vaccinations, etc."
                />
              </div>

              <div className="md:col-span-2">
                <button type="submit" className="bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600">
                  Ajouter l'Enfant
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Liste des enfants */}
        {dataLoading ? (
          <div className="text-center py-8">Chargement des enfants...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {enfants.map((enfant) => (
              <div key={enfant.id} className="bg-white rounded-lg shadow-md overflow-hidden">
                <div className="h-48 bg-gray-200 flex items-center justify-center">
                  {enfant.photo ? (
                    <img
                      src={enfant.photo || "/placeholder.svg"}
                      alt={enfant.prenom}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="text-6xl">👶</div>
                  )}
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-semibold mb-2">
                    {user.role === "visiteur" ? enfant.prenom : `${enfant.prenom} ${enfant.nom}`}
                  </h3>
                  <p className="text-gray-600 mb-2">
                    Âge: {enfant.age} ans
                  </p>
                  <p className="text-gray-600 mb-2">Sexe: {enfant.sexe === "M" ? "Garçon" : "Fille"}</p>
                  <div className="flex justify-between items-center mb-4">
                    <span
                      className={`px-2 py-1 rounded text-sm ${
                        enfant.statut === "present"
                          ? "bg-yellow-100 text-yellow-800"
                          : enfant.statut === "parraine"
                            ? "bg-green-100 text-green-800"
                            : enfant.statut === "adopte"
                              ? "bg-blue-100 text-blue-800"
                              : "bg-gray-100 text-gray-800"
                      }`}
                    >
                      {enfant.statut.replace("_", " ")}
                    </span>
                  </div>
                  {user.role !== "visiteur" && (
                    <div className="text-sm text-gray-600">
                      <p className="mb-2">
                        <strong>Arrivée:</strong> {new Date(enfant.date_arrivee).toLocaleDateString()}
                      </p>
                      <p>
                        <strong>Santé:</strong> {enfant.antecedents_medicaux || "Aucune information"}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {enfants.length === 0 && !dataLoading && (
          <div className="text-center py-8 text-gray-500">Aucun enfant trouvé</div>
        )}
      </div>
    </Layout>
  )
}
