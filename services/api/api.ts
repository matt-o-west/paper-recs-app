// TS async functions to fetch from FastApi server
import axios from 'axios'
import { AxiosResponse } from 'axios'

export const API_BASE_URL = 'http://localhost:8000'

export interface Paper {
  doi: string
  name?: string
  abstract?: string
  references?: string[]
  cited_by?: string[]
}

export interface PapersResponse {
  papers: Paper[]
  status?: number
}

// Fetch recommendations from the FastAPI server
export async function submitPapers(doiStrings: string[]) {
  try {
    // Map over DOIs and format for backend
    const paperObjects = doiStrings.map((doi) => ({ doi }))

    console.log('Sending papers to API:', paperObjects)

    // Submit papers to be processed as post request
    const submitResponse = await axios.post(`${API_BASE_URL}/papers`, {
      papers: paperObjects,
    })

    // Check if there were any invalid papers
    if (submitResponse.data.status === 400) {
      throw new Error(`Invalid DOIs: ${submitResponse.data.papers.join(', ')}`)
    }

    // Then, get the recommendations - this should fulfill if the above was successful
    const recommendationsResponse = await axios.get(
      `${API_BASE_URL}/recommendations`
    )

    return recommendationsResponse.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('API error details:', {
        status: error.response?.status,
        data: error.response?.data,
      })

      throw new Error(
        `API error: ${error.response?.status || ''} ${JSON.stringify(
          error.response?.data || error.message
        )}`
      )
    }
    throw error
  }
}

// Mock Endpoint
export async function getPapers(): Promise<Paper[]> {
  try {
    const response = await axios.get(`${API_BASE_URL}/papers`)
    return response.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      console.error('API error:', error.response?.data || error.message)
      throw new Error(`API error: ${error.response?.status || error.message}`)
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
      console.error('API error:', error.response?.data || error.message)
      throw new Error(`API error: ${error.response?.status || error.message}`)
    }
    throw error // Re-throw any other errors
  }
}
