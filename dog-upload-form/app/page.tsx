import DogUploadForm from "@/components/dog-upload-form"

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 bg-gradient-to-br from-lavender-100 to-yellow-50">
      <div className="w-full max-w-md">
        <DogUploadForm />
      </div>
    </main>
  )
}

