"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { useAuth } from "@/hooks/use-auth"
import { Layout } from "@/components/Layout"
import { useRouter } from "next/navigation"
import type { Stock } from "@/types"

export default function StockPage() {
  const { user, tokens, loading } = useAuth()
  const router = useRouter()
  const [stock, setStock] = useState<Stock[]>([])
  const [dataLoading, setDataLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    nomProduit: "",
    quantite: 0,
    seuilAlerte: 0,
    categorie: "nourriture",
  })

  useEffect(() => {
    if (!loading && !user) {
      router.push("/login")
    }
  }, [user, loading, router])

  useEffect(() => {
    if (user && tokens) {
      fetchStock()
    }
  }, [user, tokens])

  const fetchStock = async () => {
    try {
      const response = await fetch("/api/stock", {
        headers: {
          Authorization: `Bearer ${tokens?.accessToken}`,
        },
      })
      const result = await response.json()
      if (result.success) {
        setStock(result.data)
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
      const response = await fetch("/api/stock", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${tokens?.accessToken}`,
        },
        body: JSON.stringify(formData),
      })

      const result = await response.json()
      if (result.success) {
        setStock([...stock, result.data])
        setShowForm(false)
        setFormData({
          nomProduit: "",
          quantite: 0,
          seuilAlerte: 0,
          categorie: "nourriture",
        })
      }
    } catch (error) {
      console.error("Erreur:", error)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const value = e.target.type === "number" ? Number.parseInt(e.target.value) : e.target.value
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

  const canManageStock = user.role === "admin" || user.role === "logisticien"

  if (!canManageStock && user.role !== "soignant") {
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

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Gestion du Stock</h1>
          {canManageStock && (
            <button
              onClick={() => setShowForm(!showForm)}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
            >
              {showForm ? "Annuler" : "Ajouter un Produit"}
            </button>
          )}
        </div>

        {/* Formulaire d'ajout */}
        {showForm && canManageStock && (
          <div className="bg-white p-6 rounded-lg shadow-md mb-8">
            <h2 className="text-xl font-semibold mb-4">Ajouter un Produit</h2>
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Nom du produit</label>
                <input
                  type="text"
                  name="nomProduit"
                  value={formData.nomProduit}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Quantité</label>
                <input
                  type="number"
                  name="quantite"
                  value={formData.quantite}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                  min="0"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Seuil d'alerte</label>
                <input
                  type="number"
                  name="seuilAlerte"
                  value={formData.seuilAlerte}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                  min="0"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Catégorie</label>
                <select
                  name="categorie"
                  value={formData.categorie}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="nourriture">Nourriture</option>
                  <option value="medicaments">Médicaments</option>
                  <option value="vetements">Vêtements</option>
                  <option value="hygiene">Hygiène</option>
                  <option value="education">Éducation</option>
                  <option value="autre">Autre</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <button type="submit" className="bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600">
                  Ajouter le Produit
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Liste du stock */}
        {dataLoading ? (
          <div className="text-center py-8">Chargement du stock...</div>
        ) : (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Produit
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Catégorie
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Quantité
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Seuil d'alerte
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Statut
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {stock.map((item) => (
                    <tr key={item.id} className={item.quantite <= item.seuilAlerte ? "bg-red-50" : ""}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {item.nomProduit}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <span className="capitalize">{item.categorie}</span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{item.quantite}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{item.seuilAlerte}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {item.quantite <= item.seuilAlerte ? (
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                            ⚠️ Stock faible
                          </span>
                        ) : (
                          <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                            ✅ Stock OK
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {stock.length === 0 && !dataLoading && (
          <div className="text-center py-8 text-gray-500">Aucun produit en stock</div>
        )}
      </div>
    </Layout>
  )
}
