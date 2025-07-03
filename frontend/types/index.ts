export interface User {
  id: string
  username: string
  email: string
  first_name?: string
  last_name?: string
  role: string
  phone_number?: string
  is_active: boolean
  is_approved: boolean
  motivation?: string
  experience?: string
  specialization?: string
  created_at: string
  updated_at: string
}

export interface AuthTokens {
  accessToken: string
  refreshToken: string
}

export interface Enfant {
  id: string
  prenom: string
  nom: string
  date_naissance: string
  age: number
  sexe: "M" | "F"
  photo?: string
  statut: "present" | "adopte" | "famille_accueil" | "parraine"
  date_arrivee: string
  antecedents_medicaux?: string
  allergies?: string
  medicaments?: string
  notes_medicales?: string
  medecin_referent?: string
  created_by?: string
  created_at: string
  updated_at: string
}

export interface Don {
  id: string
  donateur_nom: string
  donateur_email: string
  montant: number
  type: "ponctuel" | "mensuel"
  statut: "en_attente" | "confirme" | "annule"
  date_don: string
  message?: string
  created_at: string
}

export interface Stock {
  id: string
  nom: string
  categorie: string
  quantite: number
  unite: string
  seuil_alerte: number
  date_expiration?: string
  fournisseur?: string
  prix_unitaire?: number
  created_at: string
  updated_at: string
}

export interface Famille {
  id: string
  nom: string
  prenom_contact: string
  email: string
  telephone: string
  adresse: string
  type: "adoption" | "famille_accueil"
  statut: "en_attente" | "approuve" | "rejete"
  enfants_souhaites: number
  age_min: number
  age_max: number
  sexe_preference?: "M" | "F" | "indifferent"
  motivation: string
  situation_familiale: string
  revenus_mensuels?: number
  created_at: string
  updated_at: string
}

export interface Planning {
  id: string
  titre: string
  description?: string
  date_debut: string
  date_fin: string
  type: "medical" | "educatif" | "social" | "administratif"
  responsable: string
  participants?: string[]
  statut: "planifie" | "en_cours" | "termine" | "annule"
  created_at: string
  updated_at: string
}

export interface ConsultationMedicale {
  id: string
  enfant_id: string
  medecin_id: string
  date_consultation: string
  motif: string
  diagnostic?: string
  traitement?: string
  notes: string
  prochain_rdv?: string
  created_at: string
  updated_at: string
}

export interface PendingUser {
  id: string
  username: string
  email: string
  first_name: string
  last_name: string
  role: string
  phone_number?: string
  motivation: string
  experience?: string
  specialization?: string
  created_at: string
}
