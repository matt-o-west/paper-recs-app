// TS async functions to fetch from FastApi server
import axios from 'axios'
import { AxiosResponse } from 'axios'

export const API_BASE_URL = 'http://localhost:8000'

// Fetch recommendations from the FastAPI server
export async function submitPapers(papers: string[]) {
  try {
    // If formatting needs to happen, do it here or route handler
    /*const formattedPapers = papers.map((doi) => {
      // If DOI doesn't have the doi: prefix, add it
      if (!doi.startsWith('doi:') && /^10\.\d{4,9}\/..test(doi)) {
        return `doi:${doi}`
      }
      return doi
    })*/

    console.log('Sending papers to API:', papers)

    const response = await axios.post(`${API_BASE_URL}/recommendations/`, {
      papers,
    })

    //console.log('API response:', response.data)
    return response.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      // More detailed error logging for debugging
      console.error('API error details:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: {
          url: error.config?.url,
          method: error.config?.method,
          data: error.config?.data,
        },
      })

      throw new Error(
        `API error: ${error.response?.status || ''} ${
          error.response?.statusText || ''
        } ${JSON.stringify(error.response?.data || error.message)}`
      )
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
