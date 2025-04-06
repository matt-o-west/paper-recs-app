import PapersForm from '@/components/PapersForm'

export default function Home() {
  return (
    <div className='grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]'>
      <main className='flex flex-col gap-[32px] row-start-2 items-center sm:items-start'>
        <h1 className='text-2xl font-extrabold'>PaperScout</h1>
        <p className='text-lg text-gray-200 md:w-2xl lg:w-5xl'>
          This is a web application that takes academic literature submitted by
          the user via DOI IDs. It runs them through an LLM via Groq, performs
          analysis and suggests other papers based on those most commonly cited
          between the input papers. Click the ReadMe below to learn more.
        </p>
        <PapersForm />

        <div className='flex gap-4 items-center flex-col sm:flex-row'>
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
          Team Groqstars⭐: Gannon, Matt, Sake and Ameya
        </p>
      </footer>
    </div>
  )
}
