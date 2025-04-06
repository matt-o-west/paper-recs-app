// TS async functions to fetch from FastApi server
import axios from 'axios'
import { AxiosResponse } from 'axios'

export const API_BASE_URL = 'http://localhost:8000'

// Fetch recommendations from the FastAPI server
export async function submitPapers(papers: string[]) {
  try {
    console.log('Sending papers to API:', papers)
    const response = await axios.post(`${API_BASE_URL}/recommendations/`, {
      papers,
    })

    return response.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('API error:', error.response?.data || error.message)
      throw new Error(`API error: ${error.response?.status || error.message}`)
    }

    console.error('Non-Axios error:', error)
    throw error
  }
}

// Test request
export async function getHelloWorld(): Promise<
  AxiosResponse<{ Hello: string }>
> {
  try {
    return await axios(`${API_BASE_URL}/`)
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('API error:', error.response?.data || error.message)
      throw new Error(`API error: ${error.response?.status || error.message}`)
    }
    throw error // Re-throw any other errors
  }
}
