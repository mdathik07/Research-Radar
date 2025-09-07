import { useState, useEffect } from "react"
import { Card, CardHeader, CardTitle, CardFooter } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Link, useParams } from "react-router-dom"
import { ArrowRight } from "lucide-react"
import { AppSidebar } from "@/components/CustomSidebar"
import { SidebarInset, SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { Breadcrumb, BreadcrumbItem, BreadcrumbList } from "@/components/ui/breadcrumb"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useRequireAuth } from "@/lib/randomFunctions"
import { useAxiosPrivate } from "@/axios"

export default function ResearchPaper() {
  const { id } = useParams()
  const [dataPaper, setDataPaper] = useState(null)
  const [dataRecommendations, setDataRecommendations] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [progress, setProgress] = useState(13)
  const axiosPrivateInstance = useAxiosPrivate()
  useRequireAuth()

  useEffect(() => {
    async function getPaper() {
      setIsLoading(true)
      setProgress(13)
      try {
        const responsePaper = await axiosPrivateInstance.post("paper", { id })
        setDataPaper(responsePaper?.data)
        setProgress(65)

        if (responsePaper?.data?.title) {
          const responseRecommendations = await axiosPrivateInstance.post("search", {
            query: responsePaper.data.title,
          })
          setDataRecommendations(responseRecommendations?.data)
          setProgress(100)
        }
      } catch (error) {
        console.error("Error fetching paper data:", error)
      } finally {
        setTimeout(() => {
          setIsLoading(false)
        }, 400)
      }
    }
    getPaper()
  }, [id])

  if (!dataPaper) {
    return (
      <SidebarProvider>
        <div className="flex">
          <AppSidebar className="hidden md:block" />
        </div>
      </SidebarProvider>
    )
  }

  return (
    <SidebarProvider>
      <div className="flex">
        <AppSidebar className="hidden md:block" />
        <SidebarInset>
          <div className="flex-1 flex flex-col min-h-screen max-w-full overflow-x-hidden">
            {/* Header */}
            <header className="ml-3 flex h-12 md:h-16 mb-2 text-foreground shrink-0 items-center transition-[width,height] ease-linear justify-between backdrop-filter bg-opacity-5 sticky top-0 z-50 backdrop-blur-md">
              <div className="flex items-center gap-2">
                <SidebarTrigger />
                <Separator orientation="vertical" className="h-4" />
                <Breadcrumb>
                  <BreadcrumbList>
                    <BreadcrumbItem>
                      <Link to="/home" className="flex flex-row">Home</Link>
                    </BreadcrumbItem>
                  </BreadcrumbList>
                </Breadcrumb>
              </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 px-4 pb-8 overflow-y-auto min-h-screen max-w-full">
              <div className="max-w-6xl mx-auto">
                <h1 className="text-2xl font-bold mb-4">{dataPaper.title}</h1>
                <p className="text-sm text-muted-foreground mb-4">{dataPaper.authors}</p>

                {/* Paper Display */}
                <div className="w-full h-[75vh] bg-muted rounded-lg overflow-hidden mb-8">
                  <iframe
                    src={dataPaper.url.startsWith("http://") ? dataPaper.url.replace("http://", "https://") : dataPaper.url}
                    className="w-full h-full"
                    title={dataPaper.title}
                  />
                </div>

                {/* Recommended Papers */}
                <div className="mt-8">
                  <h2 className="text-xl font-semibold mb-4">Recommended Papers</h2>
                  {isLoading ? (
                    <div className="space-y-4">
                      <Progress value={progress} className="w-full" />
                      <div className="h-72 w-full rounded-md border bg-muted/50 animate-pulse" />
                    </div>
                  ) : (
                    <ScrollArea className="h-72 w-full rounded-md border">
                      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 p-4">
                        {dataRecommendations.map((rec, index) => (
                          <Card key={index} className="bg-muted/50">
                            <CardHeader className="p-4">
                              <CardTitle className="flex justify-between items-start text-base">
                                <Link
                                  to={`/paper/${rec.id}`}
                                  className="hover:text-primary transition-colors line-clamp-2"
                                >
                                  {rec.title}
                                </Link>
                                <Link to={`/paper/${rec.id}`} className="ml-2 flex-shrink-0">
                                  <ArrowRight className="h-4 w-4" />
                                </Link>
                              </CardTitle>
                            </CardHeader>
                            <CardFooter className="p-4 pt-0">
                              <p className="text-xs text-muted-foreground line-clamp-1">{rec.authors}</p>
                            </CardFooter>
                          </Card>
                        ))}
                      </div>
                    </ScrollArea>
                  )}
                </div>
              </div>
            </main>
          </div>
        </SidebarInset>
      </div>
    </SidebarProvider>
  )
}
