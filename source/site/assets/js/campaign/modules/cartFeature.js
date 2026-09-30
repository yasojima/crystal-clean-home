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
  headerTotalAmountElement = null
  headerTotalCountElement = null
  floatingTotalAmountElement = null
  floatingTotalQuantityElement = null

  /*constructor() {
    super()
    this.headerTotalAmountElement = document.querySelector('#js-header-total-amount > span')
    this.headerTotalCountElement = document.querySelector('#js-header-total-count > span')
    this.floatingTotalAmountElement = document.querySelector('#js-floating-total-amount')
    this.floatingTotalQuantityElement = document.querySelector('#js-floating-total-quantity')
  }*/

  constructor() {
  super()

  this.headerShadowRoot = document.querySelector('#campaign-header')?.shadowRoot
  this.floatingShadowRoot = document.querySelector('#campaign-floating')?.shadowRoot

  this.headerTotalAmountElement =
    this.headerShadowRoot?.querySelector('#js-header-total-amount > span')
    ?? document.querySelector('#js-header-total-amount > span')

  this.headerTotalCountElement =
    this.headerShadowRoot?.querySelector('#js-header-total-count > span')
    ?? document.querySelector('#js-header-total-count > span')

  this.floatingTotalAmountElement =
    this.floatingShadowRoot?.querySelector('#js-floating-total-amount')
    ?? document.querySelector('#js-floating-total-amount')

  this.floatingTotalQuantityElement =
    this.floatingShadowRoot?.querySelector('#js-floating-total-quantity')
    ?? document.querySelector('#js-floating-total-quantity')
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

  async postCartData(requestCartAddData) {
    let additionalErrorMessage = ''
    const response = await this.postCartDataToApi(requestCartAddData)
    if (response) {
      const isSuccess = response.result.code === 0
      additionalErrorMessage = response.result.message ? `\n\n${response.result.message}` : ''
      if(isSuccess) {
        await this.setCartData(this.GET_METHOD_QUERY_PARAMETER)
        return response.cart
      }
    }
    alert(`カートの追加に失敗しました。${additionalErrorMessage}`)
    return null
  }
}