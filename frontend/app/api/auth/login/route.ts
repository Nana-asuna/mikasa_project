import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const { email, password } = await request.json()

    if (!email || !password) {
      return NextResponse.json({ success: false, error: "Email et mot de passe requis" }, { status: 400 })
    }

    // Communiquer avec le backend Django
    const response = await fetch('http://localhost:8000/api/v1/auth/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password }),
    })

    const data = await response.json()

    if (response.ok) {
      // Connexion réussie
      return NextResponse.json({
        success: true,
        user: data.user,
        token: data.access,
        refresh_token: data.refresh,
      })
    } else {
      // Erreur de connexion
      return NextResponse.json({ 
        success: false, 
        error: data.error || "Email ou mot de passe incorrect" 
      }, { status: 401 })
    }

  } catch (error) {
    console.error("Login error:", error)
    return NextResponse.json({ 
      success: false, 
      error: "Erreur de connexion au serveur. Vérifiez que le backend Django est démarré." 
    }, { status: 500 })
  }
}
