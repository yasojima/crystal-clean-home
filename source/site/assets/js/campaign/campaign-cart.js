(async () => {
  const { CartFeature } = await import('./modules/cartFeature.js')

  class Cart extends CartFeature {
    #BODY_FIXED_CLASS = 'is-fixed'
    #bodyElement
    #modalElement
    #insertCartItemsElement

    constructor() {
      super()
      this.#bodyElement = document.querySelector('body')
      this.init()
    }

    async init() {
      await this.setCartData()
      this.initSetupModal()
      document.querySelectorAll('.js-product [data-cart-feature="add-button"]').forEach(element => {
        element.addEventListener('click', (event) => this.addCart(event))
      })
    }

    initSetupModal() {
      const insertModalElement = `
      <dialog class="c-modal js-modal" id="addCartModal" aria-hidden="true">
        <div class="c-modal__backdrop data-modal-feature="closer"></div>
        <div class="c-modal__main">
          <button class="c-modal-closer" type="button" data-modal-feature="closer">モーダルを閉じる</button>
          <div data-modal-feature="insert-cart-items">
          </div>
        </div>
      </dialog>
      `
      document.querySelector('main').insertAdjacentHTML('beforeend', insertModalElement)
      this.#modalElement = document.querySelector('#addCartModal.js-modal')
      this.#insertCartItemsElement = this.#modalElement.querySelector('[data-modal-feature="insert-cart-items"]')
      this.#modalElement.querySelector('[data-modal-feature="closer"]').addEventListener('click', this.closeModal.bind(this))
    }


    async addCart(event) {
      const clickedAddCartButton = event.currentTarget
      clickedAddCartButton.setAttribute('disabled', 'true')
      
      // try...finally でエラー時も確実にdisabledを解除する
      try {
        const canModal = clickedAddCartButton.hasAttribute('data-use-modal')
        const href = clickedAddCartButton.getAttribute('data-href') ?? null
        const productsContainerElement = clickedAddCartButton.closest('.js-product')
        
        const arbitraryParentProductElements = productsContainerElement.querySelectorAll('[data-cart-feature="parent-product"]')

        const requestInitData = {
          temporary: 0,
          caller: 'campaign'
        }

        let cartResponses = []

        if (arbitraryParentProductElements.length > 0) {
          for (const parentElement of arbitraryParentProductElements) {
            if (Number(parentElement.value) > 0) {
              const requestProductData = this.getArbitraryPatternProductData(productsContainerElement, parentElement)
              const requestData = Object.assign({}, requestInitData, requestProductData)
              const response = await this.postCartData(requestData)
              if (response) {
                cartResponses.push(response)
              }
            }
          }
        } else {
          const requestProductData = this.getDefaultPatternProductData(productsContainerElement)
          const requestData = Object.assign(requestInitData, requestProductData)
          const response = await this.postCartData(requestData)
          if (response) {
            cartResponses.push(response)
          }
        }

        if(cartResponses.length > 0) {
          if(canModal) {
            this.showAddCartModal(cartResponses)
          }
          else if(href) {
            const hrefTarget = clickedAddCartButton.getAttribute('data-target') ?? '_self'
            window.open(href, hrefTarget)
          } else {
            alert('カートに追加しました。')
          }
        } else {
           if (!href) alert('数量を選択してください。')
        }
      } finally {
        // 処理が成功してもエラーになっても、必ず500ms後にボタンを有効化する
        setTimeout(() => {
          clickedAddCartButton.removeAttribute('disabled')
        }, 500)
      }
    }

    // 同時に追加する商品の数量が同じ & 同じでない場合
    getDefaultPatternProductData(productsContainerElement) {
      const [parentProductId, ...optionProductIds] = productsContainerElement.querySelector('[data-cart-feature="product-ids"]').value.split('_')
      const [parentProductQuantity, ...optionProductQuantities] = productsContainerElement.querySelector('[data-cart-feature="quantities"]').value.split('_')

      const requestOptionData = optionProductIds.reduce((optionsData, optionProductId, index) => {
        optionsData.push({
          parent_id: Number(parentProductId),
          id: Number(optionProductId),
          product_quantity: optionProductQuantities.length ? Number(optionProductQuantities[index]) :  Number(parentProductQuantity)
        })
        return optionsData
      }, [])

      return {
        product: {
          is_express: 0,
          id: Number(parentProductId),
          product_quantity: Number(parentProductQuantity)
        },
        options: requestOptionData ?? []
      }
    }

    // 追加する商品・数量が任意の場合
    getArbitraryPatternProductData(productsContainerElement, parentProductElement) {
      const parentProductId = Number(parentProductElement.getAttribute('data-product-id'))
      
      // 親IDに紐付くオプションのみを取得 (data-parent-product-id が一致するもの)
      let optionProductsElements = productsContainerElement.querySelectorAll(`[data-cart-feature="option-product"][data-parent-product-id="${parentProductId}"]`)
      
      // もし紐付け属性がない場合かつ親商品が1つだけなら、従来の全取得にフォールバック（互換性維持）
      if (optionProductsElements.length === 0 && productsContainerElement.querySelectorAll('[data-cart-feature="parent-product"]').length === 1) {
        optionProductsElements = productsContainerElement.querySelectorAll('[data-cart-feature="option-product"]')
      }

      const requestOptionData = Array.from(optionProductsElements).reduce((optionsData, element) => {
        const quantity = Number(element.value)
        // 数量が0より大きい場合のみデータを追加
        if (quantity > 0) {
          optionsData.push({
            parent_id: parentProductId,
            id: Number(element.getAttribute('data-product-id')),
            product_quantity: quantity
          })
        }
        return optionsData
      }, [])

      return {
        product: {
          is_express: 0,
          id: parentProductId,
          product_quantity: Number(parentProductElement.value)
        },
        options: requestOptionData ?? []
      }
    }

    openModal() {
      this.#bodyElement.classList.add(this.#BODY_FIXED_CLASS) // typo修正: this.BODY_FIXED_CLASS -> this.#BODY_FIXED_CLASS
      this.#modalElement.showModal()
      this.#modalElement.setAttribute('aria-hidden', 'false')
    }

    closeModal() {
      this.#modalElement.close()
      this.#modalElement.setAttribute('aria-hidden', 'true')
      this.#bodyElement.classList.remove(this.#BODY_FIXED_CLASS)
      // リスナー削除はbindの問題でうまく動かない可能性があるため、初期化時に一度だけ登録する形式が安全ですが、元のロジックを維持
      // this.#insertCartItemsElement.querySelector('[data-modal-feature="closer"]').removeEventListener('click', this.closeModal.bind(this)) 
    }

    getPriceData(amounts) {
      const taxIncludePrice = amounts[0].price + amounts[0].price_tax
      const discount = amounts[0].price_discount ? amounts[0].price_discount : 0
      const quantity = amounts[0].product_quantity
      return [taxIncludePrice, discount, quantity]
    }

    getRenderProductData(product) {
      const { web_cart_name, amounts, unit } = product
      const [price, discount, quantity] = this.getPriceData(amounts)
      return {
        webCartName: web_cart_name,
        price,
        discount,
        quantity,
        unit
      }
    }

    showAddCartModal(cartResponses) {
      // 単体オブジェクトの場合は配列化
      const responses = Array.isArray(cartResponses) ? cartResponses : [cartResponses]
      
      // 【修正】順次足し算するのではなく、一番最後に取得したレスポンスの「カート内総数」を使用する
      const totalQuantity = responses.length > 0 ? responses[responses.length - 1].total_quantity : 0;
      
      // 表示用データを全レスポンス分結合
      let renderProductData = []
      
      responses.forEach(response => {
        // totalQuantity += response.total_quantity // ←この行を削除
        const parentData = this.getRenderProductData(response.product)
        const optionData = response.options.map(option => this.getRenderProductData(option))
        renderProductData.push(parentData, ...optionData)
      })

      const productItemsElement = renderProductData.reduce((renderElement, data) => {
        const priceElement = data.price !== 0
          ? `<p class="c-add-cart-item-price" data-unit="${data.unit}">${data.price.toLocaleString()}</p>`
          : '<p class="c-add-cart-item-price-text">ご相談ください</p>'
        const discountElement = data.discount > 0
          ? `<div class="c-add-cart-item__detail">
              <dt class="c-add-cart-item__term c-add-cart-item__term--discount">キャンペーン割引:</dt>
              <dd class="c-add-cart-item__discount">-¥${data.discount.toLocaleString()}</dd>
            </div>`
          : ''
        renderElement += `
        <div class="c-add-cart__item c-add-cart-item">
          <h5 class="c-bullet-heading c-add-cart-item__name">${data.webCartName}</h5>
          <dl class="c-add-cart-item__details">
            <div class="c-add-cart-item__detail">
              <dt class="c-add-cart-item__term">価格:</dt>
              <dd class="c-add-cart-item__price">
                ${priceElement}
              </dd>
            </div>
            ${discountElement}
            <div class="c-add-cart-item__detail">
              <dt class="c-add-cart-item__term">${data.unit}数：</dt>
              <dd class="c-add-cart-item__quantity">${data.quantity}</dd>
            </div>
          </dl>
        </div>
        `

        return renderElement
      }, '')

      this.#insertCartItemsElement.innerHTML = `
        <div class="c-add-cart">
          <h1 class="c-add-cart__heading">カートに追加しました！</h1>
          <div class="c-add-cart__items">${productItemsElement}</div>
          <a class="c-cart-confirm-button c-add-cart__button" href="/cart/"><span class="c-cart-confirm-button__text" data-cart-count="${totalQuantity}">カートを見る</span></a>
          <button class="c-add-cart__close-button" type="button" data-modal-feature="closer">戻る</button>
        </div>
      `
      // モーダル内の戻るボタンにもイベント再設定
      this.#insertCartItemsElement.querySelector('[data-modal-feature="closer"]').addEventListener('click', this.closeModal.bind(this))
      this.openModal()
    }
  }

  new Cart()
})()