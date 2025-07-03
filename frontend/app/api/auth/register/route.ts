import { type NextRequest, NextResponse } from "next/server"
import { hashPassword } from "@/lib/auth"
import { createPendingUser, findUserByEmail, db } from "@/lib/db"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const {
      username,
      email,
      first_name,
      last_name,
      password,
      role = "visiteur",
      phone_number,
      motivation,
      experience,
      specialization,
    } = body

    // Vérifier si l'utilisateur existe déjà
    const existingUser = findUserByEmail(email)
    if (existingUser) {
      return NextResponse.json({ success: false, error: "Un utilisateur avec cet email existe déjà" }, { status: 400 })
    }

    // Vérifier si une demande est déjà en attente
    const existingPendingUser = db.pendingUsers.find((user) => user.email === email)
    if (existingPendingUser) {
      return NextResponse.json(
        { success: false, error: "Une demande avec cet email est déjà en attente d'approbation" },
        { status: 400 },
      )
    }

    // Hasher le mot de passe
    const hashedPassword = await hashPassword(password)

    // Stocker le mot de passe hashé
    db.passwords[email] = hashedPassword

    // Créer l'utilisateur en attente d'approbation
    const pendingUser = createPendingUser({
      username,
      email,
      first_name,
      last_name,
      role,
      phone_number,
      motivation,
      experience,
      specialization,
    })

    return NextResponse.json({
      success: true,
      message: "Demande d'inscription soumise avec succès. En attente d'approbation.",
      data: { pendingUser },
    })
  } catch (error) {
    console.error("Erreur lors de l'inscription:", error)
    return NextResponse.json({ success: false, error: "Erreur interne du serveur" }, { status: 500 })
  }
}
