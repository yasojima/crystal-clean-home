(async () => {
  const { CartFeature } = await import('./modules/cartFeature.js')

  class Cart extends CartFeature {
    clickedTimeoutId = 0
    addCartModalElement = null
    confirmProductItemElement = null

    constructor() {
      super()
      this.createModalStructure()
      this.init()
    }

    resolveFloatingElementsForSpecificPage() {
      if (document.body?.id !== 'page-190909-11') return

      const floatingShadowRoot =
        document.querySelector('#campaign-floating')?.shadowRoot

      if (floatingShadowRoot) {
        this.floatingTotalAmountElement =
          floatingShadowRoot.querySelector('#js-floating-total-amount')
        this.floatingTotalQuantityElement =
          floatingShadowRoot.querySelector('#js-floating-total-quantity')
      }
    }

    async setCartData(queryParameter = '?temporary=0&detail=1&caller=on_page_load') {
      this.resolveFloatingElementsForSpecificPage()
      return await super.setCartData(queryParameter)
    }

    async init() {
      await this.setCartData()
      document.querySelectorAll('.js-add-product').forEach((element) => {
        element.addEventListener('click', (event) => this.addCart(event))
      })
    }

    async addCart(event) {
      const $this = event.currentTarget
      $this.style.pointerEvents = 'none'
      clearTimeout(this.clickedTimeoutId)

      const productElement = $this.closest('.js-products')
      const mainProductElement = productElement.querySelector('input[data-main-product-id]')
      const mainProductId = Number(mainProductElement.getAttribute('data-main-product-id'))
      const mainProductQuantity = Number(mainProductElement.value)
      const optionProductElements = Array.from(productElement.querySelectorAll('input[data-option-product-id]'))

      const requestCartAddData = {
        temporary: 0,
        caller: 'campaign',
        product: {
          is_express: 0,
          id: mainProductId,
          product_quantity: mainProductQuantity
        }
      }

      const options = optionProductElements.reduce((optionData, element) => {
        const quantity = Number(element.value)
        if (quantity > 0) {
          optionData.push({
            parent_id: mainProductId,
            id: Number(element.getAttribute('data-option-product-id')),
            product_quantity: quantity
          })
        }
        return optionData
      }, [])

      if (options.length > 0) {
        requestCartAddData.options = options
      }

      const response = await this.getPostCartData(requestCartAddData)
      if (response.isSuccess) {
        await this.handleAddCartSuccess([response])
      } else {
        const additionalErrorMessage = response.message ? '\n\n' + response.message : ''
        alert('カートの追加に失敗しました。' + additionalErrorMessage)
      }

      setTimeout(() => {
        $this.style.pointerEvents = 'auto'
      }, 500)
    }
  }

  new Cart()
})()
