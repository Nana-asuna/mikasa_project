import { type NextRequest, NextResponse } from "next/server"
import { verifyAccessToken } from "@/lib/auth"
import { db, findUserById, generateId } from "@/lib/db"

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
      data: db.dons,
    })
  } catch (error) {
    console.error("Error fetching dons:", error)
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
    if (!user) {
      return NextResponse.json({ error: "Utilisateur non trouvé" }, { status: 404 })
    }

    const donData = await request.json()

    const newDon = {
      id: generateId(),
      donateur_nom: donData.donateur_nom,
      donateur_email: donData.donateur_email,
      montant: parseFloat(donData.montant),
      type: donData.type,
      statut: "confirme" as const,
      date_don: donData.date,
      message: donData.message || "",
      created_at: new Date().toISOString(),
    }

    db.dons.push(newDon)

    return NextResponse.json({
      success: true,
      data: newDon,
    })
  } catch (error) {
    console.error("Error creating don:", error)
    return NextResponse.json({ success: false, error: "Erreur interne du serveur" }, { status: 500 })
  }
}
