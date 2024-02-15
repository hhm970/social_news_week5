function onError(response) {
  alert(
    `Error Code: ${response.status}\nError Message: ${response.statusText}\nFrom URL: ${response.url}`
  )
}

window.onload = async function load() {
  const urlComponent = document.getElementById('url')
  const titleComponent = document.getElementById('title')
  const submitComponent = document.getElementById('submit_story')

  submitComponent.onclick = async function submit() {
    const url = urlComponent.value
    const title = titleComponent.value

    const response = await fetch('/stories', {
      method: 'POST',
      body: JSON.stringify({ url, title }),
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (response.status >= 300) {
      onError(response)
    }

    const data = await response.json()

    if (data.error) {
      alert(data.message)
    } else {
      window.location.href = '/'
    }
  }
}
