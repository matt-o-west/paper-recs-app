import { useFormStatus } from 'react-dom'

export default function SubmitButton() {
  const { pending } = useFormStatus()

  return (
    <button
      type='submit'
      aria-disabled={pending}
      className='bg-indigo-700 text-white px-4 py-2 rounded-sm hover:bg-indigo-400'
    >
      Submit
    </button>
  )
}
