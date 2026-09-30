(async () => {
  const { CartFeature } = await import('./modules/cartFeature.js')

  class Cart extends CartFeature {
    clickedTimeoutId = 0

    constructor() {
      super()
      this.init()
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
      const [mainProductId, optionProductId] = productElement.querySelector('input[type="hidden"][name="product-id"]').value.split('_')
      const quantity = productElement.querySelector('input[type="number"].quantity').value

      const requestCartAddData = {
        temporary: 0,
        caller: 'campaign',
        product: {
          is_express: 0,
          id: Number(mainProductId),
          product_quantity: quantity
        }
      }

      if(optionProductId) {
        requestCartAddData.options = [{
          parent_id: Number(mainProductId),
          id: Number(optionProductId),
          product_quantity: quantity
        }]
      }

      const response = await this.getPostCartData(requestCartAddData)
      if (response.isSuccess) {
        await this.setCartData(this.GET_METHOD_QUERY_PARAMETER)
        alert('カートに追加しました。')
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