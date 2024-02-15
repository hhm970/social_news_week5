function getUrl() {
  return window.location.href
}

function resetStories() {
  const stories = document.getElementById('stories')
  stories.innerHTML = ''
}

function createVoteButton(id, text) {
  const button = document.createElement('button')
  button.id = id
  button.className = 'vote-button'
  button.addEventListener('click', handleVote)
  button.innerText = text
  return button
}

function createDeleteButton(id, text) {
  const button = document.createElement('button')
  button.id = id
  button.className = 'vote-button'
  button.addEventListener('click', handleDelete)
  button.innerText = text
  return button
}

function createEditButton(id, url, text) {
  const elemID = id.split('-')
  const idNo = elemID[0]

  const button = document.createElement('button')
  button.id = id
  button.className = 'vote-button'
  button.addEventListener('click', async () => {
    await handleEdit(idNo, url, text)
  })
  button.innerText = '🖊️'
  return button
}

async function handleEdit(id, url, title) {
  const newUrl = prompt('Enter new URL', url)
  const newTitle = prompt('Enter new Title', title)

  const res = await fetch(`${getUrl()}/stories/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: newUrl, title: newTitle }),
    credentials: 'include'
  })

  if (res.status >= 300) {
    onError(res)
  }

  const data = await res.json()

  if (data.error || data.message) {
    alert(data.message)
  }

  getStories()
}

async function getStories() {
  const searchTerm = document.getElementById('search_input').value
  const sort = document.getElementById('sort').value
  const order = document.getElementById('order').value
  let url = `${getUrl()}/stories?sort=${sort}&order=${order}`

  if (searchTerm) {
    url += `&search=${searchTerm}`
  }

  console.log(`Stories Requested From: ${url}`)

  const res = await fetch(url, {
    method: 'GET',
    credentials: 'include'
  })

  if (res.status >= 300 ) {
    onError(res)
  }

  const data = await res.json()

  console.log('Data Fetched from Server: ')
  console.log(data)

  if (data.error || data.message) {
    alert(data.message)
  }

  resetStories()
  displayStories(data)
}

function onError(response) {
  alert(
    `Error Code: ${response.status}\nError Message: ${response.statusText}\nFrom URL: ${response.url}`
  )
}

async function handleVote(e) {
  const elemID = e.target.id.split('-')
  const id = elemID[0]
  const direction = elemID[1]

  const rawRes = await fetch(`${getUrl()}/stories/${id}/votes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ direction }),
    credentials: 'include'
  })

  if (rawRes.status >= 300) {
    onError(rawRes)
  }

  const data = await rawRes.json()

  if (data.error || data.message) {
    alert(data.message)
  }

  getStories()
}

async function handleDelete(e) {
  const elemID = e.target.id.split('-')
  const id = elemID[0]
  const direction = elemID[1]

  console.log(`'${direction}' Delete Button Clicked`)

  const rawRes = await fetch(`${getUrl()}/stories/${id}`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include'
  })

  if (rawRes.status >= 300) {
    onError(rawRes)
  }

  const data = await rawRes.json()

  console.log('Delete Response Received: ')

  if (data.error || data.message) {
    alert(data.message)
  }

  getStories()
}

function getContentComponent(story) {
  const contentWrapper = document.createElement('div')

  const link = document.createElement('a')
  link.href = story.url
  link.innerText = story.title

  const score = document.createElement('span')
  score.innerText = `(${story.score} points)`

  contentWrapper.append(link, score)
  return contentWrapper
}

function getVotesComponent(story) {
  const voteWrapper = document.createElement('div')
  voteWrapper.classList = 'voteWrapper'

  const upvoteButton = createVoteButton(`${story.id}-up`, '⬆')
  const downvoteButton = createVoteButton(`${story.id}-down`, '⬇')
  const deleteButton = createDeleteButton(`${story.id}-delete`, '❌')
  const editButton = createEditButton(
    `${story.id}-delete`,
    story.url,
    story.title
  )

  voteWrapper.append(upvoteButton, downvoteButton, deleteButton, editButton)
  return voteWrapper
}

function createStory(story) {
  const stories = document.getElementById('stories')
  const storyWrapper = document.createElement('div')
  storyWrapper.classList = 'storyWrapper'

  const contentWrapper = getContentComponent(story)
  const voteWrapper = getVotesComponent(story)

  storyWrapper.append(voteWrapper, contentWrapper)
  stories.append(storyWrapper)
}

function displayStories(stories) {
  stories.forEach(createStory)
}

function setupSelects() {
  const sort = document.getElementById('sort')
  const order = document.getElementById('order')

  sort.onchange = () => {
    getStories()
  }
  order.onchange = () => {
    getStories()
  }
}

function setupSearch() {
  const search = document.getElementById('search')

  search.onclick = () => {
    getStories()
  }
}

window.onload = async function load() {
  getStories()
  setupSelects()
  setupSearch()
}
