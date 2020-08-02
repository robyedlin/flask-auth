const credentials = {
  email: 'ryedlin@gmail.com',
  password: 'S3cr3tP@ss'
}

export const login = async (email = credentials.email, password = credentials.password) => {
  const headers = {}
  await cy.request({
      method: 'POST',
      url: '/users/auth-token',
      body: {
        email,
        password
      }
    })
  await cy.getCookie('csrf_access_token').then(c => {
    headers['X-CSRF-TOKEN'] = c.value
  })
  await cy.getCookie('csrf_refresh_token').then(c => {
    headers['X-CSRF-REFRESH-TOKEN'] = c.value
  })
  return headers
}
