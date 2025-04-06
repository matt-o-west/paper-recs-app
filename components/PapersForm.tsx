'use client'
import axios from 'axios'
import PaperInputs from './PaperInputs'
//import { handleSubmit } from '@/actions/actions'
import SubmitButton from './SubmitButton'
import { useState } from 'react'
import ResultCard from './ResultCard'

export interface Paper {
  doi: string
  name: string
  abstract: string
  references: string[]
  cited_by: string[]
}

export default function PapersForm() {
  const [papers, setPapers] = useState<string[]>([''])
  const [isLoading, setIsLoading] = useState(false)
  const [recommendations, setRecommendations] = useState<Paper[]>([])
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
    <div
      className={`${
        recommendations.length > 0 ? 'grid-cols-2' : 'grid-cols-1 md:min-w-xl'
      } p-8 mx-auto bg-slate-800 rounded-md max-w-md md:max-w-5xl`}
    >
      <form
        onSubmit={handleSubmit}
        className='flex flex-col gap-4 max-w-2xl mx-0'
      >
        <label htmlFor='papers' className='text-lg font-semibold'>
          Enter DOIs of papers:
        </label>
        {/* Add input fields for each PID */}
        <PaperInputs papers={papers} setPapers={setPapers} />
        <SubmitButton />
        {/* Hidden input to store all papers as JSON would go here, if we were using a server action */}
      </form>
      {/*Replace this with a real load state*/}
      {isLoading && (
        <div className='flex items-center justify-center mt-4'>
          <span className='text-gray-500'>Loading...</span>
        </div>
      )}
      {error && (
        <div className='mt-4 p-3 bg-red-50 border border-red-200 rounded text-red-700'>
          {error}
        </div>
      )}
      {recommendations.length > 0 && (
        <div className='mt-8 border-t pt-6'>
          <h2 className='text-xl font-bold mb-4'>Recommendations:</h2>
          <div className='space-y-6'>
            {recommendations.map((paper, index) => (
              <ResultCard
                paper={paper}
                index={index}
                key={paper.doi || index}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
