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

          // === PETEMO ロゴ (SVG to Canvas) ===
          // Position: (413, 302), Size: 140 x 31
          const logoImg = new Image()
          const logoSvg = `<svg width="140" height="31" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 244 54"><path fill="#6f8d1b" d="M12.654 10.118a1.91 1.91 0 1 0 0 3.819 1.91 1.91 0 0 0 0-3.819m4.909-1.882a1.91 1.91 0 1 0 1.909 1.91v-.001a1.91 1.91 0 0 0-1.909-1.909m10.496 1.882a1.91 1.91 0 1 0 0 3.819 1.91 1.91 0 0 0 0-3.819m-4.905-1.882a1.91 1.91 0 0 0-.001 3.817h.001a1.908 1.908 0 0 0 1.909-1.907v-.001a1.91 1.91 0 0 0-1.909-1.909m82.848-.818H34.244a19.16 19.16 0 0 0-13.967-6.055C9.707 1.375 1.141 9.941 1.129 20.511a19.044 19.044 0 0 0 7.282 15.023 19.119 19.119 0 0 0 8.105 3.955c1.138.199 2.291.309 3.446.329h86.04c8.943-.01 16.19-7.257 16.2-16.2-.01-8.943-7.257-16.19-16.2-16.2M10.025 33.562a16.515 16.515 0 0 1-6.349-13.051c.01-9.164 7.436-16.59 16.6-16.6a16.61 16.61 0 0 1 12.448 5.624c.242.274.59.431.955.431h72.322c7.535.009 13.642 6.116 13.65 13.651-.009 7.535-6.115 13.641-13.65 13.65h-85.2a19.387 19.387 0 0 1-5.007-.6 18.963 18.963 0 0 1-5.768-3.111m76.327-2.447a.64.64 0 0 1-.61-.43l-1.854-5.2v6.607a.648.648 0 0 1-.648.647h-3.07a.649.649 0 0 1-.647-.647V15.164c0-.357.29-.646.647-.647h3.394a.644.644 0 0 1 .617.453l2.173 6.418 2.173-6.418a.645.645 0 0 1 .618-.453h3.393c.357 0 .647.29.648.647v16.922a.648.648 0 0 1-.648.647h-3.07a.649.649 0 0 1-.647-.647v-6.607l-1.855 5.2a.641.641 0 0 1-.61.43h-.004zM16.271 14.823a1.21 1.21 0 0 0-.956 1.227v16.04c0 .357.29.646.647.647h3.021c.357 0 .647-.29.648-.647v-3.806a5.116 5.116 0 0 0 6.665-2.816l.035-.09a10.84 10.84 0 0 0-.1-8 5.483 5.483 0 0 0-5.179-3.246 28.01 28.01 0 0 0-4.511.633l-.27.058zm6.347 6.536c.048 2.044-.79 3.162-1.642 3.366a1.594 1.594 0 0 1-1.3-.311.13.13 0 0 1-.047-.1v-6.107a.125.125 0 0 1 .083-.121c.28-.083.569-.127.861-.131.357-.011.708.094 1 .3.643.472.991 1.518 1.036 3.1m18.577 7.401h-3.313a.128.128 0 0 1-.129-.127v-3.101c0-.071.057-.128.128-.128h3.12a.649.649 0 0 0 .647-.648v-2.389a.649.649 0 0 0-.647-.648h-3.119a.128.128 0 0 1-.129-.127v-3.101c0-.071.057-.128.128-.128H40.141a.645.645 0 0 0 .615-.444l.844-2.56a.65.65 0 0 0-.615-.85h-7.007a.649.649 0 0 0-.647.648v16.923c0 .357.29.646.647.647h7.209a.649.649 0 0 0 .647-.647v-2.681a.648.648 0 0 0-.647-.647m31.084.007h-3.314a.128.128 0 0 1-.128-.128v-3.1c0-.071.057-.128.128-.128h3.12a.648.648 0 0 0 .646-.648v-2.389a.648.648 0 0 0-.646-.648h-3.12a.128.128 0 0 1-.128-.128v-3.1c0-.071.057-.128.128-.128h2.269a.648.648 0 0 0 .615-.444l.844-2.56a.65.65 0 0 0-.615-.85h-7.008a.648.648 0 0 0-.646.648v16.922c0 .357.289.646.646.647h7.209c.357 0 .647-.29.648-.647v-2.681a.648.648 0 0 0-.648-.647M47.372 17.518l.845-2.56a.646.646 0 0 1 .615-.445h8.364c.28 0 .527.18.615.445l.844 2.56a.649.649 0 0 1-.615.85h-2.63a.128.128 0 0 0-.128.128v13.587c0 .357-.29.646-.647.647h-3.241a.649.649 0 0 1-.647-.647v-13.59a.128.128 0 0 0-.128-.128h-2.63a.65.65 0 0 1-.615-.85m62.765-1.709a6.08 6.08 0 0 0-4.474-1.747h-.108a6.08 6.08 0 0 0-4.474 1.747c-2.212 2.214-2.525 5.815-2.514 7.764 0 3.416.887 6.181 2.5 7.784a6.12 6.12 0 0 0 4.491 1.725h.11a6.118 6.118 0 0 0 4.49-1.725c1.61-1.6 2.5-4.368 2.5-7.784.01-1.949-.3-5.55-2.515-7.764m-3.342 13.045c-.313.316-.74.492-1.184.488h-.007a1.647 1.647 0 0 1-1.181-.488c-.809-.8-1.271-2.651-1.271-5.073-.008-2.4.46-4.249 1.287-5.073a1.57 1.57 0 0 1 1.154-.491h.033a1.57 1.57 0 0 1 1.154.491c.826.823 1.3 2.672 1.287 5.073 0 2.422-.464 4.271-1.272 5.073"/><path fill="#583c32" d="M137.155 21.137h1.316v4.343h.028c.406-.658 1.12-1.148 2.367-1.148 2.073 0 3.081 1.694 3.081 3.613 0 1.961-.91 3.866-3.067 3.866-1.274 0-2.087-.645-2.438-1.177h-.027v1.009h-1.261V21.137zm3.432 4.258c-1.429 0-2.115 1.358-2.115 2.689 0 1.19.616 2.661 2.102 2.661 1.414 0 2.003-1.583 1.975-2.703.027-1.288-.533-2.647-1.962-2.647zm4.59 8.18c.168.057.392.112.616.112 1.177 0 1.568-1.625 1.568-1.765 0-.154-.168-.519-.252-.757l-2.423-6.667h1.442l1.919 5.911h.028l1.961-5.911h1.331l-2.634 7.297c-.49 1.372-1.009 2.955-2.745 2.955-.421 0-.659-.056-.896-.098l.085-1.077zm18.439-13.5h1.891l5.312 12.567h-1.963l-1.278-3.169h-6.158l-1.278 3.169h-1.891l5.365-12.567zm.882 1.692-2.503 6.229h5.006l-2.503-6.229zm8.225-1.692h7.04v1.584h-5.239v3.673h4.771v1.585h-4.771v4.141h5.239v1.584h-7.04V20.075zm15.319-.217c3.817 0 6.05 2.773 6.05 6.5 0 3.817-2.214 6.5-6.05 6.5-3.835 0-6.05-2.683-6.05-6.5 0-3.726 2.233-6.5 6.05-6.5zm0 11.416c2.899 0 4.142-2.413 4.142-4.916 0-2.557-1.368-4.934-4.142-4.915-2.772-.019-4.141 2.358-4.141 4.915 0 2.503 1.242 4.916 4.141 4.916zm8.585-11.199h2.448l5.546 10.118h.036V20.075h1.801v12.567h-2.305l-5.69-10.334h-.036v10.334h-1.8V20.075zm17.909 0h3.295c2.575 0 4.718.899 4.718 3.763 0 2.791-2.179 3.781-4.447 3.781h-1.765v5.023h-1.801V20.075zm1.801 5.959h1.782c1.116 0 2.521-.558 2.521-2.214 0-1.585-1.656-2.161-2.772-2.161h-1.53v4.375zm8.405-5.959h7.04v1.584h-5.239v3.673h4.771v1.585h-4.771v4.141h5.239v1.584h-7.04V20.075zm12.421 1.584h-3.907v-1.584h9.615v1.584h-3.907v10.983h-1.801V21.659z"/></svg>`
          const logoBlob = new Blob([logoSvg], { type: 'image/svg+xml' })
          const logoUrl = URL.createObjectURL(logoBlob)
          logoImg.onload = () => {
            ctx.drawImage(logoImg, s(413), s(302), s(140), s(31))
            URL.revokeObjectURL(logoUrl)

            // Canvasから画像を生成
            canvas.toBlob((blob) => {
              if (blob) {
                resolve(blob)
              } else {
                reject(new Error('Failed to generate image blob'))
              }
            }, 'image/png')
          }
          logoImg.onerror = () => {
            // ロゴ読み込み失敗時はテキストでフォールバック
            ctx.fillStyle = '#6f8d1b'
            ctx.font = `bold ${s(14)}px "Arial", sans-serif`
            ctx.textAlign = 'center'
            ctx.fillText('PETEMO', s(483), s(318))

            // Canvasから画像を生成
            canvas.toBlob((blob) => {
              if (blob) {
                resolve(blob)
              } else {
                reject(new Error('Failed to generate image blob'))
              }
            }, 'image/png')
          }
          logoImg.src = logoUrl
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
