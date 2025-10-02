'use client';

import { AppSidebar } from "@/components/app-sidebar"
import { ChartLineMultiple } from "@/components/chart-area-interactive"
// import { DataTable } from "@/components/data-table"
// import { SectionCards } from "@/components/section-cards"
import { SiteHeader } from "@/components/site-header"
import {
  SidebarInset,
  SidebarProvider,
} from "@/components/ui/sidebar"
import useSWR from 'swr';

const fetcher = async (url: string) => {
  const res = await fetch(url);
  return res.json();
};

export default function Page() {
  const { data, isLoading, error } = useSWR(`/api/indexer`, fetcher, {
    refreshWhenOffline: false,
    revalidateOnFocus: false,
  });

  return (
    <SidebarProvider
      style={
        {
          "--sidebar-width": "calc(var(--spacing) * 72)",
          "--header-height": "calc(var(--spacing) * 12)",
        } as React.CSSProperties
      }
    >
      <AppSidebar variant="inset" />
      <SidebarInset>
        <SiteHeader title="Dashboard"/>
        <div className="flex flex-1 flex-col">
          <div className="@container/main flex flex-1 flex-col gap-2">
            <div className="pl-6 flex flex-row flex-wrap py-8 gap-0 md:py-6">
              {/* <SectionCards /> */}
              {/* @typescript-eslint/no-explicit-any */}
              
              {data?.filter((item: any) => { return item.active}).map((indexer: any, i: number) => {
                return (
                  <div className="pr-6 flex-shrink-0 w-full md:w-1/2 xl:w-1/3 pb-6" key={i}>
                    {/* <ChartLineDefault /> */}
                    {/* <ChartAreaInteractive indexer={indexer}/> */}
                    <ChartLineMultiple indexer={indexer}/>
                  </div>
                )
              })}
              
              {/* <DataTable data={data} /> */}
            </div>
          </div>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
