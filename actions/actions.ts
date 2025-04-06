// Server actions -> send data to the server etc - if this doesn't work use route handlers
'use server'
import { submitPapers } from '@/services/api/api'

export async function handleSubmit() {
  const formData = new FormData()
  const papers = formData.get('papers') as string
  if (!papers) {
    console.error('No papers found in form data')
    return
  }

  try {
    const parsedPapers = JSON.parse(papers)
    console.log('Parsed Papers:', parsedPapers)
  } catch (error) {
    if (!Array.isArray(papers) || papers.length === 0) {
      console.error('Invalid paper data:', papers, 'Error:', error)
      return { error: 'Please add at least one valid paper' }
    }

    console.error('Error parsing papers:', error)
    return
  }
  // Handle the form submission logic here
  console.log('Papers:', papers)

  const response = await submitPapers([papers])
  console.log('Response:', response)
}
