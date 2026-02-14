class ApiError extends Error {
  constructor(message, options = {}) {
    super(message)
    this.name = 'ApiError'
    this.code = options.code || 'api_error'
    this.status = options.status || 500
    this.payload = options.payload || null
  }
}

function encodePath(pathValue) {
  return String(pathValue || '')
    .split('/')
    .filter(Boolean)
    .map((segment) => encodeURIComponent(segment))
    .join('/')
}

async function requestApi(path, options = {}) {
  const init = {
    method: options.method || 'GET',
    headers: options.headers || {},
  }

  if (options.body instanceof FormData) {
    init.body = options.body
  } else if (options.body !== undefined) {
    init.body = JSON.stringify(options.body)
    init.headers = {
      'Content-Type': 'application/json',
      ...init.headers,
    }
  }

  const response = await fetch(path, init)
  let payload = null
  try {
    payload = await response.json()
  } catch (error) {
    throw new ApiError('Respuesta no valida del servidor.', {
      status: response.status,
      code: 'invalid_response',
    })
  }

  if (!response.ok || !payload.ok) {
    const message = payload?.error?.message || 'Error en la API.'
    const code = payload?.error?.code || 'api_error'
    throw new ApiError(message, {
      status: response.status,
      code,
      payload,
    })
  }

  return payload.data
}

export async function getLibraryNode({ path = '', q = '', kind = 'all', status = 'all' }) {
  const params = new URLSearchParams()
  params.set('path', path)
  params.set('q', q)
  params.set('kind', kind)
  params.set('status', status)
  return requestApi(`/api/v1/library/node?${params.toString()}`)
}

export async function getStory(storyPath, page) {
  const params = new URLSearchParams()
  if (page) {
    params.set('p', String(page))
  }
  const encodedPath = encodePath(storyPath)
  const suffix = params.toString() ? `?${params.toString()}` : ''
  return requestApi(`/api/v1/stories/${encodedPath}${suffix}`)
}

export async function patchStoryPage(storyPath, pageNumber, body) {
  const encodedPath = encodePath(storyPath)
  return requestApi(`/api/v1/stories/${encodedPath}/pages/${pageNumber}`, {
    method: 'PATCH',
    body,
  })
}

export async function uploadAlternative(storyPath, pageNumber, slotName, formData) {
  const encodedPath = encodePath(storyPath)
  return requestApi(`/api/v1/stories/${encodedPath}/pages/${pageNumber}/slots/${slotName}/alternatives`, {
    method: 'POST',
    body: formData,
  })
}

export async function setSlotActive(storyPath, pageNumber, slotName, alternativeId) {
  const encodedPath = encodePath(storyPath)
  return requestApi(`/api/v1/stories/${encodedPath}/pages/${pageNumber}/slots/${slotName}/active`, {
    method: 'PUT',
    body: { alternative_id: alternativeId },
  })
}

export { ApiError }
