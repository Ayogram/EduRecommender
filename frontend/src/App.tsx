import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Search,
  Bell,
  BookOpen,
  Settings,
  MoreHorizontal,
  ChevronDown,
  LogOut,
  LayoutDashboard,
  Compass,
  List,
  MessageSquare,
  PlayCircle,
  GraduationCap,
  Star,
  CheckCircle2,
  TrendingUp
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Progress } from '@/components/ui/progress'

export default function App() {
  const [activeNav, setActiveNav] = useState('My Courses')
  
  const [loading, setLoading] = useState(true)
  const [user, setUser] = useState({ name: 'Student', email: '', gpa: 0, department: '' })
  const [courses, setCourses] = useState<any[]>([])
  const [recs, setRecs] = useState<any[]>([])

  useEffect(() => {
    fetch('/api/dashboard')
      .then(res => {
        if (res.status === 401) {
          window.location.href = '/login'
          return null
        }
        return res.json()
      })
      .then(data => {
        if (data) {
          setUser(data.user)
          setCourses(data.enrolled || [])
          setRecs(data.recommendations || [])
        }
        setLoading(false)
      })
      .catch(err => {
        console.error("Failed to fetch dashboard data:", err)
        setLoading(false)
      })
  }, [])

  if (loading) {
    return <div className="h-screen w-full flex items-center justify-center bg-background text-primary">Loading EduRecommender...</div>
  }

  // Calculate Stats
  const completedCount = courses.filter(c => c.completed).length;
  const ratedCourses = courses.filter(c => c.rating && c.rating > 0);
  const avgRating = ratedCourses.length > 0 
    ? (ratedCourses.reduce((sum, c) => sum + c.rating, 0) / ratedCourses.length).toFixed(1) 
    : '0.0';

  return (
    <div className="flex h-screen w-full bg-background overflow-hidden text-foreground selection:bg-primary/20">
      
      {/* LEFT SIDEBAR - Adapted to EduRecommender */}
      <motion.aside 
        initial={{ x: -250 }}
        animate={{ x: 0 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        className="w-[260px] flex-shrink-0 border-r border-border bg-card/50 backdrop-blur-sm flex flex-col justify-between"
      >
        <div>
          {/* Logo & Brand */}
          <div className="h-20 flex items-center px-6 border-b border-border/50">
            <div className="flex items-center gap-3 w-full">
              <div className="w-9 h-9 rounded-xl bg-primary text-white flex items-center justify-center shadow-md shadow-primary/20">
                <GraduationCap className="w-5 h-5" />
              </div>
              <div className="flex-1 overflow-hidden">
                <h3 className="font-bold text-[15px] tracking-tight truncate text-foreground">EduRecommender</h3>
                <p className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider mt-0.5 truncate">Student Portal</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="p-4 space-y-1.5 mt-2">
            {[
              { icon: LayoutDashboard, label: 'My Courses' },
              { icon: Compass, label: 'Get Recommendations' },
              { icon: List, label: 'Browse All' },
              { icon: Bell, label: 'Notifications', badge: 2 },
              { icon: MessageSquare, label: 'Help Desk' },
            ].map((item) => (
              <div
                key={item.label}
                onClick={() => setActiveNav(item.label)}
                className={`flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer transition-all duration-200 ease-out group
                  ${activeNav === item.label 
                    ? 'bg-primary text-primary-foreground font-medium shadow-md shadow-primary/20' 
                    : 'text-muted-foreground hover:bg-black/5 hover:text-foreground'
                  }
                `}
              >
                <div className="flex items-center gap-3">
                  <item.icon className={`w-4 h-4 ${activeNav === item.label ? 'opacity-100' : 'opacity-70 group-hover:opacity-100'}`} />
                  <span className="text-[13px]">{item.label}</span>
                </div>
                {item.badge && (
                  <Badge variant="secondary" className={`px-1.5 py-0.5 min-w-[20px] h-[20px] flex items-center justify-center rounded-full text-[10px] border-none shadow-none ${activeNav === item.label ? 'bg-white/20 text-white' : 'bg-primary/10 text-primary'}`}>
                    {item.badge}
                  </Badge>
                )}
              </div>
            ))}
          </nav>
        </div>

        {/* User Footer */}
        <div className="p-4 border-t border-border/50">
          <div className="flex items-center justify-between p-2 rounded-xl hover:bg-black/5 cursor-pointer transition-colors group">
            <div className="flex items-center gap-3">
              <Avatar className="w-9 h-9 border border-border/50 shadow-sm">
                <AvatarImage src="/static/img/default_avatar.png" />
                <AvatarFallback className="bg-primary/10 text-primary text-xs font-semibold">
                  {user.name.charAt(0).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div>
                <p className="text-[13px] font-semibold leading-tight group-hover:text-primary transition-colors">{user.name.split(' ')[0]}</p>
                <p className="text-[11px] text-muted-foreground">{user.department || 'Student'}</p>
              </div>
            </div>
            <LogOut className="w-4 h-4 text-muted-foreground opacity-50 group-hover:opacity-100 group-hover:text-destructive transition-all" onClick={() => window.location.href = '/logout'} />
          </div>
        </div>
      </motion.aside>

      {/* MAIN CONTENT AREA */}
      <main className="flex-1 flex flex-col min-w-0 bg-[#F7F7FA]">
        
        {/* TOPBAR */}
        <header className="h-20 flex items-center justify-between px-8 z-10 sticky top-0">
          <div className="flex items-center gap-4 w-96">
            <h1 className="text-xl font-bold tracking-tight text-foreground">Overview</h1>
          </div>
          
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <Input 
                placeholder="Search courses..." 
                className="w-64 pl-9 bg-card border-none rounded-full shadow-sm shadow-black/5 focus-visible:ring-1 focus-visible:ring-primary/30 h-10 text-[13px]"
              />
            </div>
            <Button variant="ghost" size="icon" className="rounded-full w-10 h-10 bg-card border-none shadow-sm shadow-black/5 text-muted-foreground hover:text-foreground hover:bg-card">
              <Settings className="w-4 h-4" />
            </Button>
          </div>
        </header>

        {/* DASHBOARD CONTENT */}
        <ScrollArea className="flex-1 px-8 pb-12">
          <div className="max-w-[1200px] mx-auto space-y-8 pb-12 pt-2">
            
            {/* GREETING BANNER */}
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.1 }}
              className="relative overflow-hidden rounded-[24px] bg-gradient-to-br from-primary to-primary/80 text-white p-8 shadow-lg shadow-primary/20 border border-primary/20"
            >
              <div className="absolute top-[-50%] right-[-10%] w-[300px] h-[300px] bg-white/10 rounded-full blur-3xl" />
              <div className="absolute bottom-[-20%] left-[20%] w-[200px] h-[200px] bg-black/10 rounded-full blur-2xl" />
              
              <div className="relative z-10 flex items-center justify-between">
                <div className="space-y-3 max-w-xl">
                  <h2 className="text-3xl font-bold tracking-tight flex items-center gap-3">
                    Good Morning, {user.name.split(' ')[0]}
                    <span className="animate-[wave_2s_infinite] origin-bottom-right inline-block text-2xl">👋</span>
                  </h2>
                  <p className="text-white/80 text-[15px] leading-relaxed">
                    {courses.length > 0 
                      ? `You're currently taking ${courses.length} courses. We've found ${recs.length} new opportunities for you today!`
                      : "Ready to start your academic journey? Let's find your first course."}
                  </p>
                  <div className="pt-2 flex items-center gap-3">
                    <Button className="bg-white text-primary hover:bg-white/90 rounded-full px-6 shadow-sm font-semibold">
                      <Compass className="w-4 h-4 mr-2" /> Get Recommendations
                    </Button>
                    <Button variant="outline" className="bg-transparent border-white/30 text-white hover:bg-white/10 rounded-full px-6 font-semibold">
                      <List className="w-4 h-4 mr-2" /> Browse Catalog
                    </Button>
                  </div>
                </div>

                <div className="hidden md:flex flex-col items-center justify-center p-6 bg-white/10 backdrop-blur-md rounded-[20px] border border-white/20 min-w-[160px]">
                  <span className="text-white/70 text-xs font-semibold uppercase tracking-wider mb-1">Current CGPA</span>
                  <span className="text-4xl font-bold tracking-tighter">{user.gpa ? user.gpa.toFixed(2) : '0.00'}</span>
                  <Separator className="bg-white/20 w-full my-3" />
                  <span className="text-white/90 text-[11px] font-medium text-center">{user.department || 'General Student'}</span>
                </div>
              </div>
            </motion.div>

            {/* STATS GRID */}
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.4, delay: 0.2 }}
              className="grid grid-cols-2 md:grid-cols-4 gap-4"
            >
              {[
                { label: 'Enrolled Courses', value: courses.length, icon: BookOpen, color: 'text-primary', bg: 'bg-primary/10' },
                { label: 'Completed', value: completedCount, icon: CheckCircle2, color: 'text-emerald-500', bg: 'bg-emerald-500/10' },
                { label: 'AI Suggestions', value: recs.length, icon: Compass, color: 'text-amber-500', bg: 'bg-amber-500/10' },
                { label: 'Avg. Rating', value: avgRating, icon: Star, color: 'text-indigo-500', bg: 'bg-indigo-500/10' },
              ].map((stat, i) => (
                <Card key={i} className="border-none shadow-sm rounded-[20px] bg-card hover:shadow-md transition-shadow">
                  <CardContent className="p-5 flex items-center gap-4">
                    <div className={`w-12 h-12 rounded-[16px] flex items-center justify-center ${stat.bg} ${stat.color}`}>
                      <stat.icon className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="text-2xl font-bold tracking-tight text-foreground">{stat.value}</div>
                      <div className="text-xs font-medium text-muted-foreground">{stat.label}</div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
              {/* ENROLLED COURSES */}
              <div className="lg:col-span-7 space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-bold tracking-tight text-foreground flex items-center gap-2">
                    <BookOpen className="w-5 h-5 text-primary" /> Current Enrolled
                  </h2>
                  <Badge variant="secondary" className="bg-white shadow-sm border border-border/50 text-foreground px-3 py-1 rounded-full text-xs font-semibold">
                    {courses.length} Total
                  </Badge>
                </div>

                <div className="space-y-3">
                  {courses.length > 0 ? courses.map((course, i) => (
                    <motion.div key={course.id} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 + (i * 0.05) }}>
                      <Card className="border-none shadow-sm rounded-[20px] bg-card overflow-hidden group hover:shadow-md transition-all duration-300">
                        <CardContent className="p-5">
                          <div className="flex justify-between items-start mb-3">
                            <div>
                              <Badge className="bg-primary/5 text-primary hover:bg-primary/10 border-none shadow-none rounded-md px-2.5 py-0.5 text-[10px] font-bold tracking-wide uppercase mb-2">
                                {course.category}
                              </Badge>
                              <h3 className="font-bold text-[15px] leading-tight text-foreground">{course.title}</h3>
                            </div>
                            <div className="text-right">
                              <span className="text-lg font-bold text-primary block leading-none">{Math.round(course.progress || 0)}%</span>
                              <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-wider">Progress</span>
                            </div>
                          </div>
                          
                          <Progress value={course.progress || 0} className="h-1.5 mb-4 bg-primary/10" />

                          <div className="flex items-center justify-between mt-4 pt-4 border-t border-border/50">
                            <div className="flex items-center gap-4 text-xs font-medium text-muted-foreground">
                              <span className="flex items-center gap-1.5"><List className="w-3.5 h-3.5 text-primary/70" /> Module {course.current_module_id || 1}</span>
                              <span className="flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5 text-emerald-500/70" /> Grade: {course.grade || 'N/A'}</span>
                            </div>
                            <Button size="sm" className="rounded-full bg-primary/10 text-primary hover:bg-primary hover:text-white transition-colors text-xs font-semibold px-4 h-8">
                              Continue <PlayCircle className="w-3.5 h-3.5 ml-1.5" />
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  )) : (
                    <div className="text-center py-12 bg-card rounded-[24px] border border-dashed border-border/60">
                      <BookOpen className="w-8 h-8 text-muted-foreground/30 mx-auto mb-3" />
                      <h4 className="text-sm font-semibold text-foreground">No courses enrolled yet</h4>
                      <p className="text-xs text-muted-foreground mt-1 mb-4">Start your journey by exploring recommendations.</p>
                      <Button className="rounded-full shadow-sm text-xs h-8 px-4">Browse Catalog</Button>
                    </div>
                  )}
                </div>
              </div>

              {/* AI RECOMMENDATIONS */}
              <div className="lg:col-span-5 space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-lg font-bold tracking-tight text-foreground flex items-center gap-2">
                    <Star className="w-5 h-5 text-amber-500" /> AI Top Picks
                  </h2>
                  <Button variant="link" className="text-xs font-semibold text-muted-foreground hover:text-primary px-0">View All</Button>
                </div>

                <div className="space-y-3">
                  {recs.length > 0 ? recs.slice(0, 4).map((rec, i) => (
                    <motion.div key={rec.id} initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 + (i * 0.05) }}>
                      <Card className="border-none shadow-sm rounded-[20px] bg-card hover:bg-card/80 transition-colors cursor-pointer group relative overflow-hidden">
                        <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary/20 group-hover:bg-primary transition-colors" />
                        <CardContent className="p-4 pl-5 flex gap-4 items-center">
                          <div className="w-12 h-12 rounded-[14px] bg-primary/5 border border-primary/10 flex items-center justify-center flex-shrink-0 text-primary font-bold text-sm">
                            {Math.round(rec.score * 100)}%
                          </div>
                          <div className="flex-1 min-w-0">
                            <h4 className="font-bold text-[14px] leading-tight truncate text-foreground mb-1">{rec.title}</h4>
                            <div className="flex items-center gap-3 text-[11px] font-medium text-muted-foreground">
                              <span className="truncate">{rec.category}</span>
                              <span className="flex items-center gap-1 text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded-md">
                                <TrendingUp className="w-3 h-3" /> {(rec.success_probability ? rec.success_probability * 100 : rec.score * 100).toFixed(0)}% Success
                              </span>
                            </div>
                          </div>
                          <ChevronDown className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 -rotate-90 transition-all" />
                        </CardContent>
                      </Card>
                    </motion.div>
                  )) : (
                    <div className="text-center py-10 bg-card rounded-[24px] border border-dashed border-border/60">
                      <Compass className="w-8 h-8 text-muted-foreground/30 mx-auto mb-3" />
                      <h4 className="text-sm font-semibold text-foreground">Calibrating AI...</h4>
                      <p className="text-xs text-muted-foreground mt-1">We need more data to generate matches.</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

          </div>
        </ScrollArea>
      </main>
    </div>
  )
}
