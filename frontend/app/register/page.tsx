"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/hooks/use-auth"
import { Layout } from "@/components/Layout"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Info } from "lucide-react"

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    first_name: "",
    last_name: "",
    password: "",
    confirmPassword: "",
    role: "visiteur",
    phone_number: "",
    motivation: "",
    experience: "",
    specialization: "",
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState(false)


  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError("")

    if (formData.password !== formData.confirmPassword) {
      setError("Les mots de passe ne correspondent pas")
      setLoading(false)
      return
    }

    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })

      const result = await response.json()

      if (result.success) {
        setSuccess(true)
      } else {
        setError(result.error || "Erreur lors de l'inscription")
      }
    } catch (error) {
      setError("Erreur lors de l'inscription")
    }

    setLoading(false)
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const getRoleDescription = (role: string) => {
    const descriptions = {
      visiteur: "Accès limité aux informations publiques",
      donateur: "Peut faire des dons et suivre leur utilisation",
      parrain: "Peut parrainer des enfants et suivre leur évolution",
      soignant: "Personnel soignant avec accès aux dossiers médicaux",
      medecin: "Médecin avec accès complet aux dossiers médicaux et possibilité de créer des dossiers d'enfants",
      assistant_social: "Accès aux dossiers sociaux et familiaux",
      logisticien: "Gestion des stocks et de la logistique",
    }
    return descriptions[role as keyof typeof descriptions] || ""
  }

  if (success) {
    return (
      <Layout>
        <div className="max-w-2xl mx-auto mt-8 p-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-green-600">Inscription réussie !</CardTitle>
              <CardDescription>Votre demande d'inscription a été soumise avec succès.</CardDescription>
            </CardHeader>
            <CardContent>
              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  Votre compte est en attente d'approbation par un administrateur. Vous recevrez un email de
                  confirmation une fois votre compte approuvé. En attendant, vous pouvez vérifier votre adresse email en
                  cliquant sur le lien que nous vous avons envoyé.
                </AlertDescription>
              </Alert>
              <div className="mt-6">
                <Button onClick={() => router.push("/login")} className="w-full">
                  Aller à la page de connexion
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </Layout>
    )
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto mt-8 p-6">
        <Card>
          <CardHeader>
            <CardTitle>Rejoindre l'Organisation Mikasa</CardTitle>
            <CardDescription>
              Remplissez ce formulaire pour demander l'accès à notre plateforme. Votre demande sera examinée par notre
              équipe.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {error && (
              <Alert className="mb-6" variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Informations personnelles */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="first_name" className="block text-sm font-medium text-gray-700 mb-2">
                    Prénom *
                  </label>
                  <input
                    type="text"
                    id="first_name"
                    name="first_name"
                    value={formData.first_name}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="last_name" className="block text-sm font-medium text-gray-700 mb-2">
                    Nom *
                  </label>
                  <input
                    type="text"
                    id="last_name"
                    name="last_name"
                    value={formData.last_name}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                    Nom d'utilisateur *
                  </label>
                  <input
                    type="text"
                    id="username"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Email *
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label htmlFor="phone_number" className="block text-sm font-medium text-gray-700 mb-2">
                  Numéro de téléphone
                </label>
                <input
                  type="tel"
                  id="phone_number"
                  name="phone_number"
                  value={formData.phone_number}
                  onChange={handleChange}
                  placeholder="+33123456789"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              {/* Rôle demandé */}
              <div>
                <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-2">
                  Rôle demandé *
                </label>
                <select
                  id="role"
                  name="role"
                  value={formData.role}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="visiteur">Visiteur</option>
                  <option value="donateur">Donateur</option>
                  <option value="parrain">Parrain/Marraine</option>
                  <option value="soignant">Personnel Soignant</option>
                  <option value="medecin">Médecin</option>
                  <option value="assistant_social">Assistant Social</option>
                  <option value="logisticien">Logisticien</option>
                </select>
                {formData.role && <p className="text-sm text-gray-600 mt-1">{getRoleDescription(formData.role)}</p>}
              </div>

              {/* Spécialisation pour médecins et soignants */}
              {(formData.role === "medecin" || formData.role === "soignant") && (
                <div>
                  <label htmlFor="specialization" className="block text-sm font-medium text-gray-700 mb-2">
                    Spécialisation
                  </label>
                  <input
                    type="text"
                    id="specialization"
                    name="specialization"
                    value={formData.specialization}
                    onChange={handleChange}
                    placeholder="Ex: Pédiatrie, Psychologie, Infirmier..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              )}

              {/* Motivation */}
              <div>
                <label htmlFor="motivation" className="block text-sm font-medium text-gray-700 mb-2">
                  Motivation *
                </label>
                <Textarea
                  id="motivation"
                  name="motivation"
                  value={formData.motivation}
                  onChange={handleChange}
                  placeholder="Expliquez pourquoi vous souhaitez rejoindre l'Organisation Mikasa..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={4}
                  required
                />
              </div>

              {/* Expérience */}
              <div>
                <label htmlFor="experience" className="block text-sm font-medium text-gray-700 mb-2">
                  Expérience pertinente
                </label>
                <Textarea
                  id="experience"
                  name="experience"
                  value={formData.experience}
                  onChange={handleChange}
                  placeholder="Décrivez votre expérience dans le domaine social, médical ou avec les enfants..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  rows={4}
                />
              </div>

              {/* Mots de passe */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                    Mot de passe *
                  </label>
                  <input
                    type="password"
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                    Confirmer le mot de passe *
                  </label>
                  <input
                    type="password"
                    id="confirmPassword"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    required
                  />
                </div>
              </div>

              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  Votre demande sera examinée par notre équipe d'administration. Vous recevrez une notification par
                  email une fois votre compte approuvé.
                </AlertDescription>
              </Alert>

              <Button type="submit" disabled={loading} className="w-full">
                {loading ? "Inscription en cours..." : "Soumettre ma demande"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </Layout>
  )
}
