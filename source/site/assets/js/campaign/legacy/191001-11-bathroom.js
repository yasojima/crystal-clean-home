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
      if (document.body?.id !== 'page-191001-11') return

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
      document.querySelectorAll('.js-product-select').forEach((element) => {
        element.addEventListener('change', (event) => this.changeProduct(event))
      })
    }

    changeProduct(event) {
      const $this = event.currentTarget
      const productElement = $this.closest('.js-product')
      productElement.querySelector('input[type="hidden"][name="product-id"]').value = $this.value
    }

    async addCart(event) {
      const $this = event.currentTarget
      $this.style.pointerEvents = 'none'
      clearTimeout(this.clickedTimeoutId)

      const productElement = $this.closest('.js-product')
      const [mainProductId, ...optionProductIds] =
        productElement.querySelector('input[type="hidden"][name="product-id"]').value.split('_')
      const quantitySelectElement = productElement.querySelector('select[name="quantity"]')
      const quantity = quantitySelectElement ? Number(quantitySelectElement.value) : 1

      const requestCartAddData = {
        temporary: 0,
        caller: 'campaign',
        product: {
          is_express: 0,
          id: Number(mainProductId),
          product_quantity: quantity
        }
      }

      if (optionProductIds.length > 0) {
        requestCartAddData.options = optionProductIds.reduce((options, optionId) => {
          options.push({
            parent_id: Number(mainProductId),
            id: Number(optionId),
            product_quantity: quantity
          })
          return options
        }, [])
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
