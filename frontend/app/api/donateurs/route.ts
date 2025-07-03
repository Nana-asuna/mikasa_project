import { type NextRequest, NextResponse } from "next/server"
import { db, generateId, initializeDatabase } from "@/lib/db"
import { hasPermission } from "@/lib/auth"

export async function GET(request: NextRequest) {
  try {
    initializeDatabase()

    const userRole = request.headers.get("x-user-role")
    const userId = request.headers.get("x-user-id")

    let donateurs = db.donateurs

    // Les donateurs ne voient que leur propre profil
    if (userRole === "donateur" || userRole === "parrain") {
      donateurs = donateurs.filter((d) => d.userId === userId)
    } else if (!hasPermission(userRole || "", ["admin", "assistant_social"])) {
      return NextResponse.json({ success: false, error: "Accès non autorisé" }, { status: 403 })
    }

    return NextResponse.json({
      success: true,
      data: donateurs,
    })
  } catch (error) {
    return NextResponse.json({ success: false, error: "Erreur serveur" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    initializeDatabase()

    const donateurData = await request.json()

    const newDonateur = {
      id: generateId(),
      ...donateurData,
      createdAt: new Date(),
      updatedAt: new Date(),
    }

    db.donateurs.push(newDonateur)

    return NextResponse.json({
      success: true,
      data: newDonateur,
    })
  } catch (error) {
    return NextResponse.json({ success: false, error: "Erreur serveur" }, { status: 500 })
  }
}

export default function handler() {
  return new Response(JSON.stringify({ ok: true, message: "Use GET or POST for /api/donateurs" }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  })
}
