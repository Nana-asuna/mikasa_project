"use client"

import type React from "react"

import { useEffect, useState } from "react"
import { useAuth } from "@/hooks/use-auth"
import { Layout } from "@/components/Layout"
import { useRouter } from "next/navigation"
import type { User } from "@/types"

export default function AdminPage() {
  const { user, loading } = useAuth()
  const router = useRouter()
  const [users, setUsers] = useState<User[]>([])
  const [dataLoading, setDataLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    role: "visiteur",
  })

  useEffect(() => {
    if (!loading && (!user || user.role !== "admin")) {
      router.push("/dashboard")
    }
  }, [user, loading, router])

  useEffect(() => {
    if (user && user.role === "admin") {
      fetchUsers()
    }
  }, [user])

  const fetchUsers = async () => {
    try {
      const response = await fetch("/api/users", {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
      })
      const result = await response.json()
      if (result.success) {
        setUsers(result.data)
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
      const response = await fetch("/api/users", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify(formData),
      })

      const result = await response.json()
      if (result.success) {
        setUsers([...users, result.data])
        setShowForm(false)
        setFormData({
          username: "",
          email: "",
          password: "",
          role: "visiteur",
        })
      }
    } catch (error) {
      console.error("Erreur:", error)
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  if (loading || !user || user.role !== "admin") {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <div className="text-lg">Chargement...</div>
        </div>
      </Layout>
    )
  }

  const getRoleName = (role: string) => {
    const roles = {
      admin: "Administrateur",
      soignant: "Soignant",
      assistant_social: "Assistant Social",
      logisticien: "Logisticien",
      donateur: "Donateur",
      parrain: "Parrain",
      visiteur: "Visiteur",
    }
    return roles[role as keyof typeof roles] || role
  }

  const getRoleColor = (role: string) => {
    const colors = {
      admin: "bg-red-100 text-red-800",
      soignant: "bg-green-100 text-green-800",
      assistant_social: "bg-blue-100 text-blue-800",
      logisticien: "bg-yellow-100 text-yellow-800",
      donateur: "bg-purple-100 text-purple-800",
      parrain: "bg-pink-100 text-pink-800",
      visiteur: "bg-gray-100 text-gray-800",
    }
    return colors[role as keyof typeof colors] || "bg-gray-100 text-gray-800"
  }

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Administration</h1>
          <button
            onClick={() => setShowForm(!showForm)}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            {showForm ? "Annuler" : "Ajouter un Utilisateur"}
          </button>
        </div>

        {/* Statistiques */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Total Utilisateurs</h3>
            <p className="text-3xl font-bold text-blue-600">{users.length}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Administrateurs</h3>
            <p className="text-3xl font-bold text-red-600">{users.filter((u) => u.role === "admin").length}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Personnel</h3>
            <p className="text-3xl font-bold text-green-600">
              {users.filter((u) => ["soignant", "assistant_social", "logisticien"].includes(u.role)).length}
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Donateurs</h3>
            <p className="text-3xl font-bold text-purple-600">
              {users.filter((u) => ["donateur", "parrain"].includes(u.role)).length}
            </p>
          </div>
        </div>

        {/* Formulaire d'ajout */}
        {showForm && (
          <div className="bg-white p-6 rounded-lg shadow-md mb-8">
            <h2 className="text-xl font-semibold mb-4">Ajouter un Utilisateur</h2>
            <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Nom d'utilisateur</label>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Mot de passe</label>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Rôle</label>
                <select
                  name="role"
                  value={formData.role}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="visiteur">Visiteur</option>
                  <option value="donateur">Donateur</option>
                  <option value="parrain">Parrain</option>
                  <option value="soignant">Soignant</option>
                  <option value="assistant_social">Assistant Social</option>
                  <option value="logisticien">Logisticien</option>
                  <option value="admin">Administrateur</option>
                </select>
              </div>

              <div className="md:col-span-2">
                <button type="submit" className="bg-green-500 text-white px-6 py-2 rounded hover:bg-green-600">
                  Créer l'Utilisateur
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Liste des utilisateurs */}
        {dataLoading ? (
          <div className="text-center py-8">Chargement des utilisateurs...</div>
        ) : (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Utilisateur
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Rôle
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date de création
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((u) => (
                    <tr key={u.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{u.username}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{u.email}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRoleColor(u.role)}`}
                        >
                          {getRoleName(u.role)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(u.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button className="text-indigo-600 hover:text-indigo-900 mr-4">Modifier</button>
                        <button className="text-red-600 hover:text-red-900">Supprimer</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {users.length === 0 && !dataLoading && (
          <div className="text-center py-8 text-gray-500">Aucun utilisateur trouvé</div>
        )}
      </div>
    </Layout>
  )
}
