// Server actions -> send data to the server etc - if this doesn't work use route handlers
'use server'
import { getRecommendations } from '@/services/api/api'

export async function handleSubmit() {
  const formData = new FormData()
  const papers = formData.get('papers') as string

  // Handle the form submission logic here
  console.log('Papers:', papers)

  const response = await getRecommendations([papers])
  console.log('Response:', response)
}
