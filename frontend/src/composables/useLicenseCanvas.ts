interface CanvasLicenseData {
  petImage: File
  ownerName: string
  petName: string
  breed: string
  animalType: string
  birthDate: string
  color: string
  issueLocation: string
  issueDate: string
  favoriteFood?: string
  favoriteWord?: string
  microchipNo?: string
  specialNotes?: string[]
  gender?: string
}

export function useLicenseCanvas() {
  const generateLicenseImage = async (data: CanvasLicenseData): Promise<Blob> => {
    return new Promise((resolve, reject) => {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')

      if (!ctx) {
        reject(new Error('Canvas context not available'))
        return
      }

      // Figmaデザイン基準: 593 x 350 をスケールアップ (1.5倍)
      const scale = 1.5
      const baseWidth = 593
      const baseHeight = 350
      const width = Math.round(baseWidth * scale)  // 890
      const height = Math.round(baseHeight * scale) // 525
      canvas.width = width
      canvas.height = height

      // スケール適用関数
      const s = (n: number) => Math.round(n * scale)

      // 角丸の外枠を描画する関数
      const drawRoundRect = (x: number, y: number, w: number, h: number, r: number, fill = false, stroke = true) => {
        ctx.beginPath()
        ctx.moveTo(x + r, y)
        ctx.lineTo(x + w - r, y)
        ctx.arcTo(x + w, y, x + w, y + r, r)
        ctx.lineTo(x + w, y + h - r)
        ctx.arcTo(x + w, y + h, x + w - r, y + h, r)
        ctx.lineTo(x + r, y + h)
        ctx.arcTo(x, y + h, x, y + h - r, r)
        ctx.lineTo(x, y + r)
        ctx.arcTo(x, y, x + r, y, r)
        ctx.closePath()
        if (fill) ctx.fill()
        if (stroke) ctx.stroke()
      }

      // 線の設定
      ctx.lineJoin = 'miter'
      ctx.lineCap = 'butt'

      // === 背景カード (Rectangle 2) ===
      // Position: (0, 0), Size: 593 x 350, Corner: 20, Fill: #edecde
      ctx.fillStyle = '#edecde'
      drawRoundRect(0, 0, width, height, s(20), true, false)
      ctx.strokeStyle = '#c9c9c9'
      ctx.lineWidth = s(0.5)
      drawRoundRect(0, 0, width, height, s(20), false, true)

      // === 内部の白い枠 (Rectangle 6) ===
      // Position: (14, 47), Size: 565 x 291, Corner: 14, Fill: white
      ctx.fillStyle = '#ffffff'
      ctx.strokeStyle = '#000000'
      ctx.lineWidth = s(1)
      drawRoundRect(s(14), s(47), s(565), s(291), s(14), true, true)

      // === 氏名バー (Rectangle 1) ===
      // Position: (14, 12), Size: 565 x 28, Corner: 28, Fill: white
      ctx.fillStyle = '#ffffff'
      ctx.strokeStyle = '#000000'
      ctx.lineWidth = s(1)
      drawRoundRect(s(14), s(12), s(565), s(28), s(14), true, true)

      // === 氏名バーの縦線 (Line 1, Line 2) ===
      ctx.beginPath()
      ctx.moveTo(s(93), s(12))
      ctx.lineTo(s(93), s(40))
      ctx.stroke()

      ctx.beginPath()
      ctx.moveTo(s(379), s(12))
      ctx.lineTo(s(379), s(40))
      ctx.stroke()

      // === 氏名テキスト ===
      ctx.fillStyle = '#000000'
      ctx.font = `${s(18)}px "Noto Sans JP", sans-serif`
      ctx.textAlign = 'left'
      ctx.textBaseline = 'middle'
      ctx.letterSpacing = `${s(7.38)}px`
      ctx.fillText('氏名', s(32), s(26))
      ctx.letterSpacing = '0px'

      // === 氏名の値（ペット名） ===
      ctx.font = `${s(18)}px "Noto Sans JP", sans-serif`
      ctx.fillText(data.petName, s(108), s(26))

      // === 生年月日 ===
      const birthYear = data.birthDate.substring(0, 4)
      const birthMonth = data.birthDate.substring(5, 7)
      const birthDay = data.birthDate.substring(8, 10)
      const birthReiwa = parseInt(birthYear) - 2018
      const birthDateFormatted = `令和${birthReiwa < 10 ? '0' + birthReiwa : birthReiwa}年${birthMonth}月${birthDay}日`

      ctx.font = `${s(13)}px "Noto Sans JP", sans-serif`
      ctx.fillText(birthDateFormatted, s(390), s(26))

      ctx.fillText('生', s(555), s(26))

      // === 交付場所/交付の横線 (Line 3) ===
      ctx.beginPath()
      ctx.moveTo(s(14), s(73))
      ctx.lineTo(s(579), s(73))
      ctx.stroke()

      // === 交付場所/交付の縦線 (Line 4) ===
      ctx.beginPath()
      ctx.moveTo(s(93), s(47))
      ctx.lineTo(s(93), s(100))
      ctx.stroke()

      // === 交付場所テキスト ===
      ctx.font = `${s(12)}px "Noto Sans JP", sans-serif`
      ctx.fillText('交付場所', s(30), s(60))
      ctx.fillText(data.issueLocation, s(98), s(60))

      // === 交付テキスト ===
      ctx.fillText('交付', s(45), s(86))

      const issueYear = data.issueDate.substring(0, 4)
      const issueMonth = data.issueDate.substring(5, 7)
      const issueDay = data.issueDate.substring(8, 10)
      const reiwaYear = parseInt(issueYear) - 2018
      const issueDateFormatted = `令和${reiwaYear < 10 ? '0' + reiwaYear : reiwaYear}年${issueMonth}月${issueDay}日`
      ctx.fillText(issueDateFormatted, s(98), s(86))

      // === 有効期限バー (Rectangle 5) ===
      // Position: (15, 100), Size: 343 x 31, Fill: #699428
      ctx.fillStyle = '#699428'
      ctx.fillRect(s(15), s(100), s(343), s(31))

      // === 有効期限テキスト（緑バーいっぱいに） ===
      const expiryYear = parseInt(issueYear) + 3
      const expiryReiwa = expiryYear - 2018
      const expiryFormatted = `${expiryYear}年（令和${expiryReiwa < 10 ? '0' + expiryReiwa : expiryReiwa}年）${issueMonth}月${issueDay}日まで有効`

      ctx.fillStyle = '#000000'
      // テキストを緑バーの幅に合わせてスケーリング
      ctx.save()
      const barWidth = s(343) - s(10) // バーの幅からパディングを引く
      ctx.font = `bold ${s(18)}px "Noto Sans JP", sans-serif`
      const textWidth = ctx.measureText(expiryFormatted).width
      const scaleX = Math.min(barWidth / textWidth, 1.0)
      ctx.translate(s(20), s(116))
      ctx.scale(scaleX, 1)
      ctx.fillText(expiryFormatted, 0, 0)
      ctx.restore()

      // === ペット情報エリアの横線 ===
      ctx.strokeStyle = '#000000'
      ctx.lineWidth = s(1)

      // Line 6: Position: (27, 157)
      ctx.beginPath()
      ctx.moveTo(s(27), s(157))
      ctx.lineTo(s(213), s(157))
      ctx.stroke()

      // Line 7: Position: (27, 177)
      ctx.beginPath()
      ctx.moveTo(s(27), s(177))
      ctx.lineTo(s(213), s(177))
      ctx.stroke()

      // Line 8: Position: (27, 197)
      ctx.beginPath()
      ctx.moveTo(s(27), s(197))
      ctx.lineTo(s(213), s(197))
      ctx.stroke()

      // Line 9: Position: (27, 220)
      ctx.beginPath()
      ctx.moveTo(s(27), s(220))
      ctx.lineTo(s(213), s(220))
      ctx.stroke()

      // === ペット情報テキスト ===
      ctx.font = `${s(12)}px "Noto Sans JP", sans-serif`
      ctx.fillStyle = '#000000'

      // 性別
      ctx.fillText('性別　：', s(27), s(147))
      ctx.fillText(data.gender || 'オス', s(87), s(147))

      // 種類
      ctx.fillText('種類　：', s(27), s(167))
      ctx.fillText(data.breed || 'ミックス', s(87), s(167))

      // 毛色
      ctx.fillText('毛色　：', s(27), s(187))
      ctx.fillText(data.color || 'ブラック', s(87), s(187))

      // 保護者（飼い主名）
      ctx.fillText('保護者：', s(28), s(209))
      ctx.fillText(data.ownerName || 'イオンペット', s(89), s(209))

      // === 免許の条件等エリア (Rectangle 4) ===
      // Position: (23, 227), Size: 57 x 50, Corner: 10
      ctx.strokeStyle = '#000000'
      ctx.lineWidth = s(0.5)
      drawRoundRect(s(23), s(227), s(57), s(50), s(10), false, true)

      ctx.font = `${s(12)}px "Noto Sans JP", sans-serif`
      ctx.textAlign = 'center'
      ctx.fillText('免許の', s(52), s(244))
      ctx.fillText('条件等', s(52), s(264))
      ctx.textAlign = 'left'

      // === お好きな一言エリア ===
      // Line 5: Position: (98, 273)
      ctx.beginPath()
      ctx.moveTo(s(98), s(273))
      ctx.lineTo(s(328), s(273))
      ctx.stroke()

      ctx.font = `bold ${s(17)}px "Noto Sans JP", sans-serif`
      ctx.textAlign = 'center'
      ctx.fillText(data.favoriteWord || 'お好きな一言', s(213), s(255))
      ctx.textAlign = 'left'

      // === マイクロチップNo.テキスト ===
      ctx.font = `${s(10)}px "Noto Sans JP", sans-serif`
      ctx.fillText('マイクロチップNo.', s(23), s(290))

      // === 番号バー (Rectangle 8) ===
      // Position: (18, 298), Size: 338 x 35, Corner: 10
      ctx.strokeStyle = '#000000'
      ctx.lineWidth = s(1)
      drawRoundRect(s(18), s(298), s(338), s(35), s(10), false, true)

      ctx.font = `${s(14)}px "Noto Sans JP", sans-serif`
      ctx.fillText('第', s(25), s(316))

      ctx.font = `bold ${s(16)}px "Noto Sans JP", sans-serif`
      ctx.fillText(data.microchipNo || '012345678900', s(50), s(316))

      ctx.font = `${s(14)}px "Noto Sans JP", sans-serif`
      ctx.fillText('号', s(320), s(316))

      // === ペット免許証 縦書き ===
      // Position: (358, 100), Size: 35 x 195, Fill: #699428
      ctx.fillStyle = '#699428'
      ctx.textAlign = 'center'

      const verticalText = ['ペ', 'ッ', 'ト', '免', '許', '証']
      let yPos = s(120)
      const xPos = s(375)

      // 「ペット」は26px、「免許証」は23pxで描画
      verticalText.forEach((char, index) => {
        const fontSize = index < 3 ? s(26) : s(23)
        ctx.font = `${fontSize}px "Noto Sans JP", sans-serif`
        ctx.fillText(char, xPos, yPos)
        yPos += s(27)
      })

      // === 特記事項の縦書き枠 ===
      // Rectangle 10-14: Position starts at (221, 140), each 23.4 x 78
      const specialBoxStartX = s(221)
      const specialBoxY = s(140)
      const specialBoxWidth = s(23.4)
      const specialBoxHeight = s(78)

      ctx.strokeStyle = '#000000'
      ctx.lineWidth = s(0.5)

      // 特記事項ヘッダー
      ctx.fillStyle = '#ffb9b9'
      ctx.fillRect(specialBoxStartX, specialBoxY, specialBoxWidth, specialBoxHeight)
      ctx.strokeRect(specialBoxStartX, specialBoxY, specialBoxWidth, specialBoxHeight)

      // 残りの枠
      for (let i = 1; i < 6; i++) {
        ctx.strokeRect(specialBoxStartX + specialBoxWidth * i, specialBoxY, specialBoxWidth, specialBoxHeight)
      }

      // 特記事項テキスト（縦書き、5文字以上は圧縮）
      ctx.fillStyle = '#000000'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'

      // 特記事項は5項目まで（未入力はデフォルト値を使用）
      const defaultNotes = ['もふもふ', 'つぶらな瞳', 'マイペース', '良く寝る', '食欲旺盛']
      const userNotes = data.specialNotes || []
      const specialLabels = ['特記事項', ...defaultNotes.map((def, i) => userNotes[i] || def)]
      const baseCharHeight = 4 // 4文字分の基準高さ

      // 縦書き用の長音符変換（ー → ｜）
      const verticalChar = (char: string) => {
        if (char === 'ー' || char === '-' || char === '－') {
          return '｜'
        }
        return char
      }

      specialLabels.forEach((label, i) => {
        const boxCenterX = specialBoxStartX + specialBoxWidth * i + specialBoxWidth / 2
        const chars = label.split('')
        const charCount = chars.length

        // 4文字を基準として、それ以上は圧縮
        const availableHeight = specialBoxHeight - s(10) // 上下パディング
        const charSpacing = charCount > baseCharHeight
          ? availableHeight / charCount
          : s(15)

        // フォントサイズも文字数に応じて調整
        const fontSize = charCount > baseCharHeight
          ? s(12) * (baseCharHeight / charCount)
          : s(12)

        ctx.font = `${fontSize}px "Noto Sans JP", sans-serif`

        // 縦書きの開始位置を中央揃えに
        const totalTextHeight = charSpacing * (charCount - 1)
        let charY = specialBoxY + (specialBoxHeight - totalTextHeight) / 2

        chars.forEach(char => {
          ctx.fillText(verticalChar(char), boxCenterX, charY)
          charY += charSpacing
        })
      })

      // ペット画像を読み込んで描画
      const reader = new FileReader()
      reader.onload = (e) => {
        const img = new Image()
        img.onload = () => {
          // === 写真エリア (Rectangle 7) ===
          // Position: (393, 81), Size: 176 x 217, Fill: #d9d9d9
          const imgX = s(393)
          const imgY = s(81)
          const imgWidth = s(176)
          const imgHeight = s(217)

          // 写真の背景
          ctx.fillStyle = '#d9d9d9'
          ctx.fillRect(imgX, imgY, imgWidth, imgHeight)

          // アスペクト比を維持して画像を描画
          const imgScale = Math.max(imgWidth / img.width, imgHeight / img.height)
          const scaledWidth = img.width * imgScale
          const scaledHeight = img.height * imgScale
          const offsetX = (imgWidth - scaledWidth) / 2
          const offsetY = (imgHeight - scaledHeight) / 2

          ctx.save()
          ctx.beginPath()
          ctx.rect(imgX, imgY, imgWidth, imgHeight)
          ctx.clip()
          ctx.drawImage(img, imgX + offsetX, imgY + offsetY, scaledWidth, scaledHeight)
          ctx.restore()

          // === ロゴエリア（プレースホルダー） ===
          // Position: (413, 302), Size: 140 x 31
          // ロゴは許可取得後に追加予定

          // Canvasから画像を生成
          canvas.toBlob((blob) => {
            if (blob) {
              resolve(blob)
            } else {
              reject(new Error('Failed to generate image blob'))
            }
          }, 'image/png')
        }

        img.onerror = () => {
          reject(new Error('Failed to load pet image'))
        }

        img.src = e.target?.result as string
      }

      reader.onerror = () => {
        reject(new Error('Failed to read pet image file'))
      }

      reader.readAsDataURL(data.petImage)
    })
  }

  return {
    generateLicenseImage
  }
}
