<template>
  <div class="print-page">
    <!-- イベントコード入力フォーム -->
    <div v-if="!eventCode" class="event-code-form">
      <div class="form-container">
        <h1>印刷用ページ</h1>
        <p class="description">イベントコードを入力して、免許証一覧を表示します</p>

        <div class="input-group">
          <input
            v-model="inputEventCode"
            type="text"
            placeholder="イベントコードを入力"
            @keyup.enter="loadEvent"
            class="event-code-input"
          />
          <button @click="loadEvent" :disabled="!inputEventCode || loading" class="load-button">
            <span v-if="loading">読み込み中...</span>
            <span v-else>表示</span>
          </button>
        </div>

        <p v-if="error" class="error-message">{{ error }}</p>
      </div>
    </div>

    <!-- 免許証一覧 -->
    <div v-else class="license-list-container">
      <div class="header">
        <div class="header-left">
          <button @click="resetEventCode" class="back-button">← 戻る</button>
          <h1>{{ eventName }}</h1>
          <span class="event-code-badge">{{ eventCode }}</span>
        </div>
        <div class="header-right">
          <span class="license-count">{{ totalCount }}件</span>
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

      <div v-if="loading" class="loading-spinner">
        読み込み中...
      </div>

      <div v-else-if="licenses.length === 0" class="empty-state">
        <p>まだ免許証がありません</p>
        <p class="empty-hint">ユーザーがアップロードすると自動的に表示されます</p>
      </div>

      <div v-else class="license-grid">
        <div
          v-for="license in licenses"
          :key="license.id"
          class="license-card"
          @click="openModal(license)"
        >
          <div class="license-card-badge" v-if="license.receipt_number">
            #{{ license.receipt_number }}
          </div>
          <img :src="license.license_image_url" :alt="license.pet_name" />
          <div class="license-card-info">
            <span class="pet-name">{{ license.pet_name }}</span>
            <span class="owner-name">{{ license.owner_name }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 詳細モーダル -->
    <div v-if="selectedLicense" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <button class="modal-close" @click="closeModal">&times;</button>

        <div class="modal-body">
          <!-- 受付番号バッジ（画像の上） -->
          <div v-if="selectedLicense.receipt_number" class="modal-receipt-badge-container">
            <div class="modal-receipt-badge">
              受付番号: #{{ selectedLicense.receipt_number }}
            </div>
          </div>

          <!-- 画像セクション -->
          <div class="modal-image-section">
            <img :src="selectedLicense.license_image_url" :alt="selectedLicense.pet_name" class="modal-image" />
          </div>

          <!-- 印刷ボタン（画像のすぐ下） -->
          <div class="print-actions">
            <button @click="printLicense" class="print-button">
              印刷
            </button>
          </div>

          <!-- 詳細情報セクション -->
          <div class="modal-info-section">
            <h2>{{ selectedLicense.pet_name }}</h2>
            <p class="owner-info">飼い主: {{ selectedLicense.owner_name }}</p>

            <!-- 基本情報 -->
            <div class="license-details">
              <h3>基本情報</h3>
              <div class="details-grid">
                <div class="detail-item" v-if="selectedLicense.animal_type">
                  <span class="detail-label">動物種</span>
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
                <div class="detail-item" v-if="selectedLicense.birth_date">
                  <span class="detail-label">生年月日</span>
                  <span class="detail-value">{{ selectedLicense.birth_date }}</span>
                </div>
                <div class="detail-item" v-if="selectedLicense.gender">
                  <span class="detail-label">性別</span>
                  <span class="detail-value">{{ selectedLicense.gender }}</span>
                </div>
                <div class="detail-item" v-if="selectedLicense.microchip_no">
                  <span class="detail-label">マイクロチップ番号</span>
                  <span class="detail-value">{{ selectedLicense.microchip_no }}</span>
                </div>
              </div>
            </div>

            <!-- AI生成情報 -->
            <div class="ai-details" v-if="selectedLicense.favorite_food || selectedLicense.favorite_word">
              <h3>AI生成情報</h3>
              <div class="details-grid">
                <div class="detail-item" v-if="selectedLicense.favorite_food">
                  <span class="detail-label">好きな食べ物</span>
                  <span class="detail-value">{{ selectedLicense.favorite_food }}</span>
                </div>
                <div class="detail-item" v-if="selectedLicense.favorite_word">
                  <span class="detail-label">座右の銘</span>
                  <span class="detail-value">{{ selectedLicense.favorite_word }}</span>
                </div>
              </div>
            </div>

            <div class="license-meta" v-if="selectedLicense.created_at">
              <span>作成日時: {{ formatDate(selectedLicense.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { listLicensesPaginated, listNewLicenses, getEventByCode, type LicenseData } from '@/api/admin'

const inputEventCode = ref('')
const eventCode = ref('')
const eventName = ref('')
const licenses = ref<LicenseData[]>([])
const loading = ref(false)
const error = ref('')
const selectedLicense = ref<LicenseData | null>(null)
const isPolling = ref(false)
let pollingInterval: ReturnType<typeof setInterval> | null = null

// ページング用
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)
const perPage = 20

// 新着件数表示用
const newCount = ref(0)
const maxLicenseId = ref(0)

const loadEvent = async () => {
  if (!inputEventCode.value) return

  loading.value = true
  error.value = ''

  try {
    // イベント情報を取得
    const eventData = await getEventByCode(inputEventCode.value)
    eventCode.value = eventData.event_code
    eventName.value = eventData.name

    // ページング状態をリセット
    currentPage.value = 1
    maxLicenseId.value = 0
    newCount.value = 0

    // 免許証一覧を取得
    await fetchLicenses()

    // ポーリング開始
    startPolling()
  } catch (e: any) {
    const detail = e.response?.data?.detail || ''
    if (detail.includes('無効')) {
      error.value = 'このイベントは現在無効です'
    } else {
      error.value = detail || 'イベントが見つかりませんでした'
    }
  } finally {
    loading.value = false
  }
}

const fetchLicenses = async () => {
  try {
    const data = await listLicensesPaginated(eventCode.value, currentPage.value, perPage)
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
    // 新着をリセット（ページ読み込み時）
    newCount.value = 0
  } catch (e) {
    console.error('免許証一覧の取得に失敗しました', e)
  }
}

const pollNewLicenses = async () => {
  try {
    const data = await listNewLicenses(eventCode.value, maxLicenseId.value)
    totalCount.value = data.total_count

    if (data.items.length > 0) {
      // 新着がある場合
      newCount.value += data.items.length

      // 1ページ目の場合は先頭に追加
      if (currentPage.value === 1) {
        // 新着を先頭に追加
        licenses.value = [...data.items, ...licenses.value]
        // perPage件を超えた分を削除
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
  } catch (e) {
    console.error('新着免許証の取得に失敗しました', e)
  }
}

const startPolling = () => {
  if (pollingInterval) return

  isPolling.value = true
  pollingInterval = setInterval(async () => {
    // 新規データのみをポーリング（効率的）
    await pollNewLicenses()
  }, 5000) // 5秒間隔
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
  loading.value = true
  newCount.value = 0
  try {
    await fetchLicenses()
  } finally {
    loading.value = false
  }
}

const resetEventCode = () => {
  stopPolling()
  eventCode.value = ''
  eventName.value = ''
  licenses.value = []
  inputEventCode.value = ''
  currentPage.value = 1
  totalPages.value = 1
  totalCount.value = 0
  maxLicenseId.value = 0
  newCount.value = 0
}

const openModal = (license: LicenseData) => {
  selectedLicense.value = license
}

const closeModal = () => {
  selectedLicense.value = null
}

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('ja-JP')
}

const printLicense = () => {
  if (!selectedLicense.value) return

  // 非表示のiframeを作成して印刷
  const iframe = document.createElement('iframe')
  iframe.style.position = 'absolute'
  iframe.style.left = '-9999px'
  iframe.style.top = '-9999px'
  iframe.style.width = '0'
  iframe.style.height = '0'
  document.body.appendChild(iframe)

  const iframeDoc = iframe.contentWindow?.document
  if (!iframeDoc) {
    document.body.removeChild(iframe)
    return
  }

  // iframe内にHTML/CSSを書き込み
  iframeDoc.open()
  iframeDoc.write(`
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        @page {
          margin: 0;
          size: 85mm 54mm;
        }
        * {
          margin: 0;
          padding: 0;
          box-sizing: border-box;
        }
        html, body {
          width: 85mm;
          height: 54mm;
          margin: 0;
          padding: 0;
          overflow: hidden;
        }
        img {
          display: block;
          width: 85mm;
          height: 54mm;
          object-fit: contain;
        }
      </style>
    </head>
    <body>
      <img src="${selectedLicense.value.license_image_url}" />
    </body>
    </html>
  `)
  iframeDoc.close()

  // 画像読み込み完了後に印刷
  const img = iframeDoc.querySelector('img')
  if (img) {
    img.onload = () => {
      iframe.contentWindow?.print()
      // 印刷ダイアログが閉じたらiframeを削除
      setTimeout(() => {
        document.body.removeChild(iframe)
      }, 1000)
    }
    // 既にキャッシュされている場合
    if (img.complete) {
      iframe.contentWindow?.print()
      setTimeout(() => {
        document.body.removeChild(iframe)
      }, 1000)
    }
  }
}

onMounted(() => {
  // URLパラメータからイベントコードを取得（オプション）
  const urlParams = new URLSearchParams(window.location.search)
  const code = urlParams.get('code')
  if (code) {
    inputEventCode.value = code
    loadEvent()
  }
})

onUnmounted(() => {
  stopPolling()
})
</script>

<style scoped>
.print-page {
  min-height: 100vh;
  background: #f5f5f5;
}

/* イベントコード入力フォーム */
.event-code-form {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 20px;
}

.form-container {
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 400px;
  width: 100%;
}

.form-container h1 {
  margin: 0 0 10px 0;
  color: #333;
}

.description {
  color: #666;
  margin-bottom: 30px;
}

.input-group {
  display: flex;
  gap: 10px;
}

.event-code-input {
  flex: 1;
  padding: 12px 16px;
  font-size: 16px;
  border: 2px solid #ddd;
  border-radius: 8px;
  outline: none;
  transition: border-color 0.2s;
}

.event-code-input:focus {
  border-color: #4CAF50;
}

.load-button {
  padding: 12px 24px;
  font-size: 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.load-button:hover:not(:disabled) {
  background: #45a049;
}

.load-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.error-message {
  color: #e74c3c;
  margin-top: 15px;
}

/* 免許証一覧 */
.license-list-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 15px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 15px;
}

.header-left h1 {
  margin: 0;
  font-size: 24px;
}

.back-button {
  padding: 8px 16px;
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.back-button:hover {
  background: #f5f5f5;
}

.event-code-badge {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.license-count {
  color: #666;
  font-size: 14px;
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

/* ページネーション */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin: 15px 0;
  padding: 10px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.page-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
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

.loading-spinner {
  text-align: center;
  padding: 60px;
  color: #666;
  font-size: 18px;
}

.empty-state {
  text-align: center;
  padding: 60px;
  background: white;
  border-radius: 12px;
}

.empty-state p {
  margin: 0;
  color: #666;
  font-size: 18px;
}

.empty-hint {
  margin-top: 10px !important;
  font-size: 14px !important;
  color: #999 !important;
}

/* ライセンスグリッド */
.license-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.license-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
}

.license-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.license-card-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 12px;
  font-weight: bold;
  z-index: 1;
}

.license-card img {
  width: 100%;
  aspect-ratio: 16 / 10;
  object-fit: cover;
}

.license-card-info {
  padding: 12px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pet-name {
  font-weight: 600;
  color: #333;
}

.owner-name {
  color: #666;
  font-size: 14px;
}

/* モーダル */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 16px;
  max-width: 900px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

.modal-close {
  position: absolute;
  top: 15px;
  right: 15px;
  background: none;
  border: none;
  font-size: 28px;
  cursor: pointer;
  color: #666;
  z-index: 10;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.modal-close:hover {
  background: #f5f5f5;
}

.modal-body {
  display: flex;
  flex-direction: column;
}

/* 受付番号バッジコンテナ */
.modal-receipt-badge-container {
  text-align: center;
  padding: 20px 20px 10px;
  background: #f9f9f9;
}

.modal-receipt-badge {
  display: inline-block;
  background: linear-gradient(135deg, #ff9a56 0%, #ff6b35 100%);
  color: white;
  padding: 10px 24px;
  border-radius: 25px;
  font-size: 18px;
  font-weight: bold;
}

.modal-image-section {
  padding: 10px 20px;
  background: #f9f9f9;
  display: flex;
  justify-content: center;
}

.modal-image {
  max-width: 100%;
  max-height: 400px;
  object-fit: contain;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.modal-info-section {
  padding: 25px;
}

.modal-info-section h2 {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 24px;
}

.owner-info {
  color: #666;
  margin: 0 0 20px 0;
}

.license-details,
.ai-details {
  background: #f9f9f9;
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 15px;
}

.ai-details {
  background: #e8f5e9;
}

.license-details h3,
.ai-details h3 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.5px;
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
  font-size: 12px;
  color: #888;
}

.detail-value {
  font-size: 15px;
  color: #333;
  font-weight: 500;
}

.license-meta {
  font-size: 12px;
  color: #999;
  margin-bottom: 20px;
}

/* 印刷ボタン（画像のすぐ下） */
.print-actions {
  display: flex;
  justify-content: center;
  padding: 15px 20px 20px;
  background: #f9f9f9;
}

.print-button {
  padding: 14px 60px;
  font-size: 18px;
  background: linear-gradient(135deg, #ff9a56 0%, #ff6b35 100%);
  color: white;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  font-weight: 600;
}

.print-button:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

/* モバイル対応 */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-left {
    flex-wrap: wrap;
  }

  .header-left h1 {
    font-size: 20px;
  }

  .license-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 15px;
  }

  .details-grid {
    grid-template-columns: 1fr;
  }

  .input-group {
    flex-direction: column;
  }

  .form-container {
    padding: 30px 20px;
  }
}
</style>
