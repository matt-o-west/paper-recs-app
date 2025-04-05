import { useState } from 'react'

export default function PaperInputs() {
  const [papers, setPapers] = useState<string[]>([''])
  const handleChange = (index: number, value: string) => {
    const newPapers = [...papers]
    newPapers[index] = value
    setPapers(newPapers)
  }

  const handleAddPaper = () => {
    if (papers.length >= 5) {
      // Replace this with a modal or toast notification
      alert('You can only add up to 5 papers.')
    }

    setPapers([...papers, ''])
  }

  const handleRemovePaper = (index: number) => {
    const newPapers = papers.filter((_, i) => i !== index)
    setPapers(newPapers)
  }

  return (
    <div className='flex flex-col gap-4'>
      {papers.map((paper, index) => (
        <div key={index} className='flex items-center gap-2'>
          <input
            type='text'
            value={paper}
            onChange={(e) => handleChange(index, e.target.value)}
            className='border border-gray-300 rounded px-2 py-1 w-full'
          />
          <button
            type='button'
            onClick={() => handleRemovePaper(index)}
            className='bg-red-500 text-white px-2 py-1 rounded hover:bg-red-600'
          >
            Remove
          </button>
        </div>
      ))}
      <button
        type='button'
        onClick={handleAddPaper}
        className='bg-slate-500 text-white px-4 py-2 rounded hover:bg-slate-400'
      >
        Add Paper
      </button>
    </div>
  )
}
