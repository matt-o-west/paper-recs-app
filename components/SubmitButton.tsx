import { useFormStatus } from 'react-dom'

export default function SubmitButton() {
  const { pending } = useFormStatus()

  return (
    <button
      type='submit'
      aria-disabled={pending}
      className='bg-slate-500 text-white px-4 py-2 rounded-sm hover:bg-slate-400'
    >
      Submit
    </button>
  )
}
