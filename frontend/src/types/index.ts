export interface ExtraFeatures {
  expression?: string | null
  posture?: string | null
  fur_amount?: string | null
  mood?: string | null
  size?: string | null
  age_estimate?: string | null
  other_traits?: string[]
}

export interface PetInfo {
  animal_type: string
  breed: string
  confidence: number
  color?: string
  general_confidence?: number
  breed_confidence?: number
  extra_features?: ExtraFeatures
}

export interface LicenseRequest {
  pet_image: File
  owner_name: string
  pet_name: string
  issue_location: string
  issue_date: string
  gender: string
  color?: string
  favorite_word?: string
  microchip_no?: string
}

export interface LicenseResponse {
  license_image_url: string
  pet_info: PetInfo
  s3_key: string
}
