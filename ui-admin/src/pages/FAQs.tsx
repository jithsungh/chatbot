import React, { useState, useMemo } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Search,
  Filter,
  BookOpen,
  HelpCircle,
  ChevronRight,
  Star,
  Lightbulb,
  AlertTriangle,
  CheckCircle,
  List,
  ArrowRight,
  ExternalLink,
  Rocket,
  Navigation,
  Upload,
  MessageSquare,
  Building,
  Shield,
  Bot,
  X,
  Heart,
  AlertCircle,
  BarChart3,
} from "lucide-react";
import faqData from "@/data/faqData.json";

// Icon mapping for categories
const categoryIcons = {
  Rocket,
  Navigation,
  Upload,
  MessageSquare,
  Building,
  Shield,
  Bot,
  AlertTriangle,
  CheckCircle,
  BarChart3,
};

interface FAQ {
  id: string;
  question: string;
  answer: string;
  steps?: string[];
  tips?: string[];
  details?: any;
  features?: string[];
  guidelines?: string[];
  structure?: string[];
  tasks?: string[];
  schedule?: string[];
  operations?: string[];
  warnings?: string[];
  roles?: string[];
  restrictions?: string[];
  "common-causes"?: string[];
  limitations?: string[];
  tags: string[];
  // New properties for enhanced FAQ content
  best_practices?: string[];
  examples?: string[];
  troubleshooting?: string[];
  supported_formats?: string[];
  actions?: string[];
  filters?: string[];
  search_capabilities?: string[];
  filtering_options?: string[];
  common_issues?: string[];
  troubleshooting_steps?: string[];
  prevention_tips?: string[];
  sections?: string[];
  profile_info?: string[];
}

interface Category {
  id: string;
  title: string;
  icon: string;
  description: string;
  faqs: FAQ[];
}

interface QuickLink {
  title: string;
  category: string;
  faqId: string;
}

const FAQs = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedFAQ, setSelectedFAQ] = useState<FAQ | null>(null);
  const [selectedFAQCategory, setSelectedFAQCategory] =
    useState<Category | null>(null);
  const [activeView, setActiveView] = useState<"categories" | "search">(
    "categories"
  );

  const categories: Category[] = faqData.categories;
  const quickLinks: QuickLink[] = faqData.quickLinks;
  // Enhanced search functionality
  const searchInObject = (obj: any, query: string): boolean => {
    const searchLower = query.toLowerCase();

    if (typeof obj === "string") {
      return obj.toLowerCase().includes(searchLower);
    }

    if (Array.isArray(obj)) {
      return obj.some((item) => searchInObject(item, query));
    }

    if (typeof obj === "object" && obj !== null) {
      return Object.values(obj).some((value) => searchInObject(value, query));
    }

    return false;
  };

  // Filter FAQs based on search and category with enhanced search
  const filteredContent = useMemo(() => {
    let allFAQs: { faq: FAQ; category: Category; relevanceScore: number }[] =
      [];

    // Collect all FAQs with their categories
    categories.forEach((category) => {
      category.faqs.forEach((faq) => {
        let relevanceScore = 0;

        if (searchQuery.trim()) {
          const query = searchQuery.toLowerCase();

          // Calculate relevance score based on matches
          if (faq.question.toLowerCase().includes(query)) relevanceScore += 10;
          if (faq.answer.toLowerCase().includes(query)) relevanceScore += 5;
          if (faq.tags.some((tag) => tag.toLowerCase().includes(query)))
            relevanceScore += 3;

          // Search in all nested properties
          if (searchInObject(faq, query)) {
            relevanceScore += 1;
          }

          // Only include if there's a match
          if (relevanceScore > 0) {
            allFAQs.push({ faq, category, relevanceScore });
          }
        } else {
          allFAQs.push({ faq, category, relevanceScore: 1 });
        }
      });
    });

    // Apply category filter
    if (selectedCategory !== "all") {
      allFAQs = allFAQs.filter(
        ({ category }) => category.id === selectedCategory
      );
    }

    // Sort by relevance score (higher first) when searching
    if (searchQuery.trim()) {
      allFAQs.sort((a, b) => b.relevanceScore - a.relevanceScore);
    }

    return allFAQs.map(({ faq, category }) => ({ faq, category }));
  }, [searchQuery, selectedCategory, categories]);

  // Get filtered categories for category view
  const filteredCategories = useMemo(() => {
    if (selectedCategory === "all" && !searchQuery.trim()) {
      return categories;
    }

    return categories
      .filter((category) => {
        if (selectedCategory !== "all" && category.id !== selectedCategory) {
          return false;
        }

        if (searchQuery.trim()) {
          return category.faqs.some(
            (faq) =>
              faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
              faq.answer.toLowerCase().includes(searchQuery.toLowerCase()) ||
              faq.tags.some((tag) =>
                tag.toLowerCase().includes(searchQuery.toLowerCase())
              )
          );
        }

        return true;
      })
      .map((category) => ({
        ...category,
        faqs: category.faqs.filter(
          (faq) =>
            !searchQuery.trim() ||
            faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
            faq.answer.toLowerCase().includes(searchQuery.toLowerCase()) ||
            faq.tags.some((tag) =>
              tag.toLowerCase().includes(searchQuery.toLowerCase())
            )
        ),
      }));
  }, [categories, selectedCategory, searchQuery]);

  const handleFAQClick = (faq: FAQ, category: Category) => {
    setSelectedFAQ(faq);
    setSelectedFAQCategory(category);
  };

  const handleQuickLinkClick = (quickLink: QuickLink) => {
    const category = categories.find((cat) => cat.id === quickLink.category);
    const faq = category?.faqs.find((f) => f.id === quickLink.faqId);

    if (faq && category) {
      handleFAQClick(faq, category);
    }
  };

  const clearSearch = () => {
    setSearchQuery("");
    setSelectedCategory("all");
    setActiveView("categories");
  };
  const renderFAQDetail = (faq: FAQ, category: Category) => {
    const IconComponent =
      categoryIcons[category.icon as keyof typeof categoryIcons];

    // Helper function to render any array-based content
    const renderContentSection = (
      title: string,
      items: string[],
      icon: any,
      bgColor: string,
      textColor: string,
      borderColor: string
    ) => {
      if (!items || items.length === 0) return null;

      const IconComp = icon;
      return (
        <div
          className={`${bgColor} p-6 rounded-lg border ${borderColor} shadow-sm`}
        >
          <div className="flex items-center space-x-2 mb-4">
            <IconComp className={`w-5 h-5 ${textColor}`} />
            <h4
              className={`font-semibold ${textColor
                .replace("text-", "text-")
                .replace("-600", "-900")}`}
            >
              {title}
            </h4>
          </div>
          <ul className="space-y-2">
            {items.map((item, index) => (
              <li key={index} className="flex items-start space-x-3">
                <div
                  className={`w-2 h-2 ${textColor.replace(
                    "-600",
                    "-500"
                  )} rounded-full mt-2 flex-shrink-0`}
                ></div>
                <span
                  className={`text-sm ${textColor.replace(
                    "-600",
                    "-800"
                  )} leading-relaxed`}
                >
                  {item}
                </span>
              </li>
            ))}
          </ul>
        </div>
      );
    };

    return (
      <div className="space-y-6">
        {/* Header with category and question */}
        <div className="bg-gradient-to-r from-primary/5 to-accent/5 p-6 rounded-lg border border-primary/20">
          <div className="flex items-start space-x-4">
            {IconComponent && (
              <div className="p-3 bg-primary/10 rounded-lg">
                <IconComponent className="w-6 h-6 text-primary" />
              </div>
            )}
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-3">
                <Badge
                  variant="outline"
                  className="bg-primary/10 text-primary border-primary/30"
                >
                  {category.title}
                </Badge>
                <Badge variant="secondary" className="text-xs">
                  {category.description}
                </Badge>
              </div>
              <h3 className="text-2xl font-bold mb-3 text-foreground">
                {faq.question}
              </h3>
              <div className="prose prose-sm max-w-none">
                <p className="text-muted-foreground leading-relaxed text-base">
                  {faq.answer}
                </p>
              </div>
            </div>
          </div>
        </div>
        {/* Steps */}
        {faq.steps && faq.steps.length > 0 && (
          <div className="bg-gradient-to-br from-blue-50 to-blue-100/50 p-6 rounded-lg border border-blue-200 shadow-sm">
            <div className="flex items-center space-x-2 mb-4">
              <div className="p-2 bg-blue-600 rounded-lg">
                <List className="w-5 h-5 text-white" />
              </div>
              <h4 className="font-semibold text-blue-900 text-lg">
                Step-by-Step Guide
              </h4>
            </div>
            <div className="space-y-3">
              {faq.steps.map((step, index) => (
                <div
                  key={index}
                  className="flex items-start space-x-4 p-3 bg-white/60 rounded-lg border border-blue-200/50"
                >
                  <div className="flex-shrink-0 w-8 h-8 bg-gradient-to-br from-blue-600 to-blue-700 text-white rounded-full flex items-center justify-center text-sm font-bold shadow-md">
                    {index + 1}
                  </div>
                  <span className="text-sm text-blue-900 leading-relaxed font-medium flex-1">
                    {step}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}{" "}
        {/* All content sections using the helper function */}
        {renderContentSection(
          "Helpful Tips",
          faq.tips,
          Lightbulb,
          "bg-gradient-to-br from-green-50 to-emerald-50",
          "text-green-600",
          "border-green-200"
        )}
        {renderContentSection(
          "Key Features",
          faq.features,
          Star,
          "bg-gradient-to-br from-purple-50 to-violet-50",
          "text-purple-600",
          "border-purple-200"
        )}
        {renderContentSection(
          "Guidelines",
          faq.guidelines,
          BookOpen,
          "bg-gradient-to-br from-indigo-50 to-blue-50",
          "text-indigo-600",
          "border-indigo-200"
        )}
        {renderContentSection(
          "Best Practices",
          faq.best_practices,
          CheckCircle,
          "bg-gradient-to-br from-cyan-50 to-sky-50",
          "text-cyan-600",
          "border-cyan-200"
        )}
        {renderContentSection(
          "Examples",
          faq.examples,
          Lightbulb,
          "bg-gradient-to-br from-yellow-50 to-amber-50",
          "text-yellow-600",
          "border-yellow-200"
        )}
        {renderContentSection(
          "Troubleshooting",
          faq.troubleshooting,
          AlertTriangle,
          "bg-gradient-to-br from-orange-50 to-red-50",
          "text-orange-600",
          "border-orange-200"
        )}
        {renderContentSection(
          "Important Warnings",
          faq.warnings,
          AlertTriangle,
          "bg-gradient-to-br from-red-50 to-rose-50",
          "text-red-600",
          "border-red-200"
        )}
        {renderContentSection(
          "Available Operations",
          faq.operations,
          List,
          "bg-gradient-to-br from-slate-50 to-gray-50",
          "text-slate-600",
          "border-slate-200"
        )}
        {renderContentSection(
          "Supported Formats",
          faq.supported_formats,
          CheckCircle,
          "bg-gradient-to-br from-teal-50 to-green-50",
          "text-teal-600",
          "border-teal-200"
        )}
        {renderContentSection(
          "Limitations",
          faq.limitations,
          AlertTriangle,
          "bg-gradient-to-br from-amber-50 to-orange-50",
          "text-amber-600",
          "border-amber-200"
        )}
        {renderContentSection(
          "Available Actions",
          faq.actions,
          ArrowRight,
          "bg-gradient-to-br from-blue-50 to-indigo-50",
          "text-blue-600",
          "border-blue-200"
        )}
        {renderContentSection(
          "Available Filters",
          faq.filters,
          Filter,
          "bg-gradient-to-br from-violet-50 to-purple-50",
          "text-violet-600",
          "border-violet-200"
        )}
        {renderContentSection(
          "Search Capabilities",
          faq.search_capabilities,
          Search,
          "bg-gradient-to-br from-pink-50 to-rose-50",
          "text-pink-600",
          "border-pink-200"
        )}
        {renderContentSection(
          "Filtering Options",
          faq.filtering_options,
          Filter,
          "bg-gradient-to-br from-emerald-50 to-teal-50",
          "text-emerald-600",
          "border-emerald-200"
        )}
        {renderContentSection(
          "Common Issues",
          faq.common_issues,
          AlertCircle,
          "bg-gradient-to-br from-red-50 to-pink-50",
          "text-red-600",
          "border-red-200"
        )}
        {renderContentSection(
          "Troubleshooting Steps",
          faq.troubleshooting_steps,
          List,
          "bg-gradient-to-br from-blue-50 to-cyan-50",
          "text-blue-600",
          "border-blue-200"
        )}
        {renderContentSection(
          "Prevention Tips",
          faq.prevention_tips,
          Shield,
          "bg-gradient-to-br from-green-50 to-lime-50",
          "text-green-600",
          "border-green-200"
        )}
        {/* Special sections with custom rendering */}
        {faq.details && (
          <div className="bg-gradient-to-br from-gray-50 to-slate-50 p-6 rounded-lg border border-gray-200 shadow-sm">
            <div className="flex items-center space-x-2 mb-4">
              <div className="p-2 bg-gray-600 rounded-lg">
                <BookOpen className="w-5 h-5 text-white" />
              </div>
              <h4 className="font-semibold text-gray-900 text-lg">
                Additional Details
              </h4>
            </div>
            <div className="space-y-4">
              {Object.entries(faq.details).map(([key, value]) => (
                <div
                  key={key}
                  className="p-4 bg-white/60 rounded-lg border border-gray-200/50"
                >
                  <h5 className="font-medium text-gray-800 mb-2 capitalize">
                    {key.replace(/_/g, " ")}
                  </h5>{" "}
                  {Array.isArray(value) ? (
                    <ul className="space-y-1">
                      {value.map((item: string, index: number) => (
                        <li
                          key={index}
                          className="text-sm text-gray-700 flex items-start space-x-2"
                        >
                          <div className="w-1.5 h-1.5 bg-gray-400 rounded-full mt-2 flex-shrink-0"></div>
                          <span>{item}</span>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-gray-700">{String(value)}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
        {/* Tags */}
        {faq.tags && faq.tags.length > 0 && (
          <div className="pt-4 border-t border-border">
            <p className="text-sm text-muted-foreground mb-2">Related tags:</p>
            <div className="flex flex-wrap gap-2">
              {faq.tags.map((tag, index) => (
                <Badge key={index} variant="secondary" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const renderCategoryCard = (category: Category) => {
    const IconComponent =
      categoryIcons[category.icon as keyof typeof categoryIcons];
    const visibleFAQs = searchQuery.trim()
      ? category.faqs.filter(
          (faq) =>
            faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
            faq.answer.toLowerCase().includes(searchQuery.toLowerCase()) ||
            faq.tags.some((tag) =>
              tag.toLowerCase().includes(searchQuery.toLowerCase())
            )
        )
      : category.faqs;

    if (searchQuery.trim() && visibleFAQs.length === 0) {
      return null;
    }

    return (
      <Card key={category.id} className="card-hover">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            {IconComponent && (
              <IconComponent className="w-5 h-5 text-primary" />
            )}
            <span>{category.title}</span>
            <Badge variant="outline">
              {visibleFAQs.length} FAQ{visibleFAQs.length !== 1 ? "s" : ""}
            </Badge>
          </CardTitle>
          <CardDescription>{category.description}</CardDescription>
        </CardHeader>
        <CardContent>
          <Accordion type="single" collapsible className="w-full">
            {visibleFAQs.map((faq, index) => (
              <AccordionItem key={faq.id} value={faq.id}>
                <AccordionTrigger className="text-left">
                  <div className="flex items-center justify-between w-full pr-4">
                    <span className="text-sm font-medium">{faq.question}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleFAQClick(faq, category);
                      }}
                      className="ml-2 h-6 w-6 p-0"
                    >
                      <ExternalLink className="w-3 h-3" />
                    </Button>
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="space-y-3 pt-2">
                    <p className="text-sm text-muted-foreground leading-relaxed">
                      {faq.answer}
                    </p>
                    {faq.steps && faq.steps.length > 0 && (
                      <div className="text-xs text-muted-foreground">
                        <p className="font-medium mb-1">Quick steps:</p>
                        <p>{faq.steps.slice(0, 2).join(" → ")}...</p>
                      </div>
                    )}
                    <div className="flex items-center justify-between">
                      <div className="flex flex-wrap gap-1">
                        {faq.tags.slice(0, 3).map((tag, tagIndex) => (
                          <Badge
                            key={tagIndex}
                            variant="secondary"
                            className="text-xs"
                          >
                            {tag}
                          </Badge>
                        ))}
                      </div>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleFAQClick(faq, category)}
                        className="text-xs h-6"
                      >
                        View Details
                      </Button>
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Help & Documentation
          </h1>
          <p className="text-muted-foreground mt-1">
            Complete user manual and FAQs for the admin interface
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant={activeView === "categories" ? "default" : "outline"}
            size="sm"
            onClick={() => setActiveView("categories")}
          >
            <BookOpen className="w-4 h-4 mr-2" />
            Categories
          </Button>
          <Button
            variant={activeView === "search" ? "default" : "outline"}
            size="sm"
            onClick={() => setActiveView("search")}
          >
            <Search className="w-4 h-4 mr-2" />
            Search All
          </Button>
        </div>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search FAQs, topics, or keywords..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
              {searchQuery && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={clearSearch}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 h-6 w-6 p-0"
                >
                  <X className="w-4 h-4" />
                </Button>
              )}
            </div>
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-muted-foreground" />
              <Select
                value={selectedCategory}
                onValueChange={setSelectedCategory}
              >
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  {categories.map((category) => (
                    <SelectItem key={category.id} value={category.id}>
                      {category.title}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Search Results Summary */}
          {(searchQuery.trim() || selectedCategory !== "all") && (
            <div className="mt-3 pt-3 border-t border-border">
              <p className="text-sm text-muted-foreground">
                {activeView === "categories" ? (
                  <>
                    Showing{" "}
                    {filteredCategories.reduce(
                      (sum, cat) => sum + cat.faqs.length,
                      0
                    )}{" "}
                    FAQ(s) in {filteredCategories.length} categor
                    {filteredCategories.length !== 1 ? "ies" : "y"}
                  </>
                ) : (
                  <>Showing {filteredContent.length} matching FAQ(s)</>
                )}
                {(searchQuery.trim() || selectedCategory !== "all") && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={clearSearch}
                    className="ml-2 h-5 px-2 text-xs"
                  >
                    Clear filters
                  </Button>
                )}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Quick Links */}
      {!searchQuery.trim() && selectedCategory === "all" && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Heart className="w-5 h-5 text-red-500" />
              <span>Popular Topics</span>
            </CardTitle>
            <CardDescription>
              Quick access to frequently needed information
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {quickLinks.map((link, index) => (
                <Button
                  key={index}
                  variant="outline"
                  className="justify-start h-auto p-3"
                  onClick={() => handleQuickLinkClick(link)}
                >
                  <div className="flex items-center space-x-2">
                    <ChevronRight className="w-4 h-4 text-primary" />
                    <span className="text-sm">{link.title}</span>
                  </div>
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Content */}
      <Tabs
        value={activeView}
        onValueChange={(value) =>
          setActiveView(value as "search" | "categories")
        }
        className="w-full"
      >
        <TabsContent value="categories" className="mt-0">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredCategories.map(renderCategoryCard)}
          </div>

          {filteredCategories.length === 0 && (
            <Card>
              <CardContent className="p-12 text-center">
                <HelpCircle className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-lg font-medium mb-2">No FAQs found</p>
                <p className="text-muted-foreground">
                  Try adjusting your search terms or clearing filters
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="search" className="mt-0">
          <div className="space-y-4">
            {filteredContent.map(({ faq, category }) => (
              <Card key={`${category.id}-${faq.id}`} className="card-hover">
                <CardContent className="p-4">
                  <div className="flex items-start justify-between space-x-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <Badge variant="outline">{category.title}</Badge>
                        {faq.tags.slice(0, 2).map((tag, index) => (
                          <Badge
                            key={index}
                            variant="secondary"
                            className="text-xs"
                          >
                            {tag}
                          </Badge>
                        ))}
                      </div>
                      <h3 className="font-semibold mb-2">{faq.question}</h3>
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {faq.answer}
                      </p>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleFAQClick(faq, category)}
                    >
                      <ExternalLink className="w-4 h-4 mr-2" />
                      View
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {filteredContent.length === 0 && (
            <Card>
              <CardContent className="p-12 text-center">
                <Search className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-lg font-medium mb-2">
                  No matching FAQs found
                </p>
                <p className="text-muted-foreground">
                  Try different keywords or browse by categories
                </p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>

      {/* FAQ Detail Dialog */}
      <Dialog open={!!selectedFAQ} onOpenChange={() => setSelectedFAQ(null)}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center space-x-2">
              <HelpCircle className="w-5 h-5 text-primary" />
              <span>FAQ Details</span>
            </DialogTitle>
            <DialogDescription>
              {selectedFAQCategory?.description}
            </DialogDescription>
          </DialogHeader>

          {selectedFAQ && selectedFAQCategory && (
            <div className="mt-4">
              {renderFAQDetail(selectedFAQ, selectedFAQCategory)}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default FAQs;
