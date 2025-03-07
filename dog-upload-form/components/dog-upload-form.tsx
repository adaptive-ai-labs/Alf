"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { Camera, PawPrintIcon as Paw, StarIcon, ShoppingCartIcon } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"

// Sample list of dog breeds
const DOG_BREEDS = [
  "Labrador Retriever",
  "German Shepherd",
  "Golden Retriever",
  "Bulldog",
  "Beagle",
  "Poodle",
  "Rottweiler",
  "Yorkshire Terrier",
  "Boxer",
  "Dachshund",
  "Shih Tzu",
  "Siberian Husky",
  "Chihuahua",
  "Great Dane",
  "Other",
]

// Type definitions for recommendations
interface ProductReview {
  content: string;
}

interface Recommendation {
  product_id: string;
  title: string;
  url: string;
  price: string;
  image_url: string;
  rating: number | null;
  reviews: string[];
  recommendation_reason: string;
  suitability_score: number;
}

interface GroomerRecommendation {
  groomer_id: string;
  name: string;
  url: string;
  location: string;
  services: string[];
  rating: number | null;
  reviews: string[];
  recommendation_reason: string;
  suitability_score: number;
  image_url: string | null;
  contact_info: string | null;
}

interface RecommendationResponse {
  success: boolean;
  query: string;
  dog_breed: string;
  age: string;
  count: number;
  recommendations: Recommendation[];
  summary: string;
  groomer_count?: number;
  groomer_recommendations?: GroomerRecommendation[];
  groomer_summary?: string;
}

export default function DogUploadForm() {
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [breed, setBreed] = useState<string>("")
  const [age, setAge] = useState<string>("adult")
  const [isUploading, setIsUploading] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [recommendations, setRecommendations] = useState<RecommendationResponse | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [query, setQuery] = useState<string>("dog food")
  const [activeTab, setActiveTab] = useState<"products" | "groomers">("products")
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setIsUploading(true)
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result as string)
        setIsUploading(false)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    console.log("Form submitted, fetching recommendations for:", { breed, age, query })
    setIsLoading(true)
    setErrorMessage(null)
    setRecommendations(null)
    
    // Create a test element in the DOM to show the request is being made
    const testDiv = document.createElement('div')
    testDiv.id = 'api-request-log'
    testDiv.style.position = 'fixed'
    testDiv.style.bottom = '10px'
    testDiv.style.right = '10px'
    testDiv.style.padding = '10px'
    testDiv.style.background = 'rgba(0,0,0,0.8)'
    testDiv.style.color = 'white'
    testDiv.style.zIndex = '9999'
    testDiv.style.borderRadius = '5px'
    testDiv.textContent = `Requesting recommendations for ${breed} (${age})...`
    document.body.appendChild(testDiv)
    
    try {
      // Format the dog breed to match expected format (lowercase)
      const formattedBreed = breed.toLowerCase()
      
      // Build the API URL - ensure port 8000 is correct and accessible
      const apiUrl = `http://localhost:8000/api/recommend?query=${encodeURIComponent(query)}&dog_breed=${encodeURIComponent(formattedBreed)}&age=${encodeURIComponent(age.toLowerCase())}`
      console.log("Calling API at:", apiUrl)
      testDiv.textContent += `\nAPI URL: ${apiUrl}`
      
      // Simpler fetch call with minimal options
      const response = await fetch(apiUrl)
      
      testDiv.textContent += `\nResponse status: ${response.status}`
      
      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`)
      }
      
      const data = await response.json()
      console.log("Received data:", data)
      testDiv.textContent += `\nReceived ${data.recommendations?.length || 0} recommendations`
      setRecommendations(data)
      
      // Remove the test element after 3 seconds
      setTimeout(() => {
        document.body.removeChild(testDiv)
      }, 3000)
    } catch (error) {
      console.error('Error fetching recommendations:', error)
      const errorMsg = `Failed to fetch recommendations: ${error instanceof Error ? error.message : 'Unknown error'}`
      setErrorMessage(errorMsg)
      
      if (document.getElementById('api-request-log')) {
        testDiv.textContent += `\nERROR: ${errorMsg}`
        testDiv.style.background = 'rgba(255,0,0,0.8)'
        // Remove after 5 seconds on error
        setTimeout(() => {
          if (document.getElementById('api-request-log')) {
            document.body.removeChild(testDiv)
          }
        }, 5000)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const clearImage = () => {
    setImagePreview(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  return (
    <Card className="w-full border-none shadow-lg bg-gradient-to-br from-lavender-50 to-yellow-50 rounded-xl overflow-hidden">
      <CardHeader className="pb-2 pt-6">
        <CardTitle className="text-center text-2xl font-bold text-lavender-700 flex items-center justify-center gap-2">
          <Paw className="h-6 w-6" />
          <span>Alf</span>
        </CardTitle>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-6 px-6">
          {/* Image Upload */}
          <div className="flex flex-col items-center justify-center pt-2">
            <div
              className={`
                relative w-32 h-32 rounded-full overflow-hidden 
                ${!imagePreview ? "bg-gradient-to-br from-lavender-200 to-yellow-100 border-4 border-white shadow-md" : ""}
                transition-all duration-300 hover:shadow-lg
              `}
              onClick={() => fileInputRef.current?.click()}
            >
              {imagePreview ? (
                <img
                  src={imagePreview || "/placeholder.svg"}
                  alt="Dog preview"
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <Camera className="h-10 w-10 text-lavender-500 mb-1" />
                  <p className="text-xs text-lavender-600 font-medium">Add photo</p>
                </div>
              )}

              <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-20 transition-all duration-300 flex items-center justify-center">
                {imagePreview && (
                  <Button
                    type="button"
                    variant="secondary"
                    size="sm"
                    className="opacity-0 hover:opacity-100 transition-opacity duration-300 bg-white/80 hover:bg-white text-lavender-700"
                    onClick={(e) => {
                      e.stopPropagation()
                      clearImage()
                    }}
                  >
                    Change
                  </Button>
                )}
              </div>
            </div>
            <input
              ref={fileInputRef}
              id="dog-picture"
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleFileChange}
              required
            />
            <p className="mt-3 text-sm text-lavender-600 font-medium">
              {isUploading ? "Uploading..." : imagePreview ? "Looking good!" : "Tap to add your dog's photo"}
            </p>
          </div>

          {/* Breed Selection */}
          <div className="space-y-2">
            <Label htmlFor="breed" className="text-lavender-700 font-medium">
              Breed
            </Label>
            <Select value={breed} onValueChange={setBreed} required>
              <SelectTrigger id="breed" className="bg-white/80 border-lavender-200 focus:ring-lavender-300">
                <SelectValue placeholder="What breed is your dog?" />
              </SelectTrigger>
              <SelectContent className="bg-white/95">
                {DOG_BREEDS.map((breed) => (
                  <SelectItem key={breed} value={breed}>
                    {breed}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Search Query */}
          <div className="space-y-2">
            <Label htmlFor="query" className="text-lavender-700 font-medium">
              Product to Search
            </Label>
            <Select value={query} onValueChange={setQuery} required>
              <SelectTrigger id="query" className="bg-white/80 border-lavender-200 focus:ring-lavender-300">
                <SelectValue placeholder="What are you looking for?" />
              </SelectTrigger>
              <SelectContent className="bg-white/95">
                <SelectItem value="dog food">Dog Food</SelectItem>
                <SelectItem value="dog treats">Dog Treats</SelectItem>
                <SelectItem value="dog toys">Dog Toys</SelectItem>
                <SelectItem value="dog accessories">Dog Accessories</SelectItem>
                <SelectItem value="dog grooming">Dog Grooming Products</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Age Selection */}
          <div className="space-y-2">
            <Label className="text-lavender-700 font-medium">Age</Label>
            <RadioGroup value={age} onValueChange={setAge} className="flex gap-4 justify-center p-2">
              <div
                className="flex flex-col items-center space-y-1 bg-white/60 hover:bg-white/80 transition-colors rounded-lg p-3 cursor-pointer"
                onClick={() => setAge("puppy")}
              >
                <RadioGroupItem value="puppy" id="puppy" className="text-yellow-400" />
                <Label htmlFor="puppy" className="cursor-pointer text-lavender-600">
                  Puppy
                </Label>
              </div>
              <div
                className="flex flex-col items-center space-y-1 bg-white/60 hover:bg-white/80 transition-colors rounded-lg p-3 cursor-pointer"
                onClick={() => setAge("adult")}
              >
                <RadioGroupItem value="adult" id="adult" className="text-yellow-400" />
                <Label htmlFor="adult" className="cursor-pointer text-lavender-600">
                  Adult
                </Label>
              </div>
            </RadioGroup>
          </div>
        </CardContent>
        <CardFooter className="px-6 pb-6">
          <Button
            type="submit"
            className="w-full bg-gradient-to-r from-lavender-500 to-lavender-600 hover:from-lavender-600 hover:to-lavender-700 text-white font-medium py-5 rounded-xl shadow-md hover:shadow-lg transition-all duration-300"
            disabled={!breed || isLoading}
          >
            {isLoading ? "Finding Recommendations..." : "Get Recommendations"}
          </Button>
        </CardFooter>
      </form>
      
      {/* Display recommendations - OUTSIDE the form */}
      {recommendations && (
        <div className="pt-4 px-6 pb-6">
          <div className="p-4 bg-white/80 rounded-xl shadow-md">
            {/* Tab navigation - completely separate from the form */}
            <div className="flex border-b border-lavender-200 mb-4">
              <button
                onClick={() => setActiveTab("products")}
                type="button"
                className={`py-2 px-4 font-medium text-sm ${activeTab === "products"
                  ? "text-lavender-700 border-b-2 border-lavender-500" 
                  : "text-gray-500 hover:text-lavender-600"}`}
              >
                <ShoppingCartIcon className="h-4 w-4 inline mr-1" />
                Products ({recommendations.count})
              </button>
              
              {recommendations.groomer_recommendations && recommendations.groomer_recommendations.length > 0 && (
                <button
                  onClick={() => setActiveTab("groomers")}
                  type="button"
                  className={`py-2 px-4 font-medium text-sm ${activeTab === "groomers"
                    ? "text-lavender-700 border-b-2 border-lavender-500" 
                    : "text-gray-500 hover:text-lavender-600"}`}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="h-4 w-4 inline mr-1">
                    <path d="M8.5 2a6.5 6.5 0 0 0 0 13h7a6.5 6.5 0 0 0 0-13h-7z"></path>
                    <path d="M12.5 6.5a2 2 0 0 1 0 4 2 2 0 0 1 0-4z"></path>
                    <path d="M8.5 15v7"></path>
                    <path d="M15.5 15v7"></path>
                  </svg>
                  Groomers ({recommendations.groomer_count})
                </button>
              )}
            </div>
              
              {/* Product recommendations */}
              {activeTab === "products" && (
                <>
                  <h3 className="text-lg font-bold text-lavender-700 mb-2">Product Recommendations</h3>
                  <p className="text-sm text-gray-700 mb-4">{recommendations.summary}</p>
                  
                  <ScrollArea className="h-80 rounded-md border border-lavender-100 p-4">
                    <div className="space-y-6">
                      {recommendations.recommendations.map((item, index) => (
                        <div key={index} className="border border-lavender-100 rounded-lg p-4 bg-white">
                          <div className="flex gap-4 items-start">
                            <div className="w-24 h-24 rounded-md overflow-hidden bg-gray-100 flex-shrink-0">
                              <img 
                                src={item.image_url.replace('{width}', '240')} 
                                alt={item.title}
                                className="w-full h-full object-cover"
                                onError={(e) => {
                                  // Fallback image if the product image fails to load
                                  (e.target as HTMLImageElement).src = '/placeholder.svg';
                                }}
                              />
                            </div>
                            <div className="flex-1">
                              <div className="flex justify-between items-start">
                                <h4 className="font-medium text-lavender-700">{item.title}</h4>
                                <Badge variant="outline" className="ml-2 bg-yellow-50">
                                  Score: {item.suitability_score.toFixed(1)}/10
                                </Badge>
                              </div>
                              <p className="text-lavender-900 font-semibold mt-1">{item.price}</p>
                              <p className="text-sm text-gray-600 mt-2">{item.recommendation_reason}</p>
                              
                              <div className="flex gap-2 mt-3">
                                <a 
                                  href={item.url} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center gap-1 text-xs bg-lavender-100 hover:bg-lavender-200 text-lavender-700 px-3 py-1 rounded-full transition-colors"
                                >
                                  <ShoppingCartIcon className="h-3 w-3" /> Shop
                                </a>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </>
              )}
              
              {/* Groomer recommendations */}
              {activeTab === "groomers" && recommendations.groomer_recommendations && (
                <>
                  <h3 className="text-lg font-bold text-lavender-700 mb-2">Groomer Recommendations</h3>
                  <p className="text-sm text-gray-700 mb-4">{recommendations.groomer_summary}</p>
                  
                  <ScrollArea className="h-80 rounded-md border border-lavender-100 p-4">
                    <div className="space-y-6">
                      {recommendations.groomer_recommendations.map((groomer, index) => (
                        <div key={index} className="border border-lavender-100 rounded-lg p-4 bg-white">
                          <div className="flex gap-4 items-start">
                            <div className="w-24 h-24 rounded-md overflow-hidden bg-gray-100 flex-shrink-0 flex items-center justify-center text-lavender-300">
                              {groomer.image_url ? (
                                <img 
                                  src={groomer.image_url} 
                                  alt={groomer.name}
                                  className="w-full h-full object-cover"
                                  onError={(e) => {
                                    // Fallback icon if the groomer image fails to load
                                    (e.target as HTMLImageElement).src = '/placeholder.svg';
                                  }}
                                />
                              ) : (
                                <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                  <path d="M8.5 2a6.5 6.5 0 0 0 0 13h7a6.5 6.5 0 0 0 0-13h-7z"></path>
                                  <path d="M12.5 6.5a2 2 0 0 1 0 4 2 2 0 0 1 0-4z"></path>
                                  <path d="M8.5 15v7"></path>
                                  <path d="M15.5 15v7"></path>
                                </svg>
                              )}
                            </div>
                            <div className="flex-1">
                              <div className="flex justify-between items-start">
                                <h4 className="font-medium text-lavender-700">{groomer.name}</h4>
                                <Badge variant="outline" className="ml-2 bg-yellow-50">
                                  Score: {groomer.suitability_score.toFixed(1)}/10
                                </Badge>
                              </div>
                              <p className="text-lavender-900 font-semibold mt-1">{groomer.location}</p>
                              <p className="text-sm text-gray-600 mt-2">{groomer.recommendation_reason}</p>
                              
                              {groomer.services && groomer.services.length > 0 && (
                                <div className="mt-2">
                                  <p className="text-xs text-gray-500 mb-1">Services:</p>
                                  <div className="flex flex-wrap gap-1">
                                    {groomer.services.map((service, idx) => (
                                      <span key={idx} className="text-xs bg-lavender-50 text-lavender-600 px-2 py-1 rounded-full">
                                        {service}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}
                              
                              {groomer.contact_info && (
                                <p className="text-xs text-gray-500 mt-2">
                                  Contact: {groomer.contact_info}
                                </p>
                              )}
                              
                              <div className="flex gap-2 mt-3">
                                <a 
                                  href={groomer.url} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="inline-flex items-center gap-1 text-xs bg-lavender-100 hover:bg-lavender-200 text-lavender-700 px-3 py-1 rounded-full transition-colors"
                                >
                                  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                                  </svg>
                                  Visit Profile
                                </a>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </>
              )}
            </div>
          </div>
        )}
        
      {/* Display error message - OUTSIDE the form */}
      {errorMessage && (
        <div className="px-6 pb-6">
          <div className="p-4 bg-red-50 border border-red-100 rounded-lg text-red-700">
            {errorMessage}
          </div>
        </div>
      )}
    </Card>
  )
}

