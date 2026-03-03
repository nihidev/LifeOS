"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { PageWrapper } from "@/components/layout/PageWrapper"
import { GroceryForm } from "@/components/features/grocery/GroceryForm"
import { GroceryList } from "@/components/features/grocery/GroceryList"
import { useGroceryItems } from "@/hooks/useGrocery"

export default function GroceryPage() {
  const { data: items = [], isLoading } = useGroceryItems()

  return (
    <PageWrapper>
      <div className="max-w-2xl mx-auto flex flex-col gap-6">
        <h1 className="text-2xl font-bold">Grocery List</h1>

        {/* Add item */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Add Item</CardTitle>
          </CardHeader>
          <CardContent>
            <GroceryForm />
          </CardContent>
        </Card>

        {/* List */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">
              {items.length > 0
                ? `${items.length} item${items.length === 1 ? "" : "s"}`
                : "Items"}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="flex flex-col gap-2">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-12 bg-muted animate-pulse rounded-lg" />
                ))}
              </div>
            ) : (
              <GroceryList items={items} />
            )}
          </CardContent>
        </Card>
      </div>
    </PageWrapper>
  )
}
