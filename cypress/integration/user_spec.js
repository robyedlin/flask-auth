import { login } from '../utils'

const postData = {
  email: {
    changed: 'rob2@cloud9pixels.com',
    unused: 'rob@cloud9pixels.com',
    used: 'ryedlin@gmail.com',
    valid: 'ryedlin@gmail.com',
    invalid: 'ry'
  },
  password: {
    changed: 'S3cretP@ss',
    unused: 'S3cr3tP@sS',
    used: 'S3cr3tP@ss',
    valid: 'S3cr3tP@ss',
    invalid: 'S3cre'
  }
}

let savedAccessToken = null

describe('users', () => {
  /**
   * POST '/users'
   */
  it('creates new user', () => {
    cy.request({
      method: 'POST',
      url: '/users',
      body: {
        email: postData.email.valid,
        password: postData.password.valid
      }
    })
    .should('have.property', 'status',  201)
  })

  it('prevents creation of new user with used email', () => {
    cy.request({
        method: 'POST',
        url: '/users',
        failOnStatusCode: false,
        body: {
          email: postData.email.valid,
          password: postData.password.valid
        }
      })
      .should('have.property', 'status',  409)
  })

  it('prevents creation of new user with invalid username', () => {
    cy.request({
        method: 'POST',
        url: '/users',
        failOnStatusCode: false,
        body: {
          email: postData.email.invalid,
          password: postData.password.valid
        }
      })
      .should('have.property', 'status',  422)
  })

  it('prevents creation of new user with invalid password', () => {
    cy.request({
        method: 'POST',
        url: '/users',
        failOnStatusCode: false,
        body: {
          email: postData.email.valid,
          password: postData.password.invalid
        }
      })
      .should('have.property', 'status',  422)
  })

  /**
   * POST '/users/email/availability'
   */
  it('finds available email', () => {
    cy.request({
        method: 'POST',
        url: '/users/email/availability',
        body: {
          email: postData.email.unused
        }
      })
      .its('body')
      .should('deep.eq', {
        "available": true
      })
  })

  it('finds unavailable email', () => {
    cy.request({
        method: 'POST',
        url: '/users/email/availability',
        body: {
          email: postData.email.used
        }
      })
      .its('body')
      .should('deep.eq', {
        "available": false
      })
  })

  it('finds available email', () => {
    cy.request({
        method: 'POST',
        url: '/users/email/availability',
        body: {
          email: postData.email.unused
        }
      })
      .its('body')
      .should('deep.eq', {
        "available": true
      })
  })

  it('prevents email availability lookup', () => {
    cy.request({
        method: 'POST',
        url: '/users/email/availability',
        failOnStatusCode: false,
        body: {
          email: postData.email.invalid
        }
      })
      .should('have.property', 'status', 422)
  })

  /**
   * POST '/users/auth-token'
   */
  it('prevents an access and refresh token from email and password with invalid credentials', () => {
    cy.request({
        method: 'POST',
        url: '/users/auth-token',
        failOnStatusCode: false,
        body: {
          email: postData.email.valid,
          password: postData.password.invalid
        }
      })
      .should('have.property', 'status', 422)
  })

  it('prevents getting an access and refresh token from email and invalid password', () => {
    cy.request({
        method: 'POST',
        url: '/users/auth-token',
        failOnStatusCode: false,
        body: {
          email: postData.email.used,
          password: postData.password.unused
        }
      })
      .should('have.property', 'status', 401)
  })

  it('prevents getting an access and refresh token from invalid email and password', () => {
    cy.request({
        method: 'POST',
        url: '/users/auth-token',
        failOnStatusCode: false,
        body: {
          email: postData.email.unused,
          password: postData.password.used
        }
      })
      .should('have.property', 'status', 401)
  })

  it('gets an access and refresh token from email and password', () => {
    cy.request({
        method: 'POST',
        url: '/users/auth-token',
        body: {
          email: postData.email.used,
          password: postData.password.used
        }
      })
      .should('have.property', 'status', 201)
    cy.getCookie('access_token_cookie')
      .should('exist')
    cy.getCookie('refresh_token_cookie')
      .should('exist')
  })

  /**
   * PUT '/users/auth-token'
   */
  it('gets an access and refresh token from a refresh token', () => {
    login().then(headers => {
      cy.request({
        method: 'PUT',
        url: '/users/auth-token',
        headers
      })
      .should('have.property', 'status', 204)
    })
  })

  it('rejects an access and refresh token without a refresh token', () => {
    login().then(headers => {
      cy.request({
        method: 'PUT',
        failOnStatusCode: false,
        url: '/users/auth-token'
      })
      .should('have.property', 'status', 401)
    })
  })

  /**
   * DELETE '/users/auth-token'
   */
  it('logs the user out', () => {
    login().then(headers => {
      cy.request({
        method: 'DELETE',
        failOnStatusCode: false,
        url: '/users/auth-token'
      })
      .should('have.property', 'status', 204)
      cy.getCookie('access_token_cookie')
        .should('not.exist')
      cy.getCookie('refresh_token_cookie')
        .should('not.exist')
    })
  })

  /**
   * POST '/users/email'
   */
  it('prevents user email reset with unavailable email', () => {
    login().then(headers => {
      cy.request({
        method: 'PUT',
        url: '/users/email',
        failOnStatusCode: false,
        headers,
        body: {
          email: postData.email.used
        }
      })
      .should('have.property', 'status', 409)
      cy.getCookie('access_token_cookie')
        .should('exist')
      cy.getCookie('refresh_token_cookie')
        .should('exist')
    })
  })

  it('prevents user email reset with invalid email', () => {
    login().then(headers => {
      cy.request({
        method: 'PUT',
        url: '/users/email',
        failOnStatusCode: false,
        headers,
        body: {
          email: postData.email.invalid
        }
      })
      .should('have.property', 'status', 422)
      cy.getCookie('access_token_cookie')
        .should('exist')
      cy.getCookie('refresh_token_cookie')
        .should('exist')
    })
  })

  it('resets the user email', () => {
    login().then(headers => {
      cy.request({
        method: 'PUT',
        url: '/users/email',
        headers,
        body: {
          email: postData.email.changed
        }
      })
      .should('have.property', 'status', 201)
      cy.getCookie('access_token_cookie')
        .should('exist')
      cy.getCookie('refresh_token_cookie')
        .should('exist')
    })
  })

  /**
   * PUT '/users/password'
   */
  it('prevents resetting the user password with invalid password', () => {
    login(postData.email.changed).then(headers => {
      cy.request({
        method: 'PUT',
        url: '/users/password',
        failOnStatusCode: false,
        headers,
        body: {
          password: postData.password.invalid
        }
      })
      .should('have.property', 'status', 422)
      cy.getCookie('access_token_cookie')
        .should('exist')
      cy.getCookie('refresh_token_cookie')
        .should('exist')
    })
  })
  
  it('resets the user password', () => {
    login(postData.email.changed).then(headers => {
      cy.request({
        method: 'PUT',
        url: '/users/password',
        headers,
        body: {
          password: postData.password.changed
        }
      })
      .should('have.property', 'status', 204)
      cy.getCookie('access_token_cookie')
        .then(cookie => {
          // save the access token for later use for routes that involve email
          savedAccessToken = cookie.value
        })
        .should('exist')
      cy.getCookie('refresh_token_cookie')
        .should('exist')
    })
  })

  it('pretends to send forgot password email', () => {
    cy.request({
      method: 'POST',
      url: '/users/password/forgot',
      body: {
        email: postData.email.unused
      }
    })
    .should('have.property', 'status', 201)
  })

  it('sends forgot password email', () => {
    cy.request({
      method: 'POST',
      url: '/users/password/forgot',
      body: {
        email: postData.email.used
      }
    })
    .should('have.property', 'status', 201)
  })

  it('resets password from token', () => {
    cy.request({
      method: 'PUT',
      url: '/users/password/forgot',
      body: {
        // use an unused password
        password: postData.password.unused,
        // use the saved access token
        token: savedAccessToken
      }
    })
    .should('have.property', 'status', 204)
  })
})