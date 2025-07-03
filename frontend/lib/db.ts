// Simulation d'une base de données en mémoire
import type { User, Enfant, Don, Stock, Famille, Planning, ConsultationMedicale, PendingUser } from "@/types"

// Base de données simulée
export const db = {
  users: [
    {
      id: "1",
      username: "nana",
      email: "nanayaguediame@gmail.com",
      first_name: "nana",
      last_name: "diame",
      role: "admin",
      is_active: true,
      is_approved: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: "2",
      username: "medecin1",
      email: "dr.sall@orphelinat.com",
      first_name: "sall",
      last_name: "sall",
      role: "medecin",
      phone_number: "+33123456789",
      specialization: "Pédiatrie",
      is_active: true,
      is_approved: true,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ] as User[],

  pendingUsers: [] as PendingUser[],

  donateurs: [] as any[],

  enfants: [
    {
      id: "1",
      prenom: "julia",
      nom: "diop",
      date_naissance: "2018-05-15",
      age: 6,
      sexe: "F" as const,
      statut: "present" as const,
      date_arrivee: "2023-01-10",
      antecedents_medicaux: "Aucun",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    {
      id: "2",
      prenom: "saliou",
      nom: "toure",
      date_naissance: "2020-08-22",
      age: 4,
      sexe: "M" as const,
      statut: "present" as const,
      date_arrivee: "2023-03-05",
      antecedents_medicaux: "Asthme léger",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ] as Enfant[],

  dons: [
    {
      id: "1",
      donateur_nom: "Adjaratou",
      donateur_email: "donateur.adjaratou@example.com",
      montant: 100,
      type: "ponctuel" as const,
      statut: "confirme" as const,
      date_don: "2024-01-15",
      message: "Pour les enfants",
      created_at: new Date().toISOString(),
    },
  ] as Don[],

  stock: [
    {
      id: "1",
      nom: "Lait en poudre",
      categorie: "Alimentation",
      quantite: 50,
      unite: "boîtes",
      seuil_alerte: 10,
      date_expiration: "2024-12-31",
      fournisseur: "Lactalis",
      prix_unitaire: 15.5,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ] as Stock[],

  familles: [
    {
      id: "1",
      nom: "Famille Toure",
      prenom_contact: "Sophia",
      email: "princesse.sophia@email.com",
      telephone: "+221776599328",
      adresse: "Mariste, Rue Boulangerie Villa 186",
      type: "adoption" as const,
      statut: "en_attente" as const,
      enfants_souhaites: 1,
      age_min: 3,
      age_max: 8,
      sexe_preference: "indifferent" as const,
      motivation: "Nous souhaitons agrandir notre famille",
      situation_familiale: "Couple marié",
      revenus_mensuels: 4500,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ] as Famille[],

  planning: [
    {
      id: "1",
      titre: "Consultation pédiatrique",
      description: "Consultation mensuelle pour tous les enfants",
      date_debut: "2024-02-15T09:00:00Z",
      date_fin: "2024-02-15T17:00:00Z",
      type: "medical" as const,
      responsable: "Dr. Sall",
      participants: ["Julia", "Saliou"],
      statut: "planifie" as const,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
  ] as Planning[],

  consultations: [] as ConsultationMedicale[],

  // Mots de passe hashés (pour la démo)
  passwords: {
    "admin@orphelinat.com": "$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6ukx.LrUpm", // admin123
    "dr.martin@orphelinat.com": "$2a$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6ukx.LrUpm", // admin123
  } as Record<string, string>,
}

// Fonctions utilitaires
export function generateId(): string {
  return Math.random().toString(36).substr(2, 9)
}

export function initializeDatabase(): void {
  // Cette fonction peut être utilisée pour initialiser la base de données si nécessaire
  // Pour l'instant, elle ne fait rien car la base est déjà initialisée
}

export function findUserByEmail(email: string): User | undefined {
  return db.users.find((user) => user.email === email)
}

export function findUserById(id: string): User | undefined {
  return db.users.find((user) => user.id === id)
}

export function createUser(userData: Omit<User, "id" | "created_at" | "updated_at">): User {
  const newUser: User = {
    ...userData,
    id: generateId(),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }
  db.users.push(newUser)
  return newUser
}

export function createPendingUser(userData: Omit<PendingUser, "id" | "created_at">): PendingUser {
  const newPendingUser: PendingUser = {
    ...userData,
    id: generateId(),
    created_at: new Date().toISOString(),
  }
  db.pendingUsers.push(newPendingUser)
  return newPendingUser
}

export function getPendingUsers(): PendingUser[] {
  return db.pendingUsers
}

export function approvePendingUser(pendingUserId: string): User | null {
  const pendingUserIndex = db.pendingUsers.findIndex((user) => user.id === pendingUserId)
  if (pendingUserIndex === -1) return null

  const pendingUser = db.pendingUsers[pendingUserIndex]

  // Créer l'utilisateur approuvé
  const approvedUser = createUser({
    username: pendingUser.username,
    email: pendingUser.email,
    first_name: pendingUser.first_name,
    last_name: pendingUser.last_name,
    role: pendingUser.role,
    phone_number: pendingUser.phone_number,
    is_active: true,
    is_approved: true,
    motivation: pendingUser.motivation,
    experience: pendingUser.experience,
    specialization: pendingUser.specialization,
  })

  // Supprimer de la liste d'attente
  db.pendingUsers.splice(pendingUserIndex, 1)

  return approvedUser
}

export function rejectPendingUser(pendingUserId: string): boolean {
  const pendingUserIndex = db.pendingUsers.findIndex((user) => user.id === pendingUserId)
  if (pendingUserIndex === -1) return false

  db.pendingUsers.splice(pendingUserIndex, 1)
  return true
}

export function createEnfant(enfantData: Omit<Enfant, "id" | "created_at" | "updated_at">): Enfant {
  const newEnfant: Enfant = {
    ...enfantData,
    id: generateId(),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }
  db.enfants.push(newEnfant)
  return newEnfant
}

export function getEnfantsByMedecin(medecinId: string): Enfant[] {
  return db.enfants.filter((enfant) => enfant.medecin_referent === medecinId)
}

export function createConsultation(
  consultationData: Omit<ConsultationMedicale, "id" | "created_at">,
): ConsultationMedicale {
  const newConsultation: ConsultationMedicale = {
    ...consultationData,
    id: generateId(),
    created_at: new Date().toISOString(),
  }
  db.consultations.push(newConsultation)
  return newConsultation
}

export function getConsultationsByMedecin(medecinId: string): ConsultationMedicale[] {
  return db.consultations.filter((consultation) => consultation.medecin_id === medecinId)
}
