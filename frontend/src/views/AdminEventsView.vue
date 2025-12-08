<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import {
  listEvents,
  createEvent,
  getAdminInfo,
  type EventData,
} from '@/api/admin'

const router = useRouter()

const events = ref<EventData[]>([])
const isLoading = ref(true)
const showCreateModal = ref(false)

const newEvent = ref({
  name: '',
  issue_location: '',
  issue_date: new Date().toISOString().split('T')[0],
  auto_issue_date: false,
})

const baseUrl = computed(() => {
  return window.location.origin
})

onMounted(async () => {
  try {
    await getAdminInfo()
    await loadEvents()
  } catch {
    router.push('/admin/login')
  }
})

const loadEvents = async () => {
  isLoading.value = true
  try {
    events.value = await listEvents()
  } catch (err) {
    console.error('Failed to load events:', err)
  } finally {
    isLoading.value = false
  }
}

const handleCreateEvent = async () => {
  try {
    await createEvent({
      name: newEvent.value.name,
      issue_location: newEvent.value.issue_location,
      issue_date: newEvent.value.auto_issue_date ? null : newEvent.value.issue_date,
      auto_issue_date: newEvent.value.auto_issue_date,
    })
    showCreateModal.value = false
    newEvent.value = {
      name: '',
      issue_location: '',
      issue_date: new Date().toISOString().split('T')[0],
      auto_issue_date: false,
    }
    await loadEvents()
  } catch (err) {
    console.error('Failed to create event:', err)
    alert('イベントの作成に失敗しました')
  }
}

const goToDetail = (eventId: number) => {
  router.push(`/admin/events/${eventId}`)
}

const copyEventUrl = (eventCode: string, e: Event) => {
  e.stopPropagation()
  const url = `${baseUrl.value}/event/${eventCode}`
  navigator.clipboard.writeText(url)
  alert('URLをコピーしました')
}

const handleLogout = () => {
  localStorage.removeItem('admin_token')
  router.push('/admin/login')
}

const formatDate = (dateStr: string | null, autoIssueDate: boolean) => {
  if (autoIssueDate || !dateStr) return '自動（アクセス日）'
  const date = new Date(dateStr)
  return date.toLocaleDateString('ja-JP')
}
</script>

<template>
  <div class="admin-container">
    <header class="admin-header">
      <h1>イベント管理</h1>
      <button @click="handleLogout" class="logout-button">ログアウト</button>
    </header>

    <main class="admin-main">
      <div class="actions">
        <button @click="showCreateModal = true" class="create-button">
          + 新規イベント作成
        </button>
      </div>

      <div v-if="isLoading" class="loading">読み込み中...</div>

      <div v-else-if="events.length === 0" class="empty-state">
        <p>イベントがありません</p>
        <p>「新規イベント作成」ボタンからイベントを作成してください</p>
      </div>

      <div v-else class="events-list">
        <div
          v-for="event in events"
          :key="event.id"
          class="event-card"
          @click="goToDetail(event.id)"
        >
          <div class="event-header">
            <h3>{{ event.name }}</h3>
            <span :class="['status-badge', event.is_active ? 'active' : 'inactive']">
              {{ event.is_active ? '有効' : '無効' }}
            </span>
          </div>

          <div class="event-details">
            <p><strong>交付場所:</strong> {{ event.issue_location }}</p>
            <p><strong>交付日:</strong> {{ formatDate(event.issue_date, event.auto_issue_date) }}</p>
            <p><strong>イベントコード:</strong> {{ event.event_code }}</p>
          </div>

          <div class="event-url" @click.stop>
            <input
              type="text"
              :value="`${baseUrl}/event/${event.event_code}`"
              readonly
              class="url-input"
            />
            <button @click="copyEventUrl(event.event_code, $event)" class="copy-button">
              コピー
            </button>
          </div>

          <div class="event-actions">
            <span class="detail-hint">クリックして詳細を表示 &rarr;</span>
          </div>
        </div>
      </div>
    </main>

    <!-- 新規作成モーダル -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <h2>新規イベント作成</h2>
        <form @submit.prevent="handleCreateEvent">
          <div class="form-group">
            <label>イベント名</label>
            <input v-model="newEvent.name" type="text" required />
          </div>
          <div class="form-group">
            <label>交付場所</label>
            <input v-model="newEvent.issue_location" type="text" required />
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input v-model="newEvent.auto_issue_date" type="checkbox" />
              交付日を自動（アクセス日）にする
            </label>
          </div>
          <div v-if="!newEvent.auto_issue_date" class="form-group">
            <label>交付日</label>
            <input v-model="newEvent.issue_date" type="date" required />
          </div>
          <div class="modal-actions">
            <button type="button" @click="showCreateModal = false" class="cancel-button">
              キャンセル
            </button>
            <button type="submit" class="submit-button">作成</button>
          </div>
        </form>
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
  background: linear-gradient(135deg, #ff9a56 0%, #ff6b35 100%);
  color: white;
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.admin-header h1 {
  margin: 0;
  font-size: 24px;
}

.logout-button {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 8px 20px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.3s;
}

.logout-button:hover {
  background: rgba(255, 255, 255, 0.3);
}

.admin-main {
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
}

.actions {
  margin-bottom: 30px;
}

.create-button {
  background: linear-gradient(135deg, #ff9a56 0%, #ff6b35 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.create-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 154, 86, 0.4);
}

.loading,
.empty-state {
  text-align: center;
  padding: 60px;
  color: #666;
}

.empty-state p {
  margin: 10px 0;
}

.events-list {
  display: grid;
  gap: 20px;
}

.event-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.event-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.event-header h3 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
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

.event-details {
  margin-bottom: 16px;
}

.event-details p {
  margin: 8px 0;
  color: #555;
}

.event-url {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.url-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  color: #666;
  background: #f9f9f9;
}

.copy-button {
  background: #ff9a56;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.copy-button:hover {
  background: #e08a4d;
}

.event-actions {
  display: flex;
  justify-content: flex-end;
}

.detail-hint {
  color: #ff9a56;
  font-size: 14px;
  font-weight: 500;
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
  border-color: #ff9a56;
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
  background: linear-gradient(135deg, #ff9a56 0%, #ff6b35 100%);
  color: white;
  border: none;
}

.submit-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(255, 154, 86, 0.4);
}
</style>
