<template>
  <div class="home">
    <div class="container">
      <section class="upload-section">
        <h2>ペット画像をアップロード</h2>
        <div class="upload-area" @click="triggerFileInput" @drop.prevent="handleDrop" @dragover.prevent>
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            @change="handleFileSelect"
            style="display: none"
          />
          <div v-if="!previewUrl" class="upload-placeholder">
            <p>クリックまたはドラッグ&ドロップで画像を選択</p>
          </div>
          <img v-else :src="previewUrl" alt="Preview" class="preview-image" />
        </div>

        <button v-if="selectedFile && !petInfo" @click="analyzeImage" :disabled="analyzing" class="btn btn-primary">
          {{ analyzing ? '分析中...' : 'AI分析を実行' }}
        </button>

        <div v-if="petInfo" class="pet-info">
          <h3>AI分析結果</h3>
          <p><strong>動物種別:</strong> {{ petInfo.animal_type }}</p>
          <p><strong>品種:</strong> {{ petInfo.breed }}</p>
          <p v-if="petInfo.color"><strong>毛色:</strong> {{ petInfo.color }}</p>
          <p><strong>信頼度:</strong> {{ (petInfo.confidence * 100).toFixed(1) }}%</p>
        </div>
      </section>

      <section v-if="petInfo" class="form-section">
        <h2>免許証情報を入力</h2>
        <form @submit.prevent="generateLicenseCanvas">
          <div class="form-group">
            <label>飼い主名</label>
            <input v-model="formData.owner_name" type="text" placeholder="イオンペット 太郎" />
          </div>

          <div class="form-group">
            <label>ペット名</label>
            <input v-model="formData.pet_name" type="text" placeholder="イオンペット" />
          </div>

          <div class="form-group">
            <label>交付場所</label>
            <input v-model="formData.issue_location" type="text" placeholder="上野恩賜公園" />
          </div>

          <div class="form-group">
            <label>交付日</label>
            <input v-model="formData.issue_date" type="date" />
          </div>

          <div class="form-group">
            <label>生年月日</label>
            <input v-model="formData.birth_date" type="date" />
          </div>

          <div class="form-group">
            <label>性別</label>
            <select v-model="formData.gender">
              <option value="">選択してください</option>
              <option value="オス">オス</option>
              <option value="メス">メス</option>
            </select>
          </div>

          <div class="form-group">
            <label>毛色</label>
            <input v-model="formData.color" type="text" placeholder="ブラック" />
          </div>

          <div class="form-group">
            <label>好きな食べ物</label>
            <input v-model="formData.favorite_food" type="text" placeholder="ささみ" />
          </div>

          <div class="form-group">
            <label>お好きな一言</label>
            <input v-model="formData.favorite_word" type="text" placeholder="元気いっぱい！" />
          </div>

          <div class="form-group">
            <label>マイクロチップNo</label>
            <input v-model="formData.microchip_no" type="text" placeholder="123456789012345" />
          </div>

          <button type="submit" :disabled="generating" class="btn btn-success">
            {{ generating ? '生成中...' : '免許証を生成' }}
          </button>
        </form>
      </section>

      <section v-if="canvasLicenseUrl" class="result-section">
        <h2>生成された免許証</h2>
        <img :src="canvasLicenseUrl" alt="Pet License" class="license-image" />
        <div class="download-buttons">
          <button @click="handleDownload" class="btn btn-download">ダウンロード</button>
          <button @click="reset" class="btn btn-secondary">新しく作成</button>
        </div>

        <!-- iOS用モーダル -->
        <div v-if="showIosModal" class="modal-overlay" @click="showIosModal = false">
          <div class="modal-content" @click.stop>
            <h3>📱 写真アプリに保存</h3>
            <div class="modal-instructions">
              <p>1. 下の画像を<strong>長押し</strong>してください</p>
              <p>2.「"写真"に追加」または「画像を保存」を選択</p>
            </div>
            <img :src="canvasLicenseUrl" alt="Pet License" class="modal-image" />
            <button @click="showIosModal = false" class="btn btn-modal-close">閉じる</button>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { analyzePet } from '@/api/petLicense'
import { useLicenseCanvas } from '@/composables/useLicenseCanvas'
import type { PetInfo } from '@/types'

const { generateLicenseImage } = useLicenseCanvas()

const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const previewUrl = ref<string | null>(null)
const petInfo = ref<PetInfo | null>(null)
const analyzing = ref(false)
const generating = ref(false)
const canvasLicenseUrl = ref<string | null>(null)
const showIosModal = ref(false)

// iOSデバイスかどうかを判定（Safari、Chrome、その他すべてのブラウザ）
const isIosDevice = () => {
  // 方法1: User-Agentで判定
  const isIosUserAgent = /iPhone|iPad|iPod/.test(navigator.userAgent) && !(window as any).MSStream

  // 方法2: iPadOS 13以降はデスクトップモードでUser-Agentが変わるため、追加の判定
  // MacでタッチポイントがあるのはiPadOS
  const isIpadOS = navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1

  return isIosUserAgent || isIpadOS
}

const formData = ref({
  owner_name: '',
  pet_name: '',
  birth_date: '',
  issue_location: '',
  issue_date: new Date().toISOString().split('T')[0],
  gender: '',
  color: '',
  favorite_food: '',
  favorite_word: '',
  microchip_no: ''
})

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    processFile(file)
  }
}

const handleDrop = (event: DragEvent) => {
  const file = event.dataTransfer?.files[0]
  if (file) {
    processFile(file)
  }
}

const processFile = (file: File) => {
  selectedFile.value = file
  previewUrl.value = URL.createObjectURL(file)
  petInfo.value = null
  canvasLicenseUrl.value = null
}

const analyzeImage = async () => {
  if (!selectedFile.value) return

  analyzing.value = true
  try {
    petInfo.value = await analyzePet(selectedFile.value)

    // 毛色が検出された場合、フォームに自動入力
    if (petInfo.value?.color) {
      formData.value.color = petInfo.value.color
    }
  } catch (error: any) {
    console.error('AI分析エラー:', error)
    const errorMessage = error?.response?.data?.detail || error?.message || 'AI分析に失敗しました'
    alert(`エラーが発生しました: ${errorMessage}`)
    petInfo.value = null
  } finally {
    analyzing.value = false
  }
}

const generateLicenseCanvas = async () => {
  if (!selectedFile.value || !petInfo.value) return

  generating.value = true
  try {
    // デフォルト値の設定
    const defaultBirthDate = '2020-01-01'
    const defaultIssueDate = new Date().toISOString().split('T')[0]

    // Canvas APIで免許証を生成
    const blob = await generateLicenseImage({
      petImage: selectedFile.value,
      ownerName: formData.value.owner_name || 'サンプル 太郎',
      petName: formData.value.pet_name || 'ポチ',
      breed: petInfo.value.breed,
      animalType: petInfo.value.animal_type,
      birthDate: formData.value.birth_date || defaultBirthDate,
      color: formData.value.color || petInfo.value.color || 'ブラック',
      issueLocation: formData.value.issue_location || '東京都',
      issueDate: formData.value.issue_date || defaultIssueDate,
      favoriteFood: formData.value.favorite_food || 'ささみ',
      favoriteWord: formData.value.favorite_word || '元気いっぱい！',
      microchipNo: formData.value.microchip_no || '123456789012345'
    })

    // BlobからURLを生成
    canvasLicenseUrl.value = URL.createObjectURL(blob)
  } catch (error: any) {
    console.error('免許証生成エラー:', error)
    alert(`免許証生成に失敗しました: ${error.message || '不明なエラー'}`)
  } finally {
    generating.value = false
  }
}

const handleDownload = () => {
  if (!canvasLicenseUrl.value) return

  if (isIosDevice()) {
    // iOSデバイスの場合はモーダルを表示
    showIosModal.value = true
  } else {
    // Android/PCの場合は直接ダウンロード
    const link = document.createElement('a')
    link.href = canvasLicenseUrl.value
    link.download = `${formData.value.pet_name || 'pet'}_license.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
}

const reset = () => {
  selectedFile.value = null
  previewUrl.value = null
  petInfo.value = null
  canvasLicenseUrl.value = null
  formData.value = {
    owner_name: '',
    pet_name: '',
    birth_date: '',
    issue_location: '',
    issue_date: new Date().toISOString().split('T')[0],
    gender: '',
    color: '',
    favorite_food: '',
    favorite_word: '',
    microchip_no: ''
  }
}
</script>

<style scoped>
.container {
  max-width: 800px;
  margin: 0 auto;
}

section {
  background: white;
  padding: 2rem;
  margin-bottom: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

h2 {
  margin-top: 0;
  color: #333;
  border-bottom: 2px solid #667eea;
  padding-bottom: 0.5rem;
}

.upload-area {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.3s;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-area:hover {
  border-color: #667eea;
}

.preview-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
}

.pet-info {
  background: #f0f4ff;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.required {
  color: red;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.btn {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 1rem;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5568d3;
}

.btn-success {
  background: #48bb78;
  color: white;
  width: 100%;
}

.btn-success:hover {
  background: #38a169;
}

.btn-secondary {
  background: #718096;
  color: white;
}

.btn-secondary:hover {
  background: #4a5568;
}

.btn-download {
  background: #4299e1;
  color: white;
  text-decoration: none;
  display: inline-block;
}

.btn-download:hover {
  background: #3182ce;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.license-image {
  max-width: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
}

.download-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

/* レスポンシブデザイン */
@media (max-width: 768px) {
  .container {
    padding: 0 1rem;
  }

  section {
    padding: 1rem;
  }

  h2 {
    font-size: 1.25rem;
  }

  .upload-area {
    min-height: 150px;
    padding: 1rem;
  }

  .form-group input,
  .form-group select {
    font-size: 16px; /* iOSのズーム防止 */
  }

  .btn {
    width: 100%;
    padding: 0.875rem;
  }

  .download-buttons {
    flex-direction: column;
  }

  .btn-download {
    text-align: center;
  }
}

@media (max-width: 480px) {
  .license-image {
    max-width: 100%;
    height: auto;
  }

  .pet-info p {
    font-size: 0.9rem;
  }
}

/* iOS用モーダル */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  max-width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  text-align: center;
}

.modal-content h3 {
  margin-top: 0;
  color: #333;
  font-size: 1.2rem;
}

.modal-content p {
  color: #666;
  margin-bottom: 1rem;
  line-height: 1.6;
}

.modal-image {
  max-width: 100%;
  max-height: 50vh;
  border-radius: 8px;
  margin-bottom: 1rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.modal-instructions {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.modal-instructions p {
  margin: 0.5rem 0;
  text-align: left;
}

.btn-modal-close {
  background: #6c757d;
  color: white;
  width: 100%;
  margin-top: 0.5rem;
}

.btn-modal-close:hover {
  background: #5a6268;
}
</style>
