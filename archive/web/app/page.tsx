'use client'

import { useState } from 'react'
import Header from '../components/Header'
import IdeaForm from '../components/IdeaForm'
import ProgressView from '../components/ProgressView'
import ResultsView from '../components/ResultsView'
import ErrorView from '../components/ErrorView'

type ViewType = 'input' | 'progress' | 'results' | 'error'

export default function Home() {
  const [currentView, setCurrentView] = useState<ViewType>('input')
  const [taskId, setTaskId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleStartGeneration = (id: string) => {
    setTaskId(id)
    setCurrentView('progress')
    setError(null)
  }

  const handleDirectComplete = (result: any) => {
    if (result.task_id) {
      setTaskId(result.task_id)
    }
    setCurrentView('results')
    setError(null)
  }

  const handleError = (errorMsg: string) => {
    setError(errorMsg)
    setCurrentView('error')
  }

  const handleComplete = () => {
    setCurrentView('results')
  }

  const handleReset = () => {
    setCurrentView('input')
    setTaskId(null)
    setError(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <Header />
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        {currentView === 'input' && (
          <IdeaForm 
            onStartGeneration={handleStartGeneration}
            onComplete={handleDirectComplete}
            onError={handleError}
          />
        )}
        
        {currentView === 'progress' && taskId && (
          <ProgressView 
            taskId={taskId}
            onComplete={handleComplete}
            onError={handleError}
          />
        )}
        
        {currentView === 'results' && taskId && (
          <ResultsView 
            taskId={taskId}
            onReset={handleReset}
          />
        )}
        
        {currentView === 'error' && (
          <ErrorView 
            error={error}
            onReset={handleReset}
          />
        )}
      </main>
    </div>
  )
}
