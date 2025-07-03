import { NextResponse } from "next/server"
import { db } from "@/lib/db"

export async function GET() {
  try {
    // Retourner seulement les enfants à parrainer avec des informations limitées
    const enfantsPublics = db.enfants
      .filter((enfant) => enfant.statut === "present")
      .map((enfant) => ({
        id: enfant.id,
        prenom: enfant.prenom,
        age: enfant.age,
        sexe: enfant.sexe,
        photo: enfant.photo,
        statut: enfant.statut,
      }))

    return NextResponse.json({
      success: true,
      data: enfantsPublics,
    })
  } catch (error) {
    console.error("Error fetching public enfants:", error)
    return NextResponse.json({ success: false, error: "Erreur interne du serveur" }, { status: 500 })
  }
}
