import { type NextRequest, NextResponse } from "next/server"
import { db, generateId, initializeDatabase } from "@/lib/db"
import { hasPermission, hashPassword } from "@/lib/auth"

export async function GET(request: NextRequest) {
  try {
    initializeDatabase()

    const userRole = request.headers.get("x-user-role")

    if (!hasPermission(userRole || "", ["admin"])) {
      return NextResponse.json({ success: false, error: "Accès non autorisé" }, { status: 403 })
    }

    // Retourner les utilisateurs sans les mots de passe
    const users = db.users.map((user) => {
      const { password, ...userWithoutPassword } = user as any
      return userWithoutPassword
    })

    return NextResponse.json({
      success: true,
      data: users,
    })
  } catch (error) {
    return NextResponse.json({ success: false, error: "Erreur serveur" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    initializeDatabase()

    const userRole = request.headers.get("x-user-role")

    if (!hasPermission(userRole || "", ["admin"])) {
      return NextResponse.json({ success: false, error: "Accès non autorisé" }, { status: 403 })
    }

    const userData = await request.json()

    // Vérifier si l'email existe déjà
    if (db.users.find((u) => u.email === userData.email)) {
      return NextResponse.json({ success: false, error: "Cet email est déjà utilisé" }, { status: 409 })
    }

    const hashedPassword = await hashPassword(userData.password)

    const newUser = {
      id: generateId(),
      ...userData,
      password: hashedPassword,
      createdAt: new Date(),
      updatedAt: new Date(),
    }

    db.users.push(newUser)

    // Retourner l'utilisateur sans le mot de passe
    const { password, ...userWithoutPassword } = newUser

    return NextResponse.json({
      success: true,
      data: userWithoutPassword,
    })
  } catch (error) {
    return NextResponse.json({ success: false, error: "Erreur serveur" }, { status: 500 })
  }
}

export default function handler() {
  return new Response(JSON.stringify({ ok: true, message: "Use GET or POST for /api/users" }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  })
}
