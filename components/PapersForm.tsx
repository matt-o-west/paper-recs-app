'use client'
import axios from 'axios'
import PaperInputs from './PaperInputs'
//import { handleSubmit } from '@/actions/actions'
import SubmitButton from './SubmitButton'
import { useState } from 'react'

interface Recommendations {
  recommendations: string[]
}

export default function PapersForm() {
  const [papers, setPapers] = useState<string[]>([''])
  const [isLoading, setIsLoading] = useState(false)
  const [recommendations, setRecommendations] = useState<Recommendations>([''])
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      // Call route handler
      const response = await axios.post('/submitPapers', {
        papers,
      })

      if (response.status !== 200) {
        throw new Error('Failed to submit papers')
      }

      const data = response.data
      console.log('Response data:', data)
      setRecommendations(data)
    } catch (err) {
      console.error('Error:', err)
      setError(err instanceof Error ? err.message : 'An unknown error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className='flex flex-col gap-4'>
      <label htmlFor='papers' className='text-lg font-semibold'>
        Enter DOIs of papers:
      </label>
      {/* Add input fields for each PID */}
      <PaperInputs papers={papers} setPapers={setPapers} />
      <SubmitButton />
    </form>
  )
}
