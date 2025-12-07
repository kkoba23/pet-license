import axios from 'axios'
import type { PetInfo, LicenseRequest, LicenseResponse } from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'multipart/form-data'
  }
})

export const analyzePet = async (file: File): Promise<PetInfo> => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await apiClient.post<PetInfo>('/analyze-pet', formData)
  return response.data
}

export const generateLicense = async (request: LicenseRequest): Promise<LicenseResponse> => {
  const formData = new FormData()
  formData.append('pet_image', request.pet_image)
  formData.append('owner_name', request.owner_name)
  formData.append('pet_name', request.pet_name)
  formData.append('issue_location', request.issue_location)
  formData.append('issue_date', request.issue_date)
  formData.append('gender', request.gender)

  if (request.color) formData.append('color', request.color)
  if (request.favorite_word) formData.append('favorite_word', request.favorite_word)
  if (request.microchip_no) formData.append('microchip_no', request.microchip_no)

  const response = await apiClient.post<LicenseResponse>('/generate-license', formData)
  return response.data
}

export interface GeneratedProfile {
  gender: string
  pet_name: string
  owner_name: string
  special_notes: string[]
  favorite_word: string
}

export interface ExtraFeatures {
  expression?: string | null
  posture?: string | null
  fur_amount?: string | null
  size?: string | null
  age_estimate?: string | null
  other_traits?: string[]
}

export const generateProfile = async (
  animalType: string,
  breed: string,
  color?: string,
  extraFeatures?: ExtraFeatures
): Promise<GeneratedProfile> => {
  const formData = new FormData()
  formData.append('animal_type', animalType)
  formData.append('breed', breed)
  if (color) formData.append('color', color)

  // 追加特徴を送信
  if (extraFeatures) {
    if (extraFeatures.expression) formData.append('expression', extraFeatures.expression)
    if (extraFeatures.posture) formData.append('posture', extraFeatures.posture)
    if (extraFeatures.fur_amount) formData.append('fur_amount', extraFeatures.fur_amount)
    if (extraFeatures.size) formData.append('size', extraFeatures.size)
    if (extraFeatures.age_estimate) formData.append('age_estimate', extraFeatures.age_estimate)
    if (extraFeatures.other_traits && extraFeatures.other_traits.length > 0) {
      formData.append('other_traits', extraFeatures.other_traits.join(','))
    }
  }

  const response = await apiClient.post<GeneratedProfile>('/generate-profile', formData)
  return response.data
}
