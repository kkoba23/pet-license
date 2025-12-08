<template>
  <div class="home">
    <div v-if="isLoading" class="loading-container">
      <p>読み込み中...</p>
    </div>

    <div v-else-if="eventError" class="error-container">
      <div class="error-card">
        <h2>このURLは現在無効です</h2>
        <p>{{ eventError }}</p>
        <p class="error-hint">
          イベントが終了したか、URLが無効になっています。
        </p>
      </div>
    </div>

    <div v-else class="container">
      <!-- イベント情報バナー（非表示） -->
      <!-- <div class="event-info-banner">
        <h3>{{ eventData?.name }}</h3>
        <p>交付場所: {{ eventData?.issue_location }} / 交付日: {{ displayIssueDate }}</p>
      </div> -->

      <!-- 受付完了画面 -->
      <section v-if="receiptNumber" class="receipt-section">
        <div class="receipt-card">
          <div class="receipt-header">
            <span class="check-icon">&#10003;</span>
            <h2>アップロード完了</h2>
          </div>
          <p class="receipt-message">ペット健康免許証の登録が完了しました</p>
          <div class="receipt-number-box">
            <p class="receipt-label">受付番号</p>
            <p class="receipt-number">{{ receiptNumber }}</p>
          </div>
          <p class="receipt-note">この番号は控えとして保存してください</p>

          <!-- 免許証プレビュー（小さめ） -->
          <div class="receipt-preview">
            <img
              :src="canvasLicenseUrl"
              alt="Pet License"
              class="receipt-license-image"
            />
          </div>

          <div class="receipt-actions">
            <button @click="handleDownload" class="btn btn-download">
              免許証をダウンロード
            </button>
            <button @click="reset" class="btn btn-secondary">
              新しい免許証を作成
            </button>
          </div>

          <!-- iOS用モーダル -->
          <div v-if="showIosModal" class="modal-overlay" @click="showIosModal = false">
            <div class="modal-content" @click.stop>
              <h3>写真アプリに保存</h3>
              <div class="modal-instructions">
                <p>1. 下の画像を<strong>長押し</strong>してください</p>
                <p>2.「"写真"に追加」または「画像を保存」を選択</p>
              </div>
              <img :src="canvasLicenseUrl" alt="Pet License" class="modal-image" />
              <button @click="showIosModal = false" class="btn btn-modal-close">閉じる</button>
            </div>
          </div>
        </div>
      </section>

      <!-- 免許証表示エリア（生成後・受付完了前） -->
      <section v-else-if="canvasLicenseUrl" class="license-section no-header">
        <p class="click-instruction">
          入力内容を変更すると免許証がリアルタイムで更新されます。画像をクリックして編集項目に移動できます。
        </p>
        <div class="license-image-container">
          <img
            ref="licenseImageRef"
            :src="canvasLicenseUrl"
            alt="Pet License"
            class="license-image"
          />
          <!-- クリック可能エリアのオーバーレイ -->
          <div class="click-overlay" :class="{ 'show-hint': showClickHint }">
            <div
              class="click-area pet-name-header"
              @click="scrollToField('pet_name')"
              title="ペット名を編集"
            ></div>
            <div
              class="click-area birth-date"
              @click="scrollToField('birth_date')"
              title="生年月日を編集"
            ></div>
            <div
              class="click-area gender"
              @click="scrollToField('gender')"
              title="性別を編集"
            ></div>
            <div
              class="click-area breed"
              @click="scrollToField('breed')"
              title="種類を編集"
            ></div>
            <div
              class="click-area color"
              @click="scrollToField('color')"
              title="毛色を編集"
            ></div>
            <div
              class="click-area owner-name"
              @click="scrollToField('owner_name')"
              title="飼い主名を編集"
            ></div>
            <div
              class="click-area favorite-word"
              @click="scrollToField('favorite_word')"
              title="お好きな一言を編集"
            ></div>
            <div
              class="click-area microchip"
              @click="scrollToField('microchip_no')"
              title="マイクロチップNoを編集"
            ></div>
            <div
              class="click-area special-notes"
              @click="scrollToField('special_notes')"
              title="特記事項を編集"
            ></div>
          </div>
        </div>

        <div class="license-actions">
          <button
            v-if="!isSaved"
            @click="uploadLicense"
            :disabled="isUploading"
            class="btn btn-upload"
          >
            {{ isUploading ? "アップロード中..." : "免許証をアップロード" }}
          </button>
          <div v-else class="upload-success">
            <span class="success-icon">&#10003;</span> アップロード完了
          </div>
        </div>
      </section>

      <!-- 画像アップロードエリア（未生成時） -->
      <section v-else class="upload-section">
        <!-- 背景に散りばめるサンプル画像 -->
        <div class="floating-pets">
          <img
            v-for="pet in floatingPets"
            :key="pet.id"
            :src="pet.src"
            :style="pet.style"
            class="floating-pet"
            alt=""
          />
        </div>
        <div class="upload-hero">
          <div class="hero-icon">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="64"
              height="64"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
          </div>
          <h2>ペット健康免許証を作成しよう</h2>
          <p class="hero-subtitle">
            かわいいペットの写真をアップロードして、オリジナル免許証を作成
          </p>
        </div>

        <div
          class="upload-area"
          @click="triggerFileInput"
          @drop.prevent="handleDrop"
          @dragover.prevent
        >
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            @change="handleFileSelect"
            style="display: none"
          />
          <div v-if="!previewUrl" class="upload-placeholder">
            <div class="upload-icon">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="48"
                height="48"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
            </div>
            <p class="upload-text">クリックまたはドラッグ&amp;ドロップ</p>
            <p class="upload-hint">ペットの写真を選択してください</p>
          </div>
          <div v-else class="preview-container">
            <img :src="previewUrl" alt="Preview" class="preview-image" />
            <div v-if="isProcessing" class="processing-overlay">
              <div class="spinner"></div>
              <p>{{ processingStatus }}</p>
            </div>
          </div>
        </div>

        <div class="upload-features">
          <div class="feature-item">
            <span class="feature-icon">&#9889;</span>
            <span>AI自動認識</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">&#9998;</span>
            <span>簡単カスタマイズ</span>
          </div>
          <div class="feature-item">
            <span class="feature-icon">&#128190;</span>
            <span>即ダウンロード</span>
          </div>
        </div>
      </section>

      <!-- 入力フォーム（免許証生成後に表示） -->
      <section v-if="canvasLicenseUrl && !receiptNumber" class="form-section">
        <h2>免許証情報を編集</h2>

        <div class="form-grid">
          <div class="form-group" ref="field_pet_name">
            <label>ペット名（氏名欄）</label>
            <input
              v-model="formData.pet_name"
              type="text"
              :placeholder="aiPlaceholders.pet_name || 'ポチ'"
              :class="{
                'ai-placeholder': !formData.pet_name && aiPlaceholders.pet_name,
              }"
            />
          </div>

          <div class="form-group" ref="field_birth_date">
            <label>生年月日</label>
            <input v-model="formData.birth_date" type="date" />
          </div>

          <div class="form-group" ref="field_gender">
            <label>性別</label>
            <select v-model="formData.gender">
              <option value="">選択してください</option>
              <option value="オス">オス</option>
              <option value="メス">メス</option>
            </select>
          </div>

          <div class="form-group" ref="field_breed">
            <label>種類</label>
            <input
              v-model="formData.breed"
              type="text"
              :placeholder="aiPlaceholders.breed || 'ゴールデンレトリバー'"
              :class="{
                'ai-placeholder': !formData.breed && aiPlaceholders.breed,
              }"
            />
          </div>

          <div class="form-group" ref="field_color">
            <label>毛色</label>
            <input
              v-model="formData.color"
              type="text"
              :placeholder="aiPlaceholders.color || 'ブラック'"
              :class="{
                'ai-placeholder': !formData.color && aiPlaceholders.color,
              }"
            />
          </div>

          <div class="form-group" ref="field_owner_name">
            <label>飼い主名（保護者欄）</label>
            <input
              v-model="formData.owner_name"
              type="text"
              :placeholder="aiPlaceholders.owner_name || 'イオンペット 太郎'"
              :class="{
                'ai-placeholder':
                  !formData.owner_name && aiPlaceholders.owner_name,
              }"
            />
          </div>

          <div class="form-group" ref="field_favorite_word">
            <label>お好きな一言（免許の条件等）</label>
            <input
              v-model="formData.favorite_word"
              type="text"
              :placeholder="aiPlaceholders.favorite_word || '元気いっぱい！'"
              :class="{
                'ai-placeholder':
                  !formData.favorite_word && aiPlaceholders.favorite_word,
              }"
            />
          </div>

          <div class="form-group" ref="field_microchip_no">
            <label>マイクロチップNo</label>
            <input
              v-model="formData.microchip_no"
              type="text"
              placeholder="123456789012345"
            />
          </div>
        </div>

        <!-- 特記事項セクション -->
        <div class="special-notes-section" ref="field_special_notes">
          <h3>特記事項（5項目）</h3>
          <div class="special-notes-grid">
            <div
              v-for="(note, index) in formData.special_notes"
              :key="index"
              class="special-note-item"
            >
              <label>特記事項 {{ index + 1 }}</label>
              <div class="special-note-input">
                <select
                  v-model="note.type"
                  @change="onSpecialNoteTypeChange(index)"
                >
                  <option value="">選択してください</option>
                  <option
                    v-for="option in specialNoteOptions"
                    :key="option"
                    :value="option"
                  >
                    {{ option }}
                  </option>
                  <option value="other">その他（自由入力）</option>
                </select>
                <input
                  v-if="note.type === 'other'"
                  v-model="note.custom"
                  type="text"
                  placeholder="自由入力..."
                  class="custom-input"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- AI分析結果 -->
        <div v-if="petInfo" class="pet-info">
          <h3>AI分析結果</h3>
          <p><strong>動物種別:</strong> {{ petInfo.animal_type }}</p>
          <p><strong>品種:</strong> {{ petInfo.breed }}</p>
          <p v-if="petInfo.color"><strong>毛色:</strong> {{ petInfo.color }}</p>
          <p>
            <strong>信頼度:</strong>
            {{ (petInfo.confidence * 100).toFixed(1) }}%
          </p>
          <!-- 追加特徴 -->
          <div v-if="petInfo.extra_features" class="extra-features">
            <p v-if="petInfo.extra_features.expression">
              <strong>表情:</strong> {{ petInfo.extra_features.expression }}
            </p>
            <p v-if="petInfo.extra_features.posture">
              <strong>姿勢:</strong> {{ petInfo.extra_features.posture }}
            </p>
            <p v-if="petInfo.extra_features.fur_amount">
              <strong>毛量/毛質:</strong>
              {{ petInfo.extra_features.fur_amount }}
            </p>
            <p v-if="petInfo.extra_features.size">
              <strong>サイズ:</strong> {{ petInfo.extra_features.size }}
            </p>
            <p v-if="petInfo.extra_features.age_estimate">
              <strong>推定年齢:</strong>
              {{ petInfo.extra_features.age_estimate }}
            </p>
            <p
              v-if="
                petInfo.extra_features.other_traits &&
                petInfo.extra_features.other_traits.length > 0
              "
            >
              <strong>その他:</strong>
              {{ petInfo.extra_features.other_traits.join("、") }}
            </p>
          </div>
        </div>

        <!-- ダウンロード・新規作成ボタン -->
        <div class="form-action-buttons">
          <button @click="handleDownload" class="btn btn-action-full">
            ダウンロード
          </button>
          <button @click="reset" class="btn btn-action-secondary">
            新しく作成
          </button>
        </div>

        <!-- iOS用モーダル -->
        <div v-if="showIosModal" class="modal-overlay" @click="showIosModal = false">
          <div class="modal-content" @click.stop>
            <h3>写真アプリに保存</h3>
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
import { ref, onMounted, computed, watch } from "vue";
import { useRoute } from "vue-router";
import { analyzePet, generateProfile } from "@/api/petLicense";
import { getEventByCode, saveLicense, type PublicEventData } from "@/api/admin";
import { useLicenseCanvas } from "@/composables/useLicenseCanvas";
import type { PetInfo } from "@/types";

const route = useRoute();
const { generateLicenseImage } = useLicenseCanvas();

// サンプル画像のパス
const sampleImages = [
  "/image/sample001.png",
  "/image/sample002.png",
  "/image/sample003.png",
];

// ランダムに散りばめるペット画像データを生成
interface FloatingPet {
  id: number;
  src: string;
  style: {
    left: string;
    top: string;
    width: string;
    transform: string;
    animationDelay: string;
  };
}

const generateFloatingPets = (): FloatingPet[] => {
  // 3枚の画像を右上がりに回転して配置（右側のペット画像部分が見えるように左寄せ）
  // アニメーション: 上から順に開始、2秒以内に完結
  const positions = [
    { left: "10%", top: "35%", rotation: -10, delay: 0.8 },   // 一番下 → 最後
    { left: "0%", top: "12%", rotation: -15, delay: 0.4 },    // 中央 → 2番目
    { left: "-35%", top: "-5%", rotation: -5, delay: 0 },     // 一番上 → 最初
  ];

  return positions.map((pos, i) => ({
    id: i,
    src: sampleImages[i],
    style: {
      left: pos.left,
      top: pos.top,
      width: "420px",
      transform: `rotate(${pos.rotation}deg)`,
      animationDelay: `${pos.delay}s`,
    },
  }));
};

const floatingPets = ref<FloatingPet[]>(generateFloatingPets());

const isLoading = ref(true);
const eventError = ref<string | null>(null);
const eventData = ref<PublicEventData | null>(null);

// 処理状態
const isProcessing = ref(false);
const processingStatus = ref("");
const isUploading = ref(false);

// 交付日の表示（自動の場合は今日の日付）
const displayIssueDate = computed(() => {
  if (!eventData.value) return "";
  if (eventData.value.auto_issue_date || !eventData.value.issue_date) {
    return new Date().toLocaleDateString("ja-JP");
  }
  return new Date(eventData.value.issue_date).toLocaleDateString("ja-JP");
});

// 実際に使用する交付日（自動の場合は今日の日付）
const effectiveIssueDate = computed(() => {
  if (!eventData.value) return new Date().toISOString().split("T")[0];
  if (eventData.value.auto_issue_date || !eventData.value.issue_date) {
    return new Date().toISOString().split("T")[0];
  }
  return eventData.value.issue_date;
});

const fileInput = ref<HTMLInputElement | null>(null);
const selectedFile = ref<File | null>(null);
const previewUrl = ref<string | null>(null);
const petInfo = ref<PetInfo | null>(null);
const canvasLicenseUrl = ref<string | null>(null);
const licenseBlob = ref<Blob | null>(null);
const isSaved = ref(false);
const licenseImageRef = ref<HTMLImageElement | null>(null);
const showClickHint = ref(false);
const showIosModal = ref(false);

// iOSデバイスかどうかを判定（Safari、Chrome、その他すべてのブラウザ）
const isIosDevice = () => {
  // 方法1: User-Agentで判定
  const isIosUserAgent = /iPhone|iPad|iPod/.test(navigator.userAgent) && !(window as any).MSStream;

  // 方法2: iPadOS 13以降はデスクトップモードでUser-Agentが変わるため、追加の判定
  // MacでタッチポイントがあるのはiPadOS
  const isIpadOS = navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1;

  return isIosUserAgent || isIpadOS;
};

// ダウンロード処理
const handleDownload = () => {
  if (!canvasLicenseUrl.value) return;

  if (isIosDevice()) {
    // iOSデバイスの場合はモーダルを表示
    showIosModal.value = true;
  } else {
    // Android/PCの場合は直接ダウンロード
    const link = document.createElement('a');
    link.href = canvasLicenseUrl.value;
    link.download = `${formData.value.pet_name || aiPlaceholders.value.pet_name || 'pet'}_license.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
};

// フォームフィールドのref
const field_owner_name = ref<HTMLElement | null>(null);
const field_pet_name = ref<HTMLElement | null>(null);
const field_birth_date = ref<HTMLElement | null>(null);
const field_gender = ref<HTMLElement | null>(null);
const field_color = ref<HTMLElement | null>(null);
const field_breed = ref<HTMLElement | null>(null);
const field_favorite_word = ref<HTMLElement | null>(null);
const field_microchip_no = ref<HTMLElement | null>(null);
const field_special_notes = ref<HTMLElement | null>(null);

// フィールド名とrefのマッピング
const fieldRefs: Record<string, typeof field_owner_name> = {
  owner_name: field_owner_name,
  pet_name: field_pet_name,
  birth_date: field_birth_date,
  gender: field_gender,
  color: field_color,
  breed: field_breed,
  favorite_word: field_favorite_word,
  microchip_no: field_microchip_no,
  special_notes: field_special_notes,
};

// 特記事項の選択肢
const specialNoteOptions = [
  "もふもふ",
  "つぶらな瞳",
  "マイペース",
  "良く寝る",
  "食欲旺盛",
  "甘えん坊",
  "元気いっぱい",
  "おとなしい",
  "人懐っこい",
  "いたずら好き",
];

interface SpecialNote {
  type: string;
  custom: string;
}

// 特記事項のデフォルト値
const defaultSpecialNotes = [
  "もふもふ",
  "つぶらな瞳",
  "マイペース",
  "良く寝る",
  "食欲旺盛",
];

// 英語色名から日本語への変換マップ
const colorToJapanese: Record<string, string> = {
  // 基本色
  black: "黒",
  white: "白",
  gray: "グレー",
  grey: "グレー",
  brown: "茶",
  red: "赤",
  orange: "オレンジ",
  yellow: "黄",
  gold: "ゴールド",
  cream: "クリーム",
  beige: "ベージュ",
  tan: "タン",
  // ペットに多い色
  olivedrab: "オリーブ茶",
  olive: "オリーブ",
  peru: "茶",
  sienna: "シエナ茶",
  chocolate: "チョコレート",
  saddlebrown: "サドルブラウン",
  rosybrown: "ローズブラウン",
  sandybrown: "サンディブラウン",
  burlywood: "バーリーウッド",
  wheat: "小麦色",
  darkgoldenrod: "ダークゴールド",
  goldenrod: "ゴールデン",
  darkkhaki: "ダークカーキ",
  khaki: "カーキ",
  dimgray: "ダークグレー",
  darkgray: "ダークグレー",
  silver: "シルバー",
  lightgray: "ライトグレー",
  gainsboro: "ゲインズボロ",
  whitesmoke: "ホワイトスモーク",
  snow: "スノー",
  ivory: "アイボリー",
  linen: "リネン",
  antiquewhite: "アンティークホワイト",
  bisque: "ビスク",
  papayawhip: "パパイヤホイップ",
  blanchedalmond: "ブランシュアーモンド",
  navajowhite: "ナバホホワイト",
  moccasin: "モカシン",
  cornsilk: "コーンシルク",
  peachpuff: "ピーチパフ",
  mistyrose: "ミスティローズ",
  lavenderblush: "ラベンダーブラッシュ",
  seashell: "シーシェル",
  floralwhite: "フローラルホワイト",
  mintcream: "ミントクリーム",
  honeydew: "ハニーデュー",
  azure: "アジュール",
  aliceblue: "アリスブルー",
  ghostwhite: "ゴーストホワイト",
  lavender: "ラベンダー",
  slategray: "スレートグレー",
  darkslategray: "ダークスレートグレー",
  lightslategray: "ライトスレートグレー",
};

// 色名を日本語に変換する関数
const convertColorToJapanese = (color: string): string => {
  if (!color) return "";
  const lowerColor = color.toLowerCase().replace(/\s+/g, "");
  return colorToJapanese[lowerColor] || color;
};

const formData = ref({
  owner_name: "",
  pet_name: "",
  birth_date: "",
  gender: "",
  color: "",
  breed: "",
  favorite_food: "",
  favorite_word: "",
  microchip_no: "",
  special_notes: defaultSpecialNotes.map((note) => ({
    type: note,
    custom: "",
  })) as SpecialNote[],
});

// OpenAI生成値をプレースホルダーとして保存
const aiPlaceholders = ref({
  pet_name: "",
  owner_name: "",
  gender: "",
  favorite_word: "",
  breed: "",
  color: "",
});

// 受付番号
const receiptNumber = ref<string | null>(null);

// 特記事項の選択肢変更時の処理
const onSpecialNoteTypeChange = (index: number) => {
  if (formData.value.special_notes[index].type !== "other") {
    formData.value.special_notes[index].custom = "";
  }
};

// 特記事項の値を取得（表示用）
const getSpecialNoteValue = (note: SpecialNote): string => {
  if (note.type === "other") {
    return note.custom || "";
  }
  return note.type || "";
};

// 特記事項の配列を取得
const getSpecialNotesArray = (): string[] => {
  return formData.value.special_notes
    .map((note) => getSpecialNoteValue(note))
    .filter((v) => v);
};

// フォームデータの変更を監視してリアルタイム更新
let updateTimeout: ReturnType<typeof setTimeout> | null = null;
watch(
  formData,
  () => {
    if (!canvasLicenseUrl.value || !petInfo.value) return;

    // デバウンス: 入力が止まってから300ms後に更新
    if (updateTimeout) clearTimeout(updateTimeout);
    updateTimeout = setTimeout(() => {
      regenerateLicense();
    }, 300);
  },
  { deep: true }
);

onMounted(async () => {
  const eventCode = route.params.eventCode as string;
  try {
    eventData.value = await getEventByCode(eventCode);
  } catch (err: any) {
    eventError.value = err.response?.data?.detail || "イベントが見つかりません";
  } finally {
    isLoading.value = false;
  }
});

// 免許証画像クリック時のスクロール処理
const scrollToField = (fieldName: string) => {
  const fieldRef = fieldRefs[fieldName];
  if (fieldRef?.value) {
    fieldRef.value.scrollIntoView({ behavior: "smooth", block: "center" });
    // フィールド内のinput/selectにフォーカス
    const input = fieldRef.value.querySelector("input, select") as HTMLElement;
    if (input) {
      setTimeout(() => input.focus(), 300);
    }
    // ハイライトエフェクト
    fieldRef.value.classList.add("highlight");
    setTimeout(() => fieldRef.value?.classList.remove("highlight"), 1500);
  }
};

const triggerFileInput = () => {
  if (isProcessing.value) return;
  fileInput.value?.click();
};

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    processFile(file);
  }
};

const handleDrop = (event: DragEvent) => {
  if (isProcessing.value) return;
  const file = event.dataTransfer?.files[0];
  if (file) {
    processFile(file);
  }
};

// ファイル選択後、自動でAI分析→免許証生成
const processFile = async (file: File) => {
  selectedFile.value = file;
  previewUrl.value = URL.createObjectURL(file);
  petInfo.value = null;
  canvasLicenseUrl.value = null;
  isSaved.value = false;

  isProcessing.value = true;

  try {
    // Step 1: Clarifai AI分析
    processingStatus.value = "AI分析中...";
    petInfo.value = await analyzePet(file);

    // 種類と毛色をプレースホルダーに設定（フォームは空のまま）
    if (petInfo.value?.color) {
      aiPlaceholders.value.color = convertColorToJapanese(petInfo.value.color);
    }
    if (petInfo.value?.breed) {
      aiPlaceholders.value.breed = petInfo.value.breed;
    }

    // Step 2: OpenAI自動生成
    processingStatus.value = "プロフィール生成中...";
    try {
      // Clarifaiから取得した追加特徴をOpenAIに渡す
      const extraFeatures = petInfo.value.extra_features
        ? {
            expression: petInfo.value.extra_features.expression || undefined,
            posture: petInfo.value.extra_features.posture || undefined,
            fur_amount: petInfo.value.extra_features.fur_amount || undefined,
            size: petInfo.value.extra_features.size || undefined,
            age_estimate:
              petInfo.value.extra_features.age_estimate || undefined,
            other_traits: petInfo.value.extra_features.other_traits || [],
          }
        : undefined;

      const profile = await generateProfile(
        petInfo.value.animal_type,
        petInfo.value.breed,
        petInfo.value.color,
        extraFeatures
      );
      // OpenAI生成値をプレースホルダーに保存（薄いグレーで表示）
      aiPlaceholders.value.gender = profile.gender;
      aiPlaceholders.value.pet_name = profile.pet_name;
      aiPlaceholders.value.owner_name = profile.owner_name;
      aiPlaceholders.value.favorite_word = profile.favorite_word;
      // フォームは空のまま（プレースホルダーとして表示される）
      // 特記事項はプレースホルダーとして設定（選択肢なのでそのまま設定）
      if (profile.special_notes && profile.special_notes.length > 0) {
        formData.value.special_notes = profile.special_notes.map((note) => {
          if (specialNoteOptions.includes(note)) {
            return { type: note, custom: "" };
          } else {
            return { type: "other", custom: note };
          }
        });
      }
    } catch (profileError) {
      console.warn(
        "プロフィール自動生成に失敗しました。デフォルト値を使用します:",
        profileError
      );
      // プロフィール生成に失敗してもデフォルト値で続行
    }

    // Step 3: 免許証生成
    processingStatus.value = "免許証を生成中...";
    await generateLicense();
  } catch (error: any) {
    console.error("処理エラー:", error);
    const errorMessage =
      error?.response?.data?.detail || error?.message || "処理に失敗しました";
    alert(`エラーが発生しました: ${errorMessage}`);
    petInfo.value = null;
  } finally {
    isProcessing.value = false;
    processingStatus.value = "";
  }
};

// 免許証を生成
const generateLicense = async () => {
  if (!selectedFile.value || !petInfo.value || !eventData.value) return;

  const defaultBirthDate = "2020-01-01";

  // プレースホルダー値をフォールバックとして使用
  const effectivePetName =
    formData.value.pet_name || aiPlaceholders.value.pet_name || "ポチ";
  const effectiveOwnerName =
    formData.value.owner_name ||
    aiPlaceholders.value.owner_name ||
    "サンプル 太郎";
  const effectiveGender =
    formData.value.gender || aiPlaceholders.value.gender || "オス";
  const effectiveFavoriteWord =
    formData.value.favorite_word ||
    aiPlaceholders.value.favorite_word ||
    "元気いっぱい！";

  // 種類と毛色もプレースホルダー値をフォールバック
  const effectiveBreed =
    formData.value.breed || aiPlaceholders.value.breed || petInfo.value.breed;
  const effectiveColor =
    formData.value.color ||
    aiPlaceholders.value.color ||
    petInfo.value.color ||
    "ブラック";

  const blob = await generateLicenseImage({
    petImage: selectedFile.value,
    ownerName: effectiveOwnerName,
    petName: effectivePetName,
    breed: effectiveBreed,
    animalType: petInfo.value.animal_type,
    birthDate: formData.value.birth_date || defaultBirthDate,
    color: effectiveColor,
    issueLocation: eventData.value.issue_location,
    issueDate: effectiveIssueDate.value,
    favoriteFood: formData.value.favorite_food || "ささみ",
    favoriteWord: effectiveFavoriteWord,
    microchipNo: formData.value.microchip_no || "123456789012345",
    gender: effectiveGender,
    specialNotes: getSpecialNotesArray(),
  });

  licenseBlob.value = blob;

  // 古いURLを解放
  const isFirstGeneration = !canvasLicenseUrl.value;
  if (canvasLicenseUrl.value) {
    URL.revokeObjectURL(canvasLicenseUrl.value);
  }
  canvasLicenseUrl.value = URL.createObjectURL(blob);

  // 初回生成時のみ5秒間クリックヒントを表示
  if (isFirstGeneration) {
    showClickHint.value = true;
    setTimeout(() => {
      showClickHint.value = false;
    }, 5000);
  }
};

// フォーム変更時の再生成
const regenerateLicense = async () => {
  if (!selectedFile.value || !petInfo.value || !eventData.value) return;

  // 変更があった場合、保存状態をリセット
  isSaved.value = false;

  await generateLicense();
};

// S3にアップロード
const uploadLicense = async () => {
  if (
    !licenseBlob.value ||
    !eventData.value ||
    !petInfo.value ||
    !selectedFile.value
  )
    return;

  isUploading.value = true;
  try {
    // オリジナル画像をBlobに変換
    const originalBlob = await fetch(previewUrl.value!).then((r) => r.blob());

    const response = await saveLicense({
      eventCode: eventData.value.event_code,
      licenseImage: licenseBlob.value,
      originalImage: originalBlob,
      petName:
        formData.value.pet_name || aiPlaceholders.value.pet_name || "ポチ",
      ownerName:
        formData.value.owner_name ||
        aiPlaceholders.value.owner_name ||
        "サンプル 太郎",
      animalType: petInfo.value.animal_type,
      breed:
        formData.value.breed ||
        aiPlaceholders.value.breed ||
        petInfo.value.breed,
      color:
        formData.value.color ||
        aiPlaceholders.value.color ||
        petInfo.value.color,
      birthDate: formData.value.birth_date,
      gender: formData.value.gender || aiPlaceholders.value.gender,
      favoriteFood: formData.value.favorite_food,
      favoriteWord:
        formData.value.favorite_word || aiPlaceholders.value.favorite_word,
      microchipNo: formData.value.microchip_no,
    });

    isSaved.value = true;
    receiptNumber.value = response.receipt_number;
  } catch (error: any) {
    console.error("アップロードエラー:", error);
    alert(`アップロードに失敗しました: ${error.message || "不明なエラー"}`);
  } finally {
    isUploading.value = false;
  }
};

const reset = () => {
  selectedFile.value = null;
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value);
  }
  previewUrl.value = null;
  petInfo.value = null;
  if (canvasLicenseUrl.value) {
    URL.revokeObjectURL(canvasLicenseUrl.value);
  }
  canvasLicenseUrl.value = null;
  licenseBlob.value = null;
  isSaved.value = false;
  showClickHint.value = false;
  formData.value = {
    owner_name: "",
    pet_name: "",
    birth_date: "",
    gender: "",
    color: "",
    breed: "",
    favorite_food: "",
    favorite_word: "",
    microchip_no: "",
    special_notes: defaultSpecialNotes.map((note) => ({
      type: note,
      custom: "",
    })),
  };
  // プレースホルダーもリセット
  aiPlaceholders.value = {
    pet_name: "",
    owner_name: "",
    gender: "",
    favorite_word: "",
    breed: "",
    color: "",
  };
  // 受付番号をリセット
  receiptNumber.value = null;
};
</script>

<style scoped>
.loading-container,
.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  text-align: center;
}

.error-container {
  padding: 40px;
}

.error-card {
  background: #ffebee;
  padding: 40px;
  border-radius: 16px;
  max-width: 500px;
}

.error-card h2 {
  color: #c62828;
  margin: 0 0 16px;
}

.error-card p {
  color: #666;
  margin: 8px 0;
}

.error-card .error-hint {
  color: #999;
  font-size: 14px;
  margin-top: 16px;
}

.event-info-banner {
  background: linear-gradient(135deg, #ff9a56 0%, #ff6b35 100%);
  color: white;
  padding: 16px 24px;
  border-radius: 8px;
  margin-bottom: 2rem;
  text-align: center;
}

.event-info-banner h3 {
  margin: 0 0 8px;
  font-size: 20px;
}

.event-info-banner p {
  margin: 0;
  opacity: 0.9;
}

.home {
  background: #fff5eb;
  min-height: 100vh;
  margin: 0 -1rem;
  width: calc(100% + 2rem);
}

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

/* License Section */
.license-section {
  text-align: center;
}

.click-instruction {
  color: #667eea;
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 8px;
  text-align: center;
}

/* クリック可能な免許証画像コンテナ */
.license-image-container {
  position: relative;
  display: inline-block;
  width: 100%;
  margin-bottom: 1.5rem;
}

.license-image {
  max-width: 100%;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  display: block;
}

/* クリックオーバーレイ */
.click-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

/* クリック可能エリア共通スタイル */
.click-area {
  position: absolute;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s, box-shadow 0.2s;
}

.click-area:hover {
  background-color: rgba(102, 126, 234, 0.2);
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.5);
}

/* 5秒間の光るアニメーション */
.click-overlay.show-hint .click-area {
  animation: glowPulse 1s ease-in-out infinite;
}

@keyframes glowPulse {
  0%,
  100% {
    background-color: rgba(102, 126, 234, 0.1);
    box-shadow: 0 0 0 1px rgba(102, 126, 234, 0.3);
  }
  50% {
    background-color: rgba(102, 126, 234, 0.3);
    box-shadow: 0 0 8px 2px rgba(102, 126, 234, 0.6);
  }
}

/* 免許証レイアウト: 593x350 (100%) */
/* ペット名（氏名欄）エリア (108-379, 12-40) */
.click-area.pet-name-header {
  left: 18.2%;
  top: 3.4%;
  width: 45.7%;
  height: 8%;
}

/* 生年月日エリア (379-570, 12-40) */
.click-area.birth-date {
  left: 63.9%;
  top: 3.4%;
  width: 32.2%;
  height: 8%;
}

/* 性別エリア (27-213, 131-157) */
.click-area.gender {
  left: 4.6%;
  top: 38.3%;
  width: 31.4%;
  height: 5.7%;
}

/* 種類エリア (27-213, 157-177) */
.click-area.breed {
  left: 4.6%;
  top: 44%;
  width: 31.4%;
  height: 5.7%;
}

/* 毛色エリア (27-213, 177-197) */
.click-area.color {
  left: 4.6%;
  top: 50.6%;
  width: 31.4%;
  height: 5.7%;
}

/* 飼い主名（保護者欄）エリア (28-213, 197-220) */
.click-area.owner-name {
  left: 4.7%;
  top: 56.3%;
  width: 31.2%;
  height: 6.6%;
}

/* お好きな一言エリア (98-328, 227-273) */
.click-area.favorite-word {
  left: 16.5%;
  top: 64.9%;
  width: 38.8%;
  height: 13.1%;
}

/* マイクロチップNoエリア (18-356, 298-333) */
.click-area.microchip {
  left: 3%;
  top: 85.1%;
  width: 57%;
  height: 10%;
}

/* 特記事項エリア - 5項目のみ (244-338, 140-218) ヘッダーを除く */
.click-area.special-notes {
  left: 41.1%;
  top: 40%;
  width: 19.5%;
  height: 22.3%;
}

.license-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.upload-success {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #48bb78;
  font-weight: 600;
  font-size: 1.1rem;
}

.success-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: #48bb78;
  color: white;
  border-radius: 50%;
  font-size: 14px;
}

.download-buttons {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

/* Receipt Section - 受付完了画面 */
.receipt-section {
  background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
  text-align: center;
}

.receipt-card {
  background: white;
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.receipt-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 1rem;
}

.receipt-header .check-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
  color: white;
  border-radius: 50%;
  font-size: 24px;
  font-weight: bold;
}

.receipt-header h2 {
  margin: 0;
  color: #2d3748;
  border: none;
  padding: 0;
}

.receipt-message {
  color: #4a5568;
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
}

.receipt-number-box {
  background: linear-gradient(135deg, #ff9a56 0%, #ff6b35 100%);
  border-radius: 12px;
  padding: 1.5rem 2rem;
  margin: 1.5rem auto;
  max-width: 300px;
}

.receipt-label {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
  margin: 0 0 0.5rem;
}

.receipt-number {
  color: white;
  font-size: 2.5rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  margin: 0;
  font-family: "Courier New", monospace;
}

.receipt-note {
  color: #718096;
  font-size: 0.9rem;
  margin-top: 1rem;
}

.receipt-preview {
  margin: 1.5rem 0;
}

.receipt-license-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.receipt-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: center;
  margin-top: 1.5rem;
}

.receipt-actions .btn {
  min-width: 250px;
}

/* Upload Section */
.upload-section {
  background: #fff5eb;
  text-align: center;
  padding: 2rem;
  position: relative;
  overflow: hidden;
  min-height: 100vh;
  margin: 0;
  border-radius: 0;
  box-shadow: none;
}

/* 浮遊するペット画像 */
.floating-pets {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 1;
}

/* テキストの背景オーバーレイ（サンプル画像の上、テキストの下） */
.upload-section::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 245, 235, 0.7);
  z-index: 2;
  pointer-events: none;
}

.floating-pet {
  position: absolute;
  filter: drop-shadow(0 8px 24px rgba(0, 0, 0, 0.5));
  border-radius: 8px;
  animation: slideUpFade 0.5s ease-out forwards;
  opacity: 0;
}

/* アニメーションdelayはインラインスタイルで個別に設定 */

@keyframes slideUpFade {
  from {
    opacity: 0;
    translate: 0 150px;
  }
  to {
    opacity: 0.9;
    translate: 0 0;
  }
}

.upload-hero {
  margin-bottom: 2rem;
  position: relative;
  z-index: 3;
}

.hero-icon {
  color: #333;
  margin-bottom: 1rem;
}

.upload-section h2 {
  color: #333;
  border: none;
  font-size: 1.75rem;
  margin-bottom: 0.5rem;
}

.hero-subtitle {
  color: #555;
  font-size: 1rem;
  margin: 0;
}

.upload-area {
  background: white;
  border: 3px dashed #ddd;
  border-radius: 16px;
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 3;
}

.upload-area:hover {
  border-color: #ff9a56;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.upload-icon {
  color: #ff9a56;
  margin-bottom: 1rem;
}

.upload-text {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  margin: 0 0 0.5rem;
}

.upload-hint {
  color: #888;
  font-size: 0.9rem;
  margin: 0;
}

.upload-features {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-top: 1.5rem;
  position: relative;
  z-index: 3;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #333;
  font-size: 0.9rem;
}

.feature-icon {
  font-size: 1.2rem;
}

.preview-container {
  position: relative;
  width: 100%;
}

.preview-image {
  max-width: 100%;
  max-height: 400px;
  border-radius: 8px;
}

.processing-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: white;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Form Section */
.form-section {
  margin-top: 0;
}

.form-hint {
  color: #666;
  font-size: 14px;
  margin-bottom: 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.form-group {
  margin-bottom: 0;
  transition: background-color 0.3s, box-shadow 0.3s;
  padding: 0.5rem;
  margin: -0.5rem;
  border-radius: 8px;
}

/* ハイライトエフェクト */
.form-group.highlight {
  background-color: rgba(102, 126, 234, 0.15);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.4);
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
}

/* AIプレースホルダー（薄いグレー） */
.form-group input::placeholder {
  color: #999;
  opacity: 1;
}

.form-group input.ai-placeholder::placeholder {
  color: #667eea;
  font-style: italic;
  opacity: 0.7;
}

.readonly-group .readonly-input {
  background: #f5f5f5;
  color: #666;
  cursor: not-allowed;
}

.pet-info {
  background: #f0f4ff;
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1.5rem;
}

.pet-info h3 {
  margin-top: 0;
  margin-bottom: 0.5rem;
  font-size: 1rem;
  border-bottom: none;
  padding-bottom: 0;
}

.pet-info p {
  margin: 0.25rem 0;
  font-size: 0.9rem;
}

.pet-info .extra-features {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px dashed #ccc;
}

/* 特記事項セクション */
.special-notes-section {
  margin-top: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  transition: background-color 0.3s, box-shadow 0.3s;
}

.special-notes-section.highlight {
  background-color: rgba(102, 126, 234, 0.15);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.4);
}

.special-notes-section h3 {
  margin: 0 0 1rem;
  font-size: 1rem;
  color: #333;
  border-bottom: 1px solid #ddd;
  padding-bottom: 0.5rem;
}

.special-notes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.special-note-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.special-note-item label {
  font-weight: 600;
  font-size: 0.9rem;
  color: #555;
}

.special-note-input {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.special-note-input select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
  background: white;
}

.special-note-input .custom-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #667eea;
  border-radius: 4px;
  font-size: 1rem;
  box-sizing: border-box;
  background: #f0f4ff;
}

.special-note-input .custom-input:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.3);
}

/* Buttons */
.btn {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-upload {
  background: #48bb78;
  color: white;
  width: 100%;
  max-width: 300px;
  font-size: 1.1rem;
  padding: 1rem 2rem;
}

.btn-upload:hover {
  background: #38a169;
}

.btn-secondary {
  background: #718096;
  color: white;
}

.btn-secondary:hover {
  background: #4a5568;
}

/* フォーム下のアクションボタン */
.form-action-buttons {
  margin-top: 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.btn-action-full {
  background: #4299e1;
  color: white;
  width: 100%;
  max-width: 300px;
  font-size: 1.1rem;
  padding: 1rem 2rem;
  margin: 0 auto;
}

.btn-action-full:hover {
  background: #3182ce;
}

.btn-action-secondary {
  background: #718096;
  color: white;
  width: 100%;
  max-width: 300px;
  font-size: 1.1rem;
  padding: 1rem 2rem;
  margin: 0 auto;
}

.btn-action-secondary:hover {
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

@media (max-width: 768px) {
  .container {
    padding: 0;
  }

  section {
    padding: 1rem;
    margin-bottom: 1rem;
    border-radius: 0;
    box-shadow: none;
  }

  h2 {
    font-size: 1.25rem;
  }

  /* アップロードエリアを横幅いっぱいに */
  .upload-section {
    padding: 1.5rem 1rem;
  }

  .upload-section h2 {
    font-size: 1.4rem;
  }

  .hero-subtitle {
    font-size: 0.9rem;
  }

  .upload-area {
    min-height: 200px;
    padding: 2rem 1rem;
    border-radius: 12px;
  }

  .upload-text {
    display: none;
  }

  .upload-features {
    flex-direction: column;
    gap: 0.75rem;
  }

  .preview-image {
    max-height: none;
    width: 100%;
  }

  /* 受付完了画面 */
  .receipt-section {
    padding: 1.5rem 1rem;
  }

  .receipt-card {
    padding: 1.5rem 1rem;
  }

  .receipt-number {
    font-size: 2rem;
  }

  .receipt-actions .btn {
    min-width: auto;
    width: 100%;
  }

  /* 免許証画像を横幅いっぱいに */
  .license-section {
    padding: 0.25rem;
  }

  .license-section.no-header {
    padding: 0;
    background: transparent;
  }

  .license-image {
    width: 100%;
    border-radius: 0;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-group input,
  .form-group select {
    font-size: 16px;
  }

  .btn {
    width: 100%;
    padding: 0.875rem;
  }

  .download-buttons {
    flex-direction: column;
    width: 100%;
  }

  .btn-download {
    text-align: center;
  }
}
</style>
