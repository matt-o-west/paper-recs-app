import PapersForm from '@/components/PapersForm'
import Image from 'next/image'
import Link from 'next/link'

export default function Home() {
  return (
    <div className='grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]'>
      <main className='flex flex-col gap-[32px] row-start-2 items-center sm:items-start'>
        <Image
          className='dark:invert'
          src='/next.svg'
          alt='Next.js logo'
          width={180}
          height={38}
          priority
        />
        <p className='text-lg text-gray-200 md:w-2xl lg:w-5xl'>
          This is a web application that takes academic literature submitted by
          the user via DOI IDs. It runs them through an LLM via Groq, performs
          analysis and suggests other papers based on those most commonly cited
          between the input papers. Click the ReadMe below to learn more.
        </p>
        <PapersForm />

        <div className='flex gap-4 items-center flex-col sm:flex-row'>
          <Link
            href='/test'
            className='bg-slate-500 text-white px-4 py-2 rounded hover:bg-slate-300'
          >
            Test Route
          </Link>
          <a
            className='rounded-full border border-solid border-black/[.08] dark:border-white/[.145] transition-colors flex items-center justify-center hover:bg-[#f2f2f2] dark:hover:bg-[#1a1a1a] hover:border-transparent font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 w-full sm:w-auto md:w-[158px]'
            href='https://github.com/matt-o-west/paper-recs-app/blob/main/README.md'
            target='_blank'
            rel='noopener noreferrer'
          >
            ReadMe.md
          </a>
        </div>
      </main>
      <footer className='row-start-3 flex gap-[24px] flex-wrap items-center justify-center'>
        <p className='text-sm text-gray-500'>
          Made with <span className='text-red-500'>❤️</span> for Beaverhacks.
          Team: Gannon, Loaf, Sake and Paradisea
        </p>
      </footer>
    </div>
  )
}
