// TS async functions to fetch from FastApi server
import axios from 'axios'
import { AxiosResponse } from 'axios'

export const API_BASE_URL = 'http://localhost:8001'

// Fetch recommendations from the FastAPI server
export async function getRecommendations(
  papers: string[]
): Promise<AxiosResponse<{ recommendations: string[] }>> {
  try {
    const response = await axios.post(`${API_BASE_URL}/recommendations`, {
      papers,
    })
    return response
  } catch (error) {
    if (axios.isAxiosError(error)) {
      if (error.response) {
        console.log(error.response.data, error.response.status)
        throw new Error(`API error: ${error.response.status}`)
      } else if (error.request) {
        console.log(error.request)
        throw new Error('No response received from server')
      } else {
        console.log('API Error:', error.message)
        throw new Error(`Request error: ${error.message}`)
      }
    }
    throw error // Re-throw any other errors
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
      if (error.response) {
        console.log(error.response.data, error.response.status)
        throw new Error(`API error: ${error.response.status}`)
      } else if (error.request) {
        console.log(error.request)
        throw new Error('No response received from server')
      } else {
        console.log('API Error:', error.message)
        throw new Error(`Request error: ${error.message}`)
      }
    }
    throw error // Re-throw any other errors
  }
}
