(async () => {
  const { CartFeature } = await import('./modules/cartFeature.js')

  class Cart extends CartFeature {
    constructor() {
      super()
      this.setCartData()
    }
  }

  new Cart()
})()