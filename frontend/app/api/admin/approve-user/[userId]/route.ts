import { type NextRequest, NextResponse } from "next/server"
import { verifyAccessToken } from "@/lib/auth"
import { approvePendingUser, rejectPendingUser, findUserById } from "@/lib/db"

export async function POST(request: NextRequest, { params }: { params: { userId: string } }) {
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

    const { action } = await request.json()
    const userId = params.userId

    if (action === "approve") {
      const approvedUser = approvePendingUser(userId)
      if (!approvedUser) {
        return NextResponse.json({ success: false, error: "Utilisateur non trouvé" }, { status: 404 })
      }

      return NextResponse.json({
        success: true,
        message: "Utilisateur approuvé avec succès",
        data: approvedUser,
      })
    } else if (action === "reject") {
      const rejected = rejectPendingUser(userId)
      if (!rejected) {
        return NextResponse.json({ success: false, error: "Utilisateur non trouvé" }, { status: 404 })
      }

      return NextResponse.json({
        success: true,
        message: "Demande rejetée avec succès",
      })
    } else {
      return NextResponse.json({ success: false, error: "Action non valide" }, { status: 400 })
    }
  } catch (error) {
    console.error("Erreur lors de l'approbation:", error)
    return NextResponse.json({ success: false, error: "Erreur interne du serveur" }, { status: 500 })
  }
}
