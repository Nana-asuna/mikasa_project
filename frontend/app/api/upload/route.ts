import { type NextRequest, NextResponse } from "next/server"
import { hasPermission } from "@/lib/auth"

export async function POST(request: NextRequest) {
  try {
    const userRole = request.headers.get("x-user-role")

    if (!hasPermission(userRole || "", ["admin", "assistant_social"])) {
      return NextResponse.json({ success: false, error: "Accès non autorisé" }, { status: 403 })
    }

    const formData = await request.formData()
    const file = formData.get("file") as File

    if (!file) {
      return NextResponse.json({ success: false, error: "Aucun fichier fourni" }, { status: 400 })
    }

    // Vérifier le type de fichier
    if (!file.type.startsWith("image/")) {
      return NextResponse.json({ success: false, error: "Seules les images sont autorisées" }, { status: 400 })
    }

    // Simuler l'upload (en production, utilisez un service comme Vercel Blob)
    const fileName = `${Date.now()}-${file.name}`
    const fileUrl = `/uploads/${fileName}`

    return NextResponse.json({
      success: true,
      data: {
        url: fileUrl,
        fileName,
      },
    })
  } catch (error) {
    return NextResponse.json({ success: false, error: "Erreur serveur" }, { status: 500 })
  }
}

export default function handler() {
  return new Response(JSON.stringify({ ok: true, message: "Use POST to upload files" }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  })
}
