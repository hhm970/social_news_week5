function onError(response) {
  alert(
    `Error Code: ${response.status}\nError Message: ${response.statusText}\nFrom URL: ${response.url}`
  )
}

window.onload = async function load() {
  const submitComponent = document.getElementById('submit_scrape')

  submitComponent.onclick = async function submit() {
    const urlComponent = document.getElementById('url')

    const url = urlComponent.value

    const response = await fetch('/scrape', {
      method: 'POST',
      body: JSON.stringify({ url }),
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (response.status !== 200) {
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
