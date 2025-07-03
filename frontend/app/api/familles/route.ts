import { type NextRequest, NextResponse } from "next/server"
import { db, generateId, initializeDatabase } from "@/lib/db"
import { hasPermission } from "@/lib/auth"

export async function GET(request: NextRequest) {
  try {
    initializeDatabase()

    const userRole = request.headers.get("x-user-role")

    if (!hasPermission(userRole || "", ["admin", "assistant_social"])) {
      return NextResponse.json({ success: false, error: "Accès non autorisé" }, { status: 403 })
    }

    return NextResponse.json({
      success: true,
      data: db.famillesAccueil,
    })
  } catch (error) {
    return NextResponse.json({ success: false, error: "Erreur serveur" }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    initializeDatabase()

    const userRole = request.headers.get("x-user-role")

    if (!hasPermission(userRole || "", ["admin", "assistant_social"])) {
      return NextResponse.json({ success: false, error: "Accès non autorisé" }, { status: 403 })
    }

    const familleData = await request.json()

    const newFamille = {
      id: generateId(),
      ...familleData,
      dateAffectation: new Date(familleData.dateAffectation),
      enfantsAccueillis: familleData.enfantsAccueillis || [],
      createdAt: new Date(),
      updatedAt: new Date(),
    }

    db.famillesAccueil.push(newFamille)

    return NextResponse.json({
      success: true,
      data: newFamille,
    })
  } catch (error) {
    return NextResponse.json({ success: false, error: "Erreur serveur" }, { status: 500 })
  }
}

export default function handler() {
  return new Response(JSON.stringify({ ok: true, message: "Use GET or POST for /api/familles" }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  })
}
