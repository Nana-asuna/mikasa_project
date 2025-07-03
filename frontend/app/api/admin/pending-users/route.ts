import { type NextRequest, NextResponse } from "next/server"
import { verifyAccessToken } from "@/lib/auth"
import { getPendingUsers, findUserById } from "@/lib/db"

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

    const user = findUserById(payload.userId as string)
    if (!user || user.role !== "admin") {
      return NextResponse.json({ error: "Accès non autorisé" }, { status: 403 })
    }

    const pendingUsers = getPendingUsers()

    return NextResponse.json({
      success: true,
      data: pendingUsers,
    })
  } catch (error) {
    console.error("Erreur lors de la récupération des utilisateurs en attente:", error)
    return NextResponse.json({ success: false, error: "Erreur interne du serveur" }, { status: 500 })
  }
}
