// Cookie工具函数

/**
 * 设置cookie
 * @param {string} name - cookie名称
 * @param {string} value - cookie值
 * @param {number} days - 过期天数
 */
export function setCookie(name, value, days = 7) {
  const expires = new Date()
  expires.setTime(expires.getTime() + days * 24 * 60 * 60 * 1000)
  document.cookie = `${name}=${encodeURIComponent(value)};expires=${expires.toUTCString()};path=/;SameSite=Strict`
}

/**
 * 获取cookie
 * @param {string} name - cookie名称
 * @returns {string|null} - cookie值
 */
export function getCookie(name) {
  const nameEQ = name + '='
  const ca = document.cookie.split(';')
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i]
    while (c.charAt(0) === ' ') c = c.substring(1, c.length)
    if (c.indexOf(nameEQ) === 0) {
      return decodeURIComponent(c.substring(nameEQ.length, c.length))
    }
  }
  return null
}

/**
 * 删除cookie
 * @param {string} name - cookie名称
 */
export function deleteCookie(name) {
  document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`
}

/**
 * 清除所有cookie
 */
export function clearAllCookies() {
  const cookies = document.cookie.split(';')
  for (let i = 0; i < cookies.length; i++) {
    const cookie = cookies[i]
    const eqPos = cookie.indexOf('=')
    const name = eqPos > -1 ? cookie.substr(0, eqPos).trim() : cookie.trim()
    deleteCookie(name)
  }
}
