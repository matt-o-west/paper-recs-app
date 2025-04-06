import RemoveButton from './RemoveButton'

export default function PaperInputs({ papers, setPapers }) {
  const handleChange = (index: number, value: string) => {
    const newPapers = [...papers]
    newPapers[index] = value
    setPapers(newPapers)
  }

  const handleAddPaper = () => {
    if (papers.length >= 5) {
      // Replace this with a modal or toast notification
      alert('You can only add up to 5 papers.')
      return
    }

    setPapers([...papers, ''])
  }

  return (
    <div className='flex flex-col gap-4'>
      {papers.map((paper, index) => (
        <div key={index} className='flex items-center gap-2'>
          <input
            type='text'
            name={`paper-${index}`} // Use this to gather the input data
            placeholder='Enter DOI ID'
            value={paper}
            onChange={(e) => handleChange(index, e.target.value)}
            required
            className='border border-gray-300 rounded px-2 py-1 w-full'
          />
          <RemoveButton index={index} papers={papers} setPapers={setPapers} />
        </div>
      ))}
      {/* Hidden input to store all papers as JSON */}
      <input
        type='hidden'
        name='papers'
        value={JSON.stringify(papers.filter((p) => p.trim() !== ''))}
      />

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
