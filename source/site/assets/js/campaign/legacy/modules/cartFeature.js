const DATA_LAYER_EVENTS = {
  ADD_TO_CART: 'add_to_cart'
}

const CURRENCY = {
  JPY: 'JPY'
}

const PURCHASE_TYPE = {
  WEB: 'web',
  QUICK: 'quick',
  SHOP: 'shop'
}

const API_REQUEST_PURCHASE_TYPE = {
    WEB: 1,
    QUICK: 2,
    SHOP: 3
}

const API_PURCHASE_TYPE_TO_PURCHASE_TYPE = {
    [API_REQUEST_PURCHASE_TYPE.WEB]: PURCHASE_TYPE.WEB,
    [API_REQUEST_PURCHASE_TYPE.QUICK]: PURCHASE_TYPE.QUICK,
    [API_REQUEST_PURCHASE_TYPE.SHOP]: PURCHASE_TYPE.SHOP
}

export class Fetch {
  async fetchData(url, requestOptions) {
    try {
      const response = await fetch(url, requestOptions)
      if (!response.ok) {
        const statusCode = Number(response.status)
        const errorText = `HTTP Error\nStatusCode: ${statusCode}\nStatusText: ${response.statusText}`
        if (statusCode === 422) {
          console.error(errorText)
          return response.json()
        } else {
          console.error(errorText)
          return null
        }
      }
      return response.json()
    } catch (error) {
      console.error(error)
    }
  }
}

export class CartRequestFeature extends Fetch {
  API_URL_PATH_TO = ''
  cartData = null

  constructor() {
    super()
    this.API_URL_PATH_TO = `${window.location.origin}/api/v1`
  }

  request(url, method, useCsrfToken, postData) {
    const requestOptions = {
      method: method,
      headers: { 'Content-Type': 'application/json' }
    }
    if (useCsrfToken) (requestOptions.headers)['X-CSRF-Token'] = window.csrf
    if (postData) requestOptions.body = JSON.stringify(postData)
    return this.fetchData(url, requestOptions)
  }

  getCartDataFromApi(queryParameter) {
    return this.request(`${this.API_URL_PATH_TO}/cart-info${queryParameter}`, 'GET', false)
  }

  postCartDataToApi(postData) {
    return this.request(`${this.API_URL_PATH_TO}/cart-add`, 'POST', true, postData)
  }

  postProductAmountDataToApi(postData) {
    return this.request(`${this.API_URL_PATH_TO}/product-amount`, 'POST', true, postData)
  }

  deleteDataToApi(deleteData) {
    return this.request(`${this.API_URL_PATH_TO}/cart-remove`, 'DELETE', true, deleteData)
  }
}

export class CartFeature extends CartRequestFeature {
  GET_METHOD_QUERY_PARAMETER = '?temporary=0&detail=1&caller=campaign'
  headerShadowRoot = null
  floatingShadowRoot = null
  addCartModalElement = null
  confirmProductItemElement = null

  constructor() {
  super()
  this.headerShadowRoot = document.querySelector('#campaign-header')?.shadowRoot

  if (this.headerShadowRoot) {
  this.headerTotalAmountElement = this.headerShadowRoot.querySelector('#js-header-total-amount > span')
  this.headerTotalCountElement = this.headerShadowRoot.querySelector('#js-header-total-count > span')
  }
  
  this.floatingTotalAmountElement = document.querySelector('#js-floating-total-amount')
  this.floatingTotalQuantityElement = document.querySelector('#js-floating-total-quantity')
  }

  createModalStructure() {
    const modalHTML =
        '<dialog id="add-cart-modal" class="c-modal" aria-hidden="true">' +
        '<div class="c-modal__container">' +
        '<div class="c-modal__content">' +
        '<button type="button" class="c-modal__close js-modal-closer" aria-label="モーダルを閉じる">×</button>' +
        '<div id="js-add-products"></div>' +
        '<button class="c-add-cart__close-button js-modal-closer" type="button">戻る</button>' +
        '</div>' +
        '</div>' +
        '</dialog>'

    document.body.insertAdjacentHTML('beforeend', modalHTML)

    this.addCartModalElement = document.querySelector('#add-cart-modal')
    this.confirmProductItemElement = document.querySelector('#js-add-products')

    const closeButtons = this.addCartModalElement.querySelectorAll('.js-modal-closer')
    closeButtons.forEach(button => {
      button.addEventListener('click', () => this.closeModal())
    })

    this.addCartModalElement?.addEventListener('click', (event) => {
      if (event.target === this.addCartModalElement) {
        this.closeModal()
      }
    })
  }

  openModal() {
    this.addCartModalElement?.showModal()
    this.addCartModalElement?.setAttribute('aria-hidden', 'false')
  }

  closeModal() {
    this.addCartModalElement?.close()
    this.addCartModalElement?.setAttribute('aria-hidden', 'true')
  }

  getPriceData(price, priceTax, priceDiscount, priceDiscountTax) {
    if (!priceDiscountTax) {
      priceDiscountTax = 0
    }
    const taxIncludePrice = price + priceTax
    const discount = priceDiscount ? priceDiscount + priceDiscountTax : 0
    return [taxIncludePrice, discount]
  }

  addSuccessModalContents(cartAddConfirmProductData, totalQuantity) {
    const addConfirmProductsItemElement = cartAddConfirmProductData.reduce((element, data) => {
      const price = data.priceDetail.price
      const discount = data.priceDetail.discount
      const priceElement =
          price !== 0
              ? '<p class="c-add-cart-item-price" data-unit="' + data.unit + '">' + price.toLocaleString() + '</p>'
              : '<p class="c-add-cart-item-price-text">ご相談ください</p>'

      const discountItemElement =
          discount > 0
              ? '<div class="c-add-cart-item__detail">' +
              '<dt class="c-add-cart-item__term c-add-cart-item__term--discount">キャンペーン割引:</dt>' +
              '<dd class="c-add-cart-item__discount">-¥' + discount.toLocaleString() + ' (税込)／' + data.unit + '</dd>' +
              '</div>'
              : ''

      element += '<div class="c-add-cart__item c-add-cart-item">' +
          '<h5 class="c-bullet-heading c-add-cart-item__name">' + data.webCartName + '</h5>' +
          '<dl class="c-add-cart-item__details">' +
          '<div class="c-add-cart-item__detail">' +
          '<dt class="c-add-cart-item__term">価格:</dt>' +
          '<dd class="c-add-cart-item__price">' +
          priceElement +
          '</dd>' +
          '</div>' +
          discountItemElement +
          '<div class="c-add-cart-item__detail">' +
          '<dt class="c-add-cart-item__term">' + data.unit + '数：</dt>' +
          '<dd class="c-add-cart-item__quantity">' + data.quantity + '</dd>' +
          '</div>' +
          '</dl>' +
          '</div>'

      return element
    }, '')

    this.confirmProductItemElement.innerHTML =
        '<h1 class="c-add-cart__heading">カートに追加しました！</h1>' +
        '<div class="c-add-cart__items">' + addConfirmProductsItemElement + '</div>' +
        '<a class="c-cart-confirm-button c-add-cart__button" href="/cart/"><span class="c-cart-confirm-button__text" data-cart-count="' + totalQuantity + '">カートを見る</span></a>'
  }

  pushAddToCartDataLayer(addCartResponse, eventName, currency, purchaseType) {
    window.dataLayer = window.dataLayer || []
    window.dataLayer.push({ ecommerce: null })

    let totalValue = 0
    const items = []

    const responseCartAddProductData = addCartResponse.product

    if (responseCartAddProductData) {
      let discount = 0
      if (responseCartAddProductData.amounts[0].price_discount && responseCartAddProductData.amounts[0].price_discount_tax) {
        discount = responseCartAddProductData.amounts[0].price_discount + responseCartAddProductData.amounts[0].price_discount_tax
      }

      const mainProductPrice = responseCartAddProductData.amounts[0].price + responseCartAddProductData.amounts[0].price_tax - discount
      const mainProductQuantity = responseCartAddProductData.amounts[0].product_quantity
      totalValue += mainProductPrice * mainProductQuantity

      items.push({
        item_name: responseCartAddProductData.web_cart_name,
        item_id: responseCartAddProductData.pid ? String(responseCartAddProductData.pid) : String(responseCartAddProductData.id),
        price: mainProductPrice,
        quantity: mainProductQuantity,
        item_variant: ''
      })
    }

    if (addCartResponse.options) {
      addCartResponse.options.forEach((optionData) => {
        let optionDiscount = 0
        if (optionData.amounts[0].price_discount && optionData.amounts[0].price_discount_tax) {
          optionDiscount = optionData.amounts[0].price_discount + optionData.amounts[0].price_discount_tax
        }
        const optionPrice = optionData.amounts[0].price + optionData.amounts[0].price_tax - optionDiscount
        const optionQuantity = optionData.amounts[0].product_quantity
        totalValue += optionPrice * optionQuantity

        items.push({
          item_name: optionData.data_layer_option_name || optionData.web_cart_name,
          item_id: optionData.pid ? String(optionData.pid) : String(optionData.id),
          price: optionPrice,
          quantity: optionQuantity,
          item_variant: optionData.parent_web_cart_name
        })
      })
    }

    const ecommerceData = {
      value: totalValue,
      currency: currency,
      purchase_type: purchaseType,
      items: items
    }

    window.dataLayer.push({
      event: eventName,
      ecommerce: ecommerceData
    })
  }

  async handleAddCartSuccess(responses) {
    await this.setCartData(this.GET_METHOD_QUERY_PARAMETER)

    const responseArray = Array.isArray(responses) ? responses : [responses]

    let formattedConfirmData = []
    let totalQuantity = 0

    responseArray.forEach((response) => {
      if (!response?.cart) return

      const addCartResponse = response.cart

      if (addCartResponse.product) {
        const responseCartAddProductData = addCartResponse.product
        const [price, discount] = this.getPriceData(
            responseCartAddProductData.amounts[0].price,
            responseCartAddProductData.amounts[0].price_tax,
            responseCartAddProductData.amounts[0].price_discount,
            responseCartAddProductData.amounts[0].price_discount_tax
        )

        formattedConfirmData.push({
          webCartName: responseCartAddProductData.web_cart_name,
          unit: responseCartAddProductData.unit,
          priceDetail: {
            price,
            discount
          },
          quantity: responseCartAddProductData.amounts[0].product_quantity
        })
      }

      if (addCartResponse.options) {
        addCartResponse.options.forEach((optionData) => {
          const [optionPrice, optionDiscount] = this.getPriceData(
              optionData.amounts[0].price,
              optionData.amounts[0].price_tax,
              optionData.amounts[0].price_discount,
              optionData.amounts[0].price_discount_tax
          )
          formattedConfirmData.push({
            webCartName: optionData.web_cart_name,
            unit: optionData.unit,
            priceDetail: {
              price: optionPrice,
              discount: optionDiscount
            },
            quantity: optionData.amounts[0].product_quantity
          })
        })
      }

      totalQuantity += addCartResponse.total_quantity || 0
    })

    this.addSuccessModalContents(formattedConfirmData, totalQuantity)
    this.openModal()

    responseArray.forEach((response) => {
      if (response?.cart) {
        this.pushAddToCartDataLayer(
          response.cart,
          DATA_LAYER_EVENTS.ADD_TO_CART,
          CURRENCY.JPY,
          API_PURCHASE_TYPE_TO_PURCHASE_TYPE[response.cart.purchase_type]
        )
      }
    })
  }

  async setCartData(queryParameter = '?temporary=0&detail=1&caller=on_page_load') {
    const response = await this.getCartDataFromApi(queryParameter)
    if (response) {
      const isSuccess = response?.result.code === 0
      if (isSuccess) {
        window.csrf = response.result['csrf-token']
        window.cartData = response.cart
        const totalAmount = window.cartData.total_amount.toLocaleString()
        if (this.headerTotalAmountElement) this.headerTotalAmountElement.textContent = totalAmount
        if (this.headerTotalCountElement) this.headerTotalCountElement.textContent = String(window.cartData.total_quantity)
        if (this.floatingTotalAmountElement) this.floatingTotalAmountElement.dataset.cartCount = String(window.cartData.total_quantity)
        if (this.floatingTotalQuantityElement) this.floatingTotalQuantityElement.textContent = totalAmount
      } else {
        window.csrf = ''
        window.cartData = null
        console.error(`【GET Response Error】\nResult Code: ${response.result.code}\nResult Message: ${response.result.message}\n`)
      }
    }
    window.dispatchEvent(new Event('afterTokenFetch'))
  }

  async getPostCartData(requestCartAddData) {
    requestCartAddData.purchase_type = API_REQUEST_PURCHASE_TYPE.WEB
    const response = await this.postCartDataToApi(requestCartAddData)
    if (response) {
      return {
        isSuccess: response.result.code === 0,
        code: response.result.code,
        message: response.result.message,
        cart: response.cart
      }
    } else {
      return {
        isSuccess: false,
        code: 99,
        message: '',
        cart: undefined
      }
    }
  }
}
