"use client"

import { useAuth } from "@/hooks/use-auth"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import Link from "next/link"
import { Heart, Users, Shield, Award } from "lucide-react"

export default function HomePage() {
  const { user } = useAuth()

  if (user) {
    // Rediriger vers le dashboard si connecté
    window.location.href = "/dashboard"
    return null
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-blue-600">Orphelinat Mikasa</h1>
            </div>
            <div className="flex space-x-4">
              <Link href="/login">
                <Button variant="outline">Connexion</Button>
              </Link>
              <Link href="/register">
                <Button>S'inscrire</Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">Ensemble pour l'avenir des enfants</h2>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            L'Orphelinat Mikasa offre un foyer sûr, une éducation de qualité et un accompagnement personnalisé à chaque
            enfant. Notre mission est de donner à chaque enfant les outils nécessaires pour construire un avenir
            brillant et épanouissant.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/register">
              <Button size="lg" className="w-full sm:w-auto">
                Rejoindre notre équipe
              </Button>
            </Link>
            <Link href="/dons">
              <Button size="lg" variant="outline" className="w-full sm:w-auto bg-transparent">
                Faire un don
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Notre Mission */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">Comment Mikasa aide les enfants</h3>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Notre approche holistique garantit que chaque enfant reçoit les soins, l'éducation et l'amour nécessaires
              pour s'épanouir.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <Card className="text-center">
              <CardHeader>
                <Heart className="h-12 w-12 text-red-500 mx-auto mb-4" />
                <CardTitle>Soins médicaux</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Suivi médical complet avec notre équipe de médecins et infirmiers dédiés.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <Users className="h-12 w-12 text-blue-500 mx-auto mb-4" />
                <CardTitle>Éducation</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Programme éducatif adapté à chaque enfant avec soutien scolaire personnalisé.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <Shield className="h-12 w-12 text-green-500 mx-auto mb-4" />
                <CardTitle>Protection</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Environnement sécurisé et bienveillant où chaque enfant peut grandir en confiance.
                </p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardHeader>
                <Award className="h-12 w-12 text-purple-500 mx-auto mb-4" />
                <CardTitle>Développement</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-600">
                  Activités créatives, sportives et culturelles pour développer tous les talents.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Nos Valeurs */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h3 className="text-3xl font-bold text-gray-900 mb-8">Nos valeurs fondamentales</h3>
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <h4 className="text-xl font-semibold text-gray-900 mb-4">Bienveillance</h4>
              <p className="text-gray-600">
                Chaque enfant est accueilli avec amour et respect, dans un environnement chaleureux.
              </p>
            </div>
            <div>
              <h4 className="text-xl font-semibold text-gray-900 mb-4">Excellence</h4>
              <p className="text-gray-600">
                Nous nous engageons à offrir les meilleurs soins et la meilleure éducation possible.
              </p>
            </div>
            <div>
              <h4 className="text-xl font-semibold text-gray-900 mb-4">Espoir</h4>
              <p className="text-gray-600">
                Nous croyons en l'avenir de chaque enfant et l'accompagnons vers l'autonomie.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <h4 className="text-lg font-semibold mb-4">Orphelinat Mikasa</h4>
              <p className="text-gray-300">
                Offrir un avenir meilleur à chaque enfant grâce à l'amour, l'éducation et les soins.
              </p>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Contact</h4>
              <p className="text-gray-300">
                Email: contact@orphelinat-mikasa.sn
                <br />
                Téléphone: +221 33 XXX XX XX
                <br />
                Adresse: Dakar, Sénégal
              </p>
            </div>
            <div>
              <h4 className="text-lg font-semibold mb-4">Liens utiles</h4>
              <div className="space-y-2">
                <Link href="/register" className="block text-gray-300 hover:text-white">
                  Rejoindre l'équipe
                </Link>
                <Link href="/dons" className="block text-gray-300 hover:text-white">
                  Faire un don
                </Link>
                <Link href="/login" className="block text-gray-300 hover:text-white">
                  Espace personnel
                </Link>
              </div>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2024 Orphelinat Mikasa. Tous droits réservés.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
