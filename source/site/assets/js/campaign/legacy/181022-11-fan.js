(async () => {
  const { CartFeature } = await import('./modules/cartFeature.js')

  class Cart extends CartFeature {
    clickedTimeoutId = 0

    constructor() {
      super()
      this.createModalStructure()
      this.init()
    }

    resolveFloatingElementsForThisPage() {
      if (document.body?.id !== 'page-181022-11') return

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
      this.resolveFloatingElementsForThisPage()
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

      const productElement = $this.closest('.js-product')
      const [mainProductId, optionProductId] =
        productElement.querySelector('input[type="hidden"][name="product-id"]').value.split('_')
      const quantity = Number(productElement.querySelector('select[name="quantity"]').value)

      const requestCartAddData = {
        temporary: 0,
        caller: 'campaign',
        product: {
          is_express: 0,
          id: Number(mainProductId),
          product_quantity: quantity
        }
      }

      if (optionProductId) {
        requestCartAddData.options = [{
          parent_id: Number(mainProductId),
          id: Number(optionProductId),
          product_quantity: quantity
        }]
      }

      const response = await this.getPostCartData(requestCartAddData)
      if (response.isSuccess) {
        await this.handleAddCartSuccess([response])
      } else {
        const additionalErrorMessage = response.message ? `\n\n${response.message}` : ''
        alert(`カートの追加に失敗しました。${additionalErrorMessage}`)
      }

      setTimeout(() => {
        $this.style.pointerEvents = 'auto'
      }, 500)
    }
  }

  new Cart()
})()
