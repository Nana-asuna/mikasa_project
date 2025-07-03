import { type NextRequest, NextResponse } from "next/server"
import { verifyAccessToken } from "@/lib/auth"
import { db, findUserById } from "@/lib/db"

export async function GET(request: NextRequest) {
  try {
    const token = request.headers.get("authorization")?.replace("Bearer ", "")

    if (!token) {
      return NextResponse.json({ error: "Token manquant" }, { status: 401 })
    }

    const payload = await verifyAccessToken(token)
    if (!payload) {
      return NextResponse.json({ error: "Token invalide" }, { status: 401 })
    }

    const user = findUserById(payload.userId)
    if (!user) {
      return NextResponse.json({ error: "Utilisateur non trouvé" }, { status: 404 })
    }

    return NextResponse.json({
      success: true,
      data: db.enfants,
    })
  } catch (error) {
    console.error("Error fetching enfants:", error)
    return NextResponse.json({ success: false, error: "Erreur interne du serveur" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const token = request.headers.get("authorization")?.replace("Bearer ", "")

    if (!token) {
      return NextResponse.json({ error: "Token manquant" }, { status: 401 })
    }

    const payload = await verifyAccessToken(token)
    if (!payload) {
      return NextResponse.json({ error: "Token invalide" }, { status: 401 })
    }

    const user = findUserById(payload.userId)
    if (!user || !["admin", "medecin", "assistant_social"].includes(user.role)) {
      return NextResponse.json({ error: "Accès non autorisé" }, { status: 403 })
    }

    const enfantData = await request.json()

    const newEnfant = {
      id: Math.random().toString(36).substr(2, 9),
      ...enfantData,
      created_by: user.id,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }

    db.enfants.push(newEnfant)

    return NextResponse.json({
      success: true,
      data: newEnfant,
    })
  } catch (error) {
    console.error("Error creating enfant:", error)
    return NextResponse.json({ success: false, error: "Erreur interne du serveur" }, { status: 500 })
  }
}
