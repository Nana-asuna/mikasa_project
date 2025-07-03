"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { useAuth } from "@/hooks/use-auth"
import { Layout } from "@/components/Layout"
import { useRouter } from "next/navigation"
import type { Don } from "@/types"

export default function DonsPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [dons, setDons] = useState<Don[]>([])
  const [donateurs, setDonateurs] = useState<any[]>([])
  const [dataLoading, setDataLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    type: "ponctuel",
    montant: 0,
    date: new Date().toISOString().split("T")[0],
    donateur_nom: "",
    donateur_email: "",
    message: "",
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
      const [donsRes, donateursRes] = await Promise.all([
        fetch("/api/dons", {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }),
        fetch("/api/donateurs", {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
        }),
      ])

      const donsData = await donsRes.json()
      const donateursData = await donateursRes.json()

      if (donsData.success) setDons(donsData.data)
      if (donateursData.success) setDonateurs(donateursData.data)
    } catch (error) {
      console.error("Erreur:", error)
    } finally {
      setDataLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await fetch("/api/dons", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify(formData),
      })

      const result = await response.json()
      if (result.success) {
        setDons([...dons, result.data])
        setShowForm(false)
        setFormData({
          type: "ponctuel",
          montant: 0,
          date: new Date().toISOString().split("T")[0],
          donateur_nom: "",
          donateur_email: "",
          message: "",
        })
      }
    } catch (error) {
      console.error("Erreur:", error)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const value = e.target.type === "number" ? Number.parseFloat(e.target.value) : e.target.value
    setFormData({
      ...formData,
      [e.target.name]: value,
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

  const getDonateur = (donateurEmail: string) => {
    return donateurs.find((d) => d.email === donateurEmail)
  }

  const totalDons = dons.reduce((sum, don) => sum + don.montant, 0)

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Gestion des Dons</h1>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            {showForm ? "Annuler" : "Enregistrer un Don"}
          </button>
        </div>

        {/* Statistiques */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Total des Dons</h3>
            <p className="text-3xl font-bold text-green-600">{totalDons.toFixed(2)} €</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Nombre de Dons</h3>
            <p className="text-3xl font-bold text-blue-600">{dons.length}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Donateurs Actifs</h3>
            <p className="text-3xl font-bold text-purple-600">{donateurs.length}</p>
          </div>
        </div>

        {/* Formulaire d'ajout */}
        {showForm && (
          <div className="bg-white p-6 rounded-lg shadow-md mb-8">
            <h2 className="text-xl font-semibold mb-4">Enregistrer un Don</h2>
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Type de don</label>
                <select
                  name="type"
                  value={formData.type}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="ponctuel">Ponctuel</option>
                  <option value="mensuel">Mensuel</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Montant (€)</label>
                <input
                  type="number"
                  name="montant"
                  value={formData.montant}
                  onChange={handleChange}
                  step="0.01"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                  min="0"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Date</label>
                <input
                  type="date"
                  name="date"
                  value={formData.date}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Nom du donateur</label>
                <input
                  type="text"
                  name="donateur_nom"
                  value={formData.donateur_nom}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email du donateur</label>
                <input
                  type="email"
                  name="donateur_email"
                  value={formData.donateur_email}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">Message</label>
                <textarea
                  name="message"
                  value={formData.message}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Message optionnel..."
                />
              </div>

              <div className="md:col-span-2">
                <button type="submit" className="bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600">
                  Enregistrer le Don
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Liste des dons */}
        {dataLoading ? (
          <div className="text-center py-8">Chargement des dons...</div>
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
                      Montant
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Donateur
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Message
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {dons.map((don) => {
                    const donateur = getDonateur(don.donateur_email)
                    return (
                      <tr key={don.id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {new Date(don.date_don).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <span className="capitalize">{don.type}</span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {don.montant.toFixed(2)} €
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {don.donateur_nom}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">{don.message || "-"}</td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {dons.length === 0 && !dataLoading && (
          <div className="text-center py-8 text-gray-500">Aucun don enregistré</div>
        )}
      </div>
    </Layout>
  )
}
