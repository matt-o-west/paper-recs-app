'use client'
import PaperInputs from './PaperInputs'
import { handleSubmit } from '@/actions/actions'

export default function PapersForm() {
  return (
    <form onSubmit={handleSubmit} className='flex flex-col gap-4'>
      <label htmlFor='papers' className='text-lg font-semibold'>
        Enter DOIs of papers:
      </label>
      {/* Add input fields for each PID */}
      <PaperInputs />
      <button
        type='submit'
        className='bg-slate-500 text-white px-4 py-2 rounded-sm hover:bg-slate-400'
      >
        Submit
      </button>
    </form>
  )
}
