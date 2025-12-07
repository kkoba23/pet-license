import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
})

// 認証トークンをリクエストに付与するインターセプター
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 認証エラー時のインターセプター
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('admin_token')
      window.location.href = '/admin/login'
    }
    return Promise.reject(error)
  }
)

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface AdminInfo {
  id: number
  username: string
}

export interface EventData {
  id: number
  event_code: string
  name: string
  issue_location: string
  issue_date: string | null
  auto_issue_date: boolean
  is_active: boolean
  created_at?: string
}

export interface EventCreate {
  name: string
  issue_location: string
  issue_date?: string | null
  auto_issue_date: boolean
}

export interface EventUpdate {
  name?: string
  issue_location?: string
  issue_date?: string | null
  auto_issue_date?: boolean
  is_active?: boolean
}

export interface PublicEventData {
  event_code: string
  name: string
  issue_location: string
  issue_date: string | null
  auto_issue_date: boolean
}

// === 認証API ===
export const login = async (username: string, password: string): Promise<LoginResponse> => {
  const formData = new URLSearchParams()
  formData.append('username', username)
  formData.append('password', password)

  const response = await apiClient.post<LoginResponse>('/admin/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })
  return response.data
}

export const getAdminInfo = async (): Promise<AdminInfo> => {
  const response = await apiClient.get<AdminInfo>('/admin/me')
  return response.data
}

// === イベント管理API ===
export const listEvents = async (): Promise<EventData[]> => {
  const response = await apiClient.get<EventData[]>('/admin/events')
  return response.data
}

export const createEvent = async (event: EventCreate): Promise<EventData> => {
  const response = await apiClient.post<EventData>('/admin/events', event, {
    headers: {
      'Content-Type': 'application/json',
    },
  })
  return response.data
}

export const getEvent = async (eventId: number): Promise<EventData> => {
  const response = await apiClient.get<EventData>(`/admin/events/${eventId}`)
  return response.data
}

export const updateEvent = async (eventId: number, event: EventUpdate): Promise<EventData> => {
  const response = await apiClient.put<EventData>(`/admin/events/${eventId}`, event, {
    headers: {
      'Content-Type': 'application/json',
    },
  })
  return response.data
}

export const deleteEvent = async (eventId: number): Promise<void> => {
  await apiClient.delete(`/admin/events/${eventId}`)
}

// === 公開イベントAPI ===
export const getEventByCode = async (eventCode: string): Promise<PublicEventData> => {
  const response = await apiClient.get<PublicEventData>(`/events/${eventCode}`)
  return response.data
}

// === 免許証API ===
export interface LicenseData {
  id: number
  receipt_number?: string
  pet_name: string
  owner_name: string
  animal_type?: string
  breed?: string
  color?: string
  birth_date?: string
  gender?: string
  favorite_food?: string
  favorite_word?: string
  microchip_no?: string
  license_image_url: string
  original_image_url?: string
  created_at?: string
}

export interface LicenseSaveRequest {
  eventCode: string
  licenseImage: Blob
  originalImage?: Blob
  petName: string
  ownerName: string
  animalType?: string
  breed?: string
  color?: string
  birthDate?: string
  gender?: string
  favoriteFood?: string
  favoriteWord?: string
  microchipNo?: string
}

export interface LicenseSaveResponse {
  id: number
  license_image_url: string
  original_image_url?: string
  receipt_number: string
  message: string
}

export const saveLicense = async (data: LicenseSaveRequest): Promise<LicenseSaveResponse> => {
  const formData = new FormData()
  formData.append('license_image', data.licenseImage, 'license.png')
  if (data.originalImage) {
    formData.append('original_image', data.originalImage, 'original.jpg')
  }
  formData.append('pet_name', data.petName)
  formData.append('owner_name', data.ownerName)
  if (data.animalType) formData.append('animal_type', data.animalType)
  if (data.breed) formData.append('breed', data.breed)
  if (data.color) formData.append('color', data.color)
  if (data.birthDate) formData.append('birth_date', data.birthDate)
  if (data.gender) formData.append('gender', data.gender)
  if (data.favoriteFood) formData.append('favorite_food', data.favoriteFood)
  if (data.favoriteWord) formData.append('favorite_word', data.favoriteWord)
  if (data.microchipNo) formData.append('microchip_no', data.microchipNo)

  const response = await apiClient.post<LicenseSaveResponse>(
    `/licenses/${data.eventCode}/save`,
    formData
  )
  return response.data
}

export const listLicenses = async (eventCode: string): Promise<LicenseData[]> => {
  const response = await apiClient.get<LicenseData[]>(`/licenses/${eventCode}`)
  return response.data
}

export interface PaginatedLicenseResponse {
  items: LicenseData[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export interface NewLicensesResponse {
  items: LicenseData[]
  total_count: number
}

export const listLicensesPaginated = async (
  eventCode: string,
  page: number = 1,
  perPage: number = 20
): Promise<PaginatedLicenseResponse> => {
  const response = await apiClient.get<PaginatedLicenseResponse>(
    `/licenses/${eventCode}/paginated`,
    { params: { page, per_page: perPage } }
  )
  return response.data
}

export const listNewLicenses = async (
  eventCode: string,
  sinceId: number
): Promise<NewLicensesResponse> => {
  const response = await apiClient.get<NewLicensesResponse>(
    `/licenses/${eventCode}/new`,
    { params: { since_id: sinceId } }
  )
  return response.data
}

export const listLicensesByEventId = async (eventId: number): Promise<LicenseData[]> => {
  const response = await apiClient.get<LicenseData[]>(`/licenses/by-event-id/${eventId}`)
  return response.data
}

export const listLicensesByEventIdPaginated = async (
  eventId: number,
  page: number = 1,
  perPage: number = 20
): Promise<PaginatedLicenseResponse> => {
  const response = await apiClient.get<PaginatedLicenseResponse>(
    `/licenses/by-event-id/${eventId}/paginated`,
    { params: { page, per_page: perPage } }
  )
  return response.data
}

export const listNewLicensesByEventId = async (
  eventId: number,
  sinceId: number
): Promise<NewLicensesResponse> => {
  const response = await apiClient.get<NewLicensesResponse>(
    `/licenses/by-event-id/${eventId}/new`,
    { params: { since_id: sinceId } }
  )
  return response.data
}

export const deleteLicense = async (licenseId: number): Promise<void> => {
  await apiClient.delete(`/licenses/${licenseId}`)
}
