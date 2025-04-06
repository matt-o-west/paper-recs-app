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

    const response = await axios.post('/submitPapers', {
      papers,
    })
    console.log('Response:', response)

    if (response.status !== 200) {
      setError('Failed to fetch recommendations')
      setIsLoading(false)
      return
    }
    setRecommendations(response.data.papers)
    setIsLoading(false)
    console.log('Recommendations:', recommendations)
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
