<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import QRCodeVue3 from 'qrcode.vue'
import {
  getEvent,
  updateEvent,
  deleteEvent,
  getAdminInfo,
  listLicensesByEventIdPaginated,
  listNewLicensesByEventId,
  deleteLicense,
  type EventData,
  type LicenseData,
} from '@/api/admin'

const router = useRouter()
const route = useRoute()

const event = ref<EventData | null>(null)
const licenses = ref<LicenseData[]>([])
const isLoading = ref(true)
const isSaving = ref(false)
const showEditModal = ref(false)
const showLicenseModal = ref(false)
const selectedLicense = ref<LicenseData | null>(null)

// ページング用
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)
const perPage = 20

// ポーリング用
const isPolling = ref(false)
const newCount = ref(0)
const maxLicenseId = ref(0)
let pollingInterval: ReturnType<typeof setInterval> | null = null

const editForm = ref({
  name: '',
  issue_location: '',
  issue_date: '',
  auto_issue_date: false,
  is_active: true,
})

const eventId = computed(() => Number(route.params.id))

const baseUrl = computed(() => window.location.origin)

const eventUrl = computed(() => {
  if (!event.value) return ''
  return `${baseUrl.value}/event/${event.value.event_code}`
})

onMounted(async () => {
  try {
    await getAdminInfo()
    await loadEvent()
    await loadLicenses()
    startPolling()
  } catch {
    router.push('/admin/login')
  }
})

onUnmounted(() => {
  stopPolling()
})

const loadEvent = async () => {
  isLoading.value = true
  try {
    event.value = await getEvent(eventId.value)
  } catch (err) {
    console.error('Failed to load event:', err)
    router.push('/admin/events')
  } finally {
    isLoading.value = false
  }
}

const loadLicenses = async () => {
  try {
    const data = await listLicensesByEventIdPaginated(eventId.value, currentPage.value, perPage)
    licenses.value = data.items
    totalCount.value = data.total
    totalPages.value = data.total_pages

    // 最大IDを更新（ポーリング用）
    if (data.items.length > 0) {
      const maxId = Math.max(...data.items.map(l => l.id))
      if (maxId > maxLicenseId.value) {
        maxLicenseId.value = maxId
      }
    }
    newCount.value = 0
  } catch (err) {
    console.error('Failed to load licenses:', err)
  }
}

const pollNewLicenses = async () => {
  try {
    const data = await listNewLicensesByEventId(eventId.value, maxLicenseId.value)
    totalCount.value = data.total_count

    if (data.items.length > 0) {
      newCount.value += data.items.length

      // 1ページ目の場合は先頭に追加
      if (currentPage.value === 1) {
        licenses.value = [...data.items, ...licenses.value]
        if (licenses.value.length > perPage) {
          licenses.value = licenses.value.slice(0, perPage)
        }
      }

      // 最大IDを更新
      const maxId = Math.max(...data.items.map(l => l.id))
      maxLicenseId.value = maxId

      // 総ページ数を更新
      totalPages.value = Math.ceil(data.total_count / perPage)
    }
  } catch (err) {
    console.error('Failed to poll new licenses:', err)
  }
}

const startPolling = () => {
  if (pollingInterval) return
  isPolling.value = true
  pollingInterval = setInterval(async () => {
    await pollNewLicenses()
  }, 5000)
}

const stopPolling = () => {
  if (pollingInterval) {
    clearInterval(pollingInterval)
    pollingInterval = null
  }
  isPolling.value = false
}

const goToPage = async (page: number) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  isLoading.value = true
  newCount.value = 0
  try {
    await loadLicenses()
  } finally {
    isLoading.value = false
  }
}

const openEditModal = () => {
  if (!event.value) return
  editForm.value = {
    name: event.value.name,
    issue_location: event.value.issue_location,
    issue_date: event.value.issue_date || '',
    auto_issue_date: event.value.auto_issue_date,
    is_active: event.value.is_active,
  }
  showEditModal.value = true
}

const handleUpdateEvent = async () => {
  if (!event.value) return
  isSaving.value = true
  try {
    await updateEvent(event.value.id, {
      name: editForm.value.name,
      issue_location: editForm.value.issue_location,
      issue_date: editForm.value.auto_issue_date ? null : editForm.value.issue_date,
      auto_issue_date: editForm.value.auto_issue_date,
      is_active: editForm.value.is_active,
    })
    showEditModal.value = false
    await loadEvent()
  } catch (err) {
    console.error('Failed to update event:', err)
    alert('イベントの更新に失敗しました')
  } finally {
    isSaving.value = false
  }
}

const toggleActive = async () => {
  if (!event.value) return
  try {
    await updateEvent(event.value.id, {
      is_active: !event.value.is_active,
    })
    await loadEvent()
  } catch (err) {
    console.error('Failed to toggle event status:', err)
    alert('ステータスの変更に失敗しました')
  }
}

const handleDeleteEvent = async () => {
  if (!event.value) return
  if (!confirm('このイベントを削除しますか？この操作は取り消せません。')) return
  try {
    await deleteEvent(event.value.id)
    router.push('/admin/events')
  } catch (err) {
    console.error('Failed to delete event:', err)
    alert('イベントの削除に失敗しました')
  }
}

const copyEventUrl = () => {
  navigator.clipboard.writeText(eventUrl.value)
  alert('URLをコピーしました')
}

const formatDate = (dateStr: string | null) => {
  if (!dateStr) return '自動（アクセス日）'
  const date = new Date(dateStr)
  return date.toLocaleDateString('ja-JP')
}

const goBack = () => {
  router.push('/admin/events')
}

const openLicenseModal = (license: LicenseData) => {
  selectedLicense.value = license
  showLicenseModal.value = true
}

const handleDeleteLicense = async (licenseId: number) => {
  if (!confirm('この免許証を削除しますか？')) return
  try {
    await deleteLicense(licenseId)
    showLicenseModal.value = false
    await loadLicenses()
  } catch (err) {
    console.error('Failed to delete license:', err)
    alert('免許証の削除に失敗しました')
  }
}

const formatLicenseDate = (dateStr: string | undefined) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('ja-JP')
}
</script>

<template>
  <div class="admin-container">
    <header class="admin-header">
      <div class="header-left">
        <button @click="goBack" class="back-button">&larr; 戻る</button>
        <h1>イベント詳細</h1>
      </div>
    </header>

    <main class="admin-main">
      <div v-if="isLoading" class="loading">読み込み中...</div>

      <div v-else-if="event" class="event-detail">
        <div class="detail-grid">
          <div class="detail-card info-card">
            <div class="card-header">
              <h2>{{ event.name }}</h2>
              <span :class="['status-badge', event.is_active ? 'active' : 'inactive']">
                {{ event.is_active ? '有効' : '無効' }}
              </span>
            </div>

            <div class="info-list">
              <div class="info-item">
                <span class="label">イベントコード</span>
                <span class="value">{{ event.event_code }}</span>
              </div>
              <div class="info-item">
                <span class="label">交付場所</span>
                <span class="value">{{ event.issue_location }}</span>
              </div>
              <div class="info-item">
                <span class="label">交付日</span>
                <span class="value">{{ formatDate(event.issue_date) }}</span>
              </div>
              <div class="info-item">
                <span class="label">作成日</span>
                <span class="value">{{ event.created_at ? new Date(event.created_at).toLocaleDateString('ja-JP') : '-' }}</span>
              </div>
            </div>

            <div class="action-buttons">
              <button @click="openEditModal" class="edit-button">編集</button>
              <button @click="toggleActive" :class="['toggle-button', event.is_active ? 'deactivate' : 'activate']">
                {{ event.is_active ? '無効にする' : '有効にする' }}
              </button>
              <button @click="handleDeleteEvent" class="delete-button">削除</button>
            </div>
          </div>

          <div class="detail-card qr-card">
            <h3>イベントQRコード</h3>
            <div class="qr-container">
              <QRCodeVue3 :value="eventUrl" :size="200" level="M" />
            </div>
            <div class="url-section">
              <input type="text" :value="eventUrl" readonly class="url-input" />
              <button @click="copyEventUrl" class="copy-button">コピー</button>
            </div>
            <p class="qr-hint">このQRコードをスキャンすると、ユーザーがイベントページにアクセスできます</p>
          </div>
        </div>

        <!-- 免許証一覧 -->
        <div class="licenses-section">
          <div class="licenses-header">
            <h3>作成された免許証（{{ totalCount }}件）</h3>
            <div class="licenses-header-right">
              <span class="new-count" v-if="newCount > 0">+{{ newCount }}件 新着</span>
              <span class="auto-refresh-status" :class="{ active: isPolling }">
                自動更新: {{ isPolling ? 'ON' : 'OFF' }}
              </span>
            </div>
          </div>

          <!-- ページネーション（上部） -->
          <div v-if="totalPages > 1" class="pagination">
            <button @click="goToPage(1)" :disabled="currentPage === 1" class="page-btn">
              &laquo;
            </button>
            <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1" class="page-btn">
              &lsaquo;
            </button>
            <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
            <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages" class="page-btn">
              &rsaquo;
            </button>
            <button @click="goToPage(totalPages)" :disabled="currentPage === totalPages" class="page-btn">
              &raquo;
            </button>
          </div>

          <div v-if="licenses.length === 0" class="empty-licenses">
            まだ免許証が作成されていません
          </div>
          <div v-else class="licenses-grid">
            <div
              v-for="license in licenses"
              :key="license.id"
              class="license-card"
              @click="openLicenseModal(license)"
            >
              <div class="license-card-badge" v-if="license.receipt_number">
                #{{ license.receipt_number }}
              </div>
              <img :src="license.license_image_url" :alt="license.pet_name" class="license-thumbnail" />
              <div class="license-info">
                <span class="pet-name">{{ license.pet_name }}</span>
                <span class="owner-name">{{ license.owner_name }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 編集モーダル -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal">
        <h2>イベント編集</h2>
        <form @submit.prevent="handleUpdateEvent">
          <div class="form-group">
            <label>イベント名</label>
            <input v-model="editForm.name" type="text" required />
          </div>
          <div class="form-group">
            <label>交付場所</label>
            <input v-model="editForm.issue_location" type="text" required />
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input v-model="editForm.auto_issue_date" type="checkbox" />
              交付日を自動（アクセス日）にする
            </label>
          </div>
          <div v-if="!editForm.auto_issue_date" class="form-group">
            <label>交付日</label>
            <input v-model="editForm.issue_date" type="date" required />
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input v-model="editForm.is_active" type="checkbox" />
              有効
            </label>
          </div>
          <div class="modal-actions">
            <button type="button" @click="showEditModal = false" class="cancel-button" :disabled="isSaving">
              キャンセル
            </button>
            <button type="submit" class="submit-button" :disabled="isSaving">
              {{ isSaving ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 免許証詳細モーダル -->
    <div v-if="showLicenseModal && selectedLicense" class="modal-overlay" @click.self="showLicenseModal = false">
      <div class="modal license-modal">
        <div class="license-modal-header">
          <h2>{{ selectedLicense.pet_name }}の免許証</h2>
          <button @click="showLicenseModal = false" class="close-button">&times;</button>
        </div>
        <div class="license-modal-content">
          <!-- 受付番号バッジ -->
          <div v-if="selectedLicense.receipt_number" class="modal-receipt-badge">
            受付番号: #{{ selectedLicense.receipt_number }}
          </div>

          <img :src="selectedLicense.license_image_url" :alt="selectedLicense.pet_name" class="license-full-image" />

          <!-- 基本情報セクション -->
          <div class="license-details">
            <h4>基本情報</h4>
            <div class="details-grid">
              <div class="detail-item">
                <span class="detail-label">ペット名</span>
                <span class="detail-value">{{ selectedLicense.pet_name }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">飼い主名</span>
                <span class="detail-value">{{ selectedLicense.owner_name }}</span>
              </div>
              <div class="detail-item" v-if="selectedLicense.animal_type">
                <span class="detail-label">動物種別</span>
                <span class="detail-value">{{ selectedLicense.animal_type }}</span>
              </div>
              <div class="detail-item" v-if="selectedLicense.breed">
                <span class="detail-label">品種</span>
                <span class="detail-value">{{ selectedLicense.breed }}</span>
              </div>
              <div class="detail-item" v-if="selectedLicense.color">
                <span class="detail-label">毛色</span>
                <span class="detail-value">{{ selectedLicense.color }}</span>
              </div>
              <div class="detail-item" v-if="selectedLicense.gender">
                <span class="detail-label">性別</span>
                <span class="detail-value">{{ selectedLicense.gender }}</span>
              </div>
              <div class="detail-item" v-if="selectedLicense.birth_date">
                <span class="detail-label">生年月日</span>
                <span class="detail-value">{{ selectedLicense.birth_date }}</span>
              </div>
            </div>
          </div>

          <!-- AI生成情報セクション -->
          <div class="license-details ai-details" v-if="selectedLicense.favorite_word || selectedLicense.favorite_food || selectedLicense.microchip_no">
            <h4>AI生成情報</h4>
            <div class="details-grid">
              <div class="detail-item" v-if="selectedLicense.favorite_word">
                <span class="detail-label">お好きな一言</span>
                <span class="detail-value">{{ selectedLicense.favorite_word }}</span>
              </div>
              <div class="detail-item" v-if="selectedLicense.favorite_food">
                <span class="detail-label">好きな食べ物</span>
                <span class="detail-value">{{ selectedLicense.favorite_food }}</span>
              </div>
              <div class="detail-item" v-if="selectedLicense.microchip_no">
                <span class="detail-label">マイクロチップNo</span>
                <span class="detail-value">{{ selectedLicense.microchip_no }}</span>
              </div>
            </div>
          </div>

          <!-- メタ情報 -->
          <div class="license-meta">
            <span>作成日時: {{ formatLicenseDate(selectedLicense.created_at) }}</span>
          </div>
        </div>
        <div class="license-modal-actions">
          <a :href="selectedLicense.license_image_url" download class="download-button">ダウンロード</a>
          <button @click="handleDeleteLicense(selectedLicense.id)" class="delete-button">削除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin-container {
  min-height: 100vh;
  background: #f5f5f5;
}

.admin-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.back-button {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.3);
}

.admin-header h1 {
  margin: 0;
  font-size: 24px;
}

.admin-main {
  padding: 40px;
  max-width: 1000px;
  margin: 0 auto;
}

.loading {
  text-align: center;
  padding: 60px;
  color: #666;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media (max-width: 768px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}

.detail-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.status-badge {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.status-badge.active {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-badge.inactive {
  background: #ffebee;
  color: #c62828;
}

.info-list {
  margin-bottom: 24px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #eee;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  color: #666;
  font-weight: 500;
}

.info-item .value {
  color: #333;
  font-weight: 600;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.edit-button,
.toggle-button,
.delete-button {
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.edit-button {
  background: #e3f2fd;
  color: #1976d2;
  border: 1px solid #1976d2;
}

.edit-button:hover {
  background: #bbdefb;
}

.toggle-button.deactivate {
  background: #fff3e0;
  color: #e65100;
  border: 1px solid #e65100;
}

.toggle-button.activate {
  background: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #2e7d32;
}

.delete-button {
  background: #ffebee;
  color: #c62828;
  border: 1px solid #c62828;
}

.delete-button:hover {
  background: #ffcdd2;
}

.qr-card h3 {
  margin: 0 0 20px;
  color: #333;
  text-align: center;
}

.qr-container {
  display: flex;
  justify-content: center;
  padding: 20px;
  background: white;
  border-radius: 8px;
  margin-bottom: 20px;
}

.url-section {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.url-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
  color: #666;
  background: #f9f9f9;
}

.copy-button {
  background: #667eea;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.copy-button:hover {
  background: #5a6fd6;
}

.qr-hint {
  text-align: center;
  color: #888;
  font-size: 13px;
  margin: 0;
}

/* モーダル */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 32px;
  border-radius: 16px;
  width: 100%;
  max-width: 480px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal h2 {
  margin: 0 0 24px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

.form-group input[type='text'],
.form-group input[type='date'] {
  width: 100%;
  padding: 12px 14px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 16px;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input[type='checkbox'] {
  width: 18px;
  height: 18px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.cancel-button,
.submit-button {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
}

.cancel-button {
  background: #f5f5f5;
  color: #666;
  border: 1px solid #ddd;
}

.cancel-button:hover {
  background: #eee;
}

.submit-button {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.submit-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.submit-button:disabled,
.cancel-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 免許証一覧 */
.licenses-section {
  margin-top: 32px;
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.licenses-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.licenses-section h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.licenses-header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.new-count {
  background: #ff5722;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

.auto-refresh-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  background: #eee;
  color: #666;
}

.auto-refresh-status.active {
  background: #e8f5e9;
  color: #2e7d32;
}

/* ページネーション */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 8px;
}

.page-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #e0e0e0;
  border-color: #ccc;
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
  min-width: 80px;
  text-align: center;
}

.empty-licenses {
  text-align: center;
  padding: 40px;
  color: #888;
}

.licenses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.license-card {
  background: #f9f9f9;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
}

.license-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.license-card-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  z-index: 1;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.license-thumbnail {
  width: 100%;
  height: 140px;
  object-fit: cover;
}

.license-info {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.license-info .pet-name {
  font-weight: 600;
  color: #333;
}

.license-info .owner-name {
  font-size: 13px;
  color: #666;
}

/* 免許証モーダル */
.license-modal {
  max-width: 600px;
}

.license-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.license-modal-header h2 {
  margin: 0;
  font-size: 20px;
}

.close-button {
  background: none;
  border: none;
  font-size: 28px;
  color: #666;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.close-button:hover {
  color: #333;
}

.license-modal-content {
  margin-bottom: 20px;
}

.license-full-image {
  width: 100%;
  border-radius: 8px;
  margin-bottom: 16px;
}

/* 受付番号バッジ（モーダル内） */
.modal-receipt-badge {
  display: inline-block;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 16px;
}

/* 詳細情報セクション */
.license-details {
  background: #f9f9f9;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.license-details h4 {
  margin: 0 0 12px;
  color: #333;
  font-size: 14px;
  font-weight: 600;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 8px;
}

.license-details.ai-details {
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
}

.license-details.ai-details h4 {
  color: #2e7d32;
  border-bottom-color: #a5d6a7;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail-label {
  font-size: 11px;
  color: #888;
  font-weight: 500;
}

.detail-value {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.license-meta {
  text-align: right;
  font-size: 12px;
  color: #888;
  margin-bottom: 16px;
}

.license-modal-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.download-button {
  background: #667eea;
  color: white;
  padding: 10px 20px;
  border-radius: 6px;
  text-decoration: none;
  font-weight: 500;
}

.download-button:hover {
  background: #5a6fd6;
}

@media (max-width: 768px) {
  .licenses-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }

  .license-thumbnail {
    height: 100px;
  }
}
</style>
